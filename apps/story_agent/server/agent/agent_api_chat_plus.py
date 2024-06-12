# -*- coding: utf-8 -*-
import os
import sys
import requests
import json
import re

url = 'http://localhost:31512/v1/assistants/lite'

headers = {"Content-Type": "application/json"}

# 第一步：生成绘本

dic_child_age = {
    "0-3": "1. 刚刚学会说话，只能理解很简单的句子和很简单的故事情节。\n2. 故事绘本每个章节最多只能有一两句话。\n3. 绘本故事要和孩子生活贴近，可以简单的介绍一些很简单的生活知识。",
    "3-6": "1. 基本可以理解一些简单的语言，能够进行一些简单的交流沟通。\n2. 故事绘本每个章节可以适当两三句话。\n3. 开始进入幼儿园正式学习的阶段，所以多给孩子制造说的情景、机会和话题，并培养孩子的行为习惯、人身安全、入园准备这方面的知识",
    "6+": "1. 已经能够正常的交流沟通，可以理解一些比较复杂的故事绘本。\n2. 可以在故事内容中，适当增加一些篇幅和故事深度。\n3. 参照主题要求，可以仿照巧虎故事，中国传统故事、安徒生童话、格林童话等故事形式。"
}

dic_story_type = {
    "常识认知": "旨在帮助儿童了解周围世界的基本规则和事实，如颜色、形状、数目、以及日常生活中的物品和现象。常识认知故事绘本通常以互动和探索为中心，通过色彩鲜艳、易于理解的插图和简单的叙述来提升儿童对世界的认知。",
    "社交礼仪": "致力于教导儿童基本的社交技能和礼貌行为，如问候、分享、感谢、道歉等。这类绘本故事通过生动的场景和角色模仿，使孩子能够在安全的环境中学习和练习正确的社交行为。",
    "心智解读": "集中于培养儿童的情感认知与心理理解能力，教会他们如何识别自己和他人的情绪，以及如何有效地表达和处理感情。绘本中的角色常常置身于各种情绪场景中，引导孩子理解和操控内心世界。",
    "趣味": "包含各种有趣、有吸引力的故事，旨在激发儿童的想象力和创造力，同时提供愉悦的阅读体验。这些绘本充满了幽默、创意和惊喜元素，可以促进儿童语言表达和思维发展，同时保持阅读的乐趣。",
    "其他": "可以更发散的故事生成，例如传统文化、艺术、音乐或特殊主题等，这些内容介绍通常旨在丰富儿童的视野，提供更多元化的知识和体验。",
}

age_group = "0-3"
content_type = "常识认知"
avoid_content = "暴力，色情，打架"
pages = "3"
story_morale = "学习自己上厕所"
summary = "自己上厕所"
role = "里里"

story_type_intro = dic_story_type[content_type]
child_age_intro = dic_child_age[age_group]

instruction = f"""<|im_start|>system
你是一个专业的故事绘本创作者，专门给儿童创作他们可以理解的故事

## 故事绘本年龄
绘本是面向{age_group}岁小朋友的，以下是每个年龄段小朋友能理解的。下面是该年龄段小朋友的能力范围：

{child_age_intro}

## 故事绘本创作注意事项
1. 文字风格：推动剧情发展的文字应多使用陈述句，句尾可多用“呢”、“啦”、“呀”、“呦”、“哈”等字
2. 简单明了：故事的主题和情节要简单明了，语言要生动有趣。
3. 有教育意义：优秀的睡前故事应该有一定的教育意义，能够帮助孩子们学习正确的价值观和行为习惯。
4. 富有想象力：睡前故事要富有想象力和趣味性，抓住孩子们的注意力，让孩子们产生共鸣和感受。
5. 温馨愉悦：睡前故事最好给人一种轻松、温馨、愉悦的感觉，让孩子们感觉到被爱和关怀。
6. 实际生活相贴近：好的睡前故事应该与孩子们的实际生活相贴近，引发他们的思考和共鸣
7. 避免出现以下内容: {avoid_content}

## 故事绘本主题
你需要创作的绘本故事类型是{content_type}

{content_type}要求：{story_type_intro}
故事主题：《{summary}》
主角名字：{role}
"""

messages = []
input_story = {
            "role": "user",
            "content": f"""
            生成一个对应上述主题的故事大纲，要做一个{pages}页的故事绘本，输出一个有效的JSON array of objects，参考格式
[{{
    "故事标题":"xxx",
    "故事寓意": "xxx",
    "故事大纲":[{{"章节标题":"xxx", "章节梗概": "xxx"}}, {{"章节标题":"xxx", "章节梗概": "xxx"}},],
}}]

The JSON object:```json"""
        }
messages.append(input_story)

data = {
    "llm_config": {
        "model": "qwen-max",
        "model_server": "dashscope",
        "api_key": "sk-c19dd46605d04b7ba0976b60d9ea6f9c"
    },
    "agent_config": {
        "name": "test",
        "description": "test assistant",
        "instruction": instruction
    },
    'messages': messages,
    "stream": False,
    "uuid_str": "test"
}

response = requests.post(url, headers=headers, data=json.dumps(data))
text = json.loads(response.text)
story_text = text['output']['response']
print(story_text)

# 第二步
# 生成故事的画面描述

output_story = {
    "role": "assistant",
    "content": story_text
}
messages.append(output_story)
query_content = {
    "role": "user",
    "content": f"""
根据上面故事大纲生成具体的故事内容，要做一个{pages}页的故事绘本，输出一个有效的JSON array of objects，参考格式
{{
    "1":{{"画面描述": "xx", "故事内容": "xx"}},
    "2":{{"画面描述": "xx", "故事内容": "xx"}},
    "3":{{"画面描述": "xx", "故事内容": "xx"}},
    xxx
}}

The JSON object:```json
"""
}
messages.append(query_content)

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
            "instruction":instruction
        },
        'messages': messages,
        "stream": False,
        "uuid_str": "test"
    }
response = requests.post(url, headers=headers, data=json.dumps(data))
text = json.loads(response.text)
api_input = text['output']['response']
print("结果：\n")
print(api_input)


# 第三步
# 单独生成每页的图片 这里假设api_input返回的是如下格式
# {{
#     "1":{{"画面描述": "xx", "故事内容": "xx"}},
#     "2":{{"画面描述": "xx", "故事内容": "xx"}},
#     "3":{{"画面描述": "xx", "故事内容": "xx"}},
#     xxx
# }}

# 示例
api_input = {
    "1": {
        "画面描述": "温暖的卧室里，阳光洒在地面上，里里坐在小桌旁，旁边放着空空的牛奶杯，表情显得有些急迫。",
        "故事内容": "早晨，太阳公公笑眯眯，里里喝了好多牛奶，突然觉得肚子鼓鼓的，想要上厕所呢。妈妈笑着说：'里里长大了，要学会自己去厕所哦。'"
    },
    "2": {
        "画面描述": "客厅里色彩鲜艳，墙上贴着卡通动物图案，一条由彩色脚印贴纸组成的路径从餐桌延伸至厕所门，里里正沿着脚印前进，好奇又兴奋。",
        "故事内容": "里里光着小脚丫，沿着彩色的脚印贴纸，穿过客厅，绕过沙发，咦？那里有个门，门上画着个小马桶，是厕所呀！里里勇敢地推开门进去啦。"
    },
    "3": {
        "画面描述": "厕所内部装饰着可爱的海洋生物壁画，小马桶适合孩子的尺寸，里里坐在马桶上，脸上洋溢着成就感，洗手池边挂着卡通鱼儿的手巾。",
        "故事内容": "里里爬上小马桶，坐得稳稳的，哗啦啦，解决了问题。洗手时间到，里里记得用泡沫洗手液，搓搓小手心，再搓搓小手背，冲干净，擦干手。里里对着镜子笑哈哈，'我会自己上厕所啦，真棒呀！'"
    }
}

messages = []

for i in range(len(api_input)):
    content = api_input[str(i+1)]

    # 第二步
    # 接收用户输入的画风
    style_input ="请根据接下来的描述生成图片：\n"+content['画面描述']+' ' + content['故事内容']
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
            "instruction": """根据用户提供的描述来生成图像，，
            结果请严格按照![]()格式返回,除了符合下面格式的内容外不要有其他的输出
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
    pattern = r'!\[.*?\]\(((?:https?://)?[^\s]+?)(?: ".*?")?\)'
    matches = re.findall(pattern, image_response)
    
    
    api_input[str(i+1)]["image"] = matches[-1]

print("最终结果：\n")
print(str(api_input))