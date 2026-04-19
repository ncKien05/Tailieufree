# Tailieufree

Website chia sẻ tài liệu học tập, viết blog và cộng đồng dành cho sinh viên. Hệ thống được xây dựng bằng thiết kế Flask (Python) và phần quản trị dữ liệu MySQL 8.0.

## Yêu cầu hệ thống thiết yếu

- Môi trường Docker và Docker Compose (Khuyến nghị sử dụng để đồng bộ 100%).
- Hoặc cài đặt trực tiếp Python 3.10+ & MySQL Server (không khuyến khích nếu bạn không nắm vững cài đặt dependency C++ cho Pillow & bcrypt).

## Hướng dẫn khởi chạy dự án thần tốc (Qua Docker)

Sử dụng Docker là cách hoàn thiện nhất để tự động liên kết cơ sở dữ liệu và Web App.

### 1. Build và khởi động bộ máy chủ
Di chuyển cửa sổ cmd/terminal vào chung thư mục chứa file `docker-compose.yml` và chạy:
```bash
docker-compose up -d --build
```
Hệ thống sẽ tải toàn bộ dependency và tiến hành thiết lập máy chủ ở chế độ chạy ngầm (`-d`). Mọi Database, cấu trúc bảng lập trình và tài khoản Admin mặc định sẽ được **khởi tạo hoàn toàn tự động**.

### 2. Truy cập 
Chờ khoảng chục giây để hệ thống chạy ngầm khởi tạo lần đầu hoàn hảo, sau đó truy cập trình duyệt để sử dụng ứng dụng tại: [http://localhost:5000](http://localhost:5000)

**(Tài khoản Admin đã được tạo sẵn tự động để bạn truy cập trang Admin)**
- **Email đăng nhập:** `admin@tailieufree.vn`
- **Mật khẩu:** `Admin@123`

---

## 💡 Các lệnh thao tác với ứng dụng (Dành cho Dev)

- **Tắt và dừng hệ thống:**
  ```bash
  docker-compose down
  ```

- **Làm mới Toàn bộ - Xóa hệ thống cùng Database Cũ:**
  Nếu bạn có đổi file `models.py` hay Schema và muốn khởi tạo hệ thống mới cứng từ đầu, hãy thêm flag `-v` để drop cái volume lưu database cũ đi để build cái mới dễ dàng:
  ```bash
  docker-compose down -v
  docker-compose up -d --build
  ```

- **Xem lịch sử log hệ thống (Rất hữu ích khi fix lỗi Server 500):**
  ```bash
  docker-compose logs -f web
  ```