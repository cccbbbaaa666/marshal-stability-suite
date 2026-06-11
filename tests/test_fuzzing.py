import marshal
import random
import unittest

from helpers import assert_marshaled_equal, random_supported_object


class FuzzingTests(unittest.TestCase):
    def test_seeded_random_fuzzing_for_round_trip_and_determinism(self) -> None:
        randomizer = random.Random(20260609)
        for case_index in range(300):
            value = random_supported_object(randomizer)
            with self.subTest(case_index=case_index, kind=type(value).__name__):
                first_blob = marshal.dumps(value)
                second_blob = marshal.dumps(value)
                self.assertEqual(first_blob, second_blob)
                loaded = marshal.loads(first_blob)
                assert_marshaled_equal(self, value, loaded)


if __name__ == "__main__":
    unittest.main()
