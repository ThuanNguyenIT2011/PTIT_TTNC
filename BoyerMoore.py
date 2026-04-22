from time import perf_counter
from SearchResult import SearchResult


class BadCharacterHeuristic:
    PATLEN = None
    DATA_TABLE = {}

    @classmethod
    def build(cls, pattern):
        cls.PATLEN = len(pattern)
        cls.DATA_TABLE = {}
        for index, char in enumerate(pattern):
            cls.DATA_TABLE[char] = {"index": index, "shift": (cls.PATLEN - 1) - index}

    @classmethod
    def shift(cls, index, char):
        bad_char = cls.DATA_TABLE.get(char)
        if bad_char is None:
            return cls.PATLEN
        else:
            if bad_char["index"] > index:
                return 1 + ((cls.PATLEN - 1) - index)
            return bad_char["shift"]


class GoodSuffixHeuristic:
    PATLEN = None
    DATA_TABLE = {}

    @classmethod
    def build(cls, pattern: str):
        cls.PATLEN = len(pattern)
        cls.DATA_TABLE = {}

        for j in range(cls.PATLEN - 1, -1, -1):
            suffix = pattern[j + 1: cls.PATLEN]
            suffix_length = len(suffix)
            preceding_char = pattern[j]

            k = j
            while True:
                for i in range(suffix_length):
                    if k + i >= 0 and pattern[k + i] != suffix[i]:
                        break
                else:
                    if k < 0 or (k > 0 and pattern[k - 1] != preceding_char):
                        cls.DATA_TABLE[j] = {"shift": cls.PATLEN - k}
                        break
                k -= 1

        # fallback để tránh KeyError nếu có index chưa được build
        for j in range(cls.PATLEN):
            cls.DATA_TABLE.setdefault(j, {"shift": 1})

    @classmethod
    def shift(cls, index):
        return cls.DATA_TABLE[index]["shift"]


class BoyerMoore:
    ORIGINAL_TEXT = ORIGINAL_PATTERN = None
    TEXT = PATTERN = STRINGLEN = PATLEN = None
    CASE_SENSITIVE = False
    RESULT = {"time": None, "comparison": None, "position": None}

    @classmethod
    def initialize(cls, text, pattern, case_sensitive: bool = False):
        cls.ORIGINAL_TEXT = text
        cls.ORIGINAL_PATTERN = pattern
        cls.CASE_SENSITIVE = case_sensitive

        if case_sensitive:
            cls.TEXT = text
            cls.PATTERN = pattern
        else:
            cls.TEXT = text.lower()
            cls.PATTERN = pattern.lower()

        cls.STRINGLEN = len(cls.TEXT)
        cls.PATLEN = len(cls.PATTERN)

        BadCharacterHeuristic.build(cls.PATTERN)
        GoodSuffixHeuristic.build(cls.PATTERN)

    @classmethod
    def mainloop(cls):
        cls.RESULT = SearchResult([], 0, 0.0)
        start_time = perf_counter()

        if cls.PATLEN == 0 or cls.PATLEN > cls.STRINGLEN:
            cls.RESULT.elapsed_ms = (perf_counter() - start_time) * 1000
            return

        i = cls.PATLEN - 1

        while i < cls.STRINGLEN:
            j = cls.PATLEN - 1

            while j >= 0 and cls.PATTERN[j] == cls.TEXT[i]:
                cls.RESULT.comparisons += 1
                i -= 1
                j -= 1

            if j == -1:
                cls.RESULT.positions.append(i + 1)
                i += 1 + GoodSuffixHeuristic.shift(0)
            else:
                cls.RESULT.comparisons += 1
                i += max(
                    BadCharacterHeuristic.shift(j, cls.TEXT[i]),
                    GoodSuffixHeuristic.shift(j),
                )

        cls.RESULT.elapsed_ms = (perf_counter() - start_time) * 1000

    @classmethod
    def build_BoyerMoore_steps(cls):
        steps = []

        if cls.PATLEN == 0:
            steps.append({
                "window_start": 0,
                "compare_index": None,
                "matched_until": -1,
                "message": "Pattern rỗng, không thực hiện tìm kiếm."
            })
            return steps

        i = cls.PATLEN - 1

        while i < cls.STRINGLEN:
            window_start = i - (cls.PATLEN - 1)
            original_i = i
            j = cls.PATLEN - 1

            steps.append({
                "window_start": window_start,
                "compare_index": None,
                "matched_until": -1,
                "message": f"Đưa pattern vào vị trí i = {window_start}."
            })

            matched = True

            while j >= 0:
                is_match = cls.PATTERN[j] == cls.TEXT[i]

                # hiển thị text/pattern gốc để người dùng dễ hiểu
                display_text_char = cls.ORIGINAL_TEXT[i]
                display_pattern_char = cls.ORIGINAL_PATTERN[j]

                steps.append({
                    "window_start": window_start,
                    "compare_index": i,
                    "matched_until": i if is_match else i,
                    "message": (
                        f"So sánh text[{i}] = '{display_text_char}' với pattern[{j}] = '{display_pattern_char}' -> "
                        + ("KHỚP" if is_match else "KHÔNG KHỚP")
                    )
                })

                if not is_match:
                    matched = False

                    bc_shift = BadCharacterHeuristic.shift(j, cls.TEXT[i])
                    gs_shift = GoodSuffixHeuristic.shift(j)
                    shift = max(bc_shift, gs_shift)

                    steps.append({
                        "window_start": window_start,
                        "compare_index": i,
                        "matched_until": i + 1,
                        "message": (
                            f"Mismatch, bad character shift = {bc_shift}, "
                            f"good suffix shift = {gs_shift}, "
                            f"chọn dịch {shift} vị trí."
                        )
                    })

                    i = original_i + shift
                    break

                i -= 1
                j -= 1

            if matched and j == -1:
                found_pos = i + 1

                steps.append({
                    "window_start": found_pos,
                    "compare_index": None,
                    "matched_until": found_pos + cls.PATLEN - 1,
                    "message": f"Tìm thấy pattern tại vị trí {found_pos}."
                })

                shift = GoodSuffixHeuristic.shift(0)

                steps.append({
                    "window_start": found_pos,
                    "compare_index": None,
                    "matched_until": found_pos + cls.PATLEN - 1,
                    "message": f"Match hoàn toàn, dịch pattern sang phải {shift} vị trí."
                })

                i = found_pos + cls.PATLEN - 1 + shift

        return steps


if __name__ == "__main__":
    TEXT = "Which-finally-Halts.--at-that-THAT"
    PATTERN = "AT-THAT"

    print("=== Case sensitive = False ===")
    BoyerMoore.initialize(TEXT, PATTERN, case_sensitive=False)
    BoyerMoore.mainloop()
    print("Positions: ", BoyerMoore.RESULT.positions)
    print("Comparisons: ", BoyerMoore.RESULT.comparisons)
    print("Elapsed Time (ms): ", BoyerMoore.RESULT.elapsed_ms)

    print("\n=== Case sensitive = True ===")
    BoyerMoore.initialize(TEXT, PATTERN, case_sensitive=True)
    BoyerMoore.mainloop()
    print("Positions: ", BoyerMoore.RESULT.positions)
    print("Comparisons: ", BoyerMoore.RESULT.comparisons)
    print("Elapsed Time (ms): ", BoyerMoore.RESULT.elapsed_ms)