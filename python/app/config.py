import os
import json
import nltk

# ==========================================
# КОНФИГУРАЦИЯ ПУТЕЙ
# ==========================================

# Базовая директория проекта (папка python/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Путь к данным NLTK
PROJECT_NLTK_PATH = os.path.join(BASE_DIR, 'nltk_data')
nltk.data.path.append(PROJECT_NLTK_PATH)

# Путь к словарю CEFR
CEFR_DICT_PATH = os.path.join(BASE_DIR, 'app', 'data', 'cefr_dict.json')

# ==========================================
# ЗАГРУЗКА РЕСУРСОВ NLTK
# ==========================================
nltk.download('punkt', download_dir=PROJECT_NLTK_PATH, quiet=True)
nltk.download('punkt_tab', download_dir=PROJECT_NLTK_PATH, quiet=True)
nltk.download('stopwords', download_dir=PROJECT_NLTK_PATH, quiet=True)
nltk.download('wordnet', download_dir=PROJECT_NLTK_PATH, quiet=True)
nltk.download('averaged_perceptron_tagger_eng', download_dir=PROJECT_NLTK_PATH, quiet=True)

# ==========================================
# ЗАГРУЗКА СЛОВАРЯ В СИСТЕМУ
# ==========================================
CEFR_DICTIONARY = {}
try:
    with open(CEFR_DICT_PATH, encoding='utf-8') as f:
        CEFR_DICTIONARY = json.load(f)
except FileNotFoundError:
    print(f"Warning: CEFR dictionary not found at {CEFR_DICT_PATH}!")