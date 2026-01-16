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
work_rate = f"{(today_worknum - yesterday_worknum) / yesterday_worknum * 100:.4f}"
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
post_rate = f"{(today_postnum - yesterday_postnum) / yesterday_postnum * 100:.4f}"
reply_rate = f"{(today_replynum - yesterday_replynum) / yesterday_replynum * 100:.4f}"
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

# 写入到HTML（论坛）
html = f"""
<p><strong><span style=\"font-size: large;\"><img
src=\"https://static.codemao.cn/emoji/codemao/%E7%BC%96%E7%A8%8B%E7%8C%AB_%E5%97%A8%E8%B5%B7%E6%9D%A5.gif\"
alt=\"emotion_编程猫_嗨起来\"></span></strong></p>
<div>&nbsp;</div><br/>

<p><span style=\"color: #ff5050;\"><strong>
<span style=\"font-size: large;\">⚠️ 提示</span>
</strong></span></p>

<div><span style=\"color:#ff5050;\">数据由程序自动统计并上传，截止到本日23:50分</span></div>
<div>&nbsp;</div><br/>

<div><span style=\"color:#ff5050;\">首页只显示 TOP10 作品，由API自动选取</span></div>
<div>&nbsp;</div><br/>

<div><span style=\"color:#ff5050;\">你猫统计API有点问题，作品数量的统计可能会有异常情况发生</span></div>
<div>&nbsp;</div><br/><br/>

<div><strong><span style=\"font-size: large;\">📈 作品情况</span></strong></div>
<div>&nbsp;</div><br/><br/>

<div>✅ 今日上传作品：
<span style=\"color:#50aae6;\">{today_worknum - yesterday_worknum}</span> 个</div>
<div>&nbsp;</div><br/>

<div>📈 作品增长率（较昨日）：
<span style=\"color:#50aae6;\">{work_rate}</span> %</div>
<div>&nbsp;</div><br/><br/>

<div><strong><span style=\"font-size: large;\">📈 论坛情况</span></strong></div>
<div>&nbsp;</div><br/><br/>

<div>✅ 今日发布帖子：
<span style=\"color:#50aae6;\">{today_postnum - yesterday_postnum}</span> 个</div>
<div>&nbsp;</div><br/>

<div>📈 帖子增长率（较昨日）：
<span style=\"color:#50aae6;\">{post_rate}</span> %</div>
<div>&nbsp;</div><br/>

<div>✅ 今日回复帖子总数：
<span style=\"color:#50aae6;\">{today_replynum - yesterday_replynum}</span> 个</div>
<div>&nbsp;</div><br/>

<div>📈 回复增长率（较昨日）：
<span style=\"color:#50aae6;\">{reply_rate}</span> %</div>
<div>&nbsp;</div><br/><br/>

<div><strong><span style=\"font-size: large;\">🏠 首页情况</span></strong></div>
<div>&nbsp;</div><br/>

<div><span style=\"font-size: small;\">只选取TOP10作品</span></div>
<div>&nbsp;</div><br/><br/>
"""

work_no = 0

for work in items:
    work_no = work_no + 1
    html += f"""
<div>
<div><strong><span
        style=\"font-size: medium;\">《{work["work_name"]}》</span></strong></div>
<div>&nbsp;</div><br/>

<div><span style=\"font-size: small;\"><strong>🔢&nbsp;</strong></span>作品ID：
<span style=\"color: #50aae6;\">{work["work_id"]}</span></div>
<div>&nbsp;</div><br/>


<div><span style=\"font-size: small;\"><strong>🔧&nbsp;</strong></span>开发者：
<span style=\"color: #50aae6;\">{work["nickname"]}</span></div>
<div>&nbsp;</div><br/>

<div>👁 总浏览数：
<span style=\"color: #50aae6;\">{work["views_count"]}</span></div>
<div>&nbsp;</div><br/>

<div>👍🏻 总点赞数：
<span style=\"color: #50aae6;\">{work["likes_count"]}</span></div>
<div>&nbsp;</div><br/>

<div>🤔 排名：
<span style=\"color: #50aae6;\">{work_no}</span> 名</div>
<div>&nbsp;</div><br/>
</div><br/>
"""

html += f"""
<br/><div><strong><span style=\"font-size: large;\">👌🏻 统计完成</span></strong></div>
<div>&nbsp;</div><br/>

<div>Action触发时间戳：
<strong>{time.time()}</strong></div>
<div>&nbsp;</div><br/>

<div>若有统计问题，可在此帖子下进行反馈</div>
<div>&nbsp;</div><br/>

<div>黎星羽的训练师ID：1458227103</div>
<div>&nbsp;</div><br/>

<div>同时发布在图书馆，小说ID：192733</div>
<div>&nbsp;</div><br/>

<div>本帖将会发在“灌水池塘”，之后想看的话，也可以来这里找</div>
<div>&nbsp;</div><br/>

<div><img
src=\"https://static.codemao.cn/emoji/codemao/%E7%BC%96%E7%A8%8B%E7%8C%AB_%E7%82%B9%E8%B5%9E.gif\"
alt=\"emotion_编程猫_点赞\"></div>
"""

# 发布论坛

response = PostAPI(
    Path="/web/forums/boards/7/posts",
    PostData={
        "title": f"{date.today().isoformat()} 统计情况【编程猫赛博史书】",
        "content": html,
    },
    Token=token,
)

post_id = json.loads(response.text).get("id", 0)
print(f"完成论坛上传任务, 帖子ID：{post_id}")


# 发布小说

html_novel = f"""
<h1 style="font-size: 1.6em; font-weight: normal;">
    {date.today().isoformat()} 统计数据
</h1>

<p><span style="color: #ff5050;">数据由程序自动统计并上传，截止到本日23:50分</span></p>
<p><span style="color: #ff5050;">首页只显示 TOP10 作品，由API自动选取</span></p>
<p><span style="color: #ff5050;">你猫统计API有点问题，作品数量的统计可能会有异常情况发生</span></p>

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

work_no = 0

for work in items:
    work_no = work_no + 1
    html_novel += f"""
<h3 style="font-size: 1.2em; font-weight: normal;">
  《{work["work_name"]}》
</h3>
<p>作品ID：{work["work_id"]}</p>
<p>开发者：{work["nickname"]}</p>
<p>总浏览数：{work["views_count"]}</p>
<p>总点赞：{work["likes_count"]}</p>
<p>排行：{work_no} 名</p>
<br/>
"""

html_novel += f"""
<h2 style="font-size: 1.4em; font-weight: normal;">
  ============ 统计完成 ============
</h2>
<p>Action触发时间戳：{time.time()}</p>
<p>若有统计问题，可在黎星羽的作品/本日统计帖子下反馈</p>
<p>已在论坛完成发帖，帖子ID：{post_id}</p>
<p>黎星羽的训练师ID：1458227103</p>
<p>BY LiXingYu</p>
"""

response = PostAPI(
    Path="/web/fanfic/section",
    PostData={
        "title": datetime.now().strftime("%m%d"),
        "draft": html_novel,
        "draft_words_num": 0,
        "fanfic_id": 192733,
    },
    Token=token,
)

t_id = json.loads(response.text).get("id", 0)

PutAPI(Path=f"/web/fanfic/section/{t_id}/publish", Token=token)

print(f"完成小说上传任务，章节ID：{t_id}")
