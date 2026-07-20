import csv
import json

from anki_writer.cli import main


def test_cli_end_to_end_with_fake_generator(tmp_path):
    words_file = tmp_path / "words.json"
    words_file.write_text(json.dumps({"skriver": "пишет"}), encoding="utf-8")

    output_file = tmp_path / "generated.txt"

    main([str(words_file), "norwegian", "-o", str(output_file), "--fake"])

    assert output_file.exists()

    lines = output_file.read_text(encoding="utf-8").splitlines(keepends=True)
    assert lines[0] == "#separator:tab\n"
    assert lines[1] == "#html:true\n"

    reader = csv.reader(lines[2:], delimiter="\t", quotechar='"')
    rows = [row for row in reader if row and row != [""]]
    assert len(rows) == 1

    keyword, definition, example, translation = rows[0]
    assert keyword == "skriver"
    assert "skriver" in definition
    assert "пишет" in definition
    assert "Default sentence." in example
    assert translation == "Default translation."
