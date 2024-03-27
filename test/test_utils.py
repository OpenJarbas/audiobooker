import unittest

from audiobooker.utils import extract_year
from audiobooker.utils import extractor_narrator


class TestExtractorNarrator(unittest.TestCase):
    def test_single_read_by(self):
        title1 = "1996 Stephen King – The Regulators Audiobook read by Frank Muller"
        narrator1 = extractor_narrator(title1)
        self.assertEqual(narrator1.first_name, "Frank")
        self.assertEqual(narrator1.last_name, "Muller")

        title2 = "The Shining Audiobook read by Campbell Scott"
        narrator2 = extractor_narrator(title2)
        self.assertEqual(narrator2.first_name, "Campbell")
        self.assertEqual(narrator2.last_name, "Scott")

        title3 = "Alice In Wonderland read by Natasha now has its own podcast"
        narrator3 = extractor_narrator(title3)
        self.assertEqual(narrator3.first_name, "Natasha")
        self.assertEqual(narrator3.last_name, "")

    def test_audiobook_by(self):
        title1 = "Harry Potter and the Chamber of Secrets Audiobook by Jim Dale"
        narrator1 = extractor_narrator(title1)
        self.assertEqual(narrator1.first_name, "Jim")
        self.assertEqual(narrator1.last_name, "Dale")

        title2 = "Pride and Prejudice Audiobook by Jane Austen"
        narrator2 = extractor_narrator(title2)
        self.assertEqual(narrator2.first_name, "Jane")
        self.assertEqual(narrator2.last_name, "Austen")

    def test_narrated_by(self):
        title1 = "The shadow over innsmouth by H.P. Lovecraft, narrated by Wayne June"
        narrator1 = extractor_narrator(title1)
        self.assertEqual(narrator1.first_name, "Wayne")
        self.assertEqual(narrator1.last_name, "June")

        title2 = "The Catcher in the Rye by J.D. Salinger, narrated by Matt Damon"
        narrator2 = extractor_narrator(title2)
        self.assertEqual(narrator2.first_name, "Matt")
        self.assertEqual(narrator2.last_name, "Damon")

    def test_no_narrator(self):
        title = "The Great Gatsby"
        narrator = extractor_narrator(title)
        self.assertIsNone(narrator)


class TestExtractYear(unittest.TestCase):
    def test_year_present(self):
        title1 = "1996 Stephen King – The Regulators Audiobook read by Frank Muller"
        self.assertEqual(extract_year(title1), 1996)

        title2 = "Harry Potter and the Chamber of Secrets (1998) Audiobook by Jim Dale"
        self.assertEqual(extract_year(title2), 1998)

    def test_no_year(self):
        title = "The Great Gatsby"
        self.assertEqual(extract_year(title), 0)

    def test_multiple_years(self):
        title = "The Odyssey (2001) and Moby Dick (1954) Audiobook by Some Narrator"
        # Only the first year should be extracted
        self.assertEqual(extract_year(title), 2001)

    def test_year_in_sentence(self):
        title = "This is a sentence with the year 2022 in it."
        self.assertEqual(extract_year(title), 2022)


if __name__ == '__main__':
    unittest.main()
