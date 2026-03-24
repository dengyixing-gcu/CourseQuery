"""
自然语言解析模块 - 课表智能助手
"""
import re
import json
from datetime import datetime, timedelta
from openai import OpenAI

client = OpenAI(
    api_key="sk-sp-2d79aaad48c84a218ae03d48c5bb5ae2",
    base_url="https://coding.dashscope.aliyuncs.com/v1"
)

SEMESTER_START = datetime(2026, 3, 2)
WEEKDAY_MAP = {
    '周一': 0, '星期一': 0, '礼拜一': 0,
    '周二': 1, '星期二': 1, '礼拜二': 1,
    '周三': 2, '星期三': 2, '礼拜三': 2,
    '周四': 3, '星期四': 3, '礼拜四': 3,
    '周五': 4, '星期五': 4, '礼拜五': 4,
    '周六': 5, '星期六': 5, '礼拜六': 5,
    '周日': 6, '星期日': 6, '星期天': 6, '礼拜天': 6,
}

def parse_query(query, teachers=None):
    """
    解析用户查询 - 使用千问大模型
    """
    result = {
        'intent': 'unknown',
        'teacher': None,
        'date': None,
        'weekday': None,
        'lesson': None,
        'original_query': query
    }
    
    query = query.strip()
    
    system_prompt = """你是一个课表查询助手，请分析用户输入的意图，返回 JSON 格式：
{
    "intent": "query_teacher|query_date|query_weekday|query_schedule|query_info|help|unknown",
    "teacher": "教师姓名或 null",
    "date": "YYYY-MM-DD 格式或 null", 
    "weekday": 0-6 数字或 null (0=周一，6=周日),
    "lesson": 节次数字或 null
}

今天是 2026 年 3 月 24 日，星期二。学期从 2026 年 3 月 2 日开始。"""

    try:
        response = client.chat.completions.create(
            model="qwen-coding-plan",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"教师列表：{teachers}\n用户查询：{query}"}
            ],
            temperature=0.1
        )
        llm_result = json.loads(response.choices[0].message.content)
        result.update(llm_result)
    except Exception as e:
        pass
    
    return result

def extract_date(text):
    """从文本中提取日期"""
    today = datetime.now()
    
    # 模式 1: 具体日期 2026-03-20 或 2026 年 3 月 20 日
    match = re.search(r'(\d{4})[\-/.年](\d{1,2})[\-/.月](\d{1,2})[日号]?', text)
    if match:
        year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
        try:
            return datetime(year, month, day).strftime('%Y-%m-%d')
        except:
            pass
    
    # 模式 2: 3 月 20 日、3.20、03-20
    match = re.search(r'(\d{1,2})[\.月\-](\d{1,2})[日号]?', text)
    if match:
        month, day = int(match.group(1)), int(match.group(2))
        year = today.year
        try:
            return datetime(year, month, day).strftime('%Y-%m-%d')
        except:
            pass
    
    # 模式 3: 今天、明天、后天
    if '今天' in text or '今日' in text:
        return today.strftime('%Y-%m-%d')
    elif '明天' in text or '明日' in text:
        return (today + timedelta(days=1)).strftime('%Y-%m-%d')
    elif '后天' in text:
        return (today + timedelta(days=2)).strftime('%Y-%m-%d')
    
    return None

def extract_weekday(text):
    """从文本中提取星期"""
    for weekday_str, weekday_num in WEEKDAY_MAP.items():
        if weekday_str in text:
            return weekday_num
    return None

def extract_lesson(text):
    """从文本中提取节次"""
    match = re.search(r'第 (\d+) 节', text)
    if match:
        return int(match.group(1))
    
    match = re.search(r'(\d+) 节', text)
    if match:
        return int(match.group(1))
    
    return None

def generate_response(result, schedule):
    """
    根据解析结果生成回复 - 使用千问大模型
    """
    intent = result['intent']
    query = result.get('original_query', '')
    
    if not schedule:
        return "暂无课表数据，请先上传课表文件。"
    
    schedule_context = "\n".join([
        f"{c['teacher']} - {c['course']} - 星期{['一','二','三','四','五','六','日'][c['weekday']]} 第{c['start_lesson']}-{c['end_lesson']}节 - {c['location']}"
        for c in schedule[:50]
    ])
    
    system_prompt = f"""你是课表智能助手，根据以下课表数据回答用户问题。

课表数据：
{schedule_context}

请简洁、友好地回答用户问题。"""

    try:
        response = client.chat.completions.create(
            model="qwen-coding-plan",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"抱歉，处理查询时出错：{str(e)}"

def get_suggestion(result):
    """获取建议的后续问题"""
    suggestions = [
        "查看课表",
        "某位老师的课表",
        "今天的课程",
        "帮助"
    ]
    return suggestions
