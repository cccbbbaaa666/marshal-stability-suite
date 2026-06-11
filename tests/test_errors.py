import io
import marshal
import unittest


class ErrorHandlingTests(unittest.TestCase):
    def test_dumps_rejects_unsupported_types(self) -> None:
        values = [object(), lambda x: x, ErrorHandlingTests]
        for value in values:
            with self.subTest(value=type(value).__name__):
                with self.assertRaises(ValueError):
                    marshal.dumps(value)

    def test_dump_rejects_nested_unsupported_values(self) -> None:
        values = [[1, object(), 3], {"a": 1, "b": object()}, (1, object())]
        for value in values:
            with self.subTest(kind=type(value).__name__):
                with self.assertRaises(ValueError):
                    marshal.dump(value, io.BytesIO())

    def test_loads_ignores_trailing_bytes(self) -> None:
        value = {"a": 1, "b": 2}
        blob = marshal.dumps(value) + b"trailing-data"
        self.assertEqual(value, marshal.loads(blob))

    def test_loads_rejects_truncated_streams(self) -> None:
        blob = marshal.dumps({"a": [1, 2, 3]})
        for length in range(1, len(blob)):
            with self.subTest(length=length):
                with self.assertRaises((EOFError, ValueError, TypeError)):
                    marshal.loads(blob[:length])

    def test_load_rejects_invalid_tag(self) -> None:
        with self.assertRaises((ValueError, TypeError, EOFError)):
            marshal.loads(b"?")


if __name__ == "__main__":
    unittest.main()
