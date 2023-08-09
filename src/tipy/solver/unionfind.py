from .solver import Solver
from ..util import TypeError


def make_set(x):
    """
    adds a new node x that is its own parent
    """
    x.parent = x


def find(x):
    """
    returns the representative of the set that x belongs to
    """
    if x.parent != x:
        x.parent = find(x.parent)
    return x.parent


def union(x, y):
    """
    merges the set containing x and the set containing y
    """
    x_root = find(x)
    y_root = find(y)
    if x_root != y_root:
        x_root.parent = y_root


class UnionFindSolver(Solver):
    @classmethod
    def solve(cls, constraints):
        print("UnionFindSolver.solve")

        for constraint in constraints:
            make_set(constraint.left)
            make_set(constraint.right)
