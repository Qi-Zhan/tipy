from dataclasses import dataclass

@dataclass
class Type:
    pass

@dataclass
class IntType(Type):
    pass

@dataclass
class StringType(Type):
    pass

@dataclass
class PointerType(Type):
    type_: Type

@dataclass
class FunctionType(Type):
    params: list[Type]
    return_type: Type

@dataclass
class TypeVar(Type):
    id: int

@dataclass
class RecursionType(Type):
    var : TypeVar
    type_ : Type

