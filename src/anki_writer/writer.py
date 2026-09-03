import csv
import io
from typing import Any

HEADER_LINES = ["#separator:tab", "#html:true"]


class AnkiExportWriter:
    """Writes the Anki export file incrementally, flushing after every card so
    already-generated cards survive a later card's generation failure."""

    def __init__(self, path: str):
        self._path = path
        self._file: io.TextIOWrapper | None = None
        self._writer: Any | None = None

    def __enter__(self) -> "AnkiExportWriter":
        self._file = open(self._path, "w", encoding="utf-8", newline="")
        for line in HEADER_LINES:
            self._file.write(line + "\n")
        self._writer = csv.writer(
            self._file, delimiter="\t", lineterminator="\n", quoting=csv.QUOTE_MINIMAL
        )
        return self

    def write_card(self, card: tuple[str, str, str, str]) -> None:
        assert self._file is not None and self._writer is not None
        self._writer.writerow(card)
        self._file.flush()

    def __exit__(self, exc_type, exc, tb) -> None:
        if self._file is not None:
            self._file.close()


def write_anki_export(path: str, cards: list[tuple[str, str, str, str]]) -> None:
    with AnkiExportWriter(path) as writer:
        for card in cards:
            writer.write_card(card)
