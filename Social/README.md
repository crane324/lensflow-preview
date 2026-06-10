# Social - 虚拟AI相亲系统

> AI 数字人驱动的虚拟约会社交匹配平台

## 快速启动

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置 API Key
编辑 `backend/config.py`，将 `sk-your-api-key-here` 替换为你的 DeepSeek API Key。
或设置环境变量：
```bash
export OPENAI_API_KEY=sk-your-key
```

### 3. 启动
```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

### 4. 打开浏览器
```
http://localhost:8000
```

## 前端页面

| 页面 | 路径 | 说明 |
|------|------|------|
| 首页 | `/index.html` | 主页面，Hero区+心动信号站+放映室 |
| 数字人创建 | `/workshop.html` | AI分身工坊，上传聊天/填写问卷生成数字人 |
| 场景选择 | `/scene.html` | 四大约会场景（校园/职场/约会/风暴） |
| 虚拟约会 | `/dating.html?scene=campus` | 带预算系统的AI对话约会 |
| 匹配报告 | `/report.html` | 好感度评分+雷达图+对话亮点 |
| 匹配大厅 | `/match.html` | 双人相亲角独立页面 |

## 后端 API

| 接口 | 说明 |
|------|------|
| `GET /api/health` | 健康检查 |
| `POST /api/persona/analyze-chat` | 聊天记录人格分析 |
| `POST /api/persona/upload-file` | 上传聊天文件 |
| `POST /api/wechat/auto-import` | 微信聊天自动导入 |
| `POST /api/persona/analyze-photo` | 照片人格分析 |
| `GET /api/persona/questionnaire` | 获取问卷 |
| `POST /api/persona/submit-answers` | 提交问卷 |
| `POST /api/persona/generate` | 生成数字人档案 |

## 技术栈

- 前端：HTML + CSS + JS（Tailwind CSS CDN）
- 后端：Python FastAPI
- AI：DeepSeek API（兼容 OpenAI 格式）
