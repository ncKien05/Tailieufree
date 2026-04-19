# Sử dụng Python 3.10 nhỏ gọn
FROM python:3.10-slim

# Cài đặt các gói hệ thống cần thiết cho MySQL client, bcrypt, và Pillow (xử lý ảnh)
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    python3-dev \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Thiết lập thư mục làm việc
WORKDIR /app

# Sao chép và cài đặt thư viện trước để tận dụng Docker Cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ mã nguồn vào container
COPY . .

# Khai báo cổng 5000 cho Flask
EXPOSE 5000

# Các biến môi trường mặc định
ENV FLASK_APP=main.py
ENV FLASK_DEBUG=1
ENV PYTHONUNBUFFERED=1

# Tự động hóa quá trình Init Database và Tạo tài khoản Admin trước khi khởi chạy Web
# Dùng loop 'until' để đảm bảo không bị crash do MySQL khởi động/restart chậm hơn Flask
CMD ["sh", "-c", "until flask init-db; do echo 'Waiting for MySQL...'; sleep 3; done && flask create-admin && python -m flask run --host=0.0.0.0 --port=5000"]