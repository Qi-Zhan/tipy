from dataclasses import dataclass

from .analysis import Analysis, Constraint
from ..ast import *
from ..symbol import SymbolTable
from ..visitor import AstVisitor
from ..solver import UnionFindSolver
from ..type import *
from ..log import get_logger

Logger = get_logger(__name__)
Logger.setLevel('DEBUG')


@dataclass
class Equal(Constraint):
    """
    left == right
    """
    left: Type
    right: Type


class TypeResult:
    def __init__(self, map2expr, map2type):
        self.map2type = map2type
        self.map2expr = map2expr

    def get_type(self, expr: Expr) -> Type:
        return self.map2type[id(expr)]


class TypeConstraitCollection(AstVisitor):
    """
    collect type constraints from an AST
    """
    @classmethod
    def collect(cls, source: Program) -> 'TypeConstraitCollection':
        tcc = TypeConstraitCollection(source)
        tcc.visit_program(source)
        return tcc

    def __init__(self, source: Program):
        self.constraints = []
        self._st = SymbolTable.build(source)
        self._map2type = dict()  # map from id to type
        self.map2expr = dict()  # map from id to expr
        self.map2type = dict()  # final map from id to type

    def close_map(self) -> TypeResult:
        """
        close the type constraint term, return the final type map
        - use recursive type to handle the case of circular reference
        """
        def close(t: Type, typevar: TypeVar = None) -> Type:
            """
            close the type constraint term, find the final result of t
            - t: the type to be closed
            - typevar: the type variable that t should ignore, it is used to handle the case of circular reference
            """

            # t is in recursive type, do not try to close it
            if typevar is not None and isinstance(typevar, TypeVar) and t == typevar:
                return t

            origin = t
            t = t.find_parent()
            # circular reference
            if t.contain(origin):
                Logger.debug(f'circular reference: {origin} -> {t}')
                match origin:  # 1 -> pointer(1)
                    case TypeVar(_):
                        # create a new type variable
                        t = RecursionType(origin, t)
                    case _: # pragma: no cover
                        print('circular reference not handled')
                        breakpoint()

            match t:
                case PointerType(inner):
                    return PointerType(close(inner, typevar))
                case FunctionType(params, return_type):
                    params = [close(param, typevar) for param in params]
                    return_type = close(return_type)
                    return FunctionType(params, return_type)
                case RecursionType(var, type_):
                    return RecursionType(var, close(type_, var))
                case _:
                    return t

        for (id, type_) in self._map2type.items():
            result = close(type_)
            # if type contains recursive type, replace it with the recursive type
            # **IMPORTANT: I don't if this is correct**
            recursive = result.contain_class(RecursionType)
            if recursive is not None:
                self.map2type[id] = recursive
            else:
                self.map2type[id] = result

        return TypeResult(self.map2expr, self.map2type)

    # @typecheck

    def _get_typevar(self, expr: Expr | Function) -> TypeVar:
        """
        assign a new type variable to expr and return it
        """
        if isinstance(expr, Function):
            expr = expr.name
        elif not isinstance(expr, Expr):
            assert False, f'expr must be an instance of Expr, got {expr}' # pragma: no cover
        expr_id = id(expr)
        if expr_id in self._map2type:
            return self._map2type[expr_id]
        typevar = TypeVar.new()
        self._map2type[expr_id] = typevar
        self.map2expr[typevar.id] = expr
        return typevar

    def _add(self, constraint: Constraint):
        self.constraints.append(constraint)

    def visit_input(self, node: Input):
        tv = self._get_typevar(node)
        self._add(Equal(tv, IntType()))

    def visit_output(self, node: Output):
        tv = self._get_typevar(node.expr)
        self._add(Equal(tv, IntType()))
        node.expr.accept(self)

    def visit_const(self, node: Const):
        tv = self._get_typevar(node)
        match node.type_:
            case AstType.INT | AstType.BOOL:
                self._add(Equal(tv, IntType()))
            case AstType.STRING:
                self._add(Equal(tv, StringType()))
            case AstType.NULL:
                self._add(
                    Equal(tv, PointerType(TypeVar.new())))
            case _: # pragma: no cover
                raise TypeError(f'Unknown type {node.type_}')

    def visit_assign(self, node: Assign):
        tv_left = self._get_typevar(node.name)
        tv_right = self._get_typevar(node.expr)
        self._add(Equal(tv_left, tv_right))
        match node.name:
            case DerefWrite(expr):
                tv_inner = self._get_typevar(expr)
                self._add(Equal(tv_inner, PointerType(tv_right)))
            case _:
                pass
        node.expr.accept(self)
        node.name.accept(self)

    def visit_if(self, node: If):
        tv = self._get_typevar(node.cond)
        self._add(Equal(tv, IntType()))
        node.cond.accept(self)
        node.then.accept(self)
        if node.else_:
            node.else_.accept(self)

    def visit_while(self, node: While):
        tv = self._get_typevar(node.cond)
        self._add(Equal(tv, IntType()))
        node.cond.accept(self)
        node.body.accept(self)

    def visit_function(self, node: Function):
        returnstmt = node.body.returnstmt
        tv_func = self._get_typevar(node)
        tv_params = [self._get_typevar(param)
                     for param in node.parameters.params]
        tv_return = self._get_typevar(returnstmt.expr)
        type2 = FunctionType(tv_params, tv_return)
        self._add(Equal(tv_func, type2))

        # main function returns int
        if node.name.value == 'main':
            self._add(Equal(tv_return, IntType()))

        node.body.accept(self)

    def visit_vardecl(self, node: Vardecl):
        pass

    def visit_call(self, node: Call):
        """
        E(E1,..., En): [[E]] = ([[E1]], ..., [[En]]) -> [[node]]
        """
        tv_args = [self._get_typevar(arg) for arg in node.args]
        tv_expr = self._get_typevar(node)
        typ = FunctionType(tv_args, tv_expr)
        tv_name = self._get_typevar(node.name)
        self._add(Equal(tv_name, typ))
        node.name.accept(self) # important:
        for arg in node.args:
            arg.accept(self)

    def visit_alloc(self, node: Alloc):
        """
        alloc E: [[alloc E]] = ↑[[E]]
        """
        tv = self._get_typevar(node)
        tv_expr = self._get_typevar(node.expr)
        self._add(Equal(tv, PointerType(tv_expr)))
        node.expr.accept(self)

    def visit_reference(self, node: Reference):
        """
        &E: [[&E]] = ↑[[E]]
        """
        tv = self._get_typevar(node)
        tv_name = self._get_typevar(node.name)
        self._add(Equal(tv, PointerType(tv_name)))
        node.name.accept(self)

    def visit_deref(self, node: Deref):
        """
        *E: [[E]] = ↑[[*E]]
        """
        tv = self._get_typevar(node)
        tv_expr = self._get_typevar(node.expr)
        self._add(Equal(PointerType(tv), tv_expr))
        node.expr.accept(self)

    def visit_id(self, node: Id):
        tv = self._get_typevar(node)
        real_node = self._st.get(node)
        tv_node = self._get_typevar(real_node)
        self._add(Equal(tv, tv_node))

    def visit_binary_expr(self, node: BinaryExpr):
        tv_left = self._get_typevar(node.left)
        tv_right = self._get_typevar(node.right)
        tv_node = self._get_typevar(node)
        match node.op:
            case Operator.EQ:
                self._add(Equal(tv_left, tv_right))
                self._add(Equal(tv_node, IntType()))
            case _:
                self._add(Equal(tv_node, IntType()))
                self._add(Equal(tv_left, IntType()))
                self._add(Equal(tv_right, IntType()))
        node.left.accept(self)
        node.right.accept(self)


class TypeAnalysis(Analysis):

    @classmethod
    def run(cls, source: Program):
        # collect constraints
        tcc = TypeConstraitCollection.collect(source)
        # solve constraints
        UnionFindSolver.solve(tcc.constraints)
        # build type map
        return tcc.close_map()
