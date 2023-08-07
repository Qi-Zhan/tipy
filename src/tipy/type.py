from dataclasses import dataclass


@dataclass
class Type:
    pass


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

    def __repr__(self) -> str:
        return f'{self.type_}*'


@dataclass
class FunctionType(Type):
    params: list[Type]
    return_type: Type

    def __repr__(self) -> str:
        return f'({", ".join(map(str, self.params))}) -> {self.return_type}'


@dataclass
class TypeVar(Type):
    id: int

    def __repr__(self) -> str:
        return f'${self.id}'

@dataclass
class RecursionType(Type):
    var: TypeVar
    type_: Type

    def __repr__(self) -> str:
        return f'{self.var} = {self.type_}'
