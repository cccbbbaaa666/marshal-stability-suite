import hashlib
import json
import marshal
import platform
import sys


CASES = {
    "none": None,
    "big_int": 2**1000,
    "negative_zero": -0.0,
    "nan": float("nan"),
    "dict": {"a": 1, "b": [1, 2, 3]},
    "set": {"apple", "banana", "cherry"},
    "recursive_list": None,
    "code": compile("x = 1\ny = x + 2\n", "sample.py", "exec"),
}

recursive_list = []
recursive_list.append(recursive_list)
CASES["recursive_list"] = recursive_list

result = {
    "python_version": sys.version,
    "platform": platform.platform(),
    "marshal_version": marshal.version,
    "digests": {},
}

for name, value in CASES.items():
    try:
        blob = marshal.dumps(value)
        result["digests"][name] = {
            "sha256": hashlib.sha256(blob).hexdigest(),
            "size": len(blob),
        }
    except Exception as exc:
        result["digests"][name] = {
            "error": f"{type(exc).__name__}: {exc}",
        }

print(json.dumps(result, indent=2, sort_keys=True))
