FROM python:3.12-slim
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Запускаем скачивание NLTK-пакетов прямо в процессе сборки контейнера.
# (Мы скажем NLTK сохранить всё в /app/nltk_data)
RUN python -c "import nltk; nltk.download('punkt', download_dir='/app/nltk_data'); nltk.download('punkt_tab', download_dir='/app/nltk_data'); nltk.download('stopwords', download_dir='/app/nltk_data'); nltk.download('wordnet', download_dir='/app/nltk_data')"

# Открываем порт 8000, на котором будет работать FastAPI
EXPOSE 8000

# Команда для запуска сервера (Uvicorn) при старте контейнера
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]