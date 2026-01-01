# AI Movie Maker v3.2

Tool tạo video quảng cáo tự động bằng AI (Gemini + Edge TTS + MoviePy).

## Tính năng chính
- **Tạo kịch bản**: Viết kịch bản quảng cáo chi tiết với Gemini AI.
- **Giọng đọc AI**: Tạo giọng đọc tiếng Việt tự nhiên (Nam/Nữ) với nhiều cảm xúc.
- **Dựng phim tự động**: Ghép ảnh, âm thanh và phụ đề thành video hoàn chỉnh.
- **Tuỳ chỉnh cao**: Chỉnh sửa kịch bản, chọn nhạc nền, tỷ lệ khung hình (16:9, 9:16).

## Cài đặt

1. **Yêu cầu hệ thống**:
   - Python 3.8 trở lên.
   - Đã cài đặt `git`.

2. **Cài đặt thư viện**:
   Mở terminal tại thư mục dự án và chạy:
   ```bash
   pip install -r requirements.txt
   ```

## Cách chạy chương trình

1. **Khởi động ứng dụng**:
   ```bash
   streamlit run ai_movie_maker/app.py
   ```

2. **Sử dụng**:
   - Nhập **Gemini API Key**.
   - Nhập ý tưởng sản phẩm (ví dụ: "Review iPhone 17").
   - Bấm **Generate Script**.
   - Kéo xuống từng cảnh:
     - Chỉnh sửa lời thoại (nếu cần).
     - Bấm **🎵 Generate Audio**.
     - Tải ảnh lên (nếu có) hoặc để trống.
     - Bấm **🎬 Render Scene**.
   - Cuối cùng bấm **🎞 Render Full Movie** để xuất video.

## Cấu trúc dự án
- `ai_movie_maker/app.py`: File chính chạy ứng dụng.
- `ai_movie_maker/services/`: Chứa logic xử lý (Audio, Video, Generator).
- `requirements.txt`: Danh sách thư viện cần thiết.
