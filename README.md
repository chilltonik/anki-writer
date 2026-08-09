# anki-writer

Генерирует Anki-карточки для новых слов: по списку слов и их переводов локальная LLM (Hugging Face `transformers` или модель из Ollama) придумывает пример-предложение на изучаемом языке и его перевод, а программа собирает результат в файл, который импортируется в Anki через File → Import.

## Быстрый старт

```
make install-dev   # ставит рантайм- и dev-зависимости через uv (создаёт .venv сам)
make test           # прогоняет тесты (без скачивания модели)
cp .env.example .env  # опционально: настроить провайдера/модель, см. ниже
make run-fake WORDS=words.json LANG=norwegian OUT=generated.txt   # smoke-прогон без модели
make run WORDS=words.json LANG=norwegian OUT=generated.txt        # реальный прогон
```

Пакетный менеджер — [uv](https://docs.astral.sh/uv/). Makefile вызывает `uv sync`/`uv run` — отдельно создавать или активировать `.venv` не нужно, uv делает это сам на основе `pyproject.toml`/`uv.lock`.

## Установка

```
make install        # только рантайм-зависимости
make install-dev    # + pytest
```

Ставит `transformers`, `torch`, `accelerate`, `outlines` (structured generation), `pydantic`, `python-dotenv`, `requests`. При первом запуске с реальной HF-моделью веса скачиваются с Hugging Face Hub (для `Qwen/Qwen2.5-1.5B-Instruct` — несколько ГБ). Для Ollama-провайдера веса скачивать не нужно — модель должна быть уже подтянута в самой Ollama (`ollama pull <model>`), а сервер `ollama serve` — запущен.

```
make test   # прогон тестов, без скачивания весов модели
```

## Конфигурация (`.env`)

Скопируйте `.env.example` в `.env` и поправьте под себя:

```
cp .env.example .env
```

Переменные (все опциональны, CLI-флаги их переопределяют):

- `ANKI_WRITER_PROVIDER` — `hf` или `ollama` (по умолчанию `hf`).
- `ANKI_WRITER_HF_MODEL` — модель для HF-провайдера (по умолчанию `Qwen/Qwen2.5-1.5B-Instruct`).
- `ANKI_WRITER_HF_DEVICE` — `cpu`/`cuda` для HF-провайдера (по умолчанию решает `transformers`).
- `ANKI_WRITER_HF_MAX_NEW_TOKENS` — лимит новых токенов при генерации для HF-провайдера (по умолчанию `300`).
- `ANKI_WRITER_OLLAMA_MODEL` — модель для Ollama-провайдера (по умолчанию `qwen2.5:1.5b`).
- `ANKI_WRITER_OLLAMA_HOST` — адрес Ollama-сервера (по умолчанию `http://localhost:11434`).
- `ANKI_WRITER_OUTPUT` — путь к выходному файлу по умолчанию (`output.txt`).

## Использование

Входной файл — JSON, ключ — слово, значение — его перевод:

```json
{
    "skriver": "пишет",
    "spise": "есть/кушать"
}
```

Запуск:

```
make run WORDS=words.json LANG=norwegian OUT=generated.txt
```

Переменные `WORDS`/`LANG`/`OUT` необязательны — по умолчанию `words.json`/`norwegian`/`generated.txt`. Быстрая проверка пайплайна без модели, теми же переменными: `make run-fake WORDS=... LANG=... OUT=...` (эквивалент флага `--fake`).

Флаг `--fake` через `make run`/`make run-fake` не пробрасывается — для него запускайте CLI напрямую:

```
uv run python main.py words.json norwegian --fake
```

Провайдер/модель/device/output — не CLI-флаги, а переменные `.env`/окружения (см. `Settings` в `src/anki_writer/config.py` и `.env.example`).

Аргументы CLI:
- `words_file` — путь к JSON со словами.
- `language` — язык изучаемых слов. Поддерживаются: `english` (→ русский), `norwegian` (→ английский), `polish` (→ английский). Любой другой язык — ошибка с понятным сообщением.
- `--fake` — сгенерировать карточки с заглушкой вместо реальной модели (для быстрой проверки pipeline без скачивания весов и без Ollama).

Результат — текстовый файл в формате Anki plain-text export (`#separator:tab`, `#html:true`), который импортируется через Anki: File → Import → выбрать файл. При импорте нужно вручную выбрать **note type** (Cloze-производный, с полями `keyword`/`definition`/`example`/`translation` в таком порядке) и сопоставить колонки файла этим полям — файл не содержит заголовка `#notetype`/`#columns`, поэтому маппинг делается руками в диалоге импорта Anki.

Программа пишет в файл **сырые значения полей заметки**, а не готовый HTML: слово внутри `definition` и внутри сгенерированного предложения в `example` оборачивается в нативный Anki-синтаксис `{{c1::...}}` — рендеринг Front/Back карточки делает сам note type через свой шаблон (`{{cloze:definition}}`, `{{cloze:example}}`, `{{translation}}`).

## Как это устроено

- `src/anki_writer/config.py` — читает `.env`/переменные окружения в `Settings` (провайдер, модели, output по умолчанию); CLI-флаги переопределяют эти значения.
- `src/anki_writer/languages.py` — список поддерживаемых языков изучения и `resolve_target_language` (валидирует язык, возвращает язык перевода).
- `src/anki_writer/prompts/` — `build_prompt()` собирает промпт из текстового шаблона `prompts/example_sentence.txt` (плейсхолдеры `{word}`, `{word_translation}`, `{source_lang}`, `{target_lang}`).
- `src/anki_writer/llm/` — провайдеры генерации, все реализуют один протокол `SentenceGenerator.generate(prompt) -> ExampleOutput`:
  - `hf_provider.py` — `HFSentenceGenerator`, через `outlines` (structured/constrained decoding поверх HF-модели), гарантирует, что ответ модели — ровно `{"sentence": ..., "translation": ...}`.
  - `ollama_provider.py` — `OllamaSentenceGenerator`, обращается к локальному Ollama-серверу (`/api/chat`) со структурированным выводом через JSON-схему в поле `format`.
  - `base.py` — общий протокол, `ExampleOutput`, `FakeSentenceGenerator` (заглушка для тестов).
  - `create_generator(settings, fake=..., model_override=...)` — фабрика, выбирающая провайдера по `settings.provider`.
- `src/anki_writer/cards.py` — собирает 4 значения полей заметки (`keyword`, `definition`, `example`, `translation`), маскируя слово нативным cloze-синтаксисом `{{c1::...}}` и в `definition`, и в сгенерированном `example` (одним и тем же номером `c1`, чтобы оба поля скрывались/открывались синхронно на одной карточке; совпадение ищется по началу слова, чтобы ловить словоформы вроде `spiser` для `spise`; если слово в предложении не находится вовсе — предложение вставляется без клоза, с предупреждением в stdout).
- `src/anki_writer/writer.py` — пишет результат в формате Anki plain-text export, 4 колонки на строку.
- `src/anki_writer/cli.py` — оркестрация: `.env`/CLI-настройки → JSON → промпт → генерация через выбранного провайдера → значения полей → файл.

Порядок полей (`keyword`/`definition`/`example`/`translation`) — фиксированный контракт с реальным note type в Anki пользователя. Если структура note type изменится (другие поля/порядок), нужно поправить `cards.py` и порядок в `writer.py`/`cli.py`.

## Makefile

- `make install` / `make install-dev` — установка зависимостей.
- `make test` — прогон тестов.
- `make run WORDS=... LANG=... OUT=...` — генерация карточек реальной моделью.
- `make run-fake WORDS=... LANG=... OUT=...` — то же самое с заглушкой, без скачивания модели.
- `make clean` — удалить `__pycache__`, `.pytest_cache`, `*.egg-info`.


## Runs

- English
```bash
make run WORDS=data/english.json LANG=english OUT=generated/english.txt
```

- Norwegian
```bash
make run WORDS=data/norwegian.json LANG=norwegian OUT=generated/norwegian.txt
```

- Polish
```bash
make run WORDS=data/polish.json LANG=polish OUT=generated/polish.txt
```