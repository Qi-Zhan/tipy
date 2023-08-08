from dataclasses import dataclass

from tipy.ast import Alloc, Assign, BinaryExpr, Call, Const, Deref, Function, If, Reference, Vardecl

from .analysis import Analysis, Constraint
from ..ast import *
from ..symbol import SymbolTable
from ..visitor import AstVisitor
from ..solver import UnionFindSolver
from ..type import *


@dataclass
class Equal(Constraint):
    """
    - left == right
    - left can be a type variable or an expression
    - right can be a type variable or an expression
    """
    left: Expr | Type
    right: Expr | Type



class TypeConstraitCollection(AstVisitor):
    @classmethod
    def collect(cls, source: Program):
        st = SymbolTable.build(source)
        tcc = TypeConstraitCollection(st)
        tcc.visit_program(source)
        return tcc.constraints

    def __init__(self, st: SymbolTable):
        self.constraints = []
        self.st = st

    def visit_input(self, node: Input):
        self.constraints.append(Equal(node, IntType()))

    def visit_output(self, node: Output):
        self.constraints.append(Equal(node.expr, IntType()))
        node.expr.accept(self)

    def visit_const(self, node: Const):
        match node.type_:
            case AstType.INT | AstType.BOOL:
                self.constraints.append(Equal(node, IntType()))
            case AstType.STRING:
                self.constraints.append(Equal(node, StringType()))
            case AstType.NULL:
                self.constraints.append(
                    Equal(node, PointerType(TypeVar.new())))
            case _:
                raise TypeError(f'Unknown type {node.type_}')

    def visit_assign(self, node: Assign):
        self.constraints.append(Equal(node.expr, node.name))
        match node.name:
            case DerefWrite(expr):
                self.constraints.append(Equal(PointerType(expr), node.expr))
            case _:
                pass

        node.expr.accept(self)
        node.name.accept(self)

    def visit_if(self, node: If):
        self.constraints.append(Equal(node.cond, IntType()))
        node.cond.accept(self)
        node.then.accept(self)
        if node.else_:
            node.else_.accept(self)

    def visit_while(self, node: While):
        self.constraints.append(Equal(node.cond, IntType()))
        node.cond.accept(self)
        node.body.accept(self)

    def visit_function(self, node: Function):
        returnstmt = node.body.returnstmt
        type1 = node
        type2 = FunctionType(node.parameters.params, returnstmt.expr)
        self.constraints.append(Equal(type1, type2))
        node.body.accept(self)
    
    def visit_vardecl(self, node: Vardecl):
        pass

    def visit_call(self, node: Call):
        """
        E(E1,..., En): [[E]] = ([[E1]], ..., [[En]]) -> [[node]]
        """
        type1 = node.name
        type2 = FunctionType(node.args, node)
        self.constraints.append(Equal(type1, type2))
        for arg in node.args:
            arg.accept(self)

    def visit_alloc(self, node: Alloc):
        """
        alloc E: [[alloc E]] = ↑[[E]]
        """
        self.constraints.append(Equal(node, PointerType(node.expr)))
        node.expr.accept(self)

    def visit_reference(self, node: Reference):
        """
        &E: [[&E]] = ↑[[E]]
        """
        self.constraints.append(Equal(node, PointerType(node.name)))
        node.name.accept(self)

    def visit_deref(self, node: Deref):
        """
        *E: [[E]] = ↑[[*E]]
        """
        self.constraints.append(Equal(PointerType(node), node.expr))
        node.expr.accept(self)

    def visit_id(self, node: Id):
        self.constraints.append(Equal(node, self.st.get(node)))

    def visit_binary_expr(self, node: BinaryExpr):
        match node.op:
            case Operator.EQ:
                self.constraints.append(Equal(node.left, node.right))
                self.constraints.append(Equal(node.left, IntType()))
                self.constraints.append(Equal(node, IntType()))
            case _:
                self.constraints.append(Equal(node, IntType()))
                self.constraints.append(Equal(node.left, node.right))
        node.left.accept(self)
        node.right.accept(self)


class TypeAnalysis(Analysis):

    @classmethod
    def run(cls, source: Program):
        constraits = TypeConstraitCollection.collect(source)
        for c in constraits:
            print(c)
        UnionFindSolver.solve(constraits)
