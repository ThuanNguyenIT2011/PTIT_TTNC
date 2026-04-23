import unittest
from BruteForce import BruteForce
from BoyerMoore import BoyerMoore

class TestStringMatching(unittest.TestCase):
    def setUp(self):
        self.text = "Ví dụ: Boyer Moore là một thuật toán. Boyer Moore có thể nhanh hơn."
        
    def test_bruteforce_match_case_sensitive(self):
        bf = BruteForce(self.text, "Boyer Moore", case_sensitive=True)
        result = bf.search()
        self.assertEqual(result.positions, [7, 38])
        self.assertGreater(result.comparisons, 0)
        
    def test_boyermoore_match_case_sensitive(self):
        BoyerMoore.initialize(self.text, "Boyer Moore", case_sensitive=True)
        BoyerMoore.mainloop()
        result = BoyerMoore.RESULT
        self.assertEqual(result.positions, [7, 38])
        self.assertGreater(result.comparisons, 0)

    def test_case_insensitive_match(self):
        # Brute Force
        bf = BruteForce(self.text, "boyer moore", case_sensitive=False)
        result_bf = bf.search()
        self.assertEqual(result_bf.positions, [7, 38])
        
        # Boyer Moore
        BoyerMoore.initialize(self.text, "boyer moore", case_sensitive=False)
        BoyerMoore.mainloop()
        result_bm = BoyerMoore.RESULT
        self.assertEqual(result_bm.positions, [7, 38])

    def test_pattern_not_found(self):
        bf = BruteForce(self.text, "Không tồn tại", case_sensitive=True)
        result_bf = bf.search()
        self.assertEqual(result_bf.positions, [])
        
        BoyerMoore.initialize(self.text, "Không tồn tại", case_sensitive=True)
        BoyerMoore.mainloop()
        result_bm = BoyerMoore.RESULT
        self.assertEqual(result_bm.positions, [])

    def test_empty_pattern(self):
        bf = BruteForce(self.text, "", case_sensitive=True)
        self.assertEqual(bf.search().positions, [])
        
        BoyerMoore.initialize(self.text, "", case_sensitive=True)
        BoyerMoore.mainloop()
        self.assertEqual(BoyerMoore.RESULT.positions, [])

    def test_pattern_longer_than_text(self):
        long_pattern = self.text + " phần thừa"
        bf = BruteForce(self.text, long_pattern, case_sensitive=True)
        self.assertEqual(bf.search().positions, [])
        
        BoyerMoore.initialize(self.text, long_pattern, case_sensitive=True)
        BoyerMoore.mainloop()
        self.assertEqual(BoyerMoore.RESULT.positions, [])

    def test_match_at_edges(self):
        text = "Bắt đầu và kết thúc bằng Bắt"
        
        bf = BruteForce(text, "Bắt", case_sensitive=True)
        self.assertEqual(bf.search().positions, [0, 25])
        
        BoyerMoore.initialize(text, "Bắt", case_sensitive=True)
        BoyerMoore.mainloop()
        self.assertEqual(BoyerMoore.RESULT.positions, [0, 25])

    def test_special_characters(self):
        text = "Biểu thức toán học: (a + b) * c = a*c + b*c !!!"
        pattern = "(a + b) * c"
        
        bf = BruteForce(text, pattern, case_sensitive=True)
        self.assertEqual(bf.search().positions, [20])
        
        BoyerMoore.initialize(text, pattern, case_sensitive=True)
        BoyerMoore.mainloop()
        self.assertEqual(BoyerMoore.RESULT.positions, [20])

if __name__ == '__main__':
    unittest.main()