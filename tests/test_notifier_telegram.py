import unittest

from src.notifier_telegram import split_message_into_chunks


class SplitMessageTests(unittest.TestCase):
    def test_preserves_line_order_when_splitting(self) -> None:
        text = "Header line\n" + "\n".join(f"Item {i} with details" for i in range(5))
        limit = 30

        chunks = split_message_into_chunks(text, max_length=limit)

        self.assertTrue(chunks)
        self.assertTrue(all(len(chunk) <= limit for chunk in chunks))

        reconstructed_lines = []
        for chunk in chunks:
            reconstructed_lines.extend(chunk.splitlines())
        self.assertEqual(reconstructed_lines, text.splitlines())

    def test_long_line_is_chunked(self) -> None:
        long_line = "A" * 80
        text = f"Header\n{long_line}"
        limit = 25

        chunks = split_message_into_chunks(text, max_length=limit)

        self.assertGreater(len(chunks), 1)
        self.assertTrue(all(len(chunk) <= limit for chunk in chunks))
        stripped_original = text.replace("\n", "")
        stripped_reconstructed = "".join(chunk.replace("\n", "") for chunk in chunks)
        self.assertEqual(stripped_reconstructed, stripped_original)


if __name__ == "__main__":
    unittest.main()
