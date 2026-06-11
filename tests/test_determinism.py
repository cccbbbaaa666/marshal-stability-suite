import io
import marshal
import struct
import unittest

from helpers import ALL_VERSIONS, CURRENT_VERSION, marshal_hex_in_subprocess


class DeterminismTests(unittest.TestCase):
    def test_repeated_dumps_are_hash_identical(self) -> None:
        cases = [
            None,
            True,
            2**1000,
            -0.0,
            float("inf"),
            float("nan"),
            complex(-1.5, 2.25),
            "\u4f60\u597d",
            b"\x00\xffabc",
            [1, 2, {"nested": (3, 4)}],
            {"alpha": 1, "beta": 2},
        ]
        for version in ALL_VERSIONS:
            for value in cases:
                with self.subTest(version=version, value=type(value).__name__):
                    blobs = [marshal.dumps(value, version) for _ in range(20)]
                    self.assertTrue(all(blob == blobs[0] for blob in blobs))

    def test_repeated_dumps_for_set_types_are_hash_identical(self) -> None:
        cases = [
            {"apple", "banana", "cherry", "date"},
            frozenset({("x", 1), ("y", 2), ("z", 3)}),
        ]
        for version in range(2, CURRENT_VERSION + 1):
            for value in cases:
                with self.subTest(version=version, value=repr(value)):
                    blobs = [marshal.dumps(value, version) for _ in range(20)]
                    self.assertTrue(all(blob == blobs[0] for blob in blobs))

    def test_dump_and_dumps_produce_identical_bytes(self) -> None:
        value = {"k": [1, 2, 3], "nested": {"x": True}}
        buffer = io.BytesIO()
        marshal.dump(value, buffer)
        self.assertEqual(buffer.getvalue(), marshal.dumps(value))

    def test_cross_process_hash_seed_changes_do_not_change_output(self) -> None:
        expressions = [
            "{'apple', 'banana', 'cherry', 'date', 'elderberry'}",
            "frozenset({('x', 1), ('y', 2), ('z', 3)})",
            "{'numbers': [1, 2, 3], 'flags': (True, False), 'set': {'aa', 'bb'}}",
            "compile('x = 1\\ny = x + 2\\n', 'sample.py', 'exec')",
        ]
        seeds = [0, 1, 2, 42, 123, 999]
        for expression in expressions:
            with self.subTest(expression=expression):
                outputs = {
                    marshal_hex_in_subprocess(expression, CURRENT_VERSION, seed)
                    for seed in seeds
                }
                self.assertEqual(len(outputs), 1)

    def test_custom_nan_payload_is_stable_for_same_input(self) -> None:
        value = struct.unpack(">d", bytes.fromhex("7ff8000000000001"))[0]
        blobs = [marshal.dumps(value) for _ in range(10)]
        self.assertTrue(all(blob == blobs[0] for blob in blobs))


if __name__ == "__main__":
    unittest.main()
