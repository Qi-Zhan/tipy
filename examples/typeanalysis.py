"""
This is a simple example of type analysis.
Usage:
    python typeanalysis.py [filename]
    if no filename is given, it will analyze the code in the comment below.
"""

import sys
from tipy.parser import parse, parse_file
from tipy.analysis import TypeAnalysis
from tipy.ast import Id

if __name__ == '__main__':
    if len(sys.argv) > 1:
        prog = parse_file(sys.argv[1])
    else:
        # a unnessary complicated example
        # copy from [TIP] textbook
        prog = parse(
            """foo (p,x) {
            var f, q;
            if (*q == 0) {
                f = 1;
            } else {
                q  = alloc 0;
                *q = (*p) - 1;
                f = (*p)*(x(q, x));
            }
            return f;
        }

        main() {
            var n;
            n = input;
            return foo(&n, foo);
        }
        """)
    prog.dump()
    result = TypeAnalysis.run(prog)
    for expr in result.map2expr.values():
        if isinstance(expr, Id):
            print(f"{expr} line:{expr.token.line} -> {str(result.get_type(expr))}")
