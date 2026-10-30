# 莆田早安邮件

每天中国时间 07:30 自动发送一封 HTML 邮件，内容包含日期、福建莆田天气和一句早安问候。

运行在 GitHub Actions，无需本地电脑持续开机。天气由[百度地图天气 API](https://lbsyun.baidu.com/docs/webapi?title=weatherinquiry/weather/base)提供，邮件通过 Gmail SMTP 发送。

## GitHub 配置

1. 在你的 GitHub 账号新建一个**私有**仓库，并推送本项目。
2. 打开仓库的 `Settings` → `Secrets and variables` → `Actions`，添加以下 Secrets：

| Secret | 用途 |
| --- | --- |
| `BAIDU_MAP_AK` | 百度地图天气服务 AK |
| `GMAIL_ADDRESS` | 发件 Gmail 地址 |
| `GMAIL_APP_PASSWORD` | Gmail 应用专用密码 |
| `RECIPIENT_EMAIL` | 收件 QQ 邮箱地址 |

3. 在 `Actions` 页面运行一次 `Daily Morning Mail` 的 `Run workflow`，确认邮件可正常收到。

定时任务使用 UTC `23:30`，对应每天中国标准时间 `07:30`，不受夏令时影响。

## 本地测试

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
set -a; source .env; set +a
python briefing.py
```

将 `.env.example` 复制为 `.env` 后填写配置；`.env` 已被 Git 忽略，不能提交。

收件人尚未确定时不要在 GitHub 中启用或手动运行工作流。未设置 `RECIPIENT_EMAIL` 时，脚本会退出且不会发送邮件。
