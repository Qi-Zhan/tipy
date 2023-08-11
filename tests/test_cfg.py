import unittest

from tipy.parser import parse
from tipy.cfg import *

from .util import TipyTest


class TestCFG(TipyTest):

    def test_single(self):
        prog = """main(a) {
            var a;
            a = 1;
            return a;
        } 
        """
        prog = parse(prog)
        cfg = Graph.build_prog(prog)
        self.assertEqual(len(cfg.nodes), 4)
        self.assertEqual(len(cfg.edges), 3)
        # ordinary edge is empty label
        self.assertEqual(str(cfg.edges[0]), '')
        for node in cfg.nodes:
            pred = list(node.pred_nodes())
            succ = list(node.succ_nodes())
            if isinstance(node, Entry):
                self.assertEqual(len(pred), 0)
                self.assertEqual(len(succ), 1)
                self.assertEqual(str(node), 'main(a)')
            elif isinstance(node, Exit):
                self.assertEqual(len(pred), 1)
                self.assertEqual(len(succ), 0)
                self.assertIn('return  a', str(node))
            else:
                self.assertEqual(len(pred), 1)
                self.assertEqual(len(succ), 1)
                str(node)

    def test_if(self):
        prog = """main(a) {
            var a;
            a = 1;
            if (a>0) {
                a = a+1;
            }
            return a;
        } 
        """
        prog = parse(prog)
        cfg = Graph.build_prog(prog)
        self.assertEqual(len(cfg.nodes), 6)
        self.assertEqual(len(cfg.edges), 6)
        for edge in cfg.edges:
            if isinstance(edge, TrueEdge):
                self.assertEqual(str(edge), 'true')
            elif isinstance(edge, FalseEdge):
                self.assertEqual(str(edge), 'false')
        for node in cfg.nodes:
            if isinstance(node, Condition):
                self.assertIn('if', str(node))
                

    def test_ifelse(self):
        prog = """main(a) {
            var a;
            a = 1;
            if (a>0) {
                a = a+1;
            } else {
                a = a-1;
            }
            {
                
            }
            return a;
        }
        """
        prog = parse(prog)
        cfg = Graph.build_prog(prog)
        self.assertEqual(len(cfg.nodes), 7)
        self.assertEqual(len(cfg.edges), 7)

    def test_while(self):
        prog = """
        iterate(n) {
            var f;
            f = 1;
            while (n>0) {
                f = f*n;
                n = n-1; 
            }
            return f; 
        }
        """
        prog = parse(prog)
        cfg = Graph.build_prog(prog)
        self.assertEqual(len(cfg.nodes), 7)
        self.assertEqual(len(cfg.edges), 7)
        for edge in cfg.edges:
            if isinstance(edge, TrueEdge):
                self.assertIsInstance(edge.in_, Condition)
            elif isinstance(edge, FalseEdge):
                self.assertIsInstance(edge.in_, Condition)
                self.assertIsInstance(edge.out, Exit)

if __name__ == '__main__':
    unittest.main()
