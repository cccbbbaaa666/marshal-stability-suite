import marshal
import unittest

from helpers import CURRENT_VERSION, build_deep_list


class BoundaryTests(unittest.TestCase):
    def test_integer_boundaries_round_trip(self) -> None:
        values = [
            0,
            1,
            -1,
            2**31 - 1,
            -(2**31),
            2**31,
            -(2**31) - 1,
            2**63 - 1,
            -(2**63),
            2**1000,
            -(2**1000),
        ]
        for value in values:
            with self.subTest(value=value):
                self.assertEqual(value, marshal.loads(marshal.dumps(value)))

    def test_string_and_bytes_length_boundaries(self) -> None:
        lengths = [0, 1, 255, 256, 1024]
        for length in lengths:
            with self.subTest(kind="str", length=length):
                value = "a" * length
                self.assertEqual(value, marshal.loads(marshal.dumps(value)))
            with self.subTest(kind="bytes", length=length):
                value = b"x" * length
                self.assertEqual(value, marshal.loads(marshal.dumps(value)))

    def test_small_tuple_boundary(self) -> None:
        lengths = [0, 1, 255, 256]
        for length in lengths:
            with self.subTest(length=length):
                value = tuple(range(length))
                blob = marshal.dumps(value)
                self.assertEqual(value, marshal.loads(blob))
                self.assertEqual(blob, marshal.dumps(value))

    def test_empty_and_large_collections(self) -> None:
        cases = [
            [],
            {},
            set(),
            frozenset(),
            list(range(10_000)),
            {index: index for index in range(5_000)},
            set(range(5_000)),
            frozenset(range(5_000)),
        ]
        for value in cases:
            with self.subTest(kind=type(value).__name__, size=len(value)):
                blob = marshal.dumps(value)
                self.assertEqual(value, marshal.loads(blob))
                self.assertEqual(blob, marshal.dumps(value))

    def test_deep_but_valid_nesting_round_trip(self) -> None:
        value = build_deep_list(200)
        self.assertEqual(value, marshal.loads(marshal.dumps(value)))

    def test_excessive_nesting_is_rejected(self) -> None:
        value = build_deep_list(2500)
        with self.assertRaises(ValueError):
            marshal.dumps(value)

    def test_recursive_version_boundary(self) -> None:
        if CURRENT_VERSION < 3:
            self.skipTest("Recursive references require marshal version >= 3")

        value = []
        value.append(value)
        with self.assertRaises(ValueError):
            marshal.dumps(value, 2)

        loaded = marshal.loads(marshal.dumps(value))
        self.assertIs(loaded, loaded[0])


if __name__ == "__main__":
    unittest.main()
