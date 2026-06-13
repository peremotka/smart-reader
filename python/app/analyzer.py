import re

def clean_text(text: str) -> str:
    """
    Очищает текст от знаков препинания и приводит его к нижнему регистру.

    Аргументы:
    text (str): Исходная строка для обработки.

    Возвращает:
    str: Очищенная строка.
    """
    words = re.findall(r'\w+',text)

    return