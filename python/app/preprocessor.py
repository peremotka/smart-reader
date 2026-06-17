import re

def clean_text(text: str) -> list:
    """
    Очищает текст от знаков препинания, тегов HTML и приводит его к нижнему регистру.

    Аргументы:
    text (str): Исходная строка для обработки.

    Возвращает:
    list: Список очищенных токенов.
    """
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'https?://\S+|www\.\S+|\S+\.(com|ru|net|org|io)\S*', ' ', text)

    words = re.findall(r'[^\W\d_]+',text.lower())

    return words

