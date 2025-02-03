from unittest import TestCase

from cert_host_scraper.utils import divide_chunks, strip_url


class TestStripUrl(TestCase):
    def test_strip_protocol_and_www(self):
        self.assertEqual("example.com", strip_url("https://www.example.com"))

    def test_strip_protocol(self):
        self.assertEqual("example.com", strip_url("https://example.com"))

    def test_strip_www(self):
        self.assertEqual("example.com", strip_url("www.example.com"))

    def test_strip_path(self):
        self.assertEqual("example.com", strip_url("example.com/"))
        self.assertEqual("example.com", strip_url("example.com/hello"))


class TestDivideChunks(TestCase):
    def test_even_chunks(self):
        self.assertEqual(
            list(divide_chunks(["a", "b", "c", "d"], 2)), [["a", "b"], ["c", "d"]]
        )

    def test_uneven_chunks(self):
        self.assertEqual(list(divide_chunks(["a", "b", "c"], 2)), [["a", "b"], ["c"]])

    def test_single_element_chunks(self):
        self.assertEqual(list(divide_chunks(["a", "b", "c"], 1)), [["a"], ["b"], ["c"]])

    def test_chunk_size_larger_than_list(self):
        self.assertEqual(list(divide_chunks(["a", "b"], 5)), [["a", "b"]])

    def test_empty_list(self):
        self.assertEqual(list(divide_chunks([], 3)), [])

    def test_chunk_size_one(self):
        self.assertEqual(list(divide_chunks(["a"], 1)), [["a"]])
