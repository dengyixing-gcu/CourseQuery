"""
课表智能助手 - Flask 应用
可部署到 Render 等云平台
"""
from flask import Flask, render_template, request, jsonify, send_from_directory
import pandas as pd
import json
import os
from datetime import datetime
from nlp_parser import parse_query, generate_response, get_suggestion

app = Flask(__name__)

# 配置
app.config['UPLOAD_FOLDER'] = 'data'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# 全局变量存储课表数据
schedule_data = None
schedule_cache_file = 'data/schedule_cache.json'

def load_schedule_from_excel(file_path):
    """从 Excel 文件加载课表数据"""
    if not os.path.exists(file_path):
        return None
    
    df = pd.read_excel(file_path)
    schedule = []
    
    for _, row in df.iterrows():
        teacher = row.get('教师', '')
        course = row.get('课程名称', '')
        times = str(row.get('时间', '')).split(';')
        locations = str(row.get('地点', '')).split(';')
        classes = str(row.get('班级组成', ''))
        
        for i, time_str in enumerate(times):
            time_slot = parse_time_slot(time_str.strip())
            if time_slot:
                location = locations[i].strip() if i < len(locations) else ''
                schedule.append({
                    'id': f"{teacher}_{course}_{i}",
                    'teacher': teacher,
                    'course': course,
                    'weekday': time_slot['weekday'],
                    'start_lesson': time_slot['start_lesson'],
                    'end_lesson': time_slot['end_lesson'],
                    'weeks': time_slot['weeks'],
                    'location': location,
                    'classes': classes
                })
    
    return schedule

def parse_time_slot(time_str):
    """解析时间槽"""
    import re
    match = re.match(r'星期.第\s*(\d+)-(\d+)\s*节\{(.+)\}', time_str)
    if match:
        weekday_char = match.group(0)[2]
        weekday_map = {'一': 0, '二': 1, '三': 2, '四': 3, '五': 4, '六': 5, '日': 6}
        weekday = weekday_map.get(weekday_char, 0)
        start_lesson = int(match.group(1))
        end_lesson = int(match.group(2))
        weeks = parse_weeks(match.group(3))
        return {
            'weekday': weekday,
            'start_lesson': start_lesson,
            'end_lesson': end_lesson,
            'weeks': weeks
        }
    return None

def parse_weeks(week_str):
    """解析周数"""
    import re
    weeks = []
    week_str = week_str.strip('{}')
    parts = week_str.split(',')
    
    for part in parts:
        part = part.strip()
        if not part:
            continue
        clean_part = part.replace('(单)', '').replace('(双)', '')
        clean_part = clean_part.strip()
        
        match = re.match(r'(\d+)\s*-\s*(\d+)\s*周', clean_part)
        if match:
            start, end = int(match.group(1)), int(match.group(2))
            week_range = list(range(start, end + 1))
            if '(单)' in part:
                week_range = [w for w in week_range if w % 2 == 1]
            elif '(双)' in part:
                week_range = [w for w in week_range if w % 2 == 0]
            weeks.extend(week_range)
        else:
            match = re.match(r'(\d+)\s*周', clean_part)
            if match:
                week = int(match.group(1))
                weeks.append(week)
    
    return sorted(set(weeks))

def get_or_load_schedule():
    """获取或加载课表数据"""
    global schedule_data
    
    if schedule_data is not None:
        return schedule_data
    
    # 尝试从缓存加载
    if os.path.exists(schedule_cache_file):
        with open(schedule_cache_file, 'r', encoding='utf-8') as f:
            schedule_data = json.load(f)
            return schedule_data
    
    # 尝试从 Excel 加载
    excel_file = os.path.join(app.config['UPLOAD_FOLDER'], '教师课表.xlsx')
    if os.path.exists(excel_file):
        schedule_data = load_schedule_from_excel(excel_file)
        if schedule_data:
            with open(schedule_cache_file, 'w', encoding='utf-8') as f:
                json.dump(schedule_data, f, ensure_ascii=False)
            return schedule_data
    
    # 返回空列表
    schedule_data = []
    return schedule_data

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/chat')
def chat():
    """聊天页面"""
    return render_template('chat.html')

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """聊天 API"""
    data = request.json
    query = data.get('query', '')
    
    if not query:
        return jsonify({'error': '请输入查询内容'}), 400
    
    schedule = get_or_load_schedule()
    teachers = sorted(set(item['teacher'] for item in schedule)) if schedule else []
    
    result = parse_query(query, teachers)
    response = generate_response(result, schedule)
    suggestions = get_suggestion(result)
    
    return jsonify({
        'response': response,
        'suggestions': suggestions,
        'intent': result['intent'],
        'data': result
    })

@app.route('/api/schedule')
def api_schedule():
    """获取所有课表数据"""
    schedule = get_or_load_schedule()
    return jsonify(schedule)

@app.route('/api/teachers')
def api_teachers():
    """获取所有教师列表"""
    schedule = get_or_load_schedule()
    teachers = sorted(set(item['teacher'] for item in schedule))
    return jsonify(teachers)

@app.route('/api/teacher/<name>')
def api_teacher_schedule(name):
    """获取特定教师的课表"""
    schedule = get_or_load_schedule()
    teacher_schedule = [item for item in schedule if item['teacher'] == name]
    return jsonify(teacher_schedule)

@app.route('/api/upload', methods=['POST'])
def api_upload():
    """上传课表 Excel 文件"""
    global schedule_data
    
    if 'file' not in request.files:
        return jsonify({'error': '没有文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '文件名为空'}), 400
    
    if not file.filename.endswith(('.xlsx', '.xls')):
        return jsonify({'error': '只支持 Excel 文件'}), 400
    
    # 保存文件
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], '教师课表.xlsx')
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    file.save(file_path)
    
    # 重新加载课表
    schedule_data = load_schedule_from_excel(file_path)
    
    # 更新缓存
    if schedule_data:
        with open(schedule_cache_file, 'w', encoding='utf-8') as f:
            json.dump(schedule_data, f, ensure_ascii=False)
    
    return jsonify({
        'success': True,
        'message': f'成功加载 {len(schedule_data)} 条课表记录'
    })

@app.route('/health')
def health():
    """健康检查端点（用于 Render）"""
    return jsonify({'status': 'healthy', 'service': 'teacher-schedule-assistant'})

if __name__ == '__main__':
    # 确保数据目录存在
    os.makedirs('data', exist_ok=True)
    
    # 启动应用
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
