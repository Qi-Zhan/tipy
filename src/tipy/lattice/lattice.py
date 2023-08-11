""" Lattice
A partial order is a set S equipped with a binary relation ≤, which satisfies:
- Reflexivity: a ≤ a
- Antisymmetry: if a ≤ b and b ≤ a, then a = b
- Transitivity: if a ≤ b and b ≤ c, then a ≤ c

We say that an upper bound of a subset S  is an element u of the poset such that, for each s in S, s ≤ u.
A least upper bound(lub) of S, written ⋁S, is an upper bound of S which is less than or equal to every other upper bound of S.

A lattice is a partial oder in which every two elements have a lub and a glb.
A complete lattice is a lattice in which every subset has a lub and a glb.

Every complete lattice has a unique largest element, called its top(⊤),
and a unique smallest element, its bottom(⊥).
"""


class Element:
    pass


class Lattice:
    """ A semi lattice

    """
    bottom: Element = None
    top: Element = None

    @classmethod
    def lub(cls, x: Element, y: Element) -> Element:
        """ least upper bound

        """

        raise NotImplementedError(
            "you should implement this method in subclass")

    @classmethod
    def leq(cls, x: Element, y: Element) -> bool:
        """ less or equal

        """

        raise NotImplementedError(
            "you should implement this method in subclass")
