import datetime as dt
import unittest
from unittest.mock import Mock, patch
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
    def test_parse_recipients_accepts_multiple_regions(self):
        recipients = briefing.parse_recipients("福建莆田,a@qq.com\n福建省福州市，b@qq.com")
        self.assertEqual(recipients, [("福建莆田", "a@qq.com"), ("福建省福州市", "b@qq.com")])

    def test_parse_recipients_rejects_invalid_lines(self):
        with self.assertRaises(ValueError):
            briefing.parse_recipients("福建莆田")

    @patch("briefing.requests.get")
    def test_resolve_district_id_geocodes_then_reverse_geocodes(self, get):
        geocoding = Mock()
        geocoding.json.return_value = {"status": 0, "result": {"location": {"lat": 25.45, "lng": 119.0}}}
        reverse_geocoding = Mock()
        reverse_geocoding.json.return_value = {"status": 0, "result": {"addressComponent": {"adcode": "350300"}}}
        get.side_effect = [geocoding, reverse_geocoding]

        self.assertEqual(briefing.resolve_district_id("test-ak", "福建莆田"), "350300")
        self.assertEqual(get.call_count, 2)
        self.assertEqual(get.call_args_list[1].kwargs["params"]["location"], "25.45,119.0")

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

    def test_rainy_weather_gets_an_umbrella_reminder(self):
        title, advice = briefing.weather_advice({**WEATHER, "condition": "小雨"})
        self.assertEqual(title, "出门提醒")
        self.assertIn("雨伞", advice)


if __name__ == "__main__":
    unittest.main()
