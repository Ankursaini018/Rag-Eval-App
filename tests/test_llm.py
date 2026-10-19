import pytest

from rag import llm


def test_missing_key_gives_clear_error_without_leaking(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(llm.LLMConfigError, match="ANTHROPIC_API_KEY is not set"):
        llm.complete("sys", "user")


def test_unknown_provider(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "nope")
    with pytest.raises(llm.LLMConfigError, match="Unknown LLM_PROVIDER"):
        llm.complete("sys", "user")


def test_provider_and_model_are_routed(monkeypatch):
    seen = {}

    def fake_openai(model, timeout, system, user, max_tokens, temperature):
        seen.update(model=model, timeout=timeout, system=system, user=user, temperature=temperature)
        return llm.LLMResult("hi", 3, 1)

    monkeypatch.setattr(llm, "_call_openai", fake_openai)
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("LLM_MODEL", "my-model")
    monkeypatch.setenv("LLM_TIMEOUT", "12")
    out = llm.complete("S", "U")
    assert out.text == "hi" and seen == {"model": "my-model", "timeout": 12.0, "system": "S", "user": "U",
                                         "temperature": 0.0}


def test_default_model_per_provider(monkeypatch):
    monkeypatch.delenv("LLM_MODEL", raising=False)
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    assert llm._settings()[1] == "gpt-4o-mini"

class FakeCompletions:
    def __init__(self, fail_first_with=None):
        self.calls, self.fail = [], fail_first_with

    def create(self, **kw):
        self.calls.append(kw)
        if self.fail and len(self.calls) == 1:
            raise self.fail
        from types import SimpleNamespace as NS
        return NS(choices=[NS(message=NS(content="ok"))], usage=NS(prompt_tokens=11, completion_tokens=2))


def install_fake_openai(monkeypatch, completions, seen):
    import openai

    class FakeOpenAI:
        def __init__(self, **kw):
            seen.update(kw)
            self.chat = type("C", (), {"completions": completions})()

    monkeypatch.setattr(openai, "OpenAI", FakeOpenAI)


def test_openai_compatible_client_gets_base_url_and_retries(monkeypatch):
    seen, comp = {}, FakeCompletions()
    install_fake_openai(monkeypatch, comp, seen)
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "k")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://api.groq.com/openai/v1")
    monkeypatch.setenv("LLM_MAX_RETRIES", "7")
    out = llm.complete("S", "U")
    assert out.text == "ok" and out.input_tokens == 11 and out.output_tokens == 2
    assert seen["base_url"] == "https://api.groq.com/openai/v1" and seen["max_retries"] == 7
    assert "max_tokens" in comp.calls[0]


def test_falls_back_to_max_completion_tokens_when_rejected(monkeypatch):
    class Bad(Exception):
        status_code = 400
    seen, comp = {}, FakeCompletions(fail_first_with=Bad("Unsupported parameter: 'max_tokens'"))
    install_fake_openai(monkeypatch, comp, seen)
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "k")
    assert llm.complete("S", "U").text == "ok"
    assert "max_tokens" in comp.calls[0] and "max_completion_tokens" in comp.calls[1]


def test_other_errors_are_not_swallowed(monkeypatch):
    class Boom(Exception):
        status_code = 500
    install_fake_openai(monkeypatch, FakeCompletions(fail_first_with=Boom("server error")), {})
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "k")
    with pytest.raises(Boom):
        llm.complete("S", "U")


def test_pacing_waits_between_calls(monkeypatch):
    sleeps, clock = [], [100.0]
    monkeypatch.setattr(llm.time, "sleep", lambda s: sleeps.append(s))
    monkeypatch.setattr(llm.time, "monotonic", lambda: clock[0])
    monkeypatch.setenv("LLM_MIN_INTERVAL", "10")
    monkeypatch.setattr(llm, "_last_call", 0.0)
    llm._pace()                 # first call: no wait
    clock[0] += 4
    llm._pace()                 # 4 s later: must wait 6 s
    assert sleeps == [6.0]
    monkeypatch.setenv("LLM_MIN_INTERVAL", "0")
    clock[0] += 1
    llm._pace()
    assert sleeps == [6.0]      # interval 0 = no pacing

def test_max_tokens_comes_from_env(monkeypatch):
    seen = {}

    def fake(model, timeout, system, user, max_tokens, temperature):
        seen["max_tokens"] = max_tokens
        return llm.LLMResult("x")

    monkeypatch.setattr(llm, "_call_openai", fake)
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("LLM_MAX_TOKENS", "1500")
    llm.complete("S", "U")
    assert seen["max_tokens"] == 1500
    llm.complete("S", "U", max_tokens=50)          # an explicit value still wins
    assert seen["max_tokens"] == 50


def test_reasoning_effort_is_sent_only_when_set(monkeypatch):
    comp = FakeCompletions()
    install_fake_openai(monkeypatch, comp, {})
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "k")
    monkeypatch.delenv("LLM_REASONING_EFFORT", raising=False)
    llm.complete("S", "U")
    assert "extra_body" not in comp.calls[0]
    monkeypatch.setenv("LLM_REASONING_EFFORT", "low")
    llm.complete("S", "U")
    assert comp.calls[1]["extra_body"] == {"reasoning_effort": "low"}