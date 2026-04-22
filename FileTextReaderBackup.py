from __future__ import annotations

from pathlib import Path
from typing import Union

from pypdf import PdfReader
from docx import Document


class DocumentReader:

    SUPPORTED_EXTENSIONS = {".txt", ".pdf", ".docx"}

    def read(self, file_path: Union[str, Path], encoding: str = "utf-8") -> str:
       
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"Không tìm thấy file: {path}")

        if not path.is_file():
            raise ValueError(f"Đây không phải file hợp lệ: {path}")

        ext = path.suffix.lower()

        if ext not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Định dạng không hỗ trợ: {ext}. "
                f"Chỉ hỗ trợ: {', '.join(sorted(self.SUPPORTED_EXTENSIONS))}"
            )

        if ext == ".txt":
            return self._read_txt(path, encoding)
        if ext == ".pdf":
            return self._read_pdf(path)
        if ext == ".docx":
            return self._read_docx(path)

        raise ValueError(f"Không thể xử lý file: {path}")

    def _read_txt(self, path: Path, encoding: str = "utf-8") -> str:
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            return path.read_text(encoding="utf-8", errors="ignore")

    def _read_pdf(self, path: Path) -> str:
        reader = PdfReader(str(path))
        pages_text = []

        for page in reader.pages:
            text = page.extract_text() or ""
            pages_text.append(text)

        return "\n".join(pages_text).strip()

    def _read_docx(self, path: Path) -> str:
        doc = Document(str(path))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n".join(paragraphs).strip()


if __name__ == "__main__":
    reader = FileTextReader()

    file_path = "./File.pdf"  
    try:
        content = reader.read(file_path)
        print(content)
    except Exception as e:
        print(f"Lỗi: {e}")