# -*- coding: utf-8 -*-
import os
import sys
import requests
import json
import re

# 启动agent服务 sh scripts/run_assistant_server.sh
# server上需要设置dashscope api key 的环境变量
# export DASHSCOPE_API_KEY=

url = 'http://localhost:31512/v1/assistants/lite'

headers = {"Content-Type": "application/json"}

# 第一步：生成绘本

data = {
    "llm_config": {
        "model": "qwen-max",
        "model_server": "dashscope",
        "api_key": "DASHSCOPE_API_KEY"
    },
    "agent_config": {
        "name": "test",
        "description": "test assistant",
        "instruction": """你需要根据需求生成绘本故事，这一步你不需要使用工具, 需求字段有年龄段，内容类型, 角色，故事大纲， 故事寓意（如果提供了故事寓意，严格使用提供的字符，不必进行更改，没有则根据故事内容进行生成，不超过10个字），避免出现的内容，多少个章节，
                        检索用户传入的age_group字段，符合“0-3”， “3-4”， “5-6”， “6+”字段中的一个，决定故事的年龄范围
                        检索用户传入的content_type字段，符合“常识认知”， “社交礼仪”，“心智解读”， “趣味故事”字段中的一个，决定故事的主题
                        检索用户传入的avoid_content字段，来决定故事避免出现的内容，比如血腥，暴力
                        检索用户传入的pages字段，来决定故事有多少个章节
                        检索用户传入的story_morale字段，来决定故事寓意，如果没有，请根据故事类型自动输入生成故事寓意
                        生成的绘本故事需要按照严格按照下面的json格式返回
                   {
                        "story_name": "", # 故事的名字
                        "story_moral": "" , # 故事寓意，
                        "contents": [
                            {
                            "page_num": "", # 第几章故事， 例如：1
                            "title": "",  # 每一章故事的标题
                            "content": "",  # 每一章故事的内容
                            }
                        ]
                   }"""
    },
    'messages': [
        {
            "role": "user",
            "content": """
            {
              "age_group": "3-4",
              "story_type": "趣味故事",
              "role": "小松鼠",
              "summary": "小松鼠躲迷藏",
              "story_moral": "",
              "avoid_content": "",
              "pages": 3
            }
        """
        }
    ],
    "stream": False,
    "uuid_str": "test"
}

# response = requests.post(url, headers=headers, data=json.dumps(data))
# text = json.loads(response.text)
# story_text = text['output']['response']
# print(story_text)
#
# pattern = r'(?<=```json\n).*?(?=\n```)'
# matches = re.findall(pattern, story_text, flags=re.DOTALL)[0]
# print(matches)

# 第一步模拟返回
api_input = {
    "story_name": "机器人的都市冒险：纽约小狗奇遇记",
    "story_moral": "友谊与探索",
    "image_style": "动漫",
    "contents": [
        {
            "page_num": "1",
            "title": "新朋友的相遇",
            "content": "在一个阳光明媚的早晨，繁忙的纽约街头出现了一个闪亮的小机器人，名叫罗比。它有着圆滚滚的身体和好奇的眼睛，正漫步在中央公园的绿地上。突然，一只活泼的小狗，汪汪，追着飞舞的蝴蝶跑来，不小心撞倒了罗比。汪汪连忙用小鼻子碰碰罗比，仿佛在道歉。罗比眨眨眼，发出了友好的‘嘀嘀’声，它们就这样成了好朋友。"
        },
        {
            "page_num": "2",
            "title": "都市寻宝之旅",
            "content": "罗比告诉汪汪它在寻找失落的城市之心——一枚传说中的友谊徽章，能带给城市无限温暖。汪汪兴奋地摇着尾巴，决定帮助罗比。它们穿梭在高楼大厦间，经过了闪烁的霓虹灯和喧闹的时报广场。在一家古老的玩具店前，它们发现了一条线索，是一张藏宝图！随着地图的指引，它们的探险充满了欢笑和惊喜。"
        },
        {
            "page_num": "3",
            "title": "找到城市之心",
            "content": "最终，罗比和汪汪来到了布鲁克林大桥下的一片秘密花园。在那里，它们没有找到实体的徽章，却遇到了各种各样的动物朋友们，大家围在一起分享快乐和故事。罗比恍然大悟，真正的‘城市之心’就是这份团结与友爱。夕阳西下，罗比和汪汪依偎着，望着灯火辉煌的城市，心中充满了温暖。它们明白了，最好的宝藏是彼此之间的友情和共同的回忆。"
        }
    ]
}

input_contents = api_input['contents']
messages = []

for i in range(len(api_input['contents'])):
    content = api_input['contents'][i]["content"]

    # 第二步
    # 接收用户输入的画风
    style_input = content +  "image_style: 动漫"
    mes_input = {'role': 'user', 'content': style_input}
    messages.append(mes_input)
    data = {
        "llm_config": {
            "model": "qwen-max",
            "model_server": "dashscope",
            "api_key": "sk-c19dd46605d04b7ba0976b60d9ea6f9c"
        },
        "agent_config": {
            "name": "test",
            "description": "test assistant",
            "tools": ["image_gen"],
            "instruction": """根据用户提供的绘本内容，检测image_style字段符合“简约” “治愈”，“动漫”字段中的一个，必须使用此风格为上述绘本故事生成图画，
            不要有多余的解释内容内容,务必只返回![]()这样格式的URL结果
                    """   
        },
        'messages': messages,
        "stream": False,
        "uuid_str": "test"
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    text = json.loads(response.text)
    image_response = text['output']['response']
    print("结果：\n")
    print(image_response)
    image_out = {"role": "system",'content': image_response}
    messages.append(image_out)
    pattern = r'(?<=Answer:)!\[.*?\]\(((?:https?://)?[^\s]+?)(?: ".*?")?\)'
    matches = re.findall(pattern, image_response)
    
    
    api_input['contents'][i]["image"] = matches[0]

print("最终结果：\n")
print(str(api_input))
