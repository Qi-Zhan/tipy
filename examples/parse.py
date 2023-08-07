"""
This is a simple example of how to use the parser.
Usage:
    python parse.py [filename]
    if no filename is given, it will parse the code in the docstring.
"""

import sys
from pprint import pprint

from tipy.parser import parse, parse_file

if __name__ == '__main__':
    if len(sys.argv) > 1:
        prog = parse_file(sys.argv[1])
    else:
        prog = parse("""
            // This is a comment
            /* This is a mult
            iline comment */
            main(a) {
                var a;
                r=(f)(map(*l,f,z));
                v00 = 1 - (1 - v00*v00);
                output "Hello, world!";
                if (a == b) {
                    output "a is greater than b";
                } else {
                    output "a is not greater than b";
                }
                c = (a)(b);
                c = a(b,c );
                d = {a: b, c: d, e:f};
                
                return 1;
            }
            main(a, b) {
                k = {f: 4};
                return 1;
            }
        """)
    pprint(prog.functions)
    # PrettyPrinter.print(prog)
    prog.dump()
