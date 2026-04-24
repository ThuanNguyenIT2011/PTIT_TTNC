# PTIT - String Matching App 🔍

Ứng dụng Desktop mô phỏng, đánh giá và ứng dụng các thuật toán tìm kiếm chuỗi (String Matching Algorithms) bao gồm **Brute Force** và **Boyer Moore**. Đồ án được thiết kế với giao diện Tkinter hiện đại, hỗ trợ trực quan hóa thuật toán và đánh giá hiệu năng chuyên sâu.

## 🌟 Tính năng nổi bật

1. **Algorithm Visualization (Mô phỏng thuật toán)**
   - Tìm kiếm chuỗi trực tiếp trên đoạn văn bản nhập vào hoặc tải lên.
   - Tính năng **Mô phỏng từng bước (Step-by-step Simulation)** hoặc **Tự động chạy (Auto Play)** để xem cách Brute Force và Boyer Moore hoạt động đằng sau.
   - Hỗ trợ tuỳ chọn phân biệt chữ hoa/chữ thường (Case sensitive).

2. **Check Performance (Đánh giá hiệu năng)**
   - Tích hợp bộ sinh dữ liệu ngẫu nhiên với nhiều tuỳ chọn: độ dài text/pattern, ngôn ngữ, tập mẫu có sẵn,...
   - So sánh trực tiếp thời gian chạy (ms) và số phép so sánh (comparisons) giữa 2 thuật toán.
   - Hiển thị bảng chi tiết và vẽ biểu đồ trực quan bằng **Matplotlib**.
   - Hỗ trợ xuất báo cáo đánh giá ra file **PDF** (kèm biểu đồ) hoặc xuất dữ liệu ra file **CSV**.

3. **Search File (Tìm kiếm trong tệp)**
   - Ứng dụng thuật toán để tìm kiếm từ khoá trong các tệp tài liệu thực tế.
   - Hỗ trợ đọc đa dạng các định dạng: `.txt`, `.pdf`, `.docx`, `.xlsx`, `.csv` và các file mã nguồn (`.py`, `.cpp`, `.js`,...).

4. **Minigame: Word Defense 🎮**
   - Ứng dụng thực tế hai thuật toán vào một trò chơi thời gian thực (Real-time).
   - Cho phép người chơi gõ từ khóa (pattern) để so sánh chuỗi và "bắn" phá các từ vựng đang rơi xuống.
   - Tích hợp hiệu ứng âm thanh cực kỳ sống động (nhạc nền, âm thanh bắn trúng, mất mạng) bằng thư viện `pygame`.

## 💻 Yêu cầu hệ thống

- **Python**: Phiên bản >= 3.8
- Môi trường hỗ trợ hiển thị giao diện đồ hoạ (Windows, macOS, Linux có GUI).

## 🚀 Cài đặt và Sử dụng

**Bước 1:** Mở terminal/command prompt tại thư mục chứa mã nguồn.

**Bước 2:** Cài đặt các thư viện phụ thuộc bằng `pip`:
```bash
pip install -r requirements.txt
```

**Bước 3:** Chạy file chính để khởi động ứng dụng:
```bash
python main.py
```

## 📂 Cấu trúc dự án

- `main.py`: File khởi chạy chính, chứa toàn bộ mã giao diện (UI) bằng thư viện `Tkinter`.
- `BruteForce.py`: Triển khai thuật toán Brute Force và logic sinh bước mô phỏng.
- `BoyerMoore.py`: Triển khai thuật toán Boyer Moore (áp dụng Bad Character & Good Suffix heuristics).
- `FileTextReader.py`: Module hỗ trợ đọc nội dung từ các định dạng file khác nhau (PDF, Word, Excel,...).
- `TextPatternGenerator.py`: Module sinh dữ liệu test ngẫu nhiên để phục vụ đánh giá hiệu năng.
- `requirements.txt`: Danh sách các thư viện bên ngoài cần thiết (matplotlib, pypdf, python-docx, openpyxl).