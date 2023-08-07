from tipy.ast import Access, Parameters, Program, Record
from .ast import *
from .visitor import AstVisitor
from .util import SymbolError


class SpecialSymbol:
    pass


# Singleton
SpecialSymbol = SpecialSymbol()


class SymbolContext:
    """
    >>> from .ast import *
    >>> st = SymbolContext()
    >>> assert st.get('a') is None
    >>> st.push('a', 'int')
    >>> st.push('b', 'int')
    >>> assert st.get('a') == 'int'
    >>> assert st.get('b') == 'int'
    >>> st.enter_scope()
    >>> st.push('a', 'string')
    >>> assert st.get('a') == 'string'
    >>> st.exit_scope()
    >>> assert st.get('a') == 'int'
    """
    symbols: dict[Id, list[Id]]

    def __init__(self):
        self.symbols = {}

    def enter_scope(self) -> None:
        for v in self.symbols.values():
            v.append(SpecialSymbol)

    def exit_scope(self) -> None:
        for v in self.symbols.values():
            if len(v) == 0:
                continue
            while v[-1] is not SpecialSymbol:
                v.pop()
            if v[-1] is SpecialSymbol:
                v.pop()

    def push(self, name: str, id: Id) -> None:
        if name not in self.symbols:
            self.symbols[name] = [SpecialSymbol]
        self.symbols[name].append(id)

    def get(self, name: str) -> Id | None:
        if name not in self.symbols:
            return None
        for v in reversed(self.symbols[name]):
            if v is not SpecialSymbol:
                return v
        return None


class SymbolTable(AstVisitor):
    symbols: dict[Id, Id]
    context: SymbolContext

    def __init__(self):
        self.symbols = {}
        self.context = SymbolContext()

    @classmethod
    def build(cls, ast: Program) -> "SymbolTable":
        st = cls()
        ast.accept(st)
        for name, id in st.symbols.items():
            if id is None:
                raise SymbolError(f'Undefined variable {name} with line {name.token.line}')
            # print(
            #     f'{name.value} in line{name.token.line} -> {id.value} in line {id.token.line}')
        return st

    def get(self, name: Id) -> Id:
        return self[name]

    def visit_vardecl(self, node: Vardecl):
        for id in node.ids:
            self.context.push(id.value, id)

    def visit_id(self, node: Id):
        self.symbols[node] = self.context.get(node.value)

    def visit_record(self, node: Record):
        pass

    def visit_access(self, node: Access):
        node.name.accept(self)

    def visit_parameters(self, node: Parameters):
        for param in node.params:
            self.context.push(param.value, param)

    def visit_program(self, node: Program):
        for func in node.functions:
            self.context.push(func.name.value, func.name)
        for func in node.functions:
            func.accept(self)

    def visit_function(self, node: Function):
        node.parameters.accept(self)
        node.body.accept(self)

    def visit_funblock(self, node: FunBlock):
        self.context.enter_scope()
        super().visit_funblock(node)
        self.context.exit_scope()


if __name__ == "__main__":
    import doctest
    doctest.testmod()
    print('OK')
