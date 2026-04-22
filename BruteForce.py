import time
from SearchResult import SearchResult


class BruteForce:
    def __init__(self, text: str, pattern: str, case_sensitive: bool = True):
        self.original_text = text
        self.original_pattern = pattern
        self.case_sensitive = case_sensitive

        if case_sensitive:
            self.text = text
            self.pattern = pattern
        else:
            self.text = text.lower()
            self.pattern = pattern.lower()

        self.positions = []
        self.comparisons = 0

        self.n = len(self.text)
        self.m = len(self.pattern)

    def search(self) -> SearchResult:
        start = time.perf_counter()
        self.positions = []
        self.comparisons = 0

        if self.m == 0:
            return SearchResult([], 0, 0.0)

        for i in range(self.n - self.m + 1):
            match = True
            for j in range(self.m):
                self.comparisons += 1
                if self.text[i + j] != self.pattern[j]:
                    match = False
                    break
            if match:
                self.positions.append(i)

        elapsed_ms = (time.perf_counter() - start) * 1000
        return SearchResult(self.positions, self.comparisons, elapsed_ms)

    def build_bruteforce_steps(self):
        steps = []
        if self.m == 0:
            return steps

        for i in range(self.n - self.m + 1):
            steps.append({
                "window_start": i,
                "compare_index": None,
                "matched_until": -1,
                "message": f"Đưa pattern vào vị trí i = {i}."
            })

            matched = True
            for j in range(self.m):
                is_match = self.text[i + j] == self.pattern[j]

                # Hiển thị text/pattern gốc cho dễ nhìn
                display_text_char = self.original_text[i + j]
                display_pattern_char = self.original_pattern[j]

                steps.append({
                    "window_start": i,
                    "compare_index": i + j,
                    "matched_until": i + j - 1,
                    "message": (
                        f"So sánh text[{i + j}] = '{display_text_char}' với "
                        f"pattern[{j}] = '{display_pattern_char}' -> "
                        + ("KHỚP" if is_match else "KHÔNG KHỚP")
                    )
                })

                if not is_match:
                    matched = False
                    steps.append({
                        "window_start": i,
                        "compare_index": i + j,
                        "matched_until": i + j - 1,
                        "message": "Mismatch, dịch pattern sang phải 1 vị trí."
                    })
                    break

            if matched:
                steps.append({
                    "window_start": i,
                    "compare_index": None,
                    "matched_until": i + self.m - 1,
                    "message": f"Tìm thấy pattern tại vị trí {i}."
                })

        # print(steps)
        return steps


if __name__ == "__main__":
    TEXT = "Ví dụ: Boyer Moore là một thuật toán tìm kiếm chuỗi. Boyer Moore có thể nhanh hơn Brute Force trong nhiều trường hợp."
    PATTERN = "ví"

    print("=== So sánh chính xác hoa thường ===")
    bf1 = BruteForce(TEXT, PATTERN, case_sensitive=True)
    result1 = bf1.search()
    print("Positions:", result1.positions)
    print("Comparisons:", result1.comparisons)
    print("Elapsed Time (ms):", result1.elapsed_ms)

    print("\n=== So sánh bất chấp hoa thường ===")
    bf2 = BruteForce(TEXT, PATTERN, case_sensitive=False)
    result2 = bf2.search()
    print("Step", bf2.build_bruteforce_steps())
    print("Positions:", result2.positions)
    print("Comparisons:", result2.comparisons)
    print("Elapsed Time (ms):", result2.elapsed_ms)