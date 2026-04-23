import unittest
from TextPatternGenerator import TextPatternGenerator

class TestTextPatternGenerator(unittest.TestCase):
    def test_generate_basic(self):
        generator = TextPatternGenerator(
            text_length=50, pattern_length=5, num_records=10, 
            languages=["en"], allow_pattern_not_in_text=False
        )
        data = generator.generate()
        
        self.assertEqual(len(data), 10)
        for item in data:
            self.assertEqual(len(item["text"]), 50)
            self.assertEqual(len(item["pattern"]), 5)
            self.assertTrue(item["pattern_in_text"])
            self.assertIn(item["pattern"], item["text"])

    def test_allow_pattern_not_in_text(self):
        generator = TextPatternGenerator(
            text_length=20, pattern_length=5, num_records=10, 
            languages=["en"], allow_pattern_not_in_text=True
        )
        data = generator.generate()
        
        not_in_text_count = sum(1 for item in data if not item["pattern_in_text"])
        # Theo logic hiện tại: một nửa số record sẽ không chứa pattern
        self.assertEqual(not_in_text_count, 5)
        for item in data:
            if not item["pattern_in_text"]:
                self.assertNotIn(item["pattern"], item["text"])

    def test_random_lengths(self):
        generator = TextPatternGenerator(
            is_random_length_text=True, min_text_length=15, max_text_length=25,
            is_random_length_pattern=True, min_pattern_length=3, max_pattern_length=6,
            num_records=5, languages=["en"], allow_pattern_not_in_text=False
        )
        data = generator.generate()
        
        for item in data:
            self.assertTrue(15 <= len(item["text"]) <= 25)
            self.assertTrue(3 <= len(item["pattern"]) <= 6)

    def test_invalid_language(self):
        with self.assertRaises(ValueError):
            TextPatternGenerator(languages=["unsupported_lang"])

if __name__ == '__main__':
    unittest.main()