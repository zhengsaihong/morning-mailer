#!/usr/bin/env python3
"""Send a daily weather greeting through Gmail SMTP."""

from __future__ import annotations

import datetime as dt
import logging
import os
import re
import smtplib
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from html import escape
from zoneinfo import ZoneInfo

import requests

TIMEZONE = ZoneInfo("Asia/Shanghai")
BAIDU_WEATHER_URL = "https://api.map.baidu.com/weather/v1/"
BAIDU_GEOCODING_URL = "https://api.map.baidu.com/geocoding/v3/"
BAIDU_REVERSE_GEOCODING_URL = "https://api.map.baidu.com/reverse_geocoding/v3/"
MORNING_IMAGE_URL = "https://zhengsaihong.github.io/morning-mailer/assets/morning-sunrise.jpg"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("morning_mailer")


def load_config() -> dict[str, str]:
    required = ["BAIDU_MAP_AK", "GMAIL_ADDRESS", "GMAIL_APP_PASSWORD", "RECIPIENTS"]
    config = {name: os.getenv(name, "").strip() for name in required}
    missing = [name for name, value in config.items() if not value]
    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
    return config


def parse_recipients(value: str) -> list[tuple[str, str]]:
    recipients = []
    for line_number, raw_line in enumerate(value.splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        if "," not in line and "，" in line:
            line = line.replace("，", ",", 1)
        if line.count(",") != 1:
            raise ValueError(f"RECIPIENTS line {line_number} must be: 地区,邮箱")
        place, email = (part.strip() for part in line.split(","))
        if not place or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            raise ValueError(f"RECIPIENTS line {line_number} has an invalid region or email address")
        recipients.append((place, email))
    if not recipients:
        raise ValueError("RECIPIENTS must contain at least one 地区,邮箱 entry")
    return recipients


def resolve_city_id(ak: str, place: str) -> str:
    geocoding = requests.get(
        BAIDU_GEOCODING_URL,
        params={"address": place, "output": "json", "ak": ak},
        timeout=15,
    )
    geocoding.raise_for_status()
    geocoding_payload = geocoding.json()
    if geocoding_payload.get("status") != 0:
        raise RuntimeError(f"Could not find region '{place}': {geocoding_payload.get('message', 'Baidu geocoding failed')}")

    location = geocoding_payload["result"]["location"]
    reverse_geocoding = requests.get(
        BAIDU_REVERSE_GEOCODING_URL,
        params={"location": f"{location['lat']},{location['lng']}", "output": "json", "ak": ak},
        timeout=15,
    )
    reverse_geocoding.raise_for_status()
    reverse_payload = reverse_geocoding.json()
    if reverse_payload.get("status") != 0:
        raise RuntimeError(f"Could not identify region '{place}': {reverse_payload.get('message', 'Baidu reverse geocoding failed')}")

    adcode = str(reverse_payload["result"]["addressComponent"].get("adcode", ""))
    if not re.fullmatch(r"\d{6}", adcode):
        raise RuntimeError(f"Baidu did not return an administrative code for '{place}'")
    return f"{adcode[:4]}00"


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
        "把今天最不想做的一件事先做掉，后面就都是赚的。",
        "慢一点没关系，先把早餐和自己照顾好。",
        "今天不用拯救世界，先把眼前的一件小事做好。",
        "不必全速奔跑，稳定前进也算很厉害。",
        "愿你今天有好消息，也有好胃口。",
    )
    return greetings[day.toordinal() % len(greetings)]


def weather_advice(weather: dict[str, object]) -> tuple[str, str]:
    condition = str(weather["condition"])
    if "雨" in condition or "雪" in condition:
        return "出门提醒", "雨伞请带上。湿鞋不会让人显得深情，只会让袜子很有意见。"
    if int(weather["high"]) >= 30:
        return "防晒提醒", "阳光今天工作态度很积极，防晒也请同样认真。"
    if int(weather["low"]) <= 10:
        return "保暖提醒", "今天的风会认真参与对话，外套别留在椅背上。"
    return "今日节奏", "天气很配合。先出门走两步，再决定要不要跟世界讲道理。"


def render_plain_text(now: dt.datetime, weather: dict[str, object]) -> str:
    advice_title, advice_text = weather_advice(weather)
    return "\n".join(
        [
            f"早安，今天是 {now:%Y年%m月%d日}。",
            f"{weather['location']}天气：{weather['condition']}，{weather['temperature']}°C，体感 {weather['feels_like']}°C。",
            f"最高 {weather['high']}°C，最低 {weather['low']}°C，{weather['wind']}。",
            f"{advice_title}：{advice_text}",
            greeting_for(now.date()),
        ]
    )


def render_html(now: dt.datetime, weather: dict[str, object]) -> str:
    date_text = now.strftime("%Y年%m月%d日")
    weekday = "一二三四五六日"[now.weekday()]
    location = escape(str(weather["location"]))
    condition = escape(str(weather["condition"]))
    greeting = escape(greeting_for(now.date()))
    advice_title, advice_text = weather_advice(weather)
    return f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>早安，{location}</title></head>
<body style="margin:0;background:#f4f7f8;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Arial,sans-serif;color:#21363d;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#f4f7f8;padding:28px 12px;"><tr><td align="center">
    <table role="presentation" width="600" cellspacing="0" cellpadding="0" style="max-width:600px;width:100%;background:#ffffff;border-radius:8px;overflow:hidden;">
      <tr><td><img src="{MORNING_IMAGE_URL}" width="600" alt="晨光中的群山" style="display:block;width:100%;height:190px;object-fit:cover;border:0;"></td></tr>
      <tr><td style="padding:28px 34px 12px;">
        <div style="font-size:11px;font-weight:700;letter-spacing:1.2px;color:#c95f4a;">MORNING NOTE · 07:30</div>
        <div style="font-size:30px;font-weight:700;line-height:1.3;color:#21363d;margin-top:8px;">早安，{location}</div>
        <div style="font-size:14px;color:#71858b;margin-top:5px;">{date_text} · 星期{weekday}</div>
      </td></tr>
      <tr><td style="padding:14px 34px 28px;"><div style="font-size:17px;line-height:1.7;color:#425960;">{greeting}</div></td></tr>
      <tr><td style="padding:0 34px 28px;">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="border-top:1px solid #dce6e8;border-bottom:1px solid #dce6e8;">
          <tr><td style="padding:20px 0 18px;">
            <table role="presentation" width="100%" cellspacing="0" cellpadding="0"><tr>
              <td width="58%" style="vertical-align:top;"><div style="font-size:12px;font-weight:700;letter-spacing:1px;color:#71858b;">现在的天气</div><div style="font-size:22px;font-weight:700;color:#21363d;margin-top:9px;">{weather_icon(condition)}&nbsp;{condition}</div><div style="font-size:13px;color:#71858b;margin-top:8px;">{escape(str(weather['wind']))} · 体感 {weather['feels_like']}°C</div></td>
              <td align="right" style="vertical-align:top;"><span style="font-size:58px;font-weight:700;line-height:.9;color:#e16b52;">{weather['temperature']}</span><span style="font-size:20px;font-weight:700;color:#e16b52;">°C</span><div style="font-size:12px;color:#71858b;margin-top:10px;">{weather['low']}°C / {weather['high']}°C</div></td>
            </tr></table>
          </td></tr>
        </table>
      </td></tr>
      <tr><td style="padding:0 34px 26px;">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#fff1eb;border-left:4px solid #e16b52;"><tr><td style="padding:16px 18px;"><div style="font-size:12px;font-weight:700;letter-spacing:.7px;color:#b44a39;">{escape(advice_title)}</div><div style="font-size:15px;line-height:1.65;color:#60443d;margin-top:5px;">{escape(advice_text)}</div></td></tr></table>
      </td></tr>
      <tr><td style="padding:0 34px 30px;text-align:center;font-size:12px;color:#9aabb0;">天气来自百度地图 · 每天 07:30 自动送达</td></tr>
    </table>
  </td></tr></table>
</body></html>"""


def send_email(config: dict[str, str], recipient: str, subject: str, plain: str, html: str) -> None:
    message = MIMEMultipart("alternative")
    message["From"] = config["GMAIL_ADDRESS"]
    message["To"] = recipient
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
        weather_by_place: dict[str, dict[str, object]] = {}
        for place, recipient in parse_recipients(config["RECIPIENTS"]):
            if place not in weather_by_place:
                city_id = resolve_city_id(config["BAIDU_MAP_AK"], place)
                weather_by_place[place] = fetch_weather(config["BAIDU_MAP_AK"], city_id)
            weather = weather_by_place[place]
            plain = render_plain_text(now, weather)
            html = render_html(now, weather)
            send_email(config, recipient, f"早安，{weather['location']}｜{now:%Y-%m-%d}", plain, html)
            log.info("Email sent for %s", weather["location"])
    except (ValueError, requests.RequestException, RuntimeError, KeyError, smtplib.SMTPException) as error:
        log.error("Morning email was not sent: %s", error)
        sys.exit(1)


if __name__ == "__main__":
    main()
