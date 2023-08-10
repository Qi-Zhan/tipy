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
