from functools import wraps

from sanic import Blueprint, response


bp = Blueprint(__name__)


class FlatReqError(Exception):
    """Validation error from flatreq."""
    def __init__(self, message, status=400):
        self.json = {"error": message}
        self.status = status
        super().__init__(message)


@bp.exception(FlatReqError)
def handle_flatreqerror(request, exception):
    """Handle errors coming from flatreq as 4xx HTTP responses."""
    return response.json(exception.json, status=exception.status)


def flatreq2dict(request, fields):
    """GET/POST single-level/field request data to dictionary."""
    if request.method == "GET":
        multi = True
        source = request.args
    elif request.method == "POST":
        if request.content_type == "application/json":
            multi = False
            source = request.json
        elif request.content_type == "application/x-www-form-urlencoded":
            multi = True
            source = request.form
        else:
            raise FlatReqError("invalid_content_type", status=415)
    else:
        raise FlatReqError("invalid_method", status=405)

    try:
        for k, v in source.items():
            if k not in fields:
                raise FlatReqError("has_unrequired_fields")
            if (multi and len(v) > 1) or (not multi and
                                          isinstance(v, (list, dict))):
                raise FlatReqError("has_multivalued_fields")
        if multi:
            return {k: source[k][0] for k in fields if k in source}
        else:
            return {k: source[k] for k in fields if k in source}
    except (AttributeError, IndexError, KeyError):
        raise FlatReqError("invalid_input")


def flatreq(fields):
    """Decorator for GET/POST handler with a flat request input."""
    def decorator(afunc):
        @wraps(afunc)
        async def wrapper(request, **kwargs):
            kwargs.update(flatreq2dict(request, fields))
            return await afunc(request=request, **kwargs)
        return wrapper
    return decorator
