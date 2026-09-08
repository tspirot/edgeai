from titlovi.text.transliterate import cyrillic_to_latin, latin_to_cyrillic


def test_digraphs():
    assert latin_to_cyrillic("Njegoš lije džem") == "Његош лије џем"
    assert latin_to_cyrillic("ljubav NJEGA") == "љубав ЊЕГА"


def test_special_letters():
    assert latin_to_cyrillic("Ćira, đak, čaša, šuma, žaba") == "Ћира, ђак, чаша, шума, жаба"


def test_round_trip():
    text = "Пирот, Стара планина и знаковна азбука"
    assert latin_to_cyrillic(cyrillic_to_latin(text)) == text


def test_non_letters_untouched():
    # цифре, размаци и интерпункција остају; латинична слова се пресловљавају
    assert latin_to_cyrillic("Pi 5, 16 kHz — test!") == "Пи 5, 16 кХз — тест!"
