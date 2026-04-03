# Sử dụng Python 3.10 nhỏ gọn
FROM python:3.10-slim

# Cài đặt các gói hệ thống cần thiết cho MySQL client và các thư viện bảo mật (bcrypt) [cite: 2026-03-07]
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    python3-dev \
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

# Khởi chạy bằng python -m flask để đảm bảo ổn định
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]