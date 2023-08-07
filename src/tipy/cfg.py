from .ast import *


class Node:
    pass


class Edge:
    in_: Node
    out: Node


class Graph:
    nodes: list[Node]
    edges: list[Edge]

    @classmethod
    def from_prog(cls, ast: Program) -> "Graph":
        pass

    @classmethod
    def from_func(cls, ast: Function) -> "Graph":
        pass

    def __init__(self, nodes: list[Node], edges: list[Edge]) -> None:
        self.nodes = nodes
        self.edges = edges

    def __repr__(self) -> str:
        return f'Graph({self.nodes}, {self.edges})'
