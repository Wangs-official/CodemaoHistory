# Main.py

from CodemaoEDUTools import GetUserToken, GetWithoutTokenAPI, PostAPI, PutAPI
from datetime import date, datetime
import json
import time
import os

boards = ["17", "2", "10", "5", "3", "6", "27", "11", "26", "13", "7", "4", "28"]

# 登录

token = GetUserToken(os.environ["CODEMAO_PHONE"], os.environ["CODEMAO_PASSWORD"])

# 获得今日T10作品

response = GetWithoutTokenAPI(
    "/creation-tools/v1/pc/discover/subject-work?offset=0&limit=10"
)
today_index = response.text

# 获取本日作品增加情况

with open("status.json", "r") as f:
    data = json.load(f)

today_worknum = (
    GetWithoutTokenAPI("/creation-tools/v1/pc/discover/newest-work?offset=0&limit=20")
    .json()
    .get("total")
)
print(f"今日作品数量：{today_worknum}")
yesterday_worknum = data["work_count"]
work_rate = f"{(today_worknum - yesterday_worknum) / yesterday_worknum * 100:.2f}"
f.close()


# 获取本日帖子增加情况

with open("status.json", "r") as f:
    data = json.load(f)

today_postnum = 0
today_replynum = 0

for board_id in boards:
    response = GetWithoutTokenAPI(f"/web/forums/boards/{board_id}")
    n_posts = json.loads(response.text).get("n_posts", 0)
    today_postnum += n_posts
    n_reply = json.loads(response.text).get("n_discussions", 0)
    today_replynum += n_reply
print(f"今日帖子数量：{today_postnum}")
print(f"今日回复数量：{today_replynum}")
yesterday_postnum = data["post_count"]
yesterday_replynum = data["reply_count"]
post_rate = f"{(today_postnum - yesterday_postnum) / yesterday_postnum * 100:.2f}"
reply_rate = f"{(today_replynum - yesterday_replynum) / yesterday_replynum * 100:.2f}"
f.close()

# 回写数据

with open("status.json", "r", encoding="utf-8") as f:
    status = json.load(f)

status["work_count"] = today_worknum
status["post_count"] = today_postnum
status["reply_count"] = today_replynum

with open("status.json", "w", encoding="utf-8") as f:
    json.dump(status, f, ensure_ascii=False, indent=2)

f.close()

# 解析首页作品

index_data = json.loads(today_index)
items = index_data.get("items", [])

# 写入到HTML

html = f"""
<h1 style="font-size: 1.6em; font-weight: normal;">
    {date.today().isoformat()} 统计数据
</h1>

<p><span style="color: #ff5050;">数据由程序自动统计并上传，截止到本日23:50分</span></p>
<p><span style="color: #ff5050;">首页只显示 TOP10 作品，由API自动选取</span></p>
<p><span style="color: #ff5050;">由于你猫统计API有点问题，作品数量/帖子数量的统计可能会有点问题</span></p>

<h2 style="font-size: 1.4em; font-weight: normal;">
  ============ ~作品情况~ ============
</h2>
<p>今日上传作品：{today_worknum - yesterday_worknum} 个</p>
<p>作品增长率（较昨日）：{work_rate} %</p>

<h2 style="font-size: 1.4em; font-weight: normal;">
  ============ ~论坛情况~ ============
</h2>
<p>今日发布帖子：{today_postnum - yesterday_postnum} 个</p>
<p>帖子增长率（较昨日）：{post_rate} %</p>
<p>今日回复帖子总数：{today_replynum - yesterday_replynum} 个</p>
<p>回复增长率（较昨日）：{reply_rate} %</p>

<h2 style="font-size: 1.4em; font-weight: normal;">
  ============ ~首页情况~ ============
</h2>
"""

for work in items:
    html += f"""
<h3 style="font-size: 1.2em; font-weight: normal;">
  《{work["work_name"]}》
</h3>
<p>作品ID：{work["work_id"]}</p>
<p>开发者：{work["nickname"]}</p>
<p>总浏览数：{work["views_count"]}</p>
<p>总点赞：{work["likes_count"]}</p>
<br/>
"""

html += f"""
<h2 style="font-size: 1.4em; font-weight: normal;">
  ============ 统计完成 ============
</h2>
<p>Action触发时间戳：{time.time()}</p>
<p>若有统计问题，可在黎星羽的作品下反馈</p>
<p>黎星羽的训练师ID：1458227103</p>
<p>BY LiXingYu</p>
"""

# 发布

response = PostAPI(
    Path="/web/fanfic/section",
    PostData={
        "title": datetime.now().strftime("%m%d"),
        "draft": html,
        "draft_words_num": 0,
        "fanfic_id": 192733,
    },
    Token=token,
)

t_id = json.loads(response.text).get("id", 0)

PutAPI(Path=f"/web/fanfic/section/{t_id}/publish", Token=token)

print("完成上传任务")
