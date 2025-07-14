# 🚀 Vercel部署指南

## 方法1: 直接部署Streamlit应用

### 1. 准备项目
确保你的项目已经推送到GitHub。

### 2. 登录Vercel
- 访问 [vercel.com](https://vercel.com)
- 使用GitHub账号登录

### 3. 导入项目
- 点击 "New Project"
- 选择你的GitHub仓库
- 点击 "Import"

### 4. 配置部署
Vercel会自动检测到这是一个Python项目。如果没有自动检测，请手动配置：

- **Framework Preset**: Other
- **Root Directory**: `./` (保持默认)
- **Build Command**: `pip install -r requirements.txt`
- **Install Command**: `pip install -r requirements.txt`

### 5. 环境变量设置
在Vercel控制台中设置环境变量：
```
USER_NAME=your_username
WS_URL=wss://agents.dyna.ai/openapi/v1/ws/dialog/
ROBOT_KEY=your_robot_key
ROBOT_TOKEN=your_robot_token
```

### 6. 部署
点击 "Deploy" 按钮即可。

## 方法2: 使用Vercel CLI（推荐）

### 1. 安装Vercel CLI
```bash
npm install -g vercel
```

### 2. 登录
```bash
vercel login
```

### 3. 部署
在项目根目录运行：
```bash
vercel --prod
```

### 4. 设置环境变量
```bash
vercel env add USER_NAME
vercel env add WS_URL
vercel env add ROBOT_KEY
vercel env add ROBOT_TOKEN
```

## 可能遇到的问题

### 1. 内存限制
如果应用内存使用过大，可能需要升级到Pro计划。

### 2. 冷启动时间
Serverless函数可能有冷启动延迟，首次访问可能较慢。

### 3. 文件上传限制
Vercel对上传文件大小有限制，大文件可能需要使用外部存储。

### 4. 超时限制
免费计划的函数执行时间有限制（10秒），Pro计划为60秒。

## 替代方案

如果Vercel部署遇到问题，推荐以下替代方案：

### 1. Railway.app
```bash
# 安装Railway CLI
npm install -g @railway/cli

# 登录并部署
railway login
railway init
railway up
```

### 2. Render.com
- 直接连接GitHub仓库
- 自动检测Python应用
- 支持Streamlit应用

### 3. Streamlit Cloud（最佳选择）
- 专门为Streamlit应用设计
- 免费且简单
- 访问 [share.streamlit.io](https://share.streamlit.io)

## 优化建议

### 1. 减少依赖
移除不必要的依赖包以减少部署时间。

### 2. 缓存配置
使用Streamlit的缓存功能提高性能：
```python
@st.cache_data
def expensive_function():
    # 耗时操作
    pass
```

### 3. 异步处理
对于长时间运行的任务，考虑使用后台任务队列。

## 监控和维护

### 1. 查看日志
```bash
vercel logs [deployment-url]
```

### 2. 监控性能
在Vercel控制台查看函数执行时间和内存使用情况。

### 3. 自动重部署
设置GitHub webhook实现代码推送自动部署。

---

✅ **最终建议**: 如果你的其他API都在Vercel上，建议先尝试Vercel部署。如果遇到问题，Streamlit Cloud是最佳备选方案。 