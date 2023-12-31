from ..ast import Program
from ..cfg import Graph


class Analysis:
    @classmethod
    def run(cls, source: Program | Graph, *args):
        raise NotImplementedError( # pragma: no cover
            "You must implement this method in a subclass of Analysis")


class Constraint:
    pass
