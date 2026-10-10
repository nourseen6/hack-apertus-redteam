import json
import os
import random
import time
import urllib.error
import urllib.request

INNER_PREFIX = "<|inner_prefix|>"
INNER_SUFFIX = "<|inner_suffix|>"

RETRYABLE = {408, 409, 425, 429, 500, 502, 503, 504}


class ApiError(RuntimeError):
    def __init__(self, status, body):
        super().__init__(f"HTTP {status}: {body[:500]}")
        self.status = status
        self.body = body


class ChatClient:
    def __init__(self, base_url, api_key_env, user_agent="hack-apertus-redteam/0.1", timeout=600):
        self.base_url = base_url.rstrip("/")
        self.api_key = os.environ.get(api_key_env)
        if not self.api_key:
            raise RuntimeError(f"Environment variable {api_key_env} is not set")
        self.user_agent = user_agent
        self.timeout = timeout

    def _request(self, method, path, payload=None):
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        req = urllib.request.Request(
            self.base_url + path,
            data=data,
            method=method,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": self.user_agent,
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                body = json.loads(resp.read().decode("utf-8"))
                body["_headers"] = {k.lower(): v for k, v in resp.headers.items()
                                    if k.lower().startswith("x-litellm") or "cache" in k.lower()}
                return body
        except urllib.error.HTTPError as e:
            raise ApiError(e.code, e.read().decode("utf-8", "replace")) from None

    def models(self):
        return self._request("GET", "/models").get("data", [])

    def _stream(self, payload):
        """POST with stream=True and rebuild a non-streaming response body.

        Streaming keeps long thinking generations from hitting the gateway timeout.
        """
        payload = {**payload, "stream": True, "stream_options": {"include_usage": True}}
        req = urllib.request.Request(
            self.base_url + "/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            method="POST",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "text/event-stream",
                "User-Agent": self.user_agent,
            },
        )
        content, reasoning = [], []
        finish_reason = usage = model = resp_id = None
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                headers = {k.lower(): v for k, v in resp.headers.items()
                           if k.lower().startswith("x-litellm") or "cache" in k.lower()}
                for raw in resp:
                    line = raw.decode("utf-8", "replace").strip()
                    if not line.startswith("data:"):
                        continue
                    chunk = line[5:].strip()
                    if chunk == "[DONE]":
                        break
                    event = json.loads(chunk)
                    model = event.get("model") or model
                    resp_id = event.get("id") or resp_id
                    usage = event.get("usage") or usage
                    for choice in event.get("choices") or []:
                        delta = choice.get("delta") or {}
                        if delta.get("content"):
                            content.append(delta["content"])
                        r = delta.get("reasoning_content") or delta.get("reasoning")
                        if r:
                            reasoning.append(r)
                        finish_reason = choice.get("finish_reason") or finish_reason
        except urllib.error.HTTPError as e:
            raise ApiError(e.code, e.read().decode("utf-8", "replace")) from None

        message = {"content": "".join(content)}
        if reasoning:
            message["reasoning_content"] = "".join(reasoning)
        return {"id": resp_id, "model": model, "usage": usage, "_headers": headers,
                "choices": [{"message": message, "finish_reason": finish_reason}]}

    def _with_retries(self, call, retries):
        for attempt in range(retries + 1):
            try:
                return call()
            except ApiError as e:
                if e.status not in RETRYABLE or attempt == retries:
                    raise
            except (urllib.error.URLError, TimeoutError, ConnectionError):
                if attempt == retries:
                    raise
            time.sleep(min(60, 2 ** attempt) + random.random())

    def echo(self, model, text, retries=8):
        """Per-token logprobs of `text` itself (prompt scoring via /completions echo)."""
        payload = {"model": model, "prompt": text, "max_tokens": 1, "temperature": 0,
                   "echo": True, "logprobs": 0, "cache": {"no-cache": True, "no-store": True}}
        data = self._with_retries(lambda: self._request("POST", "/completions", payload), retries)
        lp = data["choices"][0]["logprobs"]
        return {"tokens": lp["tokens"], "offsets": lp["text_offset"],
                "logprobs": lp["token_logprobs"], "served_model": data.get("model"),
                "headers": data.get("_headers", {})}

    def chat(self, model, messages, max_tokens, temperature=0.0, top_p=1.0, seed=None,
             extra_body=None, retries=6, bypass_cache=True, stream=True):
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
        }
        if bypass_cache:
            payload["cache"] = {"no-cache": True, "no-store": True}
        if seed is not None:
            payload["seed"] = seed
        if extra_body:
            payload.update(extra_body)

        start = time.monotonic()
        data = self._with_retries(
            lambda: self._stream(payload) if stream else self._request("POST", "/chat/completions", payload),
            retries)

        choice = data["choices"][0]
        reasoning, answer, parse = split_reasoning(choice.get("message") or {})
        return {
            "reasoning": reasoning,
            "answer": answer,
            "parse": parse,
            "finish_reason": choice.get("finish_reason"),
            "usage": data.get("usage"),
            "latency_s": round(time.monotonic() - start, 2),
            "served_model": data.get("model"),
            "response_id": data.get("id"),
            "headers": data.get("_headers", {}),
        }


def split_reasoning(message):
    """Separate the thinking span from the visible answer.

    Servers running a reasoning parser return the span in a separate field.
    Servers without one return the raw text with Apertus inner markers.
    """
    for key in ("reasoning_content", "reasoning"):
        value = message.get(key)
        if value:
            return value.strip(), (message.get("content") or "").strip(), f"field:{key}"

    content = message.get("content") or ""
    if INNER_SUFFIX in content:
        before, _, after = content.partition(INNER_SUFFIX)
        return before.split(INNER_PREFIX, 1)[-1].strip(), after.strip(), "markers"
    if INNER_PREFIX in content:
        return content.split(INNER_PREFIX, 1)[-1].strip(), "", "markers_unterminated"
    return "", content.strip(), "none"
