from .solver import Solver
from ..util import TypeError
from ..type import *


def make_set(x: Type):
    """
    adds a new node x that is its own parent
    >>> x = TypeVar.new()
    >>> make_set(x)
    >>> assert x.parent == x
    """
    x.parent = x
    match x:
        case PointerType(inner):
            make_set(inner)
        case FunctionType(params, return_type):
            for param in params:
                make_set(param)
            make_set(return_type)


def find(x: Type) -> Type:
    """
    returns the representative of the set that x belongs to
    """
    if x.parent != x:
        x.parent = find(x.parent)
    return x.parent


def union(x: Type, y: Type):
    """
    merges the set containing x and the set containing y
    """
    x_root = find(x)
    y_root = find(y)
    if x_root != y_root:
        x_root.parent = y_root


def unify(x: Type, y: Type) -> None | TypeError:
    """
    unify two types
    """
    assert isinstance(x, Type)
    assert isinstance(y, Type)
    x_root = find(x)
    y_root = find(y)
    if x_root == y_root:
        return
    # unify procedure
    match x_root, y_root:
        case TypeVar(_), TypeVar(_):
            union(x_root, y_root)
        case TypeVar(_), _:
            union(x_root, y_root)
        case _, TypeVar(_):
            union(y_root, x_root)
        case IntType(), IntType():
            union(x_root, y_root)
        case StringType(), StringType():
            union(x_root, y_root)
        case PointerType(x_type), PointerType(y_type):
            unify(x_type, y_type)
            union(x_root, y_root)
        case FunctionType(x_params, x_return), FunctionType(y_params, y_return):
            if len(x_params) != len(y_params):
                raise TypeError(f'Cannot unify {x} and {y}')
            for x_param, y_param in zip(x_params, y_params):
                unify(x_param, y_param)
            unify(x_return, y_return)
            union(x_root, y_root)
        case _, _:
            raise TypeError(f'Cannot unify {x} and {y}')


class UnionFindSolver(Solver):
    @classmethod
    def solve(cls, constraints):
        # initialize the union-find data structure
        for constraint in constraints:
            # print(constraint)
            make_set(constraint.left)
            make_set(constraint.right)
        # unify all the constraints
        for constraint in constraints:
            unify(constraint.left, constraint.right)

        return find


if __name__ == '__main__':
    import doctest
    doctest.testmod()
    print('Ok')
