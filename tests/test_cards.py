from anki_writer.cards import build_card, mask_word_in_sentence


def test_mask_word_in_sentence_found():
    result = mask_word_in_sentence("I skriver every day.", "skriver")
    assert result == "I {{c1::skriver}} every day."


def test_mask_word_in_sentence_case_insensitive():
    result = mask_word_in_sentence("Skriver is a verb.", "skriver")
    assert result == "{{c1::Skriver}} is a verb."


def test_mask_word_in_sentence_not_found_falls_back_unmasked():
    result = mask_word_in_sentence("This has no match.", "skriver")
    assert result == "This has no match."


def test_mask_word_in_sentence_matches_inflected_form():
    result = mask_word_in_sentence("Jeg spiser maten.", "spise")
    assert result == "Jeg {{c1::spiser}} maten."


def test_mask_word_in_sentence_escapes_html():
    result = mask_word_in_sentence("Tom & Jerry skriver.", "skriver")
    assert result == "Tom &amp; Jerry {{c1::skriver}}."


def test_build_card_returns_four_fields_in_order():
    keyword, definition, example, translation = build_card(
        "skriver", "пишет", "Han skriver et brev.", "He writes a letter."
    )
    assert keyword == "skriver"
    assert definition == "{{c1::skriver}} - пишет"
    assert example == "Han {{c1::skriver}} et brev."
    assert translation == "He writes a letter."


def test_build_card_masks_inflected_word_inside_example():
    _, _, example, _ = build_card("spise", "есть/кушать", "Jeg spiser maten.", "I eat the food.")
    assert example == "Jeg {{c1::spiser}} maten."
