# 🎨 HƯỚNG DẪN SỬ DỤNG MUSE STUDIO

Chào mừng bạn đến với **Muse Studio** — trung tâm điều khiển và sáng tạo hình ảnh, video AI với tài khoản Muse cá nhân.

---

## 🚀 1. Cách khởi động (Dành cho Windows)

1. Nhấp đúp vào tệp tin **`start.bat`**.
2. Lần đầu tiên chạy, hệ thống sẽ tự động cấu hình môi trường nhẹ (mất khoảng 30 giây).
3. Trình duyệt web sẽ tự động mở giao diện **`http://localhost:18610/studio/`**.

*(Lưu ý: Không đóng cửa sổ dòng lệnh đen trong lúc sử dụng).*

---

## 🔑 2. Cách thêm tài khoản Muse để bắt đầu sáng tạo

**Cách 1 — Tự động (khuyên dùng, không cần F12):**
1. Trên thanh menu bên trái, chọn **Tài khoản Muse** &rarr; bấm nút **👁 Tự động trích xuất**.
2. Một cửa sổ trình duyệt sẽ tự mở trên máy đang chạy Muse Studio — hãy đăng nhập muse.ai trong cửa sổ đó.
3. Hệ thống tự nhận diện cookie (kể cả httpOnly) và thêm tài khoản vào pool. Xong!

**Cách 2 — Thủ công:**
1. Trên thanh menu bên trái, chọn **Tài khoản Muse** &rarr; bấm nút **+ Thêm tài khoản**.
2. Bấm vào nút **💡 Hướng dẫn lấy Cookie (3 bước)** ngay trên ô nhập:
   - **Bước 1:** Đăng nhập vào [muse.ai](https://muse.ai) trên Chrome hoặc Edge.
   - **Bước 2:** Nhấn phím `F12` &rarr; chọn tab **Network** &rarr; gõ lọc `session`.
   - **Bước 3:** Nhấn `F5` tải lại trang &rarr; bấm vào dòng `session` &rarr; trong mục *Request Headers*, sao chép giá trị của dòng **Cookie:** và dán vào Muse Studio.
3. Nhấn **Thêm tài khoản**. Hệ thống sẽ tự động kiểm tra phiên và hạn mức khả dụng của bạn.

---

## ✨ 3. Các tính năng nổi bật

- 🎨 **Image Generation (Tạo ảnh):** Mô tả chi tiết khung cảnh, chọn tỉ lệ (16:9, 1:1, 9:16,...), có thể tải ảnh tham chiếu lên để vẽ theo phong cách.
- 🎬 **Video Generation (Tạo video):** Nhập kịch bản chuyển động, điều chỉnh độ dài (5s - 10s), xem trực tiếp video sau khi render.
- 💬 **Chat Muse:** Trò chuyện, viết kịch bản, lên ý tưởng thông minh với Muse Spark.
- 🖼️ **Thư viện Media:** Quản lý toàn bộ ảnh và video đã tạo trên máy tính của bạn, hỗ trợ xem trước và tải về chỉ bằng 1 cú nhấp chuột.

---

## 🔒 4. Cam kết bảo mật & Quyền riêng tư

- **100% Chạy Cục Bộ (Local):** Mọi tác vụ, cookie và file media đều được xử lý và lưu trữ trực tiếp trên máy tính của bạn. Không gửi dữ liệu về bất kỳ máy chủ bên thứ ba nào.
- **An toàn tài khoản:** Tài khoản chạy từ chính IP mạng nhà của bạn, đảm bảo tính ổn định và độ bền cao nhất.

---

## 🛡️ 5. Bản hardened v1.5.5 — những gì đã được siết lại

Bản này bạn đang dùng đã được harden, bạn chịu mọi rủi ro khi sử dụng:

- **Cookie được mã hóa at-rest:** dùng Fernet, key tự sinh lần đầu lưu ở `data/.cookie_key` (chmod 600). Tài khoản cũ plaintext sẽ tự migrate khi khởi động. Muốn dùng key cố định: tạo bằng `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"` rồi điền vào `MUSE_STUDIO_COOKIE_KEY`.
- **Backup accounts:** mỗi lần ghi `accounts.json` sẽ backup xoay vòng `.bak`, `.bak.1`..`.bak.3`.
- **Tắt online-upgrade mặc định:** các endpoint `/admin/update/upgrade`, `/admin/repo/pull`, `/admin/repo/push` sẽ trả 403 trừ khi bạn đặt `MUSE_STUDIO_ENABLE_UPGRADE=1`. Khuyên update thủ công bằng `git pull`.
- **CORS & headers:** thêm `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`. Muốn siết CORS: đặt `MUSE_STUDIO_CORS_ALLOW_ALL=0` và liệt kê domain trong `MUSE_STUDIO_CORS_ORIGINS`.
- **Rate-limit:** mặc định 120 req/phút/IP cho `/v1/*`, chỉnh bằng `MUSE_STUDIO_RATE_LIMIT`.

### ⚠️ Lưu ý an toàn khi expose ra internet
1. Đổi `MUSE_STUDIO_KEY` ngay, không dùng key mẫu.
2. Chạy sau reverse proxy (Nginx) với HTTPS, chặn cổng CDP 19210 bằng firewall, chỉ mở 18610 qua proxy.
3. Không dùng tài khoản Muse chính; mỗi IP/VPS chỉ nên chạy vài account để tránh bị khóa hàng loạt.
4. Sao lưu định kỳ thư mục `data/` (đã mã hóa cookie nhưng vẫn cần giữ key file `.cookie_key`).
