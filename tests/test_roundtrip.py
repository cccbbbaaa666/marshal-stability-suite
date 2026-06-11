import io
import marshal
import unittest

from helpers import ALL_VERSIONS, CURRENT_VERSION, assert_marshaled_equal


class RoundTripTests(unittest.TestCase):
    def test_common_values_round_trip_across_all_versions(self) -> None:
        cases = [
            None,
            True,
            False,
            StopIteration,
            Ellipsis,
            0,
            1,
            -1,
            2**31 - 1,
            -(2**31),
            2**1000,
            -(2**1000),
            0.0,
            -0.0,
            1.5,
            float("inf"),
            float("-inf"),
            float("nan"),
            complex(1.5, -2.25),
            "",
            "ascii",
            "\u4f60\u597d",
            b"",
            b"\x00\xffabc",
            (),
            (1, "a", None),
            [],
            [1, 2, 3],
            {},
            {"a": 1, 2: "b"},
        ]
        for version in ALL_VERSIONS:
            for value in cases:
                with self.subTest(version=version, value=type(value).__name__):
                    blob = marshal.dumps(value, version)
                    loaded = marshal.loads(blob)
                    assert_marshaled_equal(self, value, loaded)

    def test_set_types_round_trip_from_version_two(self) -> None:
        if CURRENT_VERSION < 2:
            self.skipTest("Current interpreter does not support marshal version 2")

        cases = [set(), {1, 2, 3}, frozenset(), frozenset({("x", 1), ("y", 2)})]
        for version in range(2, CURRENT_VERSION + 1):
            for value in cases:
                with self.subTest(version=version, value=repr(value)):
                    blob = marshal.dumps(value, version)
                    loaded = marshal.loads(blob)
                    assert_marshaled_equal(self, value, loaded)

    def test_bytearray_is_loaded_back_as_bytes(self) -> None:
        value = bytearray(b"\x00\x01example\xff")
        blob = marshal.dumps(value)
        loaded = marshal.loads(blob)
        self.assertIsInstance(loaded, bytes)
        self.assertEqual(bytes(value), loaded)

    def test_code_object_round_trip(self) -> None:
        source = "def square(x):\n    return x * x\n"
        code = compile(source, "sample_module.py", "exec")
        blob = marshal.dumps(code)
        loaded = marshal.loads(blob)
        assert_marshaled_equal(self, code, loaded)

    def test_dump_and_load_file_api_round_trip(self) -> None:
        value = {"numbers": [1, 2, 3], "flags": (True, False)}
        buffer = io.BytesIO()
        marshal.dump(value, buffer)
        buffer.seek(0)
        loaded = marshal.load(buffer)
        assert_marshaled_equal(self, value, loaded)

    def test_recursive_and_shared_references_round_trip(self) -> None:
        if CURRENT_VERSION < 3:
            self.skipTest("Recursive references require marshal version >= 3")

        recursive_list = []
        recursive_list.append(recursive_list)
        loaded_list = marshal.loads(marshal.dumps(recursive_list))
        self.assertIs(loaded_list, loaded_list[0])

        recursive_dict = {}
        recursive_dict["self"] = recursive_dict
        loaded_dict = marshal.loads(marshal.dumps(recursive_dict))
        self.assertIs(loaded_dict, loaded_dict["self"])

        shared = []
        aliased = [shared, shared]
        loaded_alias = marshal.loads(marshal.dumps(aliased))
        self.assertIs(loaded_alias[0], loaded_alias[1])

    def test_recursive_values_are_rejected_before_version_three(self) -> None:
        recursive_list = []
        recursive_list.append(recursive_list)
        recursive_dict = {}
        recursive_dict["self"] = recursive_dict

        for version in range(min(3, CURRENT_VERSION)):
            with self.subTest(version=version, kind="list"):
                with self.assertRaises(ValueError):
                    marshal.dumps(recursive_list, version)
            with self.subTest(version=version, kind="dict"):
                with self.assertRaises(ValueError):
                    marshal.dumps(recursive_dict, version)


if __name__ == "__main__":
    unittest.main()
