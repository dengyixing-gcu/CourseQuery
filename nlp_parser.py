"""
自然语言解析模块 - 课表智能助手
"""
import os
import re
import json
from datetime import datetime, timedelta

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
    解析用户查询 - 基于规则
    """
    result = {
        'intent': 'unknown',
        'teacher': None,
        'date': None,
        'weekday': None,
        'lesson': None,
        'time_period': None,
        'original_query': query
    }
    
    query = query.strip()
    
    # 检测时间段（上午/下午/晚上）
    if any(word in query for word in ['上午', '早上', '早晨']):
        result['time_period'] = 'morning'
    elif any(word in query for word in ['下午', '午后']):
        result['time_period'] = 'afternoon'
    elif any(word in query for word in ['晚上', '晚间', '夜晚']):
        result['time_period'] = 'evening'
    
    # 检测教师名称
    if teachers:
        for teacher in teachers:
            if teacher in query:
                result['teacher'] = teacher
                result['intent'] = 'query_teacher'
                break
    
    # 检测日期
    date = extract_date(query)
    if date:
        result['date'] = date
        if result['intent'] == 'unknown':
            result['intent'] = 'query_date'
    
    # 检测星期
    weekday = extract_weekday(query)
    if weekday is not None:
        result['weekday'] = weekday
        if result['intent'] == 'unknown':
            result['intent'] = 'query_weekday'
    
    # 检测节次
    lesson = extract_lesson(query)
    if lesson:
        result['lesson'] = lesson
    
    # 检测查询类型
    if any(word in query for word in ['课表', '课程', '上课']):
        result['intent'] = 'query_schedule'
    elif any(word in query for word in ['时间', '地点', '教室']):
        result['intent'] = 'query_info'
    elif any(word in query for word in ['老师', '教师']):
        result['intent'] = 'query_teacher'
    elif any(word in query for word in ['班级', '学生']):
        result['intent'] = 'query_class'
    elif any(word in query for word in ['帮助', '帮忙', '怎么用']):
        result['intent'] = 'help'
    
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
    根据解析结果生成回复 - 基于规则
    """
    intent = result['intent']
    time_period = result.get('time_period')
    lesson = result.get('lesson')
    weekday = result.get('weekday')
    date = result.get('date')
    teacher = result.get('teacher')
    
    if not schedule:
        return "暂无课表数据，请先上传课表文件。"
    
    # 根据时间段过滤课表
    filtered_schedule = schedule
    
    if time_period == 'morning':
        filtered_schedule = [c for c in schedule if c['end_lesson'] <= 4]
    elif time_period == 'afternoon':
        filtered_schedule = [c for c in schedule if c['start_lesson'] >= 5 and c['end_lesson'] <= 8]
    elif time_period == 'evening':
        filtered_schedule = [c for c in schedule if c['start_lesson'] >= 9]
    elif lesson is not None:
        filtered_schedule = [c for c in schedule if c['start_lesson'] <= lesson <= c['end_lesson']]
    
    # 根据教师过滤
    if teacher:
        filtered_schedule = [c for c in filtered_schedule if c['teacher'] == teacher]
    
    # 根据日期/星期过滤
    if date:
        try:
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            week = (date_obj - SEMESTER_START).days // 7 + 1
            query_weekday = date_obj.weekday()
            filtered_schedule = [
                c for c in filtered_schedule 
                if c['weekday'] == query_weekday and week in c['weeks']
            ]
        except:
            pass
    elif weekday is not None:
        filtered_schedule = [c for c in filtered_schedule if c['weekday'] == weekday]
    
    # 生成回复
    time_desc = ""
    if time_period == 'morning':
        time_desc = "上午"
    elif time_period == 'afternoon':
        time_desc = "下午"
    elif time_period == 'evening':
        time_desc = "晚上"
    elif lesson:
        time_desc = f"第{lesson}节"
    
    if not filtered_schedule:
        if time_desc:
            return f"{time_desc}暂无课程安排。"
        return "暂无课程安排。"
    
    courses_info = '\n'.join([
        f"- {c['teacher']} - {c['course']} 星期{['一','二','三','四','五','六','日'][c['weekday']]} 第{c['start_lesson']}-{c['end_lesson']}节 {c['location']}"
        for c in filtered_schedule
    ])
    
    if time_desc:
        return f"{time_desc}的课程：\n{courses_info}"
    else:
        return f"共有 {len(filtered_schedule)} 门课程：\n{courses_info}"

def get_suggestion(result):
    """获取建议的后续问题"""
    suggestions = [
        "查看课表",
        "某位老师的课表",
        "今天的课程",
        "帮助"
    ]
    return suggestions
