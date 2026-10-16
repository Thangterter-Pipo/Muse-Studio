# 🎨 Muse Studio - Trung Tâm Điều Khiển Sáng Tạo AI

**🌐 Ngôn ngữ / Language:** [English](./README.md) · **Tiếng Việt**

Trung tâm điều khiển web độc lập và cổng kết nối API chuẩn OpenAI dành cho Muse AI. Biến tài khoản Muse cá nhân của bạn thành một studio AI cục bộ tốc độ cao hỗ trợ tạo ảnh, sản xuất video và trò chuyện ngôn ngữ lớn.

---

## 🌟 Tính Năng Nổi Bật

- **🎨 Tạo hình ảnh (Muse Image):** Tạo ảnh Text-to-Image & Image-to-Image chất lượng cao với đa dạng tỉ lệ khung hình (`16:9`, `1:1`, `9:16`, `4:3`, `3:4`).
- **🎬 Sản xuất video (Muse Video):** Tạo video chuyển động AI mượt mà từ mô tả văn bản hoặc khung hình ảnh tham chiếu.
- **💬 Trò chuyện AI (Muse Spark):** Chuẩn OpenAI Chat Completions với phản hồi trực tiếp dạng luồng (SSE streaming).
- **⚡ Tối ưu hóa phản hồi nhanh (Hot-Session Fast Path):** Gửi prompt siêu tốc qua React DOM State và giữ kết nối Chromium nóng, giảm tối đa độ trễ.
- **🔑 Quản lý nhiều API Key:** Dễ dàng tạo và quản lý nhiều khóa API độc lập để cắm vào các công cụ AI khác (Cursor, NextChat, Cherry Studio, Dify, OpenWebUI).
- **🚀 Đăng nhập tự động 1-Click:** Tự động mở Chrome/Edge để đăng nhập và trích xuất cookie phiên qua CDP mà không cần bấm F12.
- **📊 Theo dõi Hạn mức & Quota thời gian thực:** Đọc chính xác hạn mức gói tuần và token bổ sung không thời hạn (hỗ trợ cả Tiếng Việt và Tiếng Anh).
- **🔒 100% Cục bộ & Bảo mật quyền riêng tư:** Toàn bộ tài khoản, cookie và tệp tin media được lưu trữ trực tiếp trên máy tính của bạn.

---

## 🚀 Khởi Động Nhanh (Windows)

1. Tải về file nén phiên bản mới nhất từ mục Releases trên GitHub hoặc clone repository.
2. Nhấp đúp vào tệp tin **`start.bat`**.
   - Hệ thống sẽ tự động cài đặt thư viện cần thiết và khởi động máy chủ.
3. Trình duyệt web sẽ tự động mở:
   ```
   http://localhost:18610/studio/
   ```

---

## 🔌 Kết Nối Với Các Công Cụ AI Khác

Muse Studio cung cấp endpoint tương thích 100% chuẩn OpenAI:

- **Base URL:** `http://localhost:18610/v1` (hoặc `http://127.0.0.1:18610/v1`)
- **API Key:** Vào tab **API & Khóa truy cập** trong Muse Studio &rarr; Bấm **Tạo API Key mới**.
- **Danh sách Models khả dụng:**
  - `muse-spark`: Trò chuyện, viết mã (coding) và lên ý tưởng.
  - `muse-image`: Tạo ảnh nghệ thuật.
  - `muse-video`: Tạo video chuyển động AI.

### Ví dụ cấu hình: NextChat / Cherry Studio / Cursor
- **Nhà cung cấp:** OpenAI / Custom OpenAI
- **Địa chỉ API (Base URL):** `http://127.0.0.1:18610/v1`
- **Mô hình (Model):** `muse-spark`

---

## 🛠️ Cài Đặt Thủ Công (Đa Nền Tảng)

```bash
# Clone repository
git clone https://github.com/Thangterter-Pipo/Muse-Studio.git
cd Muse-Studio

# Cài đặt thư viện phụ thuộc
pip install -r requirements.txt

# Khởi chạy server
uvicorn app:app --host 0.0.0.0 --port 18610
```

---

## ☕ Ủng Hộ Tác Giả (Donate)

Nếu thấy Muse Studio hữu ích cho công việc và trải nghiệm của bạn, bạn có thể ủng hộ tác giả thông qua nút **Ủng hộ tác giả** ngay trên giao diện dashboard!

---

## 📄 Giấy Phép

Dự án được phát hành theo giấy phép mã nguồn mở MIT License - xem tệp [LICENSE](LICENSE) để biết thêm chi tiết.
