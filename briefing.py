#!/usr/bin/env python3
"""Send a daily weather greeting through Gmail SMTP."""

from __future__ import annotations

import datetime as dt
import logging
import os
import smtplib
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from html import escape
from zoneinfo import ZoneInfo

import requests

TIMEZONE = ZoneInfo("Asia/Shanghai")
BAIDU_WEATHER_URL = "https://api.map.baidu.com/weather/v1/"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("morning_mailer")


def load_config() -> dict[str, str]:
    required = ["BAIDU_MAP_AK", "BAIDU_DISTRICT_ID", "GMAIL_ADDRESS", "GMAIL_APP_PASSWORD", "RECIPIENT_EMAIL"]
    config = {name: os.getenv(name, "").strip() for name in required}
    missing = [name for name, value in config.items() if not value]
    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
    return config


def fetch_weather(ak: str, district_id: str) -> dict[str, object]:
    response = requests.get(
        BAIDU_WEATHER_URL,
        params={"district_id": district_id, "data_type": "all", "ak": ak},
        timeout=15,
    )
    response.raise_for_status()
    payload = response.json()
    if payload.get("status") != 0:
        raise RuntimeError(payload.get("message", "Baidu weather request failed"))

    result = payload["result"]
    now = result["now"]
    forecast = result["forecasts"][0]
    return {
        "location": str(result["location"]["name"]),
        "condition": str(now["text"]),
        "temperature": int(now["temp"]),
        "feels_like": int(now["feels_like"]),
        "wind": f"{now['wind_dir']} {now['wind_class']}",
        "high": int(forecast["high"]),
        "low": int(forecast["low"]),
    }


def weather_icon(condition: str) -> str:
    if "雷" in condition:
        return "&#9928;"
    if "雪" in condition:
        return "&#10052;"
    if "雨" in condition:
        return "&#127783;"
    if "阴" in condition or "云" in condition:
        return "&#9925;"
    return "&#9728;"


def greeting_for(day: dt.date) -> str:
    greetings = (
        "新的一天，认真生活，也别忘了照顾自己。",
        "愿你今天步履从容，所遇皆是好事。",
        "把注意力放在眼前的一件事上，慢慢做好它。",
        "清晨有光，今天也值得期待。",
        "愿你今天心有方向，行有所获。",
    )
    return greetings[day.toordinal() % len(greetings)]


def render_plain_text(now: dt.datetime, weather: dict[str, object]) -> str:
    return "\n".join(
        [
            f"早安，今天是 {now:%Y年%m月%d日}。",
            f"{weather['location']}天气：{weather['condition']}，{weather['temperature']}°C，体感 {weather['feels_like']}°C。",
            f"最高 {weather['high']}°C，最低 {weather['low']}°C，{weather['wind']}。",
            greeting_for(now.date()),
        ]
    )


def render_html(now: dt.datetime, weather: dict[str, object]) -> str:
    date_text = now.strftime("%Y年%m月%d日")
    weekday = "一二三四五六日"[now.weekday()]
    location = escape(str(weather["location"]))
    condition = escape(str(weather["condition"]))
    greeting = escape(greeting_for(now.date()))
    return f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>早安，{location}</title></head>
<body style="margin:0;background:#f3f6f4;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Arial,sans-serif;color:#183028;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#f3f6f4;padding:28px 12px;"><tr><td align="center">
    <table role="presentation" width="600" cellspacing="0" cellpadding="0" style="max-width:600px;width:100%;background:#fff;border-radius:8px;overflow:hidden;">
      <tr><td style="background:#176b4d;padding:32px 30px;color:#fff;"><div style="font-size:26px;font-weight:700;">早安</div><div style="font-size:14px;opacity:.86;margin-top:8px;">{date_text} 星期{weekday} · {location}</div></td></tr>
      <tr><td style="padding:28px 30px;"><p style="margin:0 0 22px;font-size:16px;line-height:1.7;">{greeting}</p>
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#eef7f2;border-radius:8px;"><tr><td style="padding:22px;"><div style="font-size:14px;font-weight:700;color:#176b4d;margin-bottom:14px;">{weather_icon(condition)}&nbsp; 今日天气</div><div style="font-size:34px;font-weight:700;line-height:1;">{weather['temperature']}<span style="font-size:18px;">°C</span></div><div style="font-size:15px;margin-top:10px;">{condition} · 体感 {weather['feels_like']}°C</div><div style="font-size:14px;color:#527064;margin-top:8px;">最高 {weather['high']}°C / 最低 {weather['low']}°C · {escape(str(weather['wind']))}</div></td></tr></table>
      </td></tr>
      <tr><td style="padding:0 30px 24px;color:#82958c;font-size:12px;text-align:center;">由 GitHub Actions 自动发送</td></tr>
    </table>
  </td></tr></table>
</body></html>"""


def send_email(config: dict[str, str], subject: str, plain: str, html: str) -> None:
    message = MIMEMultipart("alternative")
    message["From"] = config["GMAIL_ADDRESS"]
    message["To"] = config["RECIPIENT_EMAIL"]
    message["Subject"] = subject
    message.attach(MIMEText(plain, "plain", "utf-8"))
    message.attach(MIMEText(html, "html", "utf-8"))
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(config["GMAIL_ADDRESS"], config["GMAIL_APP_PASSWORD"].replace(" ", ""))
        smtp.send_message(message)


def main() -> None:
    try:
        config = load_config()
        now = dt.datetime.now(TIMEZONE)
        weather = fetch_weather(config["BAIDU_MAP_AK"], config["BAIDU_DISTRICT_ID"])
        plain = render_plain_text(now, weather)
        html = render_html(now, weather)
        send_email(config, f"早安，{weather['location']}｜{now:%Y-%m-%d}", plain, html)
        log.info("Email sent to %s", config["RECIPIENT_EMAIL"])
    except (ValueError, requests.RequestException, RuntimeError, KeyError) as error:
        log.error("Morning email was not sent: %s", error)
        sys.exit(1)


if __name__ == "__main__":
    main()
