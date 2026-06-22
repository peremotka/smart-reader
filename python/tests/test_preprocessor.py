import pytest
from collections import Counter
from unittest.mock import patch

from app.preprocessor import clean_and_tokenize, get_wordnet_pos, lemmatize_with_pos, filter_tokens, \
    filter_by_cefr_level, text_pipeline


@pytest.mark.parametrize("input_text, expected_output", [
    ("", []),
    ("   \n\t   ", []),
    ("<p><div><br></div></p>", []),
    ("https://google.com www.ru", []),
    ("Hello<p>World</p>Test", ["hello", "world", "test"]),
    ("HTTP://EXAMPLE.COM/XYZ", []),
])
def test_clean_and_tokenize(input_text, expected_output):
    assert clean_and_tokenize(input_text) == expected_output



@pytest.mark.parametrize("nltk_tag, expected_wordnet_pos", [
    ("VB", "v"),   # Глагол в начальной форме (Verb)
    ("VBD", "v"),  # Глагол в прошедшем времени
    ("JJ", "a"),   # Прилагательное (Adjective)
    ("JJR", "a"),  # Прилагательное в сравнительной степени
    ("RB", "r"),   # Наречие (Adverb)
    ("NN", "n"),   # Существительное (Noun)
    ("PRP", "n"),  # Местоимение -> должно упасть в дефолт ('n')
    ("", "n"),     # Пустая строка -> должно упасть в дефолт ('n')
])
def test_get_wordnet_pos_mapping(nltk_tag, expected_wordnet_pos):
    assert get_wordnet_pos(nltk_tag) == expected_wordnet_pos



@pytest.mark.parametrize("input_tokens, expected_lemmas", [
    # 1. Существительные (обычные, на -es, и исключения)
    (["cats", "dogs"], ["cat", "dog"]),
    (["boxes", "buses"], ["box", "bus"]),
    (["children", "men"], ["child", "man"]),

    # 2. Глаголы (времена, герундий и неправильные глаголы)
    (["running", "walked"], ["run", "walk"]),
    (["went", "bought", "is"], ["go", "buy", "be"]),

    # 3. Прилагательные (сравнительная и превосходная степень)
    (["happier", "coldest"], ["happy", "cold"]),
    (["bigger", "tallest"], ["big", "tall"]),

    # 4. Наречия (базовые и степени сравнения)
    (["quickly", "slowly"], ["quickly", "slowly"]),
    (["faster", "harder"], ["fast", "hard"]),
])
def test_lemmatize_with_pos_basic(input_tokens, expected_lemmas):
    assert lemmatize_with_pos(input_tokens) == expected_lemmas

def test_lemmatize_with_pos_context():
    assert lemmatize_with_pos(["they", "are", "building"]) == ["they", "be", "build"]
    assert lemmatize_with_pos(["a", "tall", "building"]) == ["a", "tall", "building"]

def test_lemmatize_with_pos_edge_cases():
    assert lemmatize_with_pos([]) == []
    assert lemmatize_with_pos(["123", "!!!"]) == ["123", "!!!"]



def test_filter_tokens_basic():
    input_lemmas = ["the", "cat", "is", "sitting", "on", "a", "mat"]
    expected = ["cat", "sitting", "mat"]

    assert filter_tokens(input_lemmas) == expected

@pytest.mark.parametrize("input_list, expected_list", [
    ([], []),
    (["the", "is", "a", "on"], []),
    (["cat", "dog"], ["cat", "dog"]),
    (["a", "!!!", "cat", "?"], ["cat"]),
])
def test_filter_tokens_edge_cases(input_list, expected_list):
    assert filter_tokens(input_list) == expected_list



TEST_CEFR_DICT = {
    "about": "A1",
    "ability": "A2",
    "abandon": "B2",
    "abolish": "C1",
}

@pytest.mark.parametrize("user_level, expected_words", [
    ("A1", [("about", "A1"), ("ability", "A2"), ("abandon", "B2"), ("abolish", "C1")]),
    ("B1", [("abandon", "B2"), ("abolish", "C1")]),
    ("C1", [("abolish", "C1")]),
])
def test_filter_by_cefr_level_basic(user_level, expected_words):
    tokens = ["about", "ability", "abandon", "abolish"]

    result = filter_by_cefr_level(tokens, user_level, cefr_dict=TEST_CEFR_DICT)
    assert result == expected_words

def test_filter_by_cefr_level_edge_cases():
    # Кейс 1: Слово отсутствует в словаре. Твой код должен дать ему дефолтный 'C2'.
    # Если у пользователя уровень B2, то 'C2' должен остаться в результате.
    assert filter_by_cefr_level(["unknownword"], "B2", cefr_dict=TEST_CEFR_DICT) == [("unknownword", "C2")]

    # Кейс 2: Пустой список токенов на входе
    assert filter_by_cefr_level([], "B1", cefr_dict=TEST_CEFR_DICT) == []

    # Кейс 3: Пользователь ввел уровень в нижнем регистре ('b2' вместо 'B2')
    # Твой код делает .upper(), так что это должно отработать корректно.
    tokens = ["abandon", "abolish"] # B2 и C1
    assert filter_by_cefr_level(tokens, "b2", cefr_dict=TEST_CEFR_DICT) == [("abandon", "B2"), ("abolish", "C1")]


# =====================================================================
# ИНТЕГРАЦИОННЫЙ ТЕСТ: Проверяем главный метод препроцессора
# =====================================================================

def test_text_pipeline_integration():
    # Передаем сырой текст с мусором и стоп-словами
    raw_text = "The cats are running! https://example.com"

    # Запускаем полный цикл
    report = text_pipeline(raw_text, "A1")

    # 1. Проверяем, что сформировалась правильная структура отчета (работа generate_analytical_report)
    assert "analytics" in report
    assert "words_to_learn" in report
    assert report["analytics"]["total_characters"] == len(raw_text)

    # 2. Проверяем, что ушел мусор (работа clean_and_tokenize и filter_tokens)
    words_to_learn = [item["word"] for item in report["words_to_learn"]]
    assert "https://example.com" not in words_to_learn
    assert "the" not in words_to_learn



