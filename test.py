class BadCharacterHeuristic:
    PATLEN = None
    DATA_TABLE = {}

    @classmethod
    def build(cls, pattern):
        cls.PATLEN = len(pattern)
        for index, char in enumerate(pattern):
            cls.DATA_TABLE[char] = {"index": index, "shift": (cls.PATLEN - 1) - index}

    @classmethod
    def shift(cls, index, char):
        bad_char = cls.DATA_TABLE.get(char)
        # NOT EXIST IN PATTERN.
        if bad_char is None:
            return cls.PATLEN
        else:
            # EXIST ON THE RIGHT OF CURRENT INDEX.
            if bad_char["index"] > index:
                return 1 + ((cls.PATLEN - 1) - index)
            # EXIST ON THE LEFT OF CURRENT INDEX.
            return bad_char["shift"]


class GoodSuffixHeuristic:
    PATLEN = None
    DATA_TABLE = {}

    @classmethod
    def build(cls, pattern: str):
        cls.PATLEN = len(pattern)

        for j in range(cls.PATLEN - 1, -1, -1):
            suffix = pattern[j + 1 : cls.PATLEN]
            suffix_length = len(suffix)
            preceding_char = pattern[j]

            k = j
            while True:
                for i in range(suffix_length):
                    if k + i >= 0 and pattern[k + i] != suffix[i]:
                        break
                else:
                    if k < 0 or (k >= 0 and pattern[k - 1] != preceding_char):
                        cls.DATA_TABLE[j] = {"shift": (cls.PATLEN - 1) + 1 - k}
                        break
                k -= 1

    @classmethod
    def shift(cls, index):
        return cls.DATA_TABLE[index]["shift"]


from time import perf_counter


class Main:
    TEXT = PATTERN = STRINGLEN = PATLEN = None
    RESULT = {"time": None, "comparison": None, "position": None}

    @classmethod
    def initialize(cls, text, pattern):
        cls.TEXT = text
        cls.PATTERN = pattern
        cls.STRINGLEN = len(text)
        cls.PATLEN = len(pattern)

        BadCharacterHeuristic.build(pattern)
        GoodSuffixHeuristic.build(pattern)

    @classmethod
    def mainloop(cls):
        cls.RESULT = {"time": 0, "comparison": 0, "position": []}
        start_time = perf_counter()
        i = cls.PATLEN - 1
        while i < cls.STRINGLEN:
            j = cls.PATLEN - 1
            while j >= 0 and cls.PATTERN[j] == cls.TEXT[i]:
                cls.RESULT["comparison"] += 1
                i -= 1
                j -= 1
            cls.RESULT["comparison"] += 1

            if j == -1:
                cls.RESULT["position"].append(i + 1)
                i += 1 + GoodSuffixHeuristic.shift(j + 1)
            else:
                i += max(
                    BadCharacterHeuristic.shift(j, cls.TEXT[i]),
                    GoodSuffixHeuristic.shift(j),
                )
        cls.RESULT["time"] = (perf_counter() - start_time) * 1000


if __name__ == "__main__":
    TEXT = "TPSIA"
    PATTERN = "P"

    Main.initialize(TEXT, PATTERN)
    Main.mainloop()
    print("RESULT: ", Main.RESULT)