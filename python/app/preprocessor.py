import os
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_NLTK_PATH = os.path.join(BASE_DIR, 'nltk_data')
nltk.data.path.append(PROJECT_NLTK_PATH)

nltk.download('punkt', download_dir=PROJECT_NLTK_PATH, quiet=True)
nltk.download('punkt_tab', download_dir=PROJECT_NLTK_PATH, quiet=True)
nltk.download('stopwords', download_dir=PROJECT_NLTK_PATH, quiet=True)
nltk.download('wordnet', download_dir=PROJECT_NLTK_PATH, quiet=True)
nltk.download('averaged_perceptron_tagger_eng', download_dir=PROJECT_NLTK_PATH, quiet=True)

def clean_and_tokenize(text: str) -> list:
    """
    Очищает текст от знаков препинания, тегов HTML, токенизирует с помощью NLTK
    и приводит к нижнему регистру.

    Аргументы:
    text (str): Исходная строка для обработки.

    Возвращает:
    list: Список токенов.
    """
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'https?://\S+|www\.\S+|\S+\.(com|ru|net|org|io)\S*', ' ', text)

    text = text.lower()
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
    """
    lemmatizer = WordNetLemmatizer()

    pos_tags = nltk.pos_tag(tokens)

    lemmatized_words = []
    for word, tag in pos_tags:
        pos = get_wordnet_pos(tag)
        lemma = lemmatizer.lemmatize(word, pos=pos)
        lemmatized_words.append(lemma)

    return lemmatized_words

def filter_tokens(tokens: list) -> list:
    """
    Удаляет стоп-слова, знаки препинания и токены длиной меньше 2 символов.
    """
    stop_words = set(stopwords.words('english'))

    tokens = [token for token in tokens if token.isalpha() and token not in stop_words and len(token) > 1]

    return tokens


def text_pipeline(text:str) :
    """
    Полный пайплайн: Очистка -> Токенизация -> Фильтрация мусора и стоп-слов -> Лемматизация.
    """
    tokens = clean_and_tokenize(text)

    lemmatized_tokens = lemmatize_with_pos(tokens)

    filtered_tokens = filter_tokens(lemmatized_tokens)

print(text_pipeline("<p>The tech-savvy student was successfully running her first NLP pipeline! </p> Check out https://github.com for more details. It's an amazing experience, isn't it? She bought 3 new books about AI and went to the library at 10 AM."))
