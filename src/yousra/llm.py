from openai import OpenAI

from yousra.persona import LEARN_PROMPT, build_system_prompt


class YousraLLM:
  def __init__(self, api_key: str, model: str, max_tweet_length: int) -> None:
    self._client = OpenAI(api_key=api_key)
    self._model = model
    self._max_len = max_tweet_length

  def reply(self, user_text: str, author: str, memories: list[str]) -> str:
    system = build_system_prompt(memories, self._max_len)
    response = self._client.chat.completions.create(
      model=self._model,
      messages=[
        {"role": "system", "content": system},
        {
          "role": "user",
          "content": (
            f"@{author} said to you on X:\n{user_text}\n\n"
            "Write Yousra's reply tweet only. No quotes around it."
          ),
        },
      ],
      temperature=0.9,
      max_tokens=120,
    )
    text = (response.choices[0].message.content or "").strip()
    return self._clip(text)

  def extract_lesson(self, reply_text: str) -> str | None:
    response = self._client.chat.completions.create(
      model=self._model,
      messages=[
        {
          "role": "user",
          "content": LEARN_PROMPT.format(text=reply_text),
        }
      ],
      temperature=0.3,
      max_tokens=80,
    )
    raw = (response.choices[0].message.content or "").strip()
    if not raw or raw.upper() == "NOTHING":
      return None
    return raw[:500]

  def _clip(self, text: str) -> str:
    text = " ".join(text.split())
    if len(text) <= self._max_len:
      return text
    return text[: self._max_len - 3].rstrip() + "..."
