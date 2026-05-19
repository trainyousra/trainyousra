import logging
import time

import tweepy

from yousra.config import Settings
from yousra.constants import DEVELOPER_HANDLE, DEVELOPER_NAME, PROJECT_NAME
from yousra.llm import YousraLLM
from yousra.memory import MemoryStore

log = logging.getLogger("yousra.bot")


class YousraBot:
  def __init__(self, settings: Settings) -> None:
    settings.validate_x()
    settings.validate_openai()
    self._settings = settings
    self._llm = YousraLLM(
      settings.openai_api_key,
      settings.openai_model,
      settings.max_tweet_length,
    )
    self._memory = MemoryStore(settings.data_dir / "yousra.db")
    self._client = tweepy.Client(
      bearer_token=settings.x_bearer_token,
      consumer_key=settings.x_api_key,
      consumer_secret=settings.x_api_secret,
      access_token=settings.x_access_token,
      access_token_secret=settings.x_access_token_secret,
      wait_on_rate_limit=True,
    )
    self._bot_user_id: str | None = None

  def _bot_id(self) -> str:
    if self._bot_user_id:
      return self._bot_user_id
    user = self._client.get_user(username=self._settings.x_bot_username)
    if not user.data:
      raise RuntimeError(f"X user @{self._settings.x_bot_username} not found")
    self._bot_user_id = user.data.id
    return self._bot_user_id

  def run_forever(self) -> None:
    log.info(
      "%s online — polling mentions (runtime by %s / @%s)",
      PROJECT_NAME,
      DEVELOPER_NAME,
      DEVELOPER_HANDLE,
    )
    while True:
      try:
        self.poll_once()
      except Exception:
        log.exception("poll cycle failed")
      time.sleep(self._settings.poll_interval_seconds)

  def poll_once(self) -> int:
    bot_id = self._bot_id()
    response = self._client.get_users_mentions(
      id=bot_id,
      max_results=10,
      tweet_fields=["author_id", "conversation_id", "created_at"],
      expansions=["author_id"],
      user_fields=["username"],
    )
    if not response.data:
      log.info("no new mentions")
      return 0

    users = {}
    if response.includes and "users" in response.includes:
      users = {u.id: u.username for u in response.includes["users"]}

    handled = 0
    for tweet in reversed(response.data):
      tweet_id = str(tweet.id)
      if self._memory.is_seen(tweet_id):
        continue
      self._memory.mark_seen(tweet_id)
      author_id = str(tweet.author_id)
      username = users.get(tweet.author_id, "someone")
      text = (tweet.text or "").strip()
      if not text:
        continue
      self._handle_mention(tweet_id, username, text)
      handled += 1
    return handled

  def _handle_mention(self, tweet_id: str, username: str, text: str) -> None:
    log.info("mention from @%s: %s", username, text[:80])
    memories = self._memory.recent_lessons(
      self._settings.max_memories_in_prompt
    )
    reply = self._llm.reply(text, username, memories)
    log.info("yousra says: %s", reply)

    self._client.create_tweet(
      text=reply,
      in_reply_to_tweet_id=tweet_id,
    )

    lesson = self._llm.extract_lesson(text)
    if lesson:
      self._memory.add_memory(tweet_id, username, lesson, text)
      log.info("learned: %s", lesson)
    else:
      log.info("nothing new to learn this time")
