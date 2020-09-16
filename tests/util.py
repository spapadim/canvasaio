import json
import os
import re
import inspect
import unittest
import inspect
import itertools

from typing import Optional, Sequence, List, Dict, Set, Container, Iterable, Callable, Union, TypeVar

from aioresponses import aioresponses
from aiohttp import hdrs

from tests import settings

ALL_URLS = re.compile('.*')

def register_uris(
    requirements: dict,
    requests_mocker: aioresponses,
    base_url: Optional[str] = None,
) -> None:
    """
    Given a list of required fixtures and an requests_mocker object,
    register each fixture as a uri with the mocker.

    :param base_url: str
    :param requirements: dict
    :param requests_mocker: requests_mock.mocker.Mocker
    """
    if base_url is None:
        base_url = settings.BASE_URL_WITH_VERSION
    for fixture, objects in requirements.items():
        try:
            with open("tests/fixtures/{}.json".format(fixture)) as file:
                data = json.loads(file.read())
        except (IOError, ValueError):
            raise ValueError("Fixture {}.json contains invalid JSON.".format(fixture))

        if not isinstance(objects, list):
            raise TypeError("{} is not a list.".format(objects))

        for obj_name in objects:
            obj = data.get(obj_name)

            if obj is None:
                raise ValueError(
                    "{} does not exist in {}.json".format(obj_name.__repr__(), fixture)
                )

            methods = hdrs.METH_ALL if obj["method"] == "ANY" else { obj["method"] }
            endpoint = obj["endpoint"]
            if type(endpoint) == str: # Original CanvasAPI fixture spec
                if endpoint == "ANY":
                    url = ALL_URLS
                else:
                    url = base_url + endpoint
            elif type(endpoint) == dict:  # Extended spec, that allows specifying match type
                if not (1 <= len(endpoint) <= 2):
                    raise TypeError("{} does not contain exactly one key-value pair".format(endpoint))
                if "url_pattern" in endpoint:
                    url = re.compile(re.escape(base_url) + endpoint["url_pattern"])
                elif "url" in endpoint:
                    if endpoint.get("ignore_query", False):
                        url = re.compile(re.escape(base_url) + re.escape(endpoint["url"]) + r'(\?.+)?$')
                    else:
                        url = base_url + endpoint["url"]  # Same as plain-string endpoint (above)
                else:
                    raise ValueError("Endpoint spec has neither url nor url_pattern")
            else:
                raise TypeError("{} is not a string or dict".format(endpoint))

            try:
                for method in methods:
                    requests_mocker.add(
                        url,
                        method,
                        payload=obj.get("data"),  # json
                        status=obj.get("status_code", 200),
                        headers=obj.get("headers", {}),
                        repeat=obj.get("repeat", False),
                    )
            except Exception as e:
                print(e)


def cleanup_file(filename):
    """
    Remove a test file from the system. If the file doesn't exist, ignore.

    `Not as stupid as it looks. <http://stackoverflow.com/a/10840586>_`
    """
    try:
        os.remove(filename)
    except OSError:
        pass


# TODO Make docstring coherent...!
def aioresponse_mock(class_or_func=None, *, method_prefix: str = "test_"):
    """
    Decorator that wraps aioresponses(), so that it can also be applied to
    a unittest.TestCase class, in addition to individual methods/functions.

    :param class_or_func: The class or function/coroutine to decorate.

    If decorating a class, then the class will be modified, so all methods
    whose name starts with method_prefix are decorated with aioresponses().
    """
    def decorator(class_or_func):
        if inspect.isclass(class_or_func):
            if not issubclass(class_or_func, unittest.TestCase):
                raise ValueError("Cannot decorate classes that aren't TestCases")
            for attr_name in dir(class_or_func):
                if not attr_name.startswith(method_prefix):
                    continue
                attr = getattr(class_or_func, attr_name)
                if not inspect.isfunction(attr):
                    continue
                # Attr is a method whose name starts with method_prefix: 
                #   decorate it, modifying class in-place
                setattr(class_or_func, attr_name, aioresponses()(attr))
            return class_or_func  # Return edited class
        else:
            # Pass thru
            return aioresponses()(class_or_func)

    if class_or_func is None:
        # Decorating with arguments, needs to return the actual decorator
        return decorator
    else:
        # Decorating without arguments
        return decorator(class_or_func)


# Miscellaneous debugging aids

_Elt = TypeVar('_Elt')
_IdxSpec = Iterable[Union[int, slice]]

def _idx_spec_to_set(spec: _IdxSpec, len: int) -> Set[int]:
    ret = set()
    for s in spec:
        if type(s) == int:
            ret.add(s)
        elif type(s) == slice:
            ret.update(range(*s.indices(len)))
        else:
            raise ValueError("Invalid element in index filter spec")
    return ret

def _filter_seq(
    s: Iterable[_Elt], 
    keep: Optional[_IdxSpec] = None, 
    skip: Optional[_IdxSpec] = None,
) -> List[_Elt]:
    """
    Filter a sequence based on specification of which indices to keep and which to skip (i.e., discard).

    :param s: Sequence to be filtered
    :param keep: Iterable of integers or slice objects that specify indices to keep.
        If ommitted, then all indices are implicitly kept
    :param skip: Iterable of integers or slice objects that further specify which indices to skip.
        This specification takes precedence over keep (i.e., if an index appears in both keep and skip, it will be skipped)

    :return: A new list containing the filtered elements of s.
    """
    if keep is None and skip is None:
        return list(s)

    if keep is not None:
        idx_set = _idx_spec_to_set(keep, len(s))
    else:
        idx_set = set(range(len(s)))
    if skip is not None:
        idx_set = set(range(len(s))) - _idx_spec_to_set(skip, len(s))
    ret = []
    for i, v in enumerate(s):
        if i in idx_set:
            ret.append(v)
    return ret

_Key = TypeVar('_Key')
_Val = TypeVar('_Val')
def _filter_dict(
    d: Dict[_Key, _Val],
    keep: Optional[Container[_Key]] = None,
    skip: Optional[Container[_Key]] = None,
) -> Dict[_Key, _Val]:
    """
    Filter a dictionary based on specification of which keys to keep and which to skip (i.e., discard).

    :param d: The dictionary to be filtered
    :param keep: A container of keys to keep. If ommitted, all are implicitly kept.
    :param skip: A container of keys to skip. Takes precedence over keep (i.e., keys that appear in both will be skipped).

    :return: A new dictionary containing the filtered key-value pairs from d.
    """
    ret = {}
    for k, v in d.items():
        if (keep is None or k in keep) and (skip is None or k not in skip):
            ret[k] = v
    return ret

def _format_args(args, kwargs):
  #return ', '.join(itertools.chain((f'{a!r}' for a in args), (f'{name}={val!r}' for name, val in kwargs.items())))
  return ', '.join(itertools.chain((f'{a}' for a in args), (f'{name}={val}' for name, val in kwargs.items())))

def _args_from_frame(frame):
  arginfo = inspect.getargvalues(frame)
  args = arginfo.locals.get(arginfo.varargs, ())
  kwargs = {argname: arginfo.locals[argname] for argname in arginfo.args}
  kwargs.update(arginfo.locals.get(arginfo.keywords, {}))
  return args, kwargs

def _format_stack(
    stack: List[inspect.FrameInfo], 
    line_prefix: str = "", 
    depth: Optional[int] = None, 
    include_args: bool = False,
) -> str:
    if depth is not None:
        stack = stack[:depth]
    ret = ""
    for i, frame in enumerate(stack):
        argstr = _format_args(*_args_from_frame(frame.frame)) if include_args else ""
        ret += f"{line_prefix}{i:2d}: {frame.function}({argstr})  [{frame.filename}:{frame.lineno}]\n"
    return ret

def log_function_decorator(
    function: Callable, 
    log_fn: Callable = print,
    *,
    log_stack: bool = False, log_stack_args: dict = {},
    keep_args: Optional[_IdxSpec] = None, skip_args: Optional[_IdxSpec] = None,
    keep_kwargs: Optional[Container[str]] = None, skip_kwargs: Optional[Container[str]] = None,
) -> Callable:
    log_stack_args = dict(line_prefix='    ', **log_stack_args)
    def _logged_function(*args, **kwargs):
        log_args = _filter_seq(args, keep_args, skip_args)
        log_kwargs = _filter_dict(kwargs, keep_kwargs, skip_kwargs)
        log_fn(
            f"CALL {function.__qualname__}" + 
            f"({_format_args(log_args, log_kwargs)})")
        if log_stack:
            stack = inspect.stack()[1:]
            log_fn(f"CALL STACK\n{_format_stack(stack, **log_stack_args)[:-1]}")
        return function(*args, **kwargs)
    return _logged_function

def log_class_method(
    cls: type, method_name: str,
    log_fn: Callable = print,
    *,
    log_stack: bool = False, log_stack_args: dict = {},
    keep_args: Optional[_IdxSpec] = None, skip_args: Optional[_IdxSpec] = None,
    keep_kwargs: Optional[Container[str]] = None, skip_kwargs: Optional[Container[str]] = None,
) -> None:
    method = getattr(cls, method_name)
    skip_args = (0,) if skip_args is None else itertools.chain(skip_args, (0,))
    logged_method = log_function_decorator(
        method, log_fn=log_fn,
        log_stack=log_stack, log_stack_args=log_stack_args,
        keep_args=keep_args, skip_args=skip_args,
        keep_kwargs=keep_kwargs, skip_kwargs=skip_kwargs,
    )
    setattr(cls, method_name, logged_method)

def log_class(
    cls: type, log_fn: Callable = print, 
    *, 
    log_stack: bool = False, log_stack_args: dict = {},
) -> None:
    for attrname in dir(cls):
        if inspect.isfunction(getattr(cls, attrname)):
            log_class_method(cls, attrname, log_fn=log_fn, log_stack=log_stack, log_stack_args=log_stack_args)