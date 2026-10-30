# 早安邮件

> 每天 07:30，让 GitHub 替你准时说早安。毕竟对象不一定每天准时回消息，但 GitHub Actions 会。

这是一个会每天发送 HTML 早安邮件的小项目：日期、你选的地点的天气和一句问候，内容不多，适合在起床前先确认今天该不该带伞，或者干脆继续躺五分钟。

它跑在 GitHub Actions 上，所以你的电脑可以安心睡觉；唯一需要保持清醒的是 GitHub。

## 它长什么样

[打开示例邮件](https://zhengsaihong.github.io/morning-mailer/) 看看收件箱里会出现的 HTML 邮件。示例使用固定的演示天气，不会访问 API，也没有任何人的密钥。

## 它会做什么

- 每天中国时间 `07:30` 发一封早安邮件
- 可同时给多人发送，每人按自己填写的地区收到对应天气
- 查询你设置地点的天气，包括温度、体感温度、最高/最低温和风力
- 用 Gmail SMTP 发邮件
- 发一份 HTML 邮件，而不是一团令人困惑的纯文本

## Fork 一下就能用

这个仓库欢迎 Fork。Fork 走的是代码，不是我的账号，也不是我的 Key，更不是我邮箱里的任何东西。

Fork 后，打开你自己仓库的 `Settings` → `Secrets and variables` → `Actions`，添加下面四个 Secrets：

| Secret | 你要放进去的东西 |
| --- | --- |
| `BAIDU_MAP_AK` | 你自己的百度地图天气服务 AK |
| `GMAIL_ADDRESS` | 负责早起干活的 Gmail 地址 |
| `GMAIL_APP_PASSWORD` | Gmail 应用专用密码，不是登录密码 |
| `RECIPIENTS` | 每行一个 `地区,邮箱`，例如 `福建省莆田市,a@qq.com` |

然后到 `Actions` 页面运行一次 `Daily Morning Mail`。收到测试邮件，说明你的自动早安小员工已经入职。

> Secrets 只保存在你 Fork 后的仓库里，不会出现在代码、提交记录或别人 Fork 的仓库中。请不要把它们直接写进 `briefing.py`，那样会让它们获得一次意外的环球旅行机会。

### 多人、多地区怎么填

在 `RECIPIENTS` Secret 里一行写一位收件人，左边是地区，右边是邮箱：

```text
福建莆田,a@qq.com
福建省福州市,b@qq.com
```

程序会把中文地区交给百度地图识别，再为每个人发送对应地区的天气。同一个地区有多人时，天气只查一次，但每个人都会收到单独的一封邮件。地区尽量写全，例如 `福建省福州市`，这样不会和其他同名地区撞车。

## 为什么是 07:30

工作流在 UTC `23:30` 运行，对应中国标准时间 `07:30`。中国没有夏令时，所以它不会因为季节变化突然睡过头。

想改时间？编辑 [`.github/workflows/daily-briefing.yml`](.github/workflows/daily-briefing.yml) 的 cron 表达式即可。

## 本地试跑

不想等到明天早上，可以在本地测试：

```bash
git clone https://github.com/<你的用户名>/morning-mailer.git
cd morning-mailer
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# 填好 .env 后再运行；别把它提交上去
set -a; source .env; set +a
python briefing.py
```

`.env` 已被 Git 忽略。它的职责很简单：安静地待在你的电脑里。

## 可改造的地方

- 想查别的城市或增加收件人：修改 `RECIPIENTS` Secret
- 想换一句问候：修改 `greeting_for()`
- 想在邮件里加日程、待办、新闻或 AI 摘要：欢迎自己折腾，也欢迎提 PR

## 许可证

[MIT](LICENSE)。拿去用、拿去改、拿去 Fork；但请把你的 Key 留在你自己的 Secrets 里。
