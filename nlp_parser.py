"""
自然语言解析模块 - 课表智能助手
"""
import re
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
    解析用户查询
    
    Args:
        query: 用户输入的查询文本
        teachers: 教师列表
    
    Returns:
        解析结果字典
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
    根据解析结果生成回复
    
    Args:
        result: parse_query 的返回结果
        schedule: 课表数据
    
    Returns:
        回复文本
    """
    intent = result['intent']
    
    if intent == 'help':
        return """您好！我是课表智能助手，可以帮您查询课表信息。

我可以回答以下问题：
- 某位老师的课表（如：张三老师的课表）
- 某一天的课程（如：明天有什么课）
- 星期几的课程（如：周三有什么课）
- 第几节的课程（如：第 3 节是谁的课）
- 某门课的信息（如：高等数学在哪里上课）

请直接告诉我您想查询的内容！"""
    
    if not schedule:
        return "暂无课表数据，请先上传课表文件。"
    
    if intent == 'query_teacher' and result['teacher']:
        teacher = result['teacher']
        teacher_courses = [c for c in schedule if c['teacher'] == teacher]
        if teacher_courses:
            courses_info = '\n'.join([
                f"- {c['course']}：星期{['一','二','三','四','五','六','日'][c['weekday']]} 第{c['start_lesson']}-{c['end_lesson']}节 {c['location']}"
                for c in teacher_courses[:5]
            ])
            return f"{teacher}老师的课程：\n{courses_info}"
        else:
            return f"未找到{teacher}老师的课程信息。"
    
    if intent == 'query_date' and result['date']:
        date_str = result['date']
        date = datetime.strptime(date_str, '%Y-%m-%d')
        week = (date - SEMESTER_START).days // 7 + 1
        weekday = date.weekday()
        
        day_courses = [
            c for c in schedule 
            if c['weekday'] == weekday and week in c['weeks']
        ]
        
        if day_courses:
            courses_info = '\n'.join([
                f"- {c['teacher']} - {c['course']} 第{c['start_lesson']}-{c['end_lesson']}节 {c['location']}"
                for c in day_courses
            ])
            return f"{date_str}（第{week}周，星期{['一','二','三','四','五','六','日'][weekday]}）的课程：\n{courses_info}"
        else:
            return f"{date_str} 暂无课程安排。"
    
    if intent == 'query_weekday' and result['weekday'] is not None:
        weekday = result['weekday']
        weekday_str = ['一','二','三','四','五','六','日'][weekday]
        
        day_courses = [c for c in schedule if c['weekday'] == weekday]
        
        if day_courses:
            courses_info = '\n'.join([
                f"- {c['teacher']} - {c['course']} 第{c['start_lesson']}-{c['end_lesson']}节 {c['location']}"
                for c in day_courses[:10]
            ])
            return f"星期{weekday_str}的课程：\n{courses_info}"
        else:
            return f"星期{weekday_str} 暂无课程安排。"
    
    if intent == 'query_schedule':
        total_courses = len(schedule)
        total_teachers = len(set(c['teacher'] for c in schedule))
        return f"共有 {total_courses} 门课程，{total_teachers} 位老师。请问您想查询哪位老师的课表？"
    
    return "我没太理解您的问题，请换种方式提问。您可以问我：\n- 张三老师的课表\n- 明天有什么课\n- 周三的课程安排"

def get_suggestion(result):
    """获取建议的后续问题"""
    suggestions = [
        "查看课表",
        "某位老师的课表",
        "今天的课程",
        "帮助"
    ]
    return suggestions
