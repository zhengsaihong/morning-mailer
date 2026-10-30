import datetime as dt
import unittest
from zoneinfo import ZoneInfo

import briefing


WEATHER = {
    "location": "示例地区",
    "condition": "多云",
    "temperature": 24,
    "feels_like": 25,
    "wind": "东北风 3级",
    "high": 28,
    "low": 21,
}


class BriefingRenderTests(unittest.TestCase):
    def test_plain_text_contains_weather_and_greeting(self):
        now = dt.datetime(2026, 10, 30, 7, 30, tzinfo=ZoneInfo("Asia/Shanghai"))
        body = briefing.render_plain_text(now, WEATHER)
        self.assertIn("示例地区天气：多云，24°C", body)
        self.assertIn(briefing.greeting_for(now.date()), body)

    def test_html_escapes_weather_text(self):
        unsafe = {**WEATHER, "condition": "晴<script>"}
        body = briefing.render_html(dt.datetime(2026, 10, 30, tzinfo=ZoneInfo("Asia/Shanghai")), unsafe)
        self.assertIn("晴&lt;script&gt;", body)
        self.assertNotIn("晴<script>", body)


if __name__ == "__main__":
    unittest.main()
