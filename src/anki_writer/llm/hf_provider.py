from anki_writer.llm.base import ExampleOutput

DEFAULT_HF_MODEL = "Qwen/Qwen2.5-1.5B-Instruct"

DEFAULT_MAX_NEW_TOKENS = 300


class HFSentenceGenerator:
    """Generates structured (sentence, translation) output from a local HF
    instruct model, using constrained/guided JSON decoding so the model can
    only produce output matching ExampleOutput's schema."""

    def __init__(
        self,
        model_name: str = DEFAULT_HF_MODEL,
        device: str | None = None,
        max_new_tokens: int = DEFAULT_MAX_NEW_TOKENS,
    ):
        import outlines
        from transformers import AutoModelForCausalLM, AutoTokenizer

        hf_model = AutoModelForCausalLM.from_pretrained(model_name)
        if device:
            hf_model = hf_model.to(device)
        tokenizer = AutoTokenizer.from_pretrained(model_name)

        model = outlines.from_transformers(hf_model, tokenizer)
        self._generator = outlines.Generator(model, ExampleOutput)
        self._max_new_tokens = max_new_tokens

    def generate(self, prompt: str) -> ExampleOutput:
        from outlines.inputs import Chat

        chat = Chat([{"role": "user", "content": prompt}])
        raw = self._generator(chat, max_new_tokens=self._max_new_tokens)
        return ExampleOutput.model_validate_json(raw)
