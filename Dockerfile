# 使用輕量版 Python 映像檔
FROM python:3.10-slim

# 設定工作目錄
WORKDIR /app

# 先複製需求清單以利用快取優化建置速度
COPY requirements.txt .

# 安裝套件
RUN pip install --no-cache-dir -r requirements.txt

# 複製其餘程式碼
COPY . .

# 開放 FastAPI 預設埠號 8000
EXPOSE 8000

# 啟動指令 (假設你的檔名是 main.py)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]