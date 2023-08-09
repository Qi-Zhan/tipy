"""
This is a simple example of type analysis.
Usage:
    python typeanalysis.py [filename]
    if no filename is given, it will parse the code in the docstring.
"""

import sys
from tipy.parser import parse, parse_file
from tipy.analysis import TypeAnalysis
from tipy.ast import Id

if __name__ == '__main__':
    if len(sys.argv) > 1:
        prog = parse_file(sys.argv[1])
    else:
        prog = parse(
            """main() {
            var p;
            p = alloc null;
            *p = p;
            return 0;
        }
        """)
    prog.dump()
    result = TypeAnalysis.run(prog)
    for expr in result.map2expr.values():
        if isinstance(expr, Id):
            print(f"{expr} line:{expr.token.line} -> {result.get_type(expr)}")
