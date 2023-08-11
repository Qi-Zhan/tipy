import enum
from dataclasses import dataclass

from lark import ast_utils, Token


class _Ast(ast_utils.Ast):
    def accept(self, _visitor): 
        raise NotImplementedError( # pragma: no cover
            'you should implement this method in subclass')


class Operator(enum.Enum):
    ADD = '+'
    SUB = '-'
    MUL = '*'
    DIV = '/'
    EQ = '=='
    NE = '!='
    LT = '<'
    GT = '>'
    LE = '<='
    GE = '>='
    REF = '&'
    DEREF = '*'


class AstType(enum.Enum):
    INT = 'int'
    BOOL = 'bool'
    STRING = 'string'
    VOID = 'void'
    NULL = 'null'


class Statement(_Ast):
    def accept(self, _visitor):
        raise NotImplementedError( # pragma: no cover
            'you should implement this method in subclass')

@dataclass
class Expr(_Ast):
    def accept(self, _visitor):
        raise NotImplementedError( # pragma: no cover
            'you should implement this method in subclass')


@dataclass
class Const(Expr):
    type_: AstType
    value: str | int | None

    def accept(self, visitor):
        visitor.visit_const(self)

    def dump(self, indent=0):
        assert (type(self.value) in (str, int, type(None))
                ), f'Const: Invalid type {type(self.value)}'
        print(' ' * indent, self.value, end=' ')


class Id(Expr):
    __match_args__ = tuple(['value'])

    token: Token
    value: str

    def __init__(self, token: Token):
        self.token = token
        self.value = token.value

    def accept(self, visitor):
        visitor.visit_id(self)

    def dump(self, indent=0):
        assert (type(self.value) == str), f'Id Invalid type {type(self.value)}'
        print(' ' * indent, self.value, end=' ')

    def __hash__(self) -> int:
        return id(self)

    def __str__(self) -> str:
        return f"{self.value}"


@dataclass
class BinaryExpr(Expr):
    left: Expr
    op: Operator
    right: Expr

    def accept(self, visitor):
        visitor.visit_binary_expr(self)

    def dump(self, indent=0):
        print(' ' * indent, self.op.value, end=' ')
        self.left.dump()
        self.right.dump()


@dataclass
class UnaryExpr(Expr):
    op: Operator
    expr: Expr

    def accept(self, visitor):
        visitor.visit_unary_expr(self)

    def dump(self, indent=0):
        assert (type(self.op) ==
                Operator), f'UExpr: Invalid type {type(self.op)}'
        print(' ' * indent, self.op.value, end=' ')
        self.expr.dump()


@dataclass
class Reference(Expr):
    name: Id

    def accept(self, visitor):
        visitor.visit_reference(self)

    def dump(self, indent=0):
        assert (type(self.name) == Id), f'Ref Invalid type {type(self.name)}'
        print(' ' * indent, '&', self.name, end=' ')


@dataclass
class Deref(Expr):
    expr: Expr

    def accept(self, visitor):
        visitor.visit_deref(self)

    def dump(self, indent=0):
        print(' ' * indent, '*', end=' ')
        self.expr.dump()


@dataclass
class Alloc(Expr):
    expr: Expr

    def accept(self, visitor):
        visitor.visit_alloc(self)

    def dump(self, indent=0):
        print(' ' * indent, 'alloc', end=' ')
        self.expr.dump()


@dataclass
class DirectFieldWrite(Expr):
    name: Id
    field: Id

    def accept(self, visitor):
        visitor.visit_direct_field_write(self)

    def dump(self, indent=0):
        assert (type(self.name) ==
                Id), f'DirectFieldWrite: Invalid type {type(self.name)}'
        assert (type(self.field) ==
                Id), f'DirectFieldWrite: Invalid type {type(self.field)}'
        print(' ' * indent, self.name.value, '.', self.field.value, end=' ')


@dataclass
class IndirectFieldWrite(Expr):
    expr: Expr
    field: Id

    def accept(self, visitor):
        visitor.visit_indirect_field_write(self)

    def dump(self, indent=0):
        assert (type(self.field) ==
                Id), f'IndirectFieldWrite: Invalid type {type(self.field)}'
        print(' ' * indent, '*', end=' ')
        self.expr.dump()
        print('.', self.field.value, end=' ')


@dataclass
class DerefWrite(Expr):
    expr: Expr

    def accept(self, visitor):
        visitor.visit_deref_write(self)

    def dump(self, indent=0):
        print(' ' * indent, '*', end=' ')
        self.expr.dump()


@dataclass
class Record(Expr):
    fields: list[(Id, Expr)]

    def accept(self, visitor):
        visitor.visit_record(self)

    def dump(self, indent=0):
        assert (type(self.fields) ==
                list), f'Record: Invalid type {type(self.fields)}'
        print(' ' * indent, '{', end=' ')
        for field in self.fields:
            print(' ' * (indent + 2), field[0].value, ':', end=' ')
            field[1].dump()
        print(' ' * indent, '}', end=' ')


@dataclass
class Access(Expr):
    name: Id | Deref | Expr
    fields: list[Id]

    def accept(self, visitor):
        visitor.visit_access(self)

    def __init__(self, *args):
        name = args[0]
        self.name = name
        ids = args[1:]
        match ids:
            case tuple(_):
                self.fields = list(ids)
            case _: # pragma: no cover
                raise TypeError('Invalid type for field, want tuple', type(ids))

    def dump(self, indent=0):
        assert (type(self.name) in (Id, Deref, Expr)
                ), f'Access: Invalid type {type(self.name)}'
        assert (type(self.fields) ==
                list), f'Access: Invalid type {type(self.fields)}'
        match self.name:
            case Id(_):
                self.name.dump()
            case Deref(expr):
                print(' ' * indent, '*', end=' ')
                expr.dump()
            case _: # pragma: no cover
                self.name.dump()
        for field in self.fields:
            print('.', field.value, end=' ')


@dataclass
class Parameters(_Ast):
    params: list[Id]

    def accept(self, visitor):
        visitor.visit_parameters(self)

    def dump(self, indent=0):
        assert (type(self.params) ==
                list), f'Parameters: Invalid type {type(self.params)}'
        print(' ' * indent, '(', end=' ')
        for name in self.params:
            name.dump()
        print(')', end=' ')


@dataclass
class Vardecl(Statement):
    ids: list[Id]

    def accept(self, visitor):
        visitor.visit_vardecl(self)

    def dump(self, indent=0):
        assert (type(self.ids) ==
                list), f'Vardecl: Invalid type {type(self.ids)}'
        print(' ' * indent, 'var', end=' ')
        for name in self.ids:
            name.dump()
        print(';')

    def __init__(self, name: Parameters | Id):
        match name:
            case Parameters(names):
                self.ids = names
            case _: # pragma: no cover
                raise TypeError('Invalid type for name', type(name))


@dataclass
class Return(Statement):
    expr: Expr

    def accept(self, visitor):
        visitor.visit_return(self)

    def dump(self, indent=0):
        print(' ' * indent, 'return', end=' ')
        self.expr.dump()
        print(';')


@dataclass
class Block(_Ast, ast_utils.AsList):
    stmts: list[Statement]

    def accept(self, visitor):
        visitor.visit_block(self)

    def dump(self, indent=0):
        assert (type(self.stmts) ==
                list), f'Block: Invalid type {type(self.stmts)}'
        print(' ' * indent, '{')
        for stmt in self.stmts:
            stmt.dump(indent + 2)
        print(' ' * indent, '}')


@dataclass
class FunBlock(Block):
    varstmts: list[Vardecl]
    stmts: list[Statement]
    returnstmt: Return

    def accept(self, visitor):
        visitor.visit_funblock(self)

    def dump(self, indent=0):
        print(' ' * indent, '{')
        for varstmt in self.varstmts:
            varstmt.dump(indent + 2)
        for stmt in self.stmts:
            stmt.dump(indent + 2)
        self.returnstmt.dump(indent + 2)
        print(' ' * indent, '}')


@dataclass
class Function(_Ast):
    name: Id
    parameters: Parameters
    body: FunBlock

    def accept(self, visitor):
        visitor.visit_function(self)

    def dump(self, indent=0):
        print(' ' * indent, 'fun', self.name.value, end=' ')
        self.parameters.dump()
        self.body.dump(indent + 2)


@dataclass
class If(Statement):
    cond: Expr
    then: Block
    else_: Block | None

    def __init__(self, cond, then, else_=None):
        self.cond = cond
        self.then = then
        self.else_ = else_

    def accept(self, visitor):
        visitor.visit_if(self)

    def dump(self, indent=0):
        print(' ' * indent, 'if', end=' ')
        self.cond.dump()
        print(' then')
        self.then.dump(indent + 2)
        if self.else_:
            print(' ' * indent, 'else')
            self.else_.dump(indent + 2)


@dataclass
class While(Statement):
    cond: Expr
    body: Block

    def accept(self, visitor):
        visitor.visit_while(self)

    def dump(self, indent=0):
        print(' ' * indent, 'while', end=' ')
        self.cond.dump()
        self.body.dump(indent + 2)


@dataclass
class Assign(Statement):
    name: Id | DirectFieldWrite | IndirectFieldWrite | DerefWrite
    expr: Expr

    def accept(self, visitor):
        visitor.visit_assign(self)

    def dump(self, indent=0):
        match self.name:
            case Id(name):
                print(' ' * indent, name, '=', end=' ')
            case DirectFieldWrite(_, _) as dfw:
                print(' ' * indent, end='')
                dfw.dump()
                print('=', end=' ')
            case IndirectFieldWrite(_, _) as ifw:
                print(' ' * indent, end='')
                ifw.dump()
                print('=', end=' ')
            case DerefWrite(_) as dw:
                print(' ' * indent, '*', end='')
                dw.dump()
                print('=', end=' ')
            case _: # pragma: no cover
                print(type(self.name))
                print(self.name.__match_args__)
                print(' ' * indent, '???', end=' ')
                breakpoint()
                assert False
        self.expr.dump()
        print(';')


@dataclass
class Input(Expr):

    def accept(self, visitor):
        visitor.visit_input(self)

    def dump(self, indent=0):
        print(' ' * indent, 'input', end=' ')


@dataclass
class Output(Statement):
    expr: Expr

    def accept(self, visitor):
        visitor.visit_output(self)

    def dump(self, indent=0):
        print(' ' * indent, 'output', end=' ')
        self.expr.dump()
        print(';')


@dataclass
class Call(Expr):
    name: Expr
    args: list[Expr]

    def accept(self, visitor):
        visitor.visit_call(self)

    def dump(self, indent=0):
        print(' ' * indent, end=' ')
        self.name.dump()
        print('(', end=' ')
        for arg in self.args:
            arg.dump()
        print(')', end=' ')


@dataclass
class Error(Statement):
    value: Expr

    def accept(self, visitor):
        visitor.visit_error(self)

    def dump(self, indent=0):
        print(' ' * indent, 'error', end=' ')


@dataclass
class Program(_Ast):
    functions: list[Function]

    def accept(self, visitor):
        visitor.visit_program(self)

    def dump(self, indent=0):
        for function in self.functions:
            function.dump(indent)
