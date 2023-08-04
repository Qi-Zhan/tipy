import enum
from dataclasses import dataclass
from typing import Optional

from lark.tree import Meta
from lark import ast_utils, Token


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


class Type(enum.Enum):
    INT = 'int'
    BOOL = 'bool'
    STRING = 'string'
    VOID = 'void'
    NULL = 'null'


class _Ast(ast_utils.Ast):
    pass


class Statement(_Ast):
    pass


class _Expr(_Ast):
    pass


@dataclass
class Const(_Expr):
    type_: Type
    value: str | int | None

    def dump(self, indent=0):
        assert (type(self.value) in (str, int, type(None))
                ), f'Const: Invalid type {type(self.value)}'
        print(' ' * indent, self.value, end=' ')


@dataclass
class Id(_Expr, ast_utils.WithMeta):
    meta: Meta
    name: str

    def __init__(self, meta: Meta, name: Token):
        self.meta = meta
        self.name = name.value

    def dump(self, indent=0):
        print(self.name, type(self.name))
        assert (type(self.name) == str), f'Id Invalid type {type(self.name)}'
        print(' ' * indent, self.name, end=' ')


@dataclass
class BinaryExpr(_Expr):
    left: _Expr
    op: Operator
    right: _Expr

    def dump(self, indent=0):
        print(' ' * indent, self.op.value, end=' ')
        self.left.dump()
        self.right.dump()


@dataclass
class UnaryExpr(_Expr):
    op: Operator
    expr: _Expr

    def dump(self, indent=0):
        assert (type(self.op) ==
                Operator), f'UExpr: Invalid type {type(self.op)}'
        print(' ' * indent, self.op.value, end=' ')
        self.expr.dump()


@dataclass
class Reference(_Expr):
    name: Id

    def dump(self, indent=0):
        assert (type(self.name) == Id), f'Ref Invalid type {type(self.name)}'
        print(' ' * indent, '&', self.name, end=' ')


@dataclass
class Deref(_Expr):
    expr: _Expr

    def dump(self, indent=0):
        print(' ' * indent, '*', end=' ')
        self.expr.dump()


@dataclass
class Alloc(_Expr):
    expr: _Expr

    def dump(self, indent=0):
        print(' ' * indent, 'alloc', end=' ')
        self.expr.dump()


@dataclass
class DirectFieldWrite(_Expr):
    id: Id
    field: Id

    def dump(self, indent=0):
        assert (type(self.id) ==
                Id), f'DirectFieldWrite: Invalid type {type(self.id)}'
        assert (type(self.field) ==
                Id), f'DirectFieldWrite: Invalid type {type(self.field)}'
        print(' ' * indent, self.id.name, '.', self.field.name, end=' ')


@dataclass
class IndirectFieldWrite(_Expr):
    expr: _Expr
    field: Id

    def dump(self, indent=0):
        assert (type(self.field) ==
                Id), f'IndirectFieldWrite: Invalid type {type(self.field)}'
        print(' ' * indent, '*', end=' ')
        self.expr.dump()
        print('.', self.field.name, end=' ')


@dataclass
class DerefWrite(_Expr):
    expr: _Expr

    def dump(self, indent=0):
        print(' ' * indent, '*', end=' ')
        self.expr.dump()


@dataclass
class Record(_Expr):
    fields: list[(Id, _Expr)]

    def dump(self, indent=0):
        assert (type(self.fields) ==
                list), f'Record: Invalid type {type(self.fields)}'
        print(' ' * indent, '{', end=' ')
        for field in self.fields:
            print(' ' * (indent + 2), field[0].name, ':', end=' ')
            field[1].dump()
        print(' ' * indent, '}', end=' ')


@dataclass
class Access(_Expr):
    name: Id | Deref | _Expr
    fields: list[Id]

    def __init__(self, *args):
        name = args[0]
        self.name = name
        ids = args[1:]
        match ids:
            case tuple(_):
                self.fields = list(ids)
            case Id(_, _):
                self.fields = [ids]
            case _:
                raise TypeError('Invalid type for field', type(ids))

    def dump(self, indent=0):
        assert (type(self.name) in (Id, Deref, _Expr)
                ), f'Access: Invalid type {type(self.name)}'
        assert (type(self.fields) ==
                list), f'Access: Invalid type {type(self.fields)}'
        match self.name:
            case Id(_, _):
                self.name.dump()
            case Deref(expr):
                print(' ' * indent, '*', end=' ')
                expr.dump()
            case _:
                self.name.dump()
        for field in self.fields:
            print('.', field.name, end=' ')


@dataclass
class Parameters(_Ast):
    names: list[Id]

    def dump(self, indent=0):
        assert (type(self.names) ==
                list), f'Parameters: Invalid type {type(self.names)}'
        print(' ' * indent, '(', end=' ')
        for name in self.names:
            name.dump()
        print(')', end=' ')


@dataclass
class Vardecl(Statement):
    names: list[Id]

    def dump(self, indent=0):
        assert (type(self.names) ==
                list), f'Vardecl: Invalid type {type(self.names)}'
        print(' ' * indent, 'var', end=' ')
        for name in self.names:
            name.dump()
        print(';')

    def __init__(self, name: Parameters | Id):
        match name:
            case Parameters(names):
                self.names = names
            case Id(_, _):
                self.names = [name]
            case _:
                raise TypeError('Invalid type for name', type(name))


@dataclass
class Return(Statement):
    value: _Expr

    def dump(self, indent=0):
        print(' ' * indent, 'return', end=' ')
        self.value.dump()
        print(';')


@dataclass
class Block(_Ast, ast_utils.AsList):
    stmts: list[Statement]

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
    ident: Id
    args: Parameters
    body: FunBlock

    def dump(self, indent=0):
        print(' ' * indent, 'fun', self.ident.name, end=' ')
        self.args.dump()
        self.body.dump(indent + 2)


@dataclass
class If(Statement):
    cond: _Expr
    then: Block
    else_: Optional[Block]

    def __init__(self, cond, then, else_=None):
        self.cond = cond
        self.then = then
        self.else_ = else_

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
    cond: _Expr
    then: Block

    def dump(self, indent=0):
        print(' ' * indent, 'while', end=' ')
        self.cond.dump()
        self.then.dump(indent + 2)


@dataclass
class Assign(Statement):
    name: Id | DirectFieldWrite | IndirectFieldWrite | DerefWrite
    expr: _Expr

    def dump(self, indent=0):
        match self.name:
            case Id(_, name):
                print(' ' * indent, name, '=', end=' ')
            case DirectFieldWrite(id, field):
                print(' ' * indent, id.name, '.', field.name, '=', end=' ')
            case IndirectFieldWrite(expr, field):
                print(' ' * indent, '*', end=' ')
                expr.dump()
                print('.', field.name, '=', end=' ')
            case DerefWrite(expr):
                print(' ' * indent, '*', end=' ')
                expr.dump()
                print('=', end=' ')
            case _:
                print(' ' * indent, '???', end=' ')
                assert False
        self.expr.dump()
        print(';')


@dataclass
class Input(Statement):

    def dump(self, indent=0):
        print(' ' * indent, 'input;')


@dataclass
class Output(Statement):
    value: _Expr

    def dump(self, indent=0):
        print(' ' * indent, 'output', end=' ')
        self.value.dump()
        print(';')


@dataclass
class Call(_Expr):
    name: Id | _Expr
    args: list[_Expr]

    def dump(self, indent=0):
        print(' ' * indent, 'call', end=' ')
        self.name.dump()
        print('(', end=' ')
        for arg in self.args:
            arg.dump()
        print(')', end=' ')


@dataclass
class Error(Statement):
    value: _Expr

    def dump(self, indent=0):
        print(' ' * indent, 'error', end=' ')


@dataclass
class Program(_Ast):
    functions: list[Function]

    def dump(self, indent=0):
        for function in self.functions:
            function.dump(indent)
