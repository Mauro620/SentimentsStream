from __future__ import annotations

from functools import wraps
from typing import Callable, Optional

from flask import Request, jsonify, request


def require_api_key(api_key: Optional[str]) -> Callable:
    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not api_key:
                return fn(*args, **kwargs)
            header_key = request.headers.get("X-API-Key")
            if header_key != api_key:
                return jsonify({"error": "unauthorized"}), 401
            return fn(*args, **kwargs)

        return wrapper

    return decorator
