class TipyException(Exception):
    pass


class SyntaxError(TipyException):
    pass


class SymbolError(TipyException):
    pass


class TypeError(TipyException):
    pass


def typecheck(func: callable):
    """
    Decorator for dynamic type checking.
    - func: function to be decorated
    - check if the arguments are of the correct type based on the type hints
    """
    def wrapper(*args, **kwargs):
        # get the type hints
        hints = func.__annotations__
        argcount = func.__code__.co_argcount
        params = func.__code__.co_varnames[:argcount]
        # check if the arguments are of the correct type
        for arg_name in hints.keys():
            arg_hint = hints[arg_name]
            index = params.index(arg_name)
            # skip the arguments that are not type hinted
            if index < 0 or index >= len(args):
                continue
            arg = args[params.index(arg_name)]
            if arg is not None and not isinstance(arg, arg_hint):
                raise TypeError(
                    f'Expected {arg_hint}, got {type(arg)}')
        for key, value in kwargs.items():
            if value is not None and not isinstance(value, hints[key]):
                raise TypeError(
                    f'Expected {hints[key]}, got {type(value)}')
        return func(*args, **kwargs)
    return wrapper


def get_output(func, *args, **kwargs) -> str:
    """
    Run the function and return the output
    """
    import io
    import sys
    old_stdout = sys.stdout
    sys.stdout = mystdout = io.StringIO()
    func(*args, **kwargs)
    sys.stdout = old_stdout
    return mystdout.getvalue()
