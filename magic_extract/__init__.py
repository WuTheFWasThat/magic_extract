"""
Based on
https://andyljones.com/posts/post-mortem-plotting.html
"""

# TODO:
# also provide a magical new local or magic_extract.up or something that exports next frame's locals
# maybe based on staying within a set of paths, e.g. a git repo

import sys
import traceback
import functools
import inspect
import ctypes
import IPython


def pretty_print_frame(frame):
    return f'filename: {frame.filename} line {frame.lineno} in {frame.function}'


def in_ipython():
    try:
        from IPython import get_ipython
        if 'IPKernelApp' not in get_ipython().config:  # pragma: no cover
            return False
    except ImportError:
        return False
    except AttributeError:
        return False
    return True


def in_interactive_python():
    return hasattr(sys, 'ps1')


def _copy_to(f, ls, gs):
    f.f_locals.update({k: v for k, v in gs.items() if k[:2] != '__'})
    f.f_locals.update({k: v for k, v in ls.items() if k[:2] != '__'})
    # Magic call to make the updates to f_locals 'stick'.
    # More info: http://pydev.blogspot.co.uk/2014/02/changing-locals-of-frame-frameflocals.html
    ctypes.pythonapi.PyFrame_LocalsToFast(ctypes.py_object(f), ctypes.c_int(0))


def _copy_out(ls, gs):
    frames = [f for f in inspect.stack()]
    if in_ipython():
        frames = [f for f in frames if f.filename.startswith('<ipython-input')]
    f = frames[-1].frame
    _copy_to(f, ls, gs)
    return f.f_code.co_name


def extract(source=None):
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
    copy_name = _copy_out(ls, gs)
    message = 'Copied {}\'s variables to {}'.format(name, copy_name)
    raise RuntimeError(message)


def embed_kernel(frame=None, kernel_name='magic-extract'):
    import ipykernel.kernelapp
    if frame is None:
        # just the caller
        frame = inspect.stack()[1][0]
    scope = {}
    scope.update(frame.f_globals)
    scope.update(frame.f_locals)

    # IPython.embed_kernel(local_ns=scope)
    from jupyter_core.paths import jupyter_runtime_dir
    connection_file = f"{jupyter_runtime_dir()}/kernel-{kernel_name}.json"
    # Initialize the kernel app
    app = ipykernel.kernelapp.IPKernelApp.instance()
    app.connection_file = connection_file
    app.initialize([])
    app.shell.user_ns.update(scope)  # Update the namespace with your scope
    # Display the connection file path and start the kernel
    # print(f"Kernel connection file: {app.abs_connection_file}")
    print(f'jupyter notebook --existing {connection_file}')

    # example programmatic client code
    """
from jupyter_core.paths import jupyter_runtime_dir
print(jupyter_runtime_dir())

import jupyter_client
connection_file = jupyter_client.find_connection_file("kernel-magic-extract.json")

client = jupyter_client.BlockingKernelClient()
client.load_connection_file(connection_file)
client.start_channels()
client.execute_interactive("print(df)")
# client.execute_interactive("quit()")
    """

    app.start()


def decorate(launch_kernel=False, launch_ipython=False):
    # print frames
    # for f in inspect.stack():
    #     print(pretty_print_frame(f))
    # decorate_frame = list(inspect.stack())[0].frame
    # print(decorate_frame)

    def decorator(wrapped):
        @functools.wraps(wrapped)
        def wrapper(*args, **kwargs):
            try:
                return wrapped(*args, **kwargs)
            except:
                print('Exception in user code:')
                print('-' * 60)
                traceback.print_exc()
                print('-' * 60)
                print('Magically extracting variables!')

                # can I access v1 from here?
                f = inspect.trace()[-1][0]
                if launch_kernel:
                    embed_kernel(f)
                elif launch_ipython:
                    # copy to current frame
                    to_f = inspect.currentframe()
                    _copy_to(to_f, f.f_locals, f.f_globals)
                    from IPython import embed
                    embed()
                else:
                    name, ls, gs = f.f_code.co_name, f.f_locals, f.f_globals
                    copy_name = _copy_out(ls, gs)
                    # copy_name = _copy_to(decorate_frame, ls, gs)
                    message = 'Copied {}\'s variables to {}'.format(name, copy_name)
                    raise RuntimeError(message)
        return wrapper
    return decorator


def debug(f, *args, launch_kernel=False, launch_ipython=False,  **kwargs):
    new_f = decorate(launch_kernel=launch_kernel, launch_ipython=launch_ipython)(f)
    return new_f(*args, **kwargs)


