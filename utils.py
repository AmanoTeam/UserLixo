import os
import time
import zipfile
import pyrogram
import ast
import importlib.util
import types
import asyncio

from asyncio.futures import Future
from functools import wraps, partial
from typing import Coroutine, Callable

loop = asyncio.get_event_loop()

def aiowrap(fn: Callable) -> Coroutine:
    @wraps(fn)
    def decorator(*args, **kwargs):
        wrapped = partial(fn, *args, **kwargs)

        return loop.run_in_executor(None, wrapped)

    return decorator


@aiowrap
def backup_sources(output_file=None):
    ctime = int(time.time())

    if output_file is not None and isinstance(output_file, str) and not output_file.lower().endswith('.zip'):
        output_file += '.zip'

    fname = output_file or 'backup-{}.zip'.format(ctime)

    with zipfile.ZipFile(fname, 'w', zipfile.ZIP_DEFLATED) as backup:
        for folder, _, files in os.walk('.'):
            for file in files:
                if file != fname and not file.endswith('.pyc') and '.heroku' not in folder.split('/') and 'dls' not in folder.split('/'):
                    backup.write(os.path.join(folder, file))

    return fname

async def meval(code, local_vars):
    # Don't clutter locals
    locs = {}
    # Restore globals later
    globs = globals().copy()
    # This code saves __name__ and __package into a kwarg passed to the function.
    # It is set before the users code runs to make sure relative imports work
    global_args = "_globs"
    while global_args in globs.keys():
        # Make sure there's no name collision, just keep prepending _s
        global_args = "_" + global_args
    local_vars[global_args] = {}
    for glob in ["__name__", "__package__"]:
        # Copy data to args we are sending
        local_vars[global_args][glob] = globs[glob]

    root = ast.parse(code, "exec")
    code = root.body
    if isinstance(code[-1], ast.Expr):  # If we can use it as a lambda return (but multiline)
        code[-1] = ast.copy_location(ast.Return(code[-1].value), code[-1])  # Change it to a return statement
    # globals().update(**<global_args>)
    glob_copy = ast.Expr(ast.Call(func=ast.Attribute(value=ast.Call(func=ast.Name(id="globals", ctx=ast.Load()),
                                                                    args=[], keywords=[]),
                                                     attr="update", ctx=ast.Load()),
                                  args=[], keywords=[ast.keyword(arg=None,
                                                                 value=ast.Name(id=global_args, ctx=ast.Load()))]))
    ast.fix_missing_locations(glob_copy)
    code.insert(0, glob_copy)
    args = []
    for a in list(map(lambda x: ast.arg(x, None), local_vars.keys())):
        ast.fix_missing_locations(a)
        args += [a]
    args = ast.arguments(args=[], vararg=None, kwonlyargs=args, kwarg=None, defaults=[],
                         kw_defaults=[None for i in range(len(args))])
    if int.from_bytes(importlib.util.MAGIC_NUMBER[:-2], 'little') >= 3410:
        args.posonlyargs = []
    fun = ast.AsyncFunctionDef(name="tmp", args=args, body=code, decorator_list=[], returns=None)
    ast.fix_missing_locations(fun)
    mod = ast.parse("")
    mod.body = [fun]
    comp = compile(mod, "<string>", "exec")

    exec(comp, {}, locs)

    r = await locs["tmp"](**local_vars)

    if isinstance(r, types.CoroutineType) or isinstance(r, Future):
        r = await r  # workaround for 3.5
    try:
        globals().clear()
        # Inconsistent state
    finally:
        globals().update(**globs)
    return r

def switch_case(switch, cases):
    if switch in cases:
        return cases[switch]
    elif 'default_case' in cases:
        return cases['default_case']
    else:
        return None