# Gunakan gambar dasar Python
FROM python:3.9-slim

# Set direktori kerja dalam container
WORKDIR /app

# Salin file requirements.txt ke direktori kerja
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Salin semua file dari direktori kerja host ke direktori kerja container
COPY . .

# Expose port yang digunakan oleh Flask
EXPOSE 5000

# Jalankan aplikasi
CMD ["python", "bot.py"]
