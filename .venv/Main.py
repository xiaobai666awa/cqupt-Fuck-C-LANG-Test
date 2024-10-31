import requests
import json
import time
from openai import OpenAI
from requests import session


def login():
    login_url = 'https://cprg.cqupt.edu.cn/train/api/student/auth'
    login_data = {
        'code': '2024212338',  # 替换为你的用户名
        'pwd': '123456'  # 替换为你的密码
    }
    login_response = requests.post(login_url, json=login_data)
    login_response.raise_for_status()  # 检查请求是否成功
    sid = login_response.json().get('sid')
    return sid
def openaikey(question_content):
    client = OpenAI(
        base_url='https://xiaoai.plus/v1',
        # sk-xxx替换为自己的key
        api_key='sk-4TJY1BgR3D53lXc1CdA9892708Cd41Bb80D1A7814014A321'
    )
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "你是一个用于写代码的大模型机器人，你不能以markdown形式输出代码你只能以文本形式输出代码，你输出的代码不能以```c和```包围"},
            {"role": "user", "content": "注意！请根据以下内容提供只包含c语言程序的代码，绝对不要出现注释和解释，绝对严禁以markdown形式输出,只要代码纯文本，且绝对不要出现(```c或```)!\n"+question_content+"\n只要代码纯文本，且绝对不要出现(```c或```)!"}
        ]
    )
    return completion.choices[0].message.content
def post_answer(session_id, ans, global_id,sid):
    data2 = {
        "sessionId": session_id,
        "answerPaper": {
            "q0": [],
            "q1": [],
            "q2": [],
            "q3": [],
            "q4": [
                {
                    "answer": ans,
                    "globalId": global_id,
                    "qType": 5
                }
            ],
            "q5": []
        }
    }
    url = f'https://cprg.cqupt.edu.cn/train/api/student/post-answer?sid={sid}'
    response = requests.post(url, json=data2)
    return response.status_code
def submit_answer(session_id,sid):
    url=f'https://cprg.cqupt.edu.cn/train/api/student/submit?sid={sid}&sessionId={session_id}'
    response = requests.get(url)
    if response.status_code == 200:
        print("提交结果:", response.text)
        return True
    else:
        print("提交失败:", response.status_code, response.text)
def get_score(session_id, sid):
    url=f'https://cprg.cqupt.edu.cn/train/api/student/score-result/{session_id}?sid={sid}'
    response = requests.get(url)
    if response.status_code == 200:
        print(response.text)
    else:
        print("error to get score")
def get_sessionid(sid):
    choose_q_url = f'https://cprg.cqupt.edu.cn/train/api/student/choose-q?sid={sid}'
    params = [{"qBaseType": 4, "number": 1, "level": 0, "tagId": 0}]  # 需要传递的参数
    q_response = requests.post(choose_q_url, json=params)  # 使用POST方法并传递参数
    q_response.raise_for_status()  # 检查请求是否成功
    questions_data = q_response.json()
    session_id = questions_data.get('sessionId')
    return session_id
def getquestions(session_id,sid):
    record_url = f'https://cprg.cqupt.edu.cn/train/api/student/record/{session_id}?sid={sid}'
    record_response = requests.get(record_url)
    record_response.raise_for_status()
    paper_data = record_response.json()
    global_id = paper_data.get('answerPaper').get('q4')[0].get('globalId')
    questions = paper_data.get('paper', {}).get('questions', [])
    return questions, global_id
def shuati(sid):
    try:
            session_id = get_sessionid(sid)
            if session_id:
                print(f"获取到 sessionId: {session_id}")
                session_id = get_sessionid(sid)
                if getquestions(session_id,sid):
                    questions,global_id = getquestions(session_id,sid)
                    question_content = questions[0].get('content')
                    print(f"题目内容: {question_content}")
                    ans = openaikey(question_content)
                    print(ans)
                    if (post_answer(session_id, ans, global_id, sid) == 200):
                        if (submit_answer(session_id, sid)):
                            time.sleep(2)
                            get_score(session_id, sid)
                    else:
                        print("答案提交失败")
                else:
                    print("未获取到题目。")
            else:
                print("未获取到 sessionId。")
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
if login():
    sid=login()
    print(f"登录成功，SID: {sid}")
    for i in range(0, 100):
        shuati(sid)
