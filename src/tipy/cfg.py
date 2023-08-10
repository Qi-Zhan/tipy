from .ast import *
from .util import get_output


class Node:
    graph: "Graph"
    value: Statement | Expr

    def __init__(self, value: Statement | Expr):
        self.value = value

    def pred(self) -> list["Node"]:
        for edge in self.graph.edges:
            if edge.out == self:
                yield edge.in_

    def succ(self) -> list["Node"]:
        for edge in self.graph.edges:
            if edge.in_ == self:
                yield edge.out

    def pred_edges(self) -> list["Edge"]:
        for edge in self.graph.edges:
            if edge.out == self:
                yield edge

    def succ_edges(self) -> list["Edge"]:
        for edge in self.graph.edges:
            if edge.in_ == self:
                yield edge

    def __str__(self) -> str:
        return get_output(self.value.dump)

class Nope(Node):
    """ A node that does nothing """
    def __init__(self):
        pass

    def __str__(self) -> str:
        return ""

class Condition(Node):
    """ A conditional node """
    cond: Expr

    def __init__(self, cond: Expr):
        self.cond = cond
        self._count = True

    def __str__(self) -> str:
        output = get_output(self.cond.dump)
        return f'if {output}'


class Entry(Node):
    """ Entry point of a function

    name : Id
        Name of the function
    params : list[Id]
        List of parameters
    """
    name: Id
    params: list[Id]

    def __init__(self, name: Id, params: list[Id]):
        self.name = name
        self.params = params

    def __str__(self) -> str:
        return f'{self.name.value}({", ".join(str(p) for p in self.params)})'


class Exit(Node):
    """ Exit point of a function

    returnstmt : Return
    """
    returnstmt: Return

    def __init__(self, returnstmt: Return):
        self.returnstmt = returnstmt

    def __str__(self) -> str:
        return get_output(self.returnstmt.dump)


class Edge:
    in_: Node
    out: Node

    def __init__(self, in_: Node, out: Node):
        self.in_ = in_
        self.out = out

    def __str__(self) -> str:
        return ""


class TrueEdge(Edge):
    """ True branch of a conditional """

    def __str__(self) -> str:
        return 'true'


class FalseEdge(Edge):
    """ False branch of a conditional """

    def __str__(self) -> str:
        return 'false'


class Graph:
    nodes: list[Node]
    edges: list[Edge]

    def __init__(self, nodes: list[Node], edges: list[Edge]) -> None:
        self.nodes = nodes
        self.edges = edges

    @classmethod
    def build_prog(cls, ast: Program) -> "Graph":
        """ Build a control flow graph from a program """
        cfg = cls([], [])
        for function in ast.functions:
            cfg.build_function(function)
        return cfg

    def build_function(self, ast: Function) -> None:
        """ Build a control flow graph from a function"""
        # build entry and exit node
        function_entry = Entry(ast.name, ast.parameters.params)
        function_exit = Exit(ast.body.returnstmt)
        self.add_node(function_entry)
        self.add_node(function_exit)

        stmts = ast.body.varstmts + ast.body.stmts
        exit = self.build_stmts(stmts, function_entry)
        self.add_edge(exit, function_exit)
        self.eliminate_nope()

    def build_stmts(self, stmts: list[Statement], entry: Node) -> Node:
        """ Build a control flow graph from a list of statements
        - get the entry node of the statement
        - return the exit node of the statement
        """
        # stmts is null, then add an edge from entry to exit
        if len(stmts) == 0:
            return entry
        else:
            entry_inter = entry
            for stmt in stmts:
                entry_inter = self.build_stmt(stmt, entry_inter)
            return entry_inter

    def build_stmt(self, stmt: Statement, entry: Node) -> Node:
        """ Build a control flow graph from a statement
        - get the entry node of the statement
        - return the exit node of the statement
        """
        match stmt:
            case Block(stmts):
                return self.build_stmts(stmts, entry)

            case If(cond, true_block, false_block):
                cond_node = Condition(cond)
                self.add_node(cond_node)
                self.add_edge(entry, cond_node)
                true_exit = self.build_stmts(
                    true_block.stmts, cond_node)
                merge = Nope()
                self.add_node(merge)
                self.add_edge(true_exit, merge)
                if false_block is None:
                    self.add_edge(cond_node, merge, False)
                else:
                    false_exit = self.build_stmts(
                        false_block.stmts, cond_node)
                    self.add_edge(false_exit, merge)
                return merge

            case While(cond, block):
                cond_node = Condition(cond)
                self.add_node(cond_node)
                self.add_edge(entry, cond_node)
                merge = Nope()
                self.add_node(merge)
                exit = self.build_stmts(block.stmts, cond_node)
                self.add_edge(cond_node, merge, False)
                # loop back to the condition
                self.add_edge(exit, cond_node)
                return merge

            case _:
                node = Node(stmt)
                self.add_node(node)
                self.add_edge(entry, node)
                return node

    def add_node(self, node: Node) -> None:
        if node in self.nodes:
            print(f'Warning: node {node} already in graph')
        self.nodes.append(node)
        node.graph = self

    def add_edge(self, in_: Node, out: Node, flag: bool = None) -> None:
        # dirty hack to make edge work with condition
        if isinstance(in_, Condition):
            if in_._count:
                in_._count = False
                flag = True
            else:
                flag = False
        if flag is None:
            edge = Edge(in_, out)
        elif flag:
            edge = TrueEdge(in_, out)
        else:
            edge = FalseEdge(in_, out)

        if edge in self.edges:
            print(f'Warning: edge {edge} already in graph')
        self.edges.append(edge)
        edge.graph = self

    def eliminate_nope(self) -> None:
        remove_nodes = []
        remove_edges = []
        for node in self.nodes:
            if isinstance(node, Nope):
                remove_nodes.append(node)
                for edge in node.pred_edges():
                    remove_edges.append(edge)
                    for succ_edge in node.succ_edges():
                        remove_edges.append(succ_edge)
                        self.add_edge(edge.in_, succ_edge.out)
        for node in remove_nodes:
            if node in self.nodes:
                self.nodes.remove(node)
        for edge in remove_edges:
            if edge in self.edges:
                self.edges.remove(edge)

    def visualize(self, filename: str = 'cfg'):
        import graphviz
        dot = graphviz.Digraph()
        for node in self.nodes:
            dot.node(str(id(node)), str(node))
        for edge in self.edges:
            dot.edge(str(id(edge.in_)), str(id(edge.out)), label=str(edge))
        dot.render(filename, view=True)

    def __repr__(self) -> str:
        return f'Graph({self.nodes}, {self.edges})'
