from anki_writer.llm.base import T


class HFSentenceGenerator:
    """Generates structured output from a local HF instruct model, using
    constrained/guided JSON decoding so the model can only produce output
    matching the requested pydantic output_type's schema."""

    def __init__(
        self,
        model_name: str,
        max_new_tokens: int,
        device: str | None = None,
    ):
        import outlines
        from transformers import AutoModelForCausalLM, AutoTokenizer

        hf_model = AutoModelForCausalLM.from_pretrained(model_name)
        if device:
            hf_model = hf_model.to(device)
        tokenizer = AutoTokenizer.from_pretrained(model_name)

        self._model = outlines.from_transformers(hf_model, tokenizer)
        self._generators: dict[type, "outlines.Generator"] = {}
        self._max_new_tokens = max_new_tokens

    def generate(self, prompt: str, output_type: type[T]) -> T:
        import outlines
        from outlines.inputs import Chat

        generator = self._generators.get(output_type)
        if generator is None:
            generator = outlines.Generator(self._model, output_type)
            self._generators[output_type] = generator

        chat = Chat([{"role": "user", "content": prompt}])
        raw = generator(chat, max_new_tokens=self._max_new_tokens)
        return output_type.model_validate_json(raw)
