import csv

from anki_writer.writer import write_anki_export


def test_write_anki_export_header_and_rows(tmp_path):
    cards = [
        (
            "skriver",
            "{{c1::skriver}} - пишет",
            "Han {{c1::skriver}} et brev.",
            "He writes a letter.",
        ),
        ("spise", "{{c1::spise}} - есть", "Jeg {{c1::spiser}} maten.", "I eat the food."),
    ]

    output_path = tmp_path / "generated.txt"
    write_anki_export(str(output_path), cards)

    lines = output_path.read_text(encoding="utf-8").splitlines(keepends=True)
    assert lines[0] == "#separator:tab\n"
    assert lines[1] == "#html:true\n"

    reader = csv.reader(lines[2:], delimiter="\t", quotechar='"')
    rows = [row for row in reader if row]
    assert rows == [list(card) for card in cards]
