import random
from typing import List, Dict, Optional


class TextPatternGenerator:
    LANGUAGE_CHARSETS = {
        "en": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ ",
        "vi": "aăâbcdđeêghiklmnoôơpqrstuưvxyAĂÂBCDĐEÊGHIKLMNOÔƠPQRSTUƯVXY ",
        "fr": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZàâçéèêëîïôùûüÿæœÀÂÇÉÈÊËÎÏÔÙÛÜŸÆŒ ",
        "de": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZäöüßÄÖÜ ",
        "es": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZáéíóúñüÁÉÍÓÚÑÜ ",
        "jp": "あいうえおかきくけこさしすせそたちつてとなにぬねのまみむめもやゆよらりるれろわをんアイウエオカキクケコサシスセソタチツテトナニヌネノマミムメモヤユヨラリルレロワヲン ",
        "kr": "가나다라마바사아자차카타파하거너더러머버서어저처커터퍼허 ",
        "cn": "的一是在不了有人这中大为上个国我以要他时来用们生到作地于出就分对成会可主发年动同工也行 ",
    }

    def __init__(
        self,
        text_length: int = 50,
        pattern_length: int = 5,
        is_random_length_text: bool = False,
        is_random_length_pattern: bool = False,
        languages: Optional[List[str]] = None,
        num_records: int = 10,
        min_text_length: int = 10,
        max_text_length: int = 200,
        min_pattern_length: int = 2,
        max_pattern_length: int = 20,
        allow_pattern_not_in_text: bool = False,
        seed: Optional[int] = None,
    ):
        self.text_length = text_length
        self.pattern_length = pattern_length
        self.is_random_length_text = is_random_length_text
        self.is_random_length_pattern = is_random_length_pattern
        self.languages = languages or ["en"]
        self.num_records = num_records
        self.min_text_length = min_text_length
        self.max_text_length = max_text_length
        self.min_pattern_length = min_pattern_length
        self.max_pattern_length = max_pattern_length
        self.allow_pattern_not_in_text = allow_pattern_not_in_text

        if seed is not None:
            random.seed(seed)

        self._validate_inputs()

    def _validate_inputs(self):
        if not self.languages:
            raise ValueError("languages không được rỗng.")
        if self.num_records <= 0:
            raise ValueError("num_records phải > 0.")
        if self.text_length <= 0:
            raise ValueError("text_length phải > 0.")
        if self.pattern_length <= 0:
            raise ValueError("pattern_length phải > 0.")

        unsupported = [lang for lang in self.languages if lang not in self.LANGUAGE_CHARSETS]
        if unsupported:
            raise ValueError(
                f"Ngôn ngữ không hỗ trợ: {unsupported}. "
                f"Các ngôn ngữ hỗ trợ: {list(self.LANGUAGE_CHARSETS.keys())}"
            )

    def _distribute_records_evenly(self, total: int, items: List[str]) -> Dict[str, int]:
        """
        """
        base = total // len(items)
        remainder = total % len(items)

        result = {}
        for i, item in enumerate(items):
            result[item] = base + (1 if i < remainder else 0)
        return result

    def _get_text_length(self) -> int:
        if self.is_random_length_text:
            return random.randint(self.min_text_length, self.max_text_length)
        return self.text_length

    def _get_pattern_length(self) -> int:
        if self.is_random_length_pattern:
            return random.randint(self.min_pattern_length, self.max_pattern_length)
        return self.pattern_length

    def _generate_random_text(self, length: int, language: str) -> str:
        charset = self.LANGUAGE_CHARSETS[language]
        text = "".join(random.choice(charset) for _ in range(length)).strip()
        if text:
            return text
        return "".join(random.choice(charset.replace(" ", "")) for _ in range(length))

    def _generate_pattern_in_text(self, text: str, pattern_length: int) -> str:
        if pattern_length > len(text):
            pattern_length = len(text)

        start_idx = random.randint(0, len(text) - pattern_length)
        return text[start_idx:start_idx + pattern_length]

    def _generate_pattern_not_in_text(
        self,
        text: str,
        pattern_length: int,
        language: str,
        max_attempts: int = 200
    ) -> str:
        charset = self.LANGUAGE_CHARSETS[language].replace(" ", "")

        if pattern_length <= 0:
            raise ValueError("pattern_length phải > 0.")

        for _ in range(max_attempts):
            pattern = "".join(random.choice(charset) for _ in range(pattern_length))
            if pattern not in text:
                return pattern

        base_pattern = self._generate_pattern_in_text(text, pattern_length)
        base_list = list(base_pattern)

        for i, ch in enumerate(base_list):
            alternatives = [c for c in charset if c != ch]
            random.shuffle(alternatives)
            for alt in alternatives:
                candidate = base_list.copy()
                candidate[i] = alt
                candidate_str = "".join(candidate)
                if candidate_str not in text:
                    return candidate_str

        raise RuntimeError("Không thể sinh pattern không nằm trong text.")

    def _build_match_plan(self) -> List[bool]:
        """
        Nếu allow_pattern_not_in_text=True:
            số lượng True/False gần bằng nhau.
            True  = pattern nằm trong text
            False = pattern không nằm trong text
        Nếu False:
            tất cả đều True
        """
        if not self.allow_pattern_not_in_text:
            return [True] * self.num_records

        num_match = self.num_records // 2
        num_not_match = self.num_records - num_match

        plan = [True] * num_match + [False] * num_not_match
        random.shuffle(plan)
        return plan

    def generate(self) -> List[Dict]:
        results = []

        lang_distribution = self._distribute_records_evenly(self.num_records, self.languages)

        match_plan = self._build_match_plan()
        plan_index = 0

        for language in self.languages:
            for _ in range(lang_distribution[language]):
                current_text_length = self._get_text_length()
                current_pattern_length = self._get_pattern_length()

                if current_pattern_length > current_text_length:
                    current_pattern_length = current_text_length

                text = self._generate_random_text(current_text_length, language)

                should_match = match_plan[plan_index]
                plan_index += 1

                if should_match:
                    pattern = self._generate_pattern_in_text(text, current_pattern_length)
                else:
                    pattern = self._generate_pattern_not_in_text(
                        text=text,
                        pattern_length=current_pattern_length,
                        language=language
                    )

                results.append({
                    "language": language,
                    "text": text,
                    "pattern": pattern,
                    "text_length": len(text),
                    "pattern_length": len(pattern),
                    "pattern_in_text": pattern in text
                })

        random.shuffle(results)
        return results
    
if __name__ == "__main__":
    generator = TextPatternGenerator(
        text_length=5,
        pattern_length=1,
        is_random_length_text=False,
        is_random_length_pattern=False,
        languages=["en", "vi", "fr"],
        num_records=10,
        min_text_length=5,
        max_text_length=10,
        min_pattern_length=3,
        max_pattern_length=5,
        allow_pattern_not_in_text=True,
        seed=42
    )

    dataset = generator.generate()
    for record in dataset:
        print(record)