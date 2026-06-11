import math
import os
import random
import string
import subprocess
import sys
from types import CodeType
from typing import Any, Optional

import marshal

ALL_VERSIONS = tuple(range(marshal.version + 1))
CURRENT_VERSION = marshal.version
UNICODE_SAMPLES = ["\u4f60\u597d", "\u03c0", "\u2603"]


def assert_marshaled_equal(test_case, expected: Any, actual: Any) -> None:
    if isinstance(expected, float):
        if math.isnan(expected):
            test_case.assertTrue(math.isnan(actual))
            return
        if expected == 0.0:
            test_case.assertEqual(
                math.copysign(1.0, expected),
                math.copysign(1.0, actual),
            )
            return
        test_case.assertEqual(expected, actual)
        return

    if isinstance(expected, complex):
        assert_marshaled_equal(test_case, expected.real, actual.real)
        assert_marshaled_equal(test_case, expected.imag, actual.imag)
        return

    if isinstance(expected, bytearray):
        test_case.assertIsInstance(actual, (bytes, bytearray))
        test_case.assertEqual(bytes(expected), bytes(actual))
        return

    if isinstance(expected, tuple):
        test_case.assertIsInstance(actual, tuple)
        test_case.assertEqual(len(expected), len(actual))
        for left_item, right_item in zip(expected, actual):
            assert_marshaled_equal(test_case, left_item, right_item)
        return

    if isinstance(expected, list):
        test_case.assertIsInstance(actual, list)
        test_case.assertEqual(len(expected), len(actual))
        for left_item, right_item in zip(expected, actual):
            assert_marshaled_equal(test_case, left_item, right_item)
        return

    if isinstance(expected, dict):
        test_case.assertIsInstance(actual, dict)
        test_case.assertEqual(set(expected.keys()), set(actual.keys()))
        for key, value in expected.items():
            assert_marshaled_equal(test_case, value, actual[key])
        return

    if isinstance(expected, CodeType):
        test_case.assertIsInstance(actual, CodeType)
        test_case.assertEqual(marshal.dumps(expected), marshal.dumps(actual))
        return

    test_case.assertEqual(expected, actual)


def marshal_hex_in_subprocess(
    expression: str,
    version: int = CURRENT_VERSION,
    hash_seed: Optional[int] = None,
) -> str:
    code = (
        "import marshal, sys\n"
        "namespace = {\n"
        "    '__builtins__': __builtins__,\n"
        "    'bytearray': bytearray,\n"
        "    'compile': compile,\n"
        "    'complex': complex,\n"
        "    'float': float,\n"
        "    'frozenset': frozenset,\n"
        "    'StopIteration': StopIteration,\n"
        "    'Ellipsis': Ellipsis,\n"
        "}\n"
        "value = eval(sys.argv[1], namespace, namespace)\n"
        "print(marshal.dumps(value, int(sys.argv[2])).hex())\n"
    )
    env = os.environ.copy()
    if hash_seed is not None:
        env["PYTHONHASHSEED"] = str(hash_seed)
    result = subprocess.run(
        [sys.executable, "-c", code, expression, str(version)],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )
    return result.stdout.strip()


def build_deep_list(depth: int) -> list:
    root = []
    current = root
    for _ in range(depth):
        child = []
        current.append(child)
        current = child
    return root


def random_supported_object(randomizer: random.Random, depth: int = 0) -> Any:
    if depth >= 3 or randomizer.random() < 0.45:
        return random_scalar(randomizer)

    choice = randomizer.choice(["tuple", "list", "dict", "set", "frozenset"])
    size = randomizer.randint(0, 4)

    if choice == "tuple":
        return tuple(random_supported_object(randomizer, depth + 1) for _ in range(size))
    if choice == "list":
        return [random_supported_object(randomizer, depth + 1) for _ in range(size)]
    if choice == "dict":
        return {
            random_hashable_value(randomizer): random_supported_object(
                randomizer,
                depth + 1,
            )
            for _ in range(size)
        }

    values = {random_hashable_value(randomizer) for _ in range(size)}
    if choice == "set":
        return values
    return frozenset(values)


def random_hashable_value(randomizer: random.Random) -> Any:
    choice = randomizer.choice(["int", "bool", "str", "bytes", "tuple"])
    if choice == "int":
        return random_integer(randomizer)
    if choice == "bool":
        return randomizer.choice([True, False])
    if choice == "str":
        return random_string(randomizer)
    if choice == "bytes":
        return random_bytes(randomizer)
    return (random_integer(randomizer), random_string(randomizer))


def random_scalar(randomizer: random.Random) -> Any:
    choice = randomizer.choice(
        [
            "none",
            "bool",
            "int",
            "float",
            "complex",
            "str",
            "bytes",
            "bytearray",
        ]
    )
    if choice == "none":
        return None
    if choice == "bool":
        return randomizer.choice([True, False])
    if choice == "int":
        return random_integer(randomizer)
    if choice == "float":
        return random_float(randomizer)
    if choice == "complex":
        return complex(random_float(randomizer), random_float(randomizer))
    if choice == "str":
        return random_string(randomizer)
    if choice == "bytes":
        return random_bytes(randomizer)
    return bytearray(random_bytes(randomizer))


def random_integer(randomizer: random.Random) -> int:
    special_values = [0, 1, -1, 2**31 - 1, -(2**31), 2**63 - 1, -(2**63)]
    if randomizer.random() < 0.5:
        return randomizer.choice(special_values)
    bit_count = randomizer.randint(1, 256)
    value = randomizer.getrandbits(bit_count)
    if randomizer.choice([True, False]):
        return value
    return -value


def random_float(randomizer: random.Random) -> float:
    special_values = [
        0.0,
        -0.0,
        1.5,
        -2.75,
        float("inf"),
        float("-inf"),
        float("nan"),
    ]
    if randomizer.random() < 0.6:
        return randomizer.choice(special_values)
    return randomizer.uniform(-1_000_000.0, 1_000_000.0)


def random_string(randomizer: random.Random) -> str:
    if randomizer.random() < 0.3:
        return randomizer.choice(UNICODE_SAMPLES)
    size = randomizer.randint(0, 12)
    alphabet = string.ascii_letters + string.digits + "_-"
    return "".join(randomizer.choice(alphabet) for _ in range(size))


def random_bytes(randomizer: random.Random) -> bytes:
    size = randomizer.randint(0, 12)
    return bytes(randomizer.randrange(256) for _ in range(size))
