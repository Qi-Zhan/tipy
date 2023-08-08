import sys
from lark import Lark, ast_utils, Transformer, v_args
from .ast import *

__all__ = ['parse', 'parse_file']

this_module = sys.modules[__name__]


class ToAst(Transformer):

    def start(self, x: list):
        return Program(x)

    @v_args(inline=True)
    def string(self, s: str):
        return Const(AstType.STRING, s[1:-1])

    @v_args(inline=True)
    def null(self):
        return Const(AstType.NULL, None)

    @v_args(inline=True)
    def number(self, n: str):
        return Const(AstType.INT, int(n))

    def name_list(self, x: list):
        return Parameters(x)

    def funblock(self, stmts: list):
        varstmt = []
        stmt = []
        returnstmt = None
        for s in stmts:
            match s:
                case Vardecl(_):
                    varstmt.append(s)
                case Return(_):
                    returnstmt = s
                case _:
                    stmt.append(s)
        return FunBlock(stmt, varstmt, returnstmt)

    @v_args(inline=True)
    def eq(self, left, right):
        return BinaryExpr(left, Operator.EQ, right)

    @v_args(inline=True)
    def ne(self, left, right):
        return BinaryExpr(left, Operator.NE, right)

    @v_args(inline=True)
    def lt(self, left, right):
        return BinaryExpr(left, Operator.LT, right)

    @v_args(inline=True)
    def gt(self, left, right):
        return BinaryExpr(left, Operator.GT, right)

    @v_args(inline=True)
    def le(self, left, right):
        return BinaryExpr(left, Operator.LE, right)

    @v_args(inline=True)
    def ge(self, left, right):
        return BinaryExpr(left, Operator.GE, right)

    @v_args(inline=True)
    def add(self, left, right):
        return BinaryExpr(left, Operator.ADD, right)

    @v_args(inline=True)
    def sub(self, left, right):
        return BinaryExpr(left, Operator.SUB, right)

    @v_args(inline=True)
    def mul(self, left, right):
        return BinaryExpr(left, Operator.MUL, right)

    @v_args(inline=True)
    def div(self, left, right):
        return BinaryExpr(left, Operator.DIV, right)

    @v_args(inline=True)
    def neg(self, expr):
        return UnaryExpr(Operator.NE, expr)

    @v_args(inline=True)
    def funapp(self, name, args):
        return Call(name, args)

    def parens(self, x):
        return x[0]

    def field_list(self, x: list):
        if len(x) == 0:
            return []
        else:
            fields = []
            for one_field in x:
                fields.append((one_field.children[0], one_field.children[1]))
            return fields

    def expr_list(self, x: list):
        return x

    @v_args(inline=True)
    def directfieldwrite(self, x, y):
        return DirectFieldWrite(x, y)

    @v_args(inline=True)
    def indirectfieldwrite(self, x, y):
        return IndirectFieldWrite(x, y)

    @v_args(inline=True)
    def derefwrite(self, x):
        return DerefWrite(x)


parser = Lark.open("tip.lark", parser="earley", rel_to=__file__)


transformer = ast_utils.create_transformer(this_module, ToAst())


def parse(text):
    tree = parser.parse(text)
    return transformer.transform(tree)


def parse_file(filename):
    with open(filename) as f:
        return parse(f.read())
