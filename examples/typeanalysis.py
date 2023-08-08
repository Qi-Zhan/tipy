"""
This is a simple example of type analysis.
Usage:
    python typeanalysis.py [filename]
    if no filename is given, it will parse the code in the docstring.
"""

import sys
from tipy.parser import parse, parse_file
from tipy.analysis import TypeAnalysis

if __name__ == '__main__':
    if len(sys.argv) > 1:
        prog = parse_file(sys.argv[1])
    else:
        prog = parse(
        """short() {
        var x, y, z;
        x = input;
        y = alloc x;
        *y = x;
        z = *y;
        return z;
        }
        """)
    prog.dump()
    TypeAnalysis.run(prog)
