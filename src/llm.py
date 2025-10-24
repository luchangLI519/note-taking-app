"""Lightweight LLM helper used by the app.

This module intentionally keeps imports lightweight and avoids making any network
calls at import-time. Call `translate_text(text, target_lang)` to perform a
translation. When run as a script it prints which keys are configured but does
not attempt a real API call.
"""

import os
import json
import traceback
from dotenv import load_dotenv

# Load .env from project root (one level up from src/)
_here = os.path.abspath(os.path.dirname(__file__))
_project_root = os.path.abspath(os.path.join(_here, '..'))
load_dotenv(os.path.join(_project_root, '.env'))

# Configuration
OPENAI_KEY = os.getenv('OPENAI_API_KEY') or os.getenv('OPENAI_API_TOKEN')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
BASE_URL = os.getenv('BASE_URL')  # optional custom endpoint
DEFAULT_MODEL = os.getenv('MODEL', 'gpt-4.1-mini')
MOCK_TRANSLATION = os.getenv('MOCK_TRANSLATION', '0') in ('1', 'true', 'True')


def _make_client():
  """Create and return an OpenAI client and model name.

  Raises RuntimeError if no suitable API key is configured.
  """
  try:
    from openai import OpenAI
  except Exception as e:
    raise RuntimeError(f'openai package not available: {e}')

  # Prefer explicit OpenAI key from .env or environment
  key = OPENAI_KEY
  if key:
    client = OpenAI(api_key=key)
    return client, DEFAULT_MODEL

  # Optional GitHub models gateway (less common)
  if GITHUB_TOKEN:
    endpoint = BASE_URL or 'https://models.github.ai/inference'
    client = OpenAI(api_key=GITHUB_TOKEN, base_url=endpoint)
    model = os.getenv('MODEL', 'openai/gpt-4.1-mini')
    return client, model

  raise RuntimeError('No API key configured. Set OPENAI_API_KEY in .env or environment')


def call_llm_model(model_name, messages, temperature=1.0, top_p=1.0, retries=3, timeout=15):
  """Call the configured LLM and return assistant content string.

  This implements a simple retry/backoff loop to be more robust for
  intermittent network errors.
  """
  client, _ = _make_client()

  last_exc = None
  for attempt in range(1, retries + 1):
    try:
      # The OpenAI Python client uses httpx under the hood and accepts a
      # `timeout` parameter in some call signatures; the SDK also exposes
      # client._client which is httpx.Client; keeping this simple we rely on
      # the client's high-level call and guard with overall attempt timeout.
      resp = client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=temperature,
        top_p=top_p,
      )

      # Extract text safely
      if hasattr(resp, 'choices') and len(resp.choices) > 0:
        # OpenAI SDK objects: resp.choices[0].message.content
        try:
          return getattr(resp.choices[0].message, 'content', None) or resp.choices[0].message.content
        except Exception:
          # Fallback if shape differs
          try:
            return resp.choices[0]['message']['content']
          except Exception:
            return str(resp)

      if isinstance(resp, dict):
        choices = resp.get('choices') or []
        if choices:
          return choices[0].get('message', {}).get('content')

      return str(resp)

    except Exception as e:
      last_exc = e
      if attempt < retries:
        backoff = 1.5 ** attempt
        print(f"LLM call failed (attempt {attempt}/{retries}), retrying in {backoff:.1f}s: {e}")
        import time

        time.sleep(backoff)
        continue
      # exhausted retries
      raise


def translate_text(text, target_lang):
  """Translate `text` into `target_lang` and return the translated string.

  This function will raise RuntimeError if the client is not configured, or
  propagate other client/network exceptions to the caller.
  """
  prompt = (
    f"Translate the following text to {target_lang}. "
    "Preserve the original meaning, keep code blocks and lists formatted, "
    "and only return the translated text without extra commentary.\n\n"
    f"Original:\n{text}"
  )

  messages = [{"role": "user", "content": prompt}]
  # If no API key is configured we allow an optional mock translation for
  # local development when MOCK_TRANSLATION=1. Otherwise propagate the
  # RuntimeError to the caller so the route can return an informative error.
  try:
    client, model = _make_client()
  except RuntimeError as e:
    if MOCK_TRANSLATION:
      # Very small, deterministic mock translation for dev/testing.
      return _mock_translate(text, target_lang)
    raise

  return call_llm_model(model, messages, temperature=0, top_p=1.0)


def _mock_translate(text, target_lang):
  """Return a deterministic mock "translation" for development when no
  API key is present. This keeps the UI flow usable without contacting an
  external API. It should NOT be used in production."""
  # Simple mock: annotate and keep original formatting. For certain common
  # short greetings do a tiny human-friendly mapping.
  mapping = {
    ('hello', 'zh'): '你好',
    ('hi', 'zh'): '嗨',
    ('how are you', 'zh'): '你好吗',
    ('hello', 'en'): 'Hello',
  }
  lower = text.strip().lower()
  for k, v in mapping.items():
    if k[0] in lower and k[1] == target_lang:
      return f"[MOCK TRANSLATION to {target_lang}]\n\n{v}\n\n(原文)\n{text}"

  return f"[MOCK TRANSLATION to {target_lang}]\n\n{text}"


if __name__ == '__main__':
  import sys

  print('llm.py smoke test')
  print('Loaded .env from:', os.path.join(_project_root, '.env'))
  print('OPENAI_KEY set:', bool(OPENAI_KEY))
  print('GITHUB_TOKEN set:', bool(GITHUB_TOKEN))
  print('BASE_URL:', BASE_URL)
  print('MODEL:', DEFAULT_MODEL)

  # Simple CLI: python src/llm.py "text to translate" [target_lang]
  if len(sys.argv) > 1:
    src_text = sys.argv[1]
    tgt = sys.argv[2] if len(sys.argv) > 2 else 'zh'
    print(f"Translating to {tgt}: {src_text}")
    try:
      out = translate_text(src_text, tgt)
      print('\n=== TRANSLATION ===\n')
      print(out)
    except Exception as e:
      print('Translation failed:', e)
      traceback.print_exc()
  else:
    print('\nTo run a translation example:')
    print("  python src/llm.py \"Hello world\" zh")
 