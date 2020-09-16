# CanvasAIO - port of CanvasAPI to asyncio/aiohttp

This fork of CanvasAPI is a relatively quick port to async Python, using the `aiohttp` and `aioresponses` library (instead of `requests` and `requests_mock`; the latter for unit testing).

Feel free to use/experiment with it (at your own risk, of course).  This fork is *not* affiliated in any way related to the UCF project (and, therefore, not supported by them either).  However, feel free to use/experiment with it (at your own risk, of course).

For further information, the [original CanvasAPI repository](https://github.com/ucfopen/canvasapi) may be of some help.

## Notes

The original API is modified as little as possible.  For the most part, all you should need to do is:
- For the `Canvas` client object:
  - Either use it as an async context manager (e.g., `async with Canvas(API_URL, API_KEY) as canvas: ...`),
  - Or remember to close it when done (e.g., `canvas.close()`).
- For all request methods:
  - If they **do _not_** return a `PaginatedList`, then just `await` the method call itself.
  - If they **do** return a `PaginatedList` (say, `pl`), do not await the method call; instead, either await elements (e.g., `await pl[i]`) or asynchronously iterate over the result or slices (e.g., `async for it in pl` or `async for it in pl[i:j]`).