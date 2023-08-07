from tipy.ast import Id, Program
from .ast import *
from .visitor import AstVisitor


class PrettyPrinter(AstVisitor):
    indent = 0

    @classmethod
    def print(cls, ast: Program):
        pp = cls()
        ast.accept(pp)

    def visit_program(self, node: Program):
        raise NotImplementedError("PrettyPrinter.visit_program")

    def visit_function(self, node: Function):
        print(' ' * self.indent, 'fun', end=' ')
        node.name.accept(self)
        node.parameters.accept(self)
        self.indent += 2
        node.body.accept(self)
        self.indent -= 2

    def visit_id(self, node: Id):
        assert (type(node.value) == str), f'Id Invalid type {type(self.name)}'
        print(' ' * self.indent, node.value, end=' ')
