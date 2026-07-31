import csv

HEADER_LINES = ["#separator:tab", "#html:true"]


def write_anki_export(path: str, cards: list[tuple[str, str, str, str]]) -> None:
    with open(path, "w", encoding="utf-8", newline="") as f:
        for line in HEADER_LINES:
            f.write(line + "\n")
        writer = csv.writer(f, delimiter="\t", lineterminator="\n", quoting=csv.QUOTE_MINIMAL)
        writer.writerows(cards)
