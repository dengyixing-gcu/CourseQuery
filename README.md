# 课表智能助手 📚

一个智能课表查询助手，支持自然语言对话查询课表信息。

## ✨ 功能特性

- 🤖 **智能对话** - 使用自然语言查询课表
- 📅 **多种查询** - 按老师、日期、星期查询
- 📤 **文件上传** - 支持 Excel 课表文件上传
- 💬 **实时对话** - 流畅的聊天界面体验
- ☁️ **云端部署** - 支持 Render 等平台部署

## 🚀 快速开始

### 本地运行

```bash
# 克隆项目
git clone https://github.com/YOUR_USERNAME/teacher-schedule-assistant.git
cd teacher-schedule-assistant

# 安装依赖
pip install -r requirements.txt

# 运行应用
python app.py

# 或使用 gunicorn
gunicorn app:app --bind 0.0.0.0:5000
```

访问 http://localhost:5000

### Render 部署

1. **Fork 本项目** 到您的 GitHub 账号

2. **在 Render 创建新服务**
   - 访问 https://render.com
   - 点击 "New +" → "Web Service"
   - 连接您的 GitHub 仓库
   - 使用以下配置：
     - **Name**: teacher-schedule-assistant
     - **Environment**: Python
     - **Region**: Singapore (新加坡)
     - **Branch**: main
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`

3. **添加环境变量**
   - `PYTHON_VERSION`: 3.11.0
   - `FLASK_ENV`: production

4. **点击 "Create Web Service"**

5. **等待部署完成**
   - Render 会自动构建并部署
   - 部署成功后会提供一个 https:// 开头的域名

6. **上传课表文件**
   - 访问部署后的网址
   - 在首页上传您的课表 Excel 文件
   - 然后点击 "开始对话" 使用智能查询

## 📋 课表文件格式

支持 Excel 格式（.xlsx 或 .xls），包含以下列：

| 列名 | 说明 | 示例 |
|------|------|------|
| 教师 | 教师姓名 | 张三 |
| 课程名称 | 课程名称 | 高等数学 |
| 时间 | 上课时间 | 星期一第 1-2 节{1-16 周} |
| 地点 | 上课地点 | 教学楼 A101 |
| 班级组成 | 班级信息 | 计算机 2101 班 |

## 🤖 API 接口

### POST /api/chat

聊天接口

```json
{
  "query": "张三老师明天的课"
}
```

响应：
```json
{
  "response": "张三老师的课程...",
  "suggestions": ["查看课表", "今天有什么课"],
  "intent": "query_teacher",
  "data": {...}
}
```

### POST /api/upload

上传课表文件

```
Content-Type: multipart/form-data
file: [Excel 文件]
```

### GET /api/schedule

获取所有课表数据

### GET /api/teachers

获取所有教师列表

### GET /health

健康检查（用于 Render 监控）

## 📁 项目结构

```
teacher-schedule-assistant/
├── app.py                 # Flask 主应用
├── nlp_parser.py          # NLP 解析模块
├── requirements.txt       # Python 依赖
├── render.yaml           # Render 配置
├── README.md             # 项目说明
├── templates/            # HTML 模板
│   ├── index.html        # 首页（上传）
│   └── chat.html         # 聊天页面
└── data/                 # 数据目录
    └── 教师课表.xlsx      # 课表文件
```

## 🌐 在线演示

访问部署在 Render 的演示版本：
[https://YOUR_APP.onrender.com](https://YOUR_APP.onrender.com)

## 🛠️ 技术栈

- **后端**: Flask 3.0
- **前端**: HTML5 + CSS3 + JavaScript
- **数据处理**: Pandas
- **部署**: Render
- **Python**: 3.11

## 📝 更新日志

### v1.0.0 (2026-03-23)
- ✨ 初始版本发布
- 🤖 智能对话查询
- 📤 Excel 文件上传
- ☁️ Render 部署支持

## 📄 许可证

MIT License

## 👥 作者

您的名字

## 🙏 致谢

感谢 Render 提供的免费托管服务！

---

**注意**: 首次访问 Render 部署的应用可能需要 30-50 秒的冷启动时间。
