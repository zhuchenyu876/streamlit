# 🚀 长时间运行应用部署和优化指南

## 📊 你的应用特点
- ⏱️ 单次访问可能超过几个小时
- 💾 使用sklearn等重型机器学习框架
- 🔄 数据处理和分析密集型任务
- 📈 资源消耗较大

## 🎯 最佳部署方案排序

### 1. 🏆 Streamlit Cloud（首选）
**优势：**
- ✅ 无执行时间限制
- ✅ 免费使用
- ✅ 自动处理sklearn等重型库
- ✅ 专为Streamlit设计
- ✅ 自动休眠/唤醒机制

**部署步骤：**
1. 推送到GitHub
2. 访问 [share.streamlit.io](https://share.streamlit.io)
3. 连接仓库，选择 `app.py`
4. 点击Deploy

### 2. 🥈 Railway（备选）
**优势：**
- ✅ 支持长时间运行
- ✅ 良好的资源管理
- ✅ 简单部署

**部署命令：**
```bash
npm install -g @railway/cli
railway login
railway init
railway up
```

### 3. 🥉 Render（免费备选）
**优势：**
- ✅ 免费层支持长时间运行
- ✅ 自动休眠节省资源

## 🔧 性能优化建议

### 1. 内存优化
在 `app.py` 中添加缓存：
```python
import streamlit as st

# 缓存模型加载
@st.cache_resource
def load_model():
    # 加载sklearn模型
    return model

# 缓存数据处理
@st.cache_data
def process_data(df):
    # 数据处理逻辑
    return processed_df
```

### 2. 进度显示优化
```python
# 在长时间运行的任务中添加进度条
progress_bar = st.progress(0)
status_text = st.empty()

for i in range(total_steps):
    # 执行任务
    progress_bar.progress((i + 1) / total_steps)
    status_text.text(f'处理中... {i+1}/{total_steps}')
```

### 3. 错误处理和重试机制
```python
import time
import functools

def retry_on_failure(max_retries=3, delay=1):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    time.sleep(delay * (2 ** attempt))
            return None
        return wrapper
    return decorator
```

### 4. 资源监控
```python
import psutil
import streamlit as st

# 显示资源使用情况
def show_resource_usage():
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("CPU使用率", f"{psutil.cpu_percent():.1f}%")
    with col2:
        st.metric("内存使用率", f"{psutil.virtual_memory().percent:.1f}%")
    with col3:
        st.metric("磁盘使用率", f"{psutil.disk_usage('/').percent:.1f}%")
```

## 🛡️ 部署注意事项

### 1. 环境变量配置
创建 `.env` 文件：
```env
USER_NAME=your_username
WS_URL=wss://agents.dyna.ai/openapi/v1/ws/dialog/
ROBOT_KEY=your_robot_key
ROBOT_TOKEN=your_robot_token
STREAMLIT_SERVER_HEADLESS=true
```

### 2. 依赖优化
创建 `requirements.txt` 精简版：
```txt
streamlit>=1.28.0
pandas>=1.5.0
scikit-learn>=1.3.0
python-dotenv>=0.19.0
requests>=2.28.0
plotly>=5.0.0
```

### 3. 应用配置
已创建 `.streamlit/config.toml` 优化配置。

## 🚨 常见问题解决

### 1. 内存不足
- 使用 `@st.cache_data` 缓存数据
- 分批处理大数据集
- 释放不需要的变量

### 2. 执行超时
- 只有serverless平台有限制
- Streamlit Cloud无此限制
- 使用异步处理长任务

### 3. 应用崩溃
- 添加异常处理
- 使用try-catch包装关键代码
- 保存中间结果

## 🎉 快速开始

1. **立即部署到Streamlit Cloud：**
   ```bash
   git add .
   git commit -m "Deploy to Streamlit Cloud"
   git push origin main
   ```
   然后访问 [share.streamlit.io](https://share.streamlit.io)

2. **本地测试优化后的配置：**
   ```bash
   streamlit run app.py
   ```

3. **监控应用性能：**
   - 添加资源监控代码
   - 使用Streamlit Cloud的内置监控

---

✅ **推荐流程：** Streamlit Cloud → Railway → Render → 自建服务器 