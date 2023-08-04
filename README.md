# TIP-Python

This is python implementation for [TIP](https://github.com/cs-au-dk/TIP), which aims to teach the art of static analysis.

`tip_examples/` contains some examples of TIP programs, they are all from the original [TIP](https://github.com/cs-au-dk/TIP) repository.

### Install

```bash
pip install -e .
```

We do not aim to publish this package, so we use `pip install -e .` to install this package in editable mode.

### Example

See `examples/` for all analysis we implemented of TIP program.

* `parse.py` parse TIP program into AST


### Test

```bash
make test
```
