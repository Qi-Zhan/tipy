from dataclasses import dataclass


@dataclass
class Type:
    def find_parent(self) -> 'Type':
        """
        find the representative of the set that this type belongs to
        """
        if self.parent != self:
            self.parent = self.parent.find_parent()
        return self.parent

    def contain(self, t: 'Type') -> bool:
        return False


@dataclass
class IntType(Type):

    def __repr__(self) -> str:
        return 'int'


@dataclass
class StringType(Type):

    def __repr__(self) -> str:
        return 'string'


@dataclass
class PointerType(Type):
    type_: Type

    def contain(self, t: Type) -> bool:
        return self.type_.contain(t)

    def __repr__(self) -> str:
        assert isinstance(
            self.type_, Type), f'type_ must be an instance of Type, got {self.type_}'
        return f'↑{self.type_}'


@dataclass
class FunctionType(Type):
    params: list[Type]
    return_type: Type

    def contain(self, t: Type) -> bool:
        return any(param.contain(t) for param in self.params) or self.return_type.contain(t)

    def __repr__(self) -> str:
        for param in self.params:
            assert isinstance(param, Type)
        assert isinstance(self.return_type, Type)
        return f'({", ".join(map(str, self.params))}) -> {self.return_type}'


typevar = 0


@dataclass
class TypeVar(Type):
    id: int

    @classmethod
    def new(cls):
        global typevar
        typevar += 1
        return cls(typevar)

    def __repr__(self) -> str:
        return f'${self.id}'


@dataclass
class RecursionType(Type):
    var: TypeVar
    type_: Type

    def __repr__(self) -> str:
        assert isinstance(self.var, TypeVar)
        assert isinstance(self.type_, Type)
        return f'μ{self.var}.{self.type_}'
