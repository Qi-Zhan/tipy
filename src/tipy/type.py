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

    def contain_class(self, c):
        return None


@dataclass
class TypeVar(Type):
    id: int

    def __init__(self, id: int) -> None:
        self.id = id
        self.parent = self

    @classmethod
    def new(cls):
        global typevar
        typevar += 1
        return cls(typevar)

    def __str__(self) -> str:
        return f'${self.id}'


@dataclass
class IntType(Type):

    def __init__(self) -> None:
        self.parent = self

    def __str__(self) -> str:
        return 'int'


@dataclass
class StringType(Type):

    def __init__(self) -> None:
        self.parent = self

    def __str__(self) -> str:
        return 'string'


@dataclass
class PointerType(Type):
    type_: Type

    def __init__(self, type_: Type) -> None:
        self.type_ = type_
        self.parent = self

    def contain(self, t: Type) -> bool:
        return self.type_.contain(t) or self.type_ == t

    def contain_class(self, t) -> bool:
        if self.type_.contain_class(t):
            return self.type_.contain_class(t)
        if isinstance(self.type_, t):
            return self.type_

    def __str__(self) -> str:
        assert isinstance(
            self.type_, Type), f'type_ must be an instance of Type, got {self.type_}'
        return f'↑{str(self.type_)}'


@dataclass
class FunctionType(Type):
    params: list[Type]
    return_type: Type

    def __init__(self, params: list[Type], return_type: Type) -> None:
        self.params = params
        self.return_type = return_type
        self.parent = self

    def contain(self, t: Type) -> bool:
        for param in self.params:
            if param.contain(t):
                return True
            if param == t:
                return True
        return self.return_type.contain(t) or self.return_type == t

    def contain_class(self, c):
        for param in self.params:
            if param.contain_class(c):
                return param.contain_class(c)
            if isinstance(param, c):
                return param
        if self.return_type.contain_class(c):
            return self.return_type.contain_class(c)
        if isinstance(self.return_type, c):
            return self.return_type

    def __str__(self) -> str:
        for param in self.params:
            assert isinstance(param, Type)
        assert isinstance(self.return_type, Type)
        return f'({", ".join(map(str, self.params))}) -> {str(self.return_type)}'


typevar = 0


@dataclass
class RecursionType(Type):
    """
    recursive type
    - var: TypeVar
    - type_: Type

    form μa.t is considered as a type t[a := μa.t]
    """
    var: TypeVar
    type_: Type

    def __init__(self, var: TypeVar, type_: Type) -> None:
        self.var = var
        self.type_ = type_
        self.parent = self

    def __str__(self) -> str:
        assert isinstance(self.var, TypeVar)
        assert isinstance(self.type_, Type)
        return f'μ{str(self.var)}.{str(self.type_)}'
