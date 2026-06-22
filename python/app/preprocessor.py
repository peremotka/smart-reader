import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from collections import Counter

from app.config import CEFR_DICTIONARY

LEMMATIZER = WordNetLemmatizer()
STOP_WORDS = set(stopwords.words("english"))

LEVEL_SCALE = ["A1", "A2", "B1", "B2", "C1", "C2"]
# Хэш-таблица для мгновенного поиска веса уровня O(1)
LEVEL_WEIGHTS = {lvl: idx for idx, lvl in enumerate(LEVEL_SCALE)}

def clean_and_tokenize(text: str) -> list:
    """
    Очищает текст от знаков препинания, тегов HTML, токенизирует с помощью NLTK
    и приводит к нижнему регистру.

    Аргументы:
    text (str): Исходная строка для обработки.

    Возвращает:
    list: Список токенов.
    """
    text = text.lower()

    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'https?://\S+|www\.\S+|\S+\.(com|ru|net|org|io)\S*', ' ', text)

    tokens = word_tokenize(text)

    return tokens

def get_wordnet_pos(tag: str) -> str:
    """
    Вспомогательная функция: переводит теги NLTK в формат, который понятен лемматизатору WordNet.
    """
    if tag.startswith('V'):
        return 'v'  # Глагол (Verb)
    elif tag.startswith('J'):
        return 'a'  # Прилагательное (Adjective)
    elif tag.startswith('R'):
        return 'r'  # Наречие (Adverb)
    else:
        return 'n'  # По умолчанию — существительное (Noun)

def lemmatize_with_pos(tokens: list) -> list:
    """
    Лемматизирует слова с учетом их реальной части речи.

    Аргументы:
    tokens (list): Список исходных слов (токенов).

    Возвращает:
    list: Список базовых форм слов (лемм).
    """
    pos_tags = nltk.pos_tag(tokens)

    return [
        LEMMATIZER.lemmatize(word, pos=get_wordnet_pos(tag))
        for word, tag in pos_tags
    ]

def filter_tokens(tokens: list) -> list:
    """
    Удаляет стоп-слова, знаки препинания и токены длиной меньше 2 символов.

    Аргументы:
    tokens (list): Список лемматизированных слов.

    Возвращает:
    list: Очищенный список значимых слов.
    """
    return [
        token
        for token in tokens
        if token.isalpha() and token not in STOP_WORDS and len(token) > 1
    ]

def filter_by_cefr_level(tokens:list[str], user_level:str, cefr_dict: dict = CEFR_DICTIONARY):
    """
    Фильтрует леммы, оставляя только те, которые соответствуют или ВЫШЕ уровня пользователя.
    (Например, если у пользователя B1, мы оставляем B1, B2, C1, чтобы он учил незнакомые сложные слова).

    Аргументы:
    tokens (list[str]): Список уникальных слов для проверки.
    user_level (str): Текущий уровень владения языком пользователя (например, 'B1').
    cefr_dict (dict): Словарь соответствия слов уровням CEFR. По умолчанию используется CEFR_DICTIONARY.

    Возвращает:
    list: Список кортежей вида [(слово, уровень_сложности), ...].
    """
    user_weight = LEVEL_WEIGHTS.get(user_level.upper(), 0)
    result_data = []

    for word in tokens:
        word_level = cefr_dict.get(word, 'C2')
        word_weight = LEVEL_WEIGHTS.get(word_level, 5)

        if word_weight >= user_weight:
            result_data.append((word, word_level))

    return result_data

def generate_analytical_report(original_text: str, complex_words_with_levels: list, counts: Counter) -> dict:
    """
    Формирует единый аналитический отчет на основе уже отфильтрованных данных.

    Аргументы:
    original_text (str): Исходный необработанный текст для подсчета символов.
    complex_words_with_levels (list): Список отфильтрованных кортежей (слово, уровень).
    counts (Counter): Объект Counter с частотностью упоминания каждого слова.

    Возвращает:
    dict: Структурированный отчет с метриками аналитики и списком слов для изучения.
    """
    words_to_learn = []

    for word, level in complex_words_with_levels:
        words_to_learn.append({
            "word": word,
            "count": counts[word],
            "level": level
        })

    return {
        "analytics": {
            "total_characters": len(original_text),
            "total_words_count": sum(counts.values()),
            "complex_words_count": len(complex_words_with_levels)
        },
        "words_to_learn": words_to_learn
    }

def text_pipeline(text:str, user_level: str):
    """
    Полный пайплайн: Очистка и токенизация -> Лемматизация -> Фильтрация мусора и стоп-слов.

    Аргументы:
    text (str): Входной сырой текст (может содержать HTML и ссылки).
    user_level (str): Уровень пользователя для фильтрации сложности.

    Возвращает:
    dict: Финальный аналитический отчет со статистикой текста и подборкой сложных слов.
    """
    tokens = clean_and_tokenize(text)
    lemmatized_tokens = lemmatize_with_pos(tokens)
    filtered_tokens = filter_tokens(lemmatized_tokens)

    counts = Counter(filtered_tokens)

    unique_complex_words = filter_by_cefr_level(list(counts.keys()), user_level)

    return generate_analytical_report(text, unique_complex_words, counts)