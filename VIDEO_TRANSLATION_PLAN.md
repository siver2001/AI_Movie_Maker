# Kế hoạch phát triển Module: Video Voice Translator (Modular Design)

## Mục tiêu
Xây dựng hệ thống tách và dịch giọng nói video với kiến trúc **Module hóa cao (Highly Modular)**. Các thành phần hoạt động độc lập, dễ dàng thay thế, nâng cấp hoặc tái sử dụng cho các mục đích khác.

## Kiến trúc Module (Proposed Architecture)

Hệ thống sẽ được chia thành các class chuyên biệt (Single Responsibility Principle).

```
ai_movie_maker/
└── content_dubber/               # Tên package mới (hoặc voice_translator)
    ├── __init__.py
    ├── audio_extractor.py        # Trích xuất audio từ video
    ├── vocal_separator.py        # Tách giọng (Demucs)
    ├── speech_transcriber.py     # Transcribe (Whisper)
    ├── text_translator.py        # Dịch thuật (Gemini)
    ├── voice_synthesizer.py      # TTS (Edge-TTS)
    ├── audio_mixer.py            # Xử lý ghép/mix audio
    └── dubbing_pipeline.py       # Class điều phối (Orchestrator)
```

## Chi tiết các Module

### 1. Module: AudioExtractor (`audio_extractor.py`)
*   **Chức năng**: Trích xuất luồng âm thanh gốc từ file video.
*   **Input**: Đường dẫn file Video (mp4, mkv...).
*   **Output**: Đường dẫn file Audio (wav/mp3).
*   **Công nghệ**: `ffmpeg-python` hoặc `moviepy`.

### 2. Module: VocalSeparator (`vocal_separator.py`)
*   **Chức năng**: Tách file audio thành 2 thành phần: Vocals (giọng nói) và Accompaniment (nhạc nền/tiếng động).
*   **Input**: File Audio gốc.
*   **Output**:
    *   `vocals.wav` (chứa giọng nói sạch).
    *   `background.wav` (nhạc nền đã loại bỏ giọng nói).
*   **Công nghệ**: `demucs` (Meta).

### 3. Module: SpeechTranscriber (`speech_transcriber.py`)
*   **Chức năng**: Chuyển đổi audio giọng nói thành văn bản kèm thông tin thời gian (timestamps).
*   **Input**: File `vocals.wav`.
*   **Output**: List các segments. Mỗi segment gồm: `{ start, end, text }`.
*   **Công nghệ**: `openai-whisper`.

### 4. Module: TextTranslator (`text_translator.py`)
*   **Chức năng**: Dịch danh sách các câu thoại sang ngôn ngữ đích, giữ nguyên ngữ cảnh.
*   **Input**: List segments (text gốc).
*   **Output**: List segments (text đã dịch).
*   **Công nghệ**: `google-genai` (Gemini).

### 5. Module: VoiceSynthesizer (`voice_synthesizer.py`)
*   **Chức năng**: Chuyển đổi văn bản đã dịch thành file âm thanh (TTS).
*   **Input**: Segment đã dịch (`text`, `duration` mong muốn - optional để time stretch).
*   **Output**: File audio cho từng câu thoại hoặc một file audio dài nối liền.
*   **Công nghệ**: `edge-tts`.

### 6. Module: AudioMixer (`audio_mixer.py`)
*   **Chức năng**:
    *   Đồng bộ thời gian (Time-stretching/Padding) audio mới dựa trên timestamp cũ.
    *   Trộn (Mix) audio mới vào track nhạc nền (`background.wav`).
    *   Điều chỉnh volume (tự động giảm nhạc nền khi có thoại - Ducking).
*   **Input**: List audio files (TTS), `background.wav`, Timestamps.
*   **Output**: File `final_mix.wav`.

### 7. Module: DubbingPipeline (`dubbing_pipeline.py`)
*   **Chức năng**: Gọi lần lượt các module trên. Quản lý luồng dữ liệu, xử lý lỗi chung.

## Phương án công nghệ

| Chức năng | Công nghệ / Thư viện | Ghi chú |
| :--- | :--- | :--- |
| **Separation** | `demucs` | Yêu cầu PyTorch. Cân nhắc dùng model `htdemucs` (nhanh hơn). |
| **STT** | `openai-whisper` | Model `base` hoặc `small` cân bằng giữa tốc độ/chất lượng. |
| **Translation** | `google-genai` | Sử dụng prompt kỹ để dịch văn phong nói (conversational). |
| **TTS** | `edge-tts` | Chọn giọng đọc phù hợp với giới tính (cần detect gender nếu có thể - *Advanced*). |

## Kế hoạch thực hiện (Updated Tasks)

- [ ] **Giai đoạn 1: Base Modules** (Implement độc lập, test độc lập)
    - [ ] Setup `audio_extractor.py` & `audio_mixer.py`.
    - [ ] Setup `vocal_separator.py` (Demucs).
    - [ ] Setup `speech_transcriber.py` (Whisper).

- [ ] **Giai đoạn 2: Translation & TTS Modules**
    - [ ] Setup `text_translator.py` (Gemini API).
    - [ ] Setup `voice_synthesizer.py` (Edge-TTS).

- [ ] **Giai đoạn 3: Logic Đồng bộ (Synchronization)**
    - [ ] Xử lý bài toán khớp thời gian (Audio Duration Matching) trong `AudioMixer`. Đây là phần khó nhất.

- [ ] **Giai đoạn 4: Đóng gói Pipeline**
    - [ ] Viết class `DubbingPipeline` kết nối tất cả.
