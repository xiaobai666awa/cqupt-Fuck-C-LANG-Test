import requests
import json
import time
from openai import OpenAI
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
# def get_response(url, data):
#     response = requests.post(url, json=data)
#     response_dict = json.loads(response.text)
#     response_content = response_dict["response"]
#     return response_content
def post_answer(session_id, ans, global_id,sid):
    # 构建数据格式
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
    # 发送请求
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
# 登录信息
login_url = 'https://cprg.cqupt.edu.cn/train/api/student/auth'
login_data = {
    'code': '2024212341',  # 替换为你的用户名
    'pwd': '123456'  # 替换为你的密码
}
def get_score(session_id, sid):
    url=f'https://cprg.cqupt.edu.cn/train/api/student/score-result/{session_id}?sid={sid}'
    response = requests.get(url)
    if response.status_code == 200:
        print(response.text)
    else:
        print("error to get score")
# 发起登录请求
def shuati(sid):
    try:
        if(1):
            choose_q_url = f'https://cprg.cqupt.edu.cn/train/api/student/choose-q?sid={sid}'
            params = [{"qBaseType": 4, "number": 1, "level": 0, "tagId": 0}]  # 需要传递的参数

            # 发起获取题目的请求
            q_response = requests.post(choose_q_url, json=params)  # 使用POST方法并传递参数
            q_response.raise_for_status()  # 检查请求是否成功

            # 处理题目数据
            questions_data = q_response.json()
            session_id = questions_data.get('sessionId')
            if session_id:
                print(f"获取到 sessionId: {session_id}")

                # 根据 sessionId 获取题目详细信息
                record_url = f'https://cprg.cqupt.edu.cn/train/api/student/record/{session_id}?sid={sid}'
                record_response = requests.get(record_url)
                record_response.raise_for_status()  # 检查请求是否成功

                # 处理题目详细信息

                paper_data = record_response.json()
                global_id = paper_data.get('answerPaper').get('q4')[0].get('globalId')
                questions = paper_data.get('paper', {}).get('questions', [])

                # 直接提取第一道题的内容
                if questions:
                    question_content = questions[0].get('content')  # 提取第一道题的内容
                    print(f"题目内容: {question_content}")
                    # data = {
                    #     "model": "qwen14ba",
                    #     "prompt": "注意！请根据以下内容提供只包含c语言程序的代码，绝对不要出现注释和解释，绝对严禁出现markdown语法，之要代码纯文本，且不要出现```c或```\n"+question_content,
                    #     "stream": False
                    # }
                    # ans = get_response(url_generate, data)
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
        else:
            print("未获取到 SID，登录失败。")
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")


login_response = requests.post(login_url, json=login_data)
login_response.raise_for_status()  # 检查请求是否成功
sid = login_response.json().get('sid')
if sid:
    print(f"登录成功，SID: {sid}")
    for i in range(0,20):
        shuati(sid)