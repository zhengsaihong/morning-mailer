# 早安邮件

> 每天 07:30，让 GitHub 替你说早安。对象不一定回消息，但 GitHub Actions 连已读都没有，直接开口。

这是一个定时往邮箱投递 HTML 早安邮件的小项目。它知道日期、知道天气、会说一句人话；至于你会不会起床，它尊重你的命运。

它住在 GitHub Actions 里，所以你的电脑可以继续装死。每天早上，云端会准时把天气塞进邮箱，像一个情绪稳定、没有边界感的电子熟人。

## 它到底长啥样

[打开示例邮件](https://zhengsaihong.github.io/morning-mailer/) 看看它在收件箱里会装成什么样。示例使用固定演示天气，不访问 API，也不会偷偷顺走任何人的密钥。

## 它每天在忙什么

- 每天中国时间 `07:30` 发一封早安邮件，比不少人类关系稳定
- 可以同时发给多人，大家各看各的天气，互不干涉地活着
- 查询温度、体感、最高/最低温和风力，替你确认今天是不是适合出门
- 用 Gmail SMTP 发邮件，走的是正门
- 发 HTML 邮件，不会把你的收件箱写成上古日志文件

## Fork 一下，命运从这里分叉

这个仓库欢迎 Fork。Fork 走的是代码，不是我的账号、我的 Key，也不是我邮箱里那点脆弱的隐私。你 Fork 之后，它就认你当老板。

Fork 后，打开你自己仓库的 `Settings` → `Secrets and variables` → `Actions`，添加下面四个 Secrets：

| Secret | 你要放进去的东西 |
| --- | --- |
| `BAIDU_MAP_AK` | 你自己的百度地图天气服务 AK，别借，借了它也不认识你 |
| `GMAIL_ADDRESS` | 负责替你早起上班的 Gmail 地址 |
| `GMAIL_APP_PASSWORD` | Gmail 应用专用密码，不是登录密码，别把家门钥匙扔这儿 |
| `RECIPIENTS` | 每行一个 `地区,邮箱`，例如 `福建省莆田市,a@qq.com` |

然后到 `Actions` 页面运行一次 `Daily Morning Mail`。收到测试邮件，说明你的赛博早八员工已经到岗；它不摸鱼，也不会申请调休。

> Secrets 只保存在你 Fork 后的仓库，不会出现在代码、提交记录或别人 Fork 的仓库。请不要把它们直接写进 `briefing.py`，不然你的密钥就会开始一场没有签证的世界巡演。

### 多人、多地区，怎么安排

在 `RECIPIENTS` Secret 里，一行写一位需要被天气提醒的人。左边是地区，右边是邮箱：

```text
福建莆田,a@qq.com
福建省福州市,b@qq.com
```

程序会把中文地区交给百度地图识别，并按城市级天气发送。例如 `福建莆田` 和 `福建省莆田市` 都显示为“莆田市”，不会因为城市中心落在某个区，就把整座城市偷偷缩小。同一个地区有多人时，天气只查一次，但每个人都会收到单独一封邮件，主打一个雨露均沾。地区尽量写全，例如 `福建省福州市`，避免它在地图上产生身份焦虑。

## 为什么非得 07:30

工作流在 UTC `23:30` 运行，对应中国标准时间 `07:30`。中国没有夏令时，所以它不会随着季节变换突然开始摆烂。

想改时间？编辑 [`.github/workflows/daily-briefing.yml`](.github/workflows/daily-briefing.yml) 的 cron 表达式即可。改成中午也行，早安迟到一点，问题不大，生活已经够难了。

## 本地召唤仪式

不想等明天早上，可以在本地跑一次：

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

`.env` 已被 Git 忽略。它唯一的工作就是安静待在你的电脑里，不要出去社交。

## 你还能把它改成什么怪东西

- 想查别的城市或增加收件人：修改 `RECIPIENTS` Secret
- 想换一句问候：修改 `greeting_for()`，让它更像你，也更难评价
- 想加日程、待办、新闻或 AI 摘要：可以，项目不会阻止你走向信息过载

## 许可证，拿去吧

[MIT](LICENSE)。拿去用、拿去改、拿去 Fork；但请把你的 Key 留在自己的 Secrets 里。电子世界很大，密钥别乱跑。
