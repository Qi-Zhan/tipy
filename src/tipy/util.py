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
        print(hints)
        print(args)
        # check if the arguments are of the correct type
        for i, arg in enumerate(args):
            print(arg)
            if arg is not None and not isinstance(arg, hints[list(hints)[i]]):
                raise TypeError(
                    f'Expected {hints[list(hints)[i]]}, got {type(arg)}')
        for key, value in kwargs.items():
            if value is not None and not isinstance(value, hints[key]):
                raise TypeError(
                    f'Expected {hints[key]}, got {type(value)}')
        return func(*args, **kwargs)
    return wrapper
