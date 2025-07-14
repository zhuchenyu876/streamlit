# 🚀 完整部署指南 - 本地与Streamlit Cloud兼容

## 📋 系统环境兼容性

### ✅ 已完成的环境兼容性改进

1. **统一文件管理系统**
   - 创建了 `file_manager.py` 统一处理文件操作
   - 自动检测云端/本地环境
   - 智能文件存储（本地文件 + Session State）

2. **修复的关键问题**
   - 添加了缺失的 `websockets>=11.0.0` 依赖
   - 修复了所有文件读写权限问题
   - 解决了目录创建权限问题
   - 统一了模板文件访问逻辑

3. **更新的核心文件**
   - `app.py` - 主应用逻辑
   - `advanced_llm_dashboard.py` - 高级分析面板
   - `dashboard.py` - 基础分析面板
   - `file_manager.py` - 统一文件管理（新增）

---

## 🔧 本地部署

### 环境要求
- Python 3.8+
- pip包管理器

### 安装步骤

1. **克隆项目**
   ```bash
   git clone https://github.com/YOUR_USERNAME/llm-qa-analyzer.git
   cd llm-qa-analyzer
   ```

2. **创建虚拟环境**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **运行应用**
   ```bash
   streamlit run app.py
   ```

5. **访问应用**
   - 打开浏览器访问 `http://localhost:8501`

---

## ☁️ Streamlit Cloud部署

### 第1步：准备GitHub仓库

1. **创建GitHub仓库**
   - 前往 [GitHub](https://github.com)
   - 创建新仓库：`llm-qa-analyzer`
   - 设置为公开仓库

2. **推送代码**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: LLM QA Analysis System"
   git remote add origin https://github.com/YOUR_USERNAME/llm-qa-analyzer.git
   git branch -M main
   git push -u origin main
   ```

### 第2步：配置Streamlit Cloud

1. **访问Streamlit Cloud**
   - 打开 [share.streamlit.io](https://share.streamlit.io)
   - 使用GitHub账号登录

2. **创建新应用**
   - 点击 "New app"
   - 选择您的GitHub仓库
   - 设置参数：
     - Repository: `YOUR_USERNAME/llm-qa-analyzer`
     - Branch: `main`
     - Main file path: `app.py`
     - App URL: 自定义应用URL

3. **部署应用**
   - 点击 "Deploy!"
   - 等待2-5分钟完成部署

### 第3步：配置环境变量（可选）

如果需要设置API密钥：

1. **在Streamlit Cloud中设置Secrets**
   - 进入应用管理页面
   - 点击 "Settings" → "Secrets"
   - 添加配置：
     ```toml
     [secrets]
     OPENAI_API_KEY = "your_api_key_here"
     ROBOT_KEY = "your_robot_key"
     ROBOT_TOKEN = "your_robot_token"
     ```

---

## 📁 文件存储机制

### 本地环境
- ✅ 文件正常保存到磁盘
- ✅ 目录自动创建
- ✅ 支持文件下载和上传

### 云端环境
- ✅ 自动检测云端环境
- ✅ 文件保存到Session State
- ✅ 支持文件下载（从内存）
- ⚠️ 文件在会话结束后清空

---

## 🔍 功能支持对比

| 功能 | 本地环境 | Streamlit Cloud |
|------|----------|----------------|
| 文件上传 | ✅ 完全支持 | ✅ 完全支持 |
| 数据分析 | ✅ 完全支持 | ✅ 完全支持 |
| 结果下载 | ✅ 完全支持 | ✅ 完全支持 |
| 配置保存 | ✅ 持久化 | ⚠️ 会话级 |
| 文件历史 | ✅ 持久化 | ⚠️ 会话级 |
| API调用 | ✅ 完全支持 | ✅ 完全支持 |

---

## 🚨 常见问题解决

### 1. 导入错误
```
ImportError: cannot import name 'Client' from 'client'
```
**解决方案**: 已添加 `websockets>=11.0.0` 到依赖列表

### 2. 文件权限错误
```
OSError: Cannot save file into a non-existent directory
```
**解决方案**: 已实现智能文件管理，自动处理权限问题

### 3. 模板文件缺失
```
FileNotFoundError: template.csv not found
```
**解决方案**: 已实现内置模板系统，无需外部文件

---

## 💡 最佳实践

### 本地开发
1. 使用虚拟环境
2. 定期备份分析结果
3. 配置API密钥到环境变量

### 云端部署
1. 使用Streamlit Secrets管理敏感信息
2. 及时下载重要分析结果
3. 定期检查应用状态

---

## 🔄 更新应用

### 本地更新
```bash
git pull origin main
pip install -r requirements.txt
```

### 云端更新
```bash
git add .
git commit -m "Update: 描述更改"
git push origin main
```
Streamlit Cloud会自动检测更改并重新部署。

---

## 📞 技术支持

### 日志查看
- **本地**: 查看终端输出
- **云端**: 点击 "Manage app" → "Logs"

### 常用命令
```bash
# 检查依赖
pip freeze

# 测试应用
streamlit run app.py --server.headless true

# 清理缓存
streamlit cache clear
```

---

## 🎯 部署验证清单

### 本地环境验证
- [ ] 应用正常启动
- [ ] 文件上传功能正常
- [ ] 数据分析功能正常
- [ ] 结果下载功能正常
- [ ] 配置保存功能正常

### 云端环境验证
- [ ] 应用正常访问
- [ ] 文件上传功能正常
- [ ] 数据分析功能正常
- [ ] 结果下载功能正常
- [ ] 环境自动检测正常

---

## 🔗 相关链接

- [Streamlit Cloud文档](https://docs.streamlit.io/streamlit-cloud)
- [GitHub部署指南](https://docs.github.com/en/pages)
- [Python虚拟环境](https://docs.python.org/3/tutorial/venv.html)

---

**部署完成！** 🎉

您的LLM QA分析系统现在可以在本地和云端环境中无缝运行！ 