# Main.py

from CodemaoEDUTools import GetUserToken, GetWithoutTokenAPI, PostAPI, PutAPI
from datetime import date, datetime
import json
import time
import os
import requests

boards = ["17", "2", "10", "5", "3", "6", "27", "11", "26", "13", "7", "4", "28"]

# 登录

token = GetUserToken(os.environ["CODEMAO_PHONE"], os.environ["CODEMAO_PASSWORD"])

headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Connection": "keep-alive",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
    "authorization": token,
}

# 获得今日T10作品

response = GetWithoutTokenAPI(
    "/creation-tools/v1/pc/discover/subject-work?offset=0&limit=10"
)
today_index = response.text

# 获取本日作品增加情况

with open("status.json", "r") as f:
    data = json.load(f)

yesterday_workid = data["work_lastid"]
yesterday_worknum = data["work_count"]

today_workid = json.loads(
    requests.post(
        url="https://api-creation.codemao.cn/kitten/r2/work",
        json={
            "name": "临时作品",
            "work_url": "https://creation.bcmcdn.com/445/kitten/d2ViXzIwMDJfMTQ1ODIyNzEwM18xXzE3Njc5NzAyMDU5MjNfY2U2NGFhYmM=.bcm4",
            "preview": "https://creation.bcmcdn.com/445/kitten/d2ViXzIwMDFfMTQ1ODIyNzEwM18xXzE3Njc5NzAyMDU2MTRfY2RhNTQ1MzM=",
            "orientation": 1,
            "sample_id": "",
            "version": "4.11.18",
            "work_source_label": 1,
            "save_type": 2,
        },
        headers=headers,
    ).text
).get("id")
print(f"测试的作品ID：{today_workid}")
print(f"今日作品数量：{today_workid - yesterday_workid}")
today_worknum = today_workid - yesterday_workid
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
post_rate = f"{(today_postnum - yesterday_postnum) / yesterday_postnum * 100:.4f}"
reply_rate = f"{(today_replynum - yesterday_replynum) / yesterday_replynum * 100:.4f}"
f.close()

# 回写数据

with open("status.json", "r", encoding="utf-8") as f:
    status = json.load(f)

status["work_count"] = today_worknum
status["work_lastid"] = today_workid
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
<p><span style=\"color: #ff5050;\"><strong>
<span style=\"font-size: large;\">⚠️ 提示</span>
</strong></span></p>

<div><span style=\"color:#ff5050;\">数据由程序自动统计并上传，截止到本日23:50分</span></div>
<div>&nbsp;</div><br/>

<div><span style=\"color:#ff5050;\">首页只显示 TOP10 作品，由API自动选取</span></div>
<div>&nbsp;</div><br/>

<div><strong><span style=\"font-size: large;\">📈 作品情况</span></strong></div>
<div>&nbsp;</div><br/><br/>

<div>✅ 今日上传作品：
<span style=\"color:#50aae6;\">{today_worknum}</span> 个</div>
<div>&nbsp;</div><br/>

<div>📈 作品增长率（较昨日）：
<span style=\"color:#50aae6;\">{work_rate}</span> %</div>
<div>&nbsp;</div><br/><br/>

<div><strong><span style=\"font-size: large;\">📈 论坛情况</span></strong></div>
<div>&nbsp;</div><br/><br/>

<div>✅ 今日发布帖子：
<span style=\"color:#50aae6;\">{today_postnum - yesterday_postnum}</span> 个</div>
<div>&nbsp;</div><br/>

<div>📈 帖子整体增长率（较昨日）：
<span style=\"color:#50aae6;\">{post_rate}</span> %</div>
<div>&nbsp;</div><br/>

<div>✅ 今日回复帖子总数：
<span style=\"color:#50aae6;\">{today_replynum - yesterday_replynum}</span> 个</div>
<div>&nbsp;</div><br/>

<div>📈 回复整体增长率（较昨日）：
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

<div>同时发布在图书馆，小说ID：192733</div>
<div>&nbsp;</div><br/>

<div>此Bot由HachimLab创造，欢迎查看我们的官网：Https://Hachimlab.top/</div>
<div>&nbsp;</div><br/>

<div>HachimLab是一个公益的编程猫第三方脚本制作工作室，欢迎各位的加入！</div>
<div>&nbsp;</div><br/>

<div>本帖将会发在“灌水池塘”，之后想看的话，也可以来这里找</div>
<div>&nbsp;</div><br/>
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

if response.status_code == 201:
    post_id = json.loads(response.text).get("id", 0)
    print(f"完成论坛上传任务, 帖子ID：{post_id}")
else:
    print(f"社区状态异常: {response.status_code}，跳过发帖任务")
    print(f"{response.text}")


# # 发布小说

# html_novel = f"""
# <h1 style="font-size: 1.6em; font-weight: normal;">
#     {date.today().isoformat()} 统计数据
# </h1>

# <p><span style="color: #ff5050;">数据由程序自动统计并上传，截止到本日23:50分</span></p>
# <p><span style="color: #ff5050;">首页只显示 TOP10 作品，由API自动选取</span></p>

# <h2 style="font-size: 1.4em; font-weight: normal;">
#   ============ ~作品情况~ ============
# </h2>
# <p>今日上传作品：{today_worknum} 个</p>
# <p>作品增长率（较昨日）：{work_rate} %</p>

# <h2 style="font-size: 1.4em; font-weight: normal;">
#   ============ ~论坛情况~ ============
# </h2>
# <p>今日发布帖子：{today_postnum - yesterday_postnum} 个</p>
# <p>帖子整体增长率（较昨日）：{post_rate} %</p>
# <p>今日回复帖子总数：{today_replynum - yesterday_replynum} 个</p>
# <p>回复整体增长率（较昨日）：{reply_rate} %</p>

# <h2 style="font-size: 1.4em; font-weight: normal;">
#   ============ ~首页情况~ ============
# </h2>
# """

# work_no = 0

# for work in items:
#     work_no = work_no + 1
#     html_novel += f"""
# <h3 style="font-size: 1.2em; font-weight: normal;">
#   《{work["work_name"]}》
# </h3>
# <p>作品ID：{work["work_id"]}</p>
# <p>开发者：{work["nickname"]}</p>
# <p>总浏览数：{work["views_count"]}</p>
# <p>总点赞：{work["likes_count"]}</p>
# <p>排行：{work_no} 名</p>
# <br/>
# """

# html_novel += f"""
# <h2 style="font-size: 1.4em; font-weight: normal;">
#   ============ 统计完成 ============
# </h2>
# <p>Action触发时间戳：{time.time()}</p>
# <p>若有统计问题，可在黎星羽的作品/本日统计帖子下反馈</p>
# <p>已在论坛完成发帖，请在灌水池塘内寻找最新帖子</p>
# <p>此Bot由HachimLab创造，欢迎查看我们的官网：Https://Hachimlab.top/</p>
# <p>HachimLab是一个公益的编程猫第三方脚本制作工作室，欢迎各位的加入！</p>
# <p>BY HachimLab</p>
# """

# response = PostAPI(
#     Path="/web/fanfic/section",
#     PostData={
#         "title": datetime.now().strftime("%m%d"),
#         "draft": html_novel,
#         "draft_words_num": 0,
#         "fanfic_id": 192733,
#     },
#     Token=token,
# )

# t_id = json.loads(response.text).get("id", 0)

# PutAPI(Path=f"/web/fanfic/section/{t_id}/publish", Token=token)

# print(f"完成小说上传任务，章节ID：{t_id}")
