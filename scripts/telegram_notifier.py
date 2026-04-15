"""
Telegram notifier utility for operational process logging.

Usage:
- Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID env vars.
- Instantiate TelegramNotifier(process_name="...").
- Send structured status messages for start/progress/success/error.
"""
from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Optional

import requests


@dataclass
class TelegramNotifier:
    process_name: str
    bot_token: Optional[str] = None
    chat_id: Optional[str] = None
    enabled: bool = True
    timeout: int = 10

    def __post_init__(self) -> None:
        self.bot_token = self.bot_token or os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = self.chat_id or os.getenv("TELEGRAM_CHAT_ID")
        self.enabled = bool(self.enabled and self.bot_token and self.chat_id)

    def _format(self, level: str, message: str) -> str:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        return f"[{timestamp}] [{self.process_name}] [{level}]\n{message}"

    def send(self, message: str, level: str = "INFO") -> bool:
        if not self.enabled:
            return False

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": self._format(level, message),
            "disable_web_page_preview": True,
        }

        try:
            response = requests.post(url, json=payload, timeout=self.timeout)
            return response.status_code == 200
        except requests.RequestException:
            return False

    def info(self, message: str) -> bool:
        return self.send(message, level="INFO")

    def warning(self, message: str) -> bool:
        return self.send(message, level="WARN")

    def error(self, message: str) -> bool:
        return self.send(message, level="ERROR")

    def success(self, message: str) -> bool:
        return self.send(message, level="SUCCESS")
