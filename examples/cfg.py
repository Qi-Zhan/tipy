"""
This is a simple example of visualizing control flow graph.
Usage:
    python cfg.py [filename]
    if no filename is given, it will use the code in the docstring.
"""

import sys

from tipy.parser import parse, parse_file
from tipy.cfg import Graph

if __name__ == '__main__':
    if len(sys.argv) > 1:
        prog = parse_file(sys.argv[1])
    else:
        prog = parse("""
        iterate(n) {
            var f;
            f = 1;
            while (n>0) {
                f = f*n;
                n = n-1; 
            }
            return f; 
        }
        """)
    cfg = Graph.build_prog(prog)
    cfg.visualize()