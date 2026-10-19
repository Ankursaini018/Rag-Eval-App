"""One small wrapper around the LLM, so the rest of the code never touches a vendor library.

Settings come from environment variables (or a local .env file that is NOT committed):
    LLM_PROVIDER      anthropic (default) | openai        ('openai' also covers OpenAI-compatible servers)
    LLM_MODEL         model name; sensible default per provider
    ANTHROPIC_API_KEY / OPENAI_API_KEY
    OPENAI_BASE_URL   only for OpenAI-compatible providers (Groq, Gemini, a local Ollama ...)
    LLM_TIMEOUT       seconds before giving up on a call (default 30)
    LLM_MAX_RETRIES   how often the client retries a rate-limited (429) call, waiting as the server asks (default 5)
    LLM_MIN_INTERVAL  minimum seconds between two calls; slows us down to stay under free-tier limits (default 0)
    LLM_MAX_TOKENS    longest reply we allow (default 600). Reasoning models need more, e.g. 1500
    LLM_REASONING_EFFORT  low | medium | high, only for reasoning models such as gpt-oss (default: not sent)
"""
import os
import time 
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()   # reads .env if present; real environment variables always win

DEFAULT_MODELS = {"anthropic": "claude-haiku-5-5", "openai": "gpt-4o-mini"}


class LLMConfigError(RuntimeError):
    """The LLM is not set up (missing key, unknown provider). Messages never contain the key itself."""


@dataclass
class LLMResult:
    text: str
    input_tokens: int = 0
    output_tokens: int = 0


def _settings() -> tuple[str, str, float]:
    provider = os.getenv("LLM_PROVIDER", "anthropic").lower()
    if provider not in DEFAULT_MODELS:
        raise LLMConfigError(f"Unknown LLM_PROVIDER '{provider}'. Use one of: {', '.join(DEFAULT_MODELS)}")
    return provider, os.getenv("LLM_MODEL") or DEFAULT_MODELS[provider], float(os.getenv("LLM_TIMEOUT", "30"))


def _require_key(name: str) -> str:
    key = os.getenv(name)
    if not key:
        raise LLMConfigError(f"{name} is not set. Add it to your .env file (see .env.example).")
    return key


def _call_anthropic(model: str, timeout: float, system: str, user: str, max_tokens: int, temperature: float) -> LLMResult:
    import anthropic
    client = anthropic.Anthropic(api_key=_require_key("ANTHROPIC_API_KEY"), timeout=timeout)
    r = client.messages.create(model=model, max_tokens=max_tokens, temperature=temperature, system=system,
                               messages=[{"role": "user", "content": user}])
    text = "".join(block.text for block in r.content if getattr(block, "type", "") == "text")
    return LLMResult(text, r.usage.input_tokens, r.usage.output_tokens)


def _call_openai(model: str, timeout: float, system: str, user: str, max_tokens: int, temperature: float) -> LLMResult:
    from openai import OpenAI
    client = OpenAI(api_key=_require_key("OPENAI_API_KEY"), base_url=os.getenv("OPENAI_BASE_URL") or None,
                    timeout=timeout, max_retries=int(os.getenv("LLM_MAX_RETRIES", "5")))
    request = dict(model=model, temperature=temperature,
                   messages=[{"role": "system", "content": system}, {"role": "user", "content": user}])
    effort = os.getenv("LLM_REASONING_EFFORT")
    if effort:   # reasoning models think before answering; 'low' keeps that cheap and fast
        request["extra_body"] = {"reasoning_effort": effort}
    try:
        r = client.chat.completions.create(max_tokens=max_tokens, **request)
    except Exception as e:
        # Some models/providers only accept the newer name `max_completion_tokens`: retry once with it.
        if getattr(e, "status_code", None) == 400 and "max_tokens" in str(e):
            r = client.chat.completions.create(max_completion_tokens=max_tokens, **request)
        else:
            raise
    usage = r.usage
    return LLMResult(r.choices[0].message.content or "",
                     getattr(usage, "prompt_tokens", 0) or 0, getattr(usage, "completion_tokens", 0) or 0)


_last_call = 0.0


def _pace() -> None:
    """Free tiers cap tokens per minute. LLM_MIN_INTERVAL=10 means 'at most one call every 10 seconds'."""
    global _last_call
    gap = float(os.getenv("LLM_MIN_INTERVAL", "0"))
    wait = _last_call + gap - time.monotonic()
    if gap > 0 and wait > 0:
        time.sleep(wait)
    _last_call = time.monotonic()


def complete(system: str, user: str, max_tokens: int | None = None, temperature: float = 0.0) -> LLMResult:
    """Send one question, get one answer. temperature=0 makes answers as repeatable as possible,
    which matters when we compare experiments later."""
    provider, model, timeout = _settings()
    max_tokens = max_tokens or int(os.getenv("LLM_MAX_TOKENS", "600"))
    _pace()
    call = {"anthropic": _call_anthropic, "openai": _call_openai}[provider]
    return call(model, timeout, system, user, max_tokens, temperature)