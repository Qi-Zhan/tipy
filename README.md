# TIP-Python

This is python implementation for [TIP](https://github.com/cs-au-dk/TIP), which aims to teach the art of static analysis.

`tip_examples/` contains some examples of TIP programs, they are mostly from the original [TIP](https://github.com/cs-au-dk/TIP) repository. `field_write.tip`, `string_op.tip` are added by us.

## Install

It is recommended to use python3.11 to run this project.

```bash
pip install lark
pip install -e .
```

We do not aim to publish this package, so we use `pip install -e .` to install this package in editable mode for testing and development.

## Example

See `examples/` for all analysis we implemented of TIP program.

* `parse.py` parse TIP program into AST
* `typeanalysis.py` type check and infer types of TIP program from AST
* `cfg.py` generate control flow graph from AST, you can use `dot` to visualize it

## Test

```bash
make test
```

For coverage report, run `make coverage`. It is recommended to use `Coverage Gutters` in VSCode to visualize coverage report.

```bash
pip install coverage # install coverage
make coverage
```
