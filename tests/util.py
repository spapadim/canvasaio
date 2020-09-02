import json
import os
import re
import inspect
import unittest

from typing import Optional

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
