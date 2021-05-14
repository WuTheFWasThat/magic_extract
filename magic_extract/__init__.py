"""
Based on
https://andyljones.com/posts/post-mortem-plotting.html
"""

import inspect
import ctypes

def _copy_out(ls, gs, is_ipython=False):
    frames = [f for f in inspect.stack()]
    if is_ipython:
        frames = [f for f in frames if f.filename.startswith('<ipython-input')]
    f = frames[-1].frame
    f.f_locals.update({k: v for k, v in gs.items() if k[:2] != '__'})
    f.f_locals.update({k: v for k, v in ls.items() if k[:2] != '__'})
    # Magic call to make the updates to f_locals 'stick'.
    # More info: http://pydev.blogspot.co.uk/2014/02/changing-locals-of-frame-frameflocals.html
    ctypes.pythonapi.PyFrame_LocalsToFast(ctypes.py_object(f), ctypes.c_int(0))
    return f.f_code.co_name

def extract(source=None, is_ipython=False):
    """Copies the variables of the caller up to iPython. Useful for debugging.
    .. code-block:: python
        def f():
            x = 'hello world'
            extract()
        f() # raises an error
        print(x) # prints 'hello world'
        https://andyljones.com/posts/post-mortem-plotting.html
    """
    if source is None:
        frames = inspect.stack()
        caller = frames[1].frame
        name, ls, gs = caller.f_code.co_name, caller.f_locals, caller.f_globals
    elif hasattr(source, '__func__'):
        func = source.__func__
        name, ls, gs = func.__qualname__, (func.__closure__ or {}), func.__globals__
    elif hasattr(source, '__init__'):
        func = source.__init__.__func__
        name, ls, gs = func.__qualname__, (func.__closure__ or {}), func.__globals__
    else:
        raise ValueError(f'Don\'t support source {source}')
    copy_name = _copy_out(ls, gs, is_ipython=is_ipython)
    message = 'Copied {}\'s variables to {}'.format(name, copy_name)
    raise RuntimeError(message)


def debug(f, *args, is_ipython=False, **kwargs):
    try:
        return f(*args, **kwargs)
    except:
        # can I access v1 from here?
        f = inspect.trace()[-1][0]
        name, ls, gs = f.f_code.co_name, f.f_locals, f.f_globals
        copy_name = _copy_out(ls, gs, is_ipython=is_ipython)
        message = 'Copied {}\'s variables to {}'.format(name, copy_name)
        raise RuntimeError(message)

