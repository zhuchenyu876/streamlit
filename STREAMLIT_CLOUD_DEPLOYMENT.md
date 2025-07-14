# 🚀 Streamlit Cloud 部署完整指南

## 📁 **需要上传的文件清单**

### ✅ **核心应用文件（必须上传）**
```
app.py                           # 主应用文件
ui_components.py                 # UI组件模块
llm_analyzer.py                  # LLM分析器
advanced_llm_analyzer.py         # 高级LLM分析器
client.py                        # 客户端接口
dashboard.py                     # 数据仪表板
advanced_llm_dashboard.py        # 高级仪表板
json_dashboard.py                # JSON仪表板
json_metrics_analyzer.py         # JSON指标分析器
metrics.py                       # 质量指标计算
multi_agent_analyzer.py          # 多智能体分析器
```

### ✅ **配置文件（必须上传）**
```
requirements.txt                 # Python依赖
.streamlit/config.toml          # Streamlit配置
.gitignore                      # Git忽略文件
```

### ✅ **公共配置目录（必须上传）**
```
public/
├── agents.csv                  # 智能体配置模板
├── analyzer_config.csv         # 分析器配置模板
└── template.csv                # 测试数据模板
```

### ✅ **文档文件（推荐上传）**
```
README.md                       # 项目说明
QUICK_START.md                 # 快速开始指南
CHANGELOG.md                   # 更新日志
llm_analysis_config_guide.md   # LLM配置指南
LANGUAGE_FEATURE_README.md     # 语言功能说明
PAUSE_FEATURE_GUIDE.md         # 暂停功能指南
UI_IMPROVEMENT_DEMO.md         # UI改进演示
USER_EXPERIENCE_TEST.md        # 用户体验测试
西班牙语CSV文件处理完整指南.md    # 西班牙语处理指南
```

### ✅ **工具脚本（可选上传）**
```
start.py                       # 启动脚本
start.bat                      # Windows启动脚本
deploy.sh                      # Linux部署脚本
monitor.sh                     # 监控脚本
optimize_server.sh             # 服务器优化脚本
```

### ✅ **测试文件（可选上传）**
```
test_advanced_llm_analysis.py   # 高级分析测试
test_json_dashboard.py          # JSON仪表板测试
test_spanish_file.py            # 西班牙语文件测试
debug_llm_test.py               # LLM调试测试
```

## ❌ **不需要上传的文件（已在.gitignore中）**

### 🚫 **系统和缓存文件**
```
__pycache__/                   # Python缓存
.venv/                         # 虚拟环境
.idea/                         # IDE配置
.env                           # 本地环境变量
```

### 🚫 **日志和临时文件**
```
log/                           # 日志目录
temp_*.csv                     # 临时CSV文件
test_result.txt                # 测试结果
```

### 🚫 **分析结果文件（太大）**
```
qa_analysis_results/           # 分析结果目录
analysis_*.xlsx               # 分析结果Excel
```

### 🚫 **测试数据文件（太大）**
```
轮胎测试数据*.csv             # 轮胎测试数据
轮胎场景.xlsx                # 轮胎场景Excel
LISTA*.xlsx                   # 价格清单Excel
```

### 🚫 **Streamlit密钥文件**
```
.streamlit/secrets.toml        # 密钥配置（手动在云端配置）
```

## 🚀 **部署步骤**

### 1. **清理项目**
```bash
# 删除缓存和临时文件
rm -rf __pycache__
rm -rf .venv
rm -rf log
rm temp_*.csv
```

### 2. **推送到GitHub**
```bash
git add .
git commit -m "Deploy to Streamlit Cloud"
git push origin main
```

### 3. **部署到Streamlit Cloud**
1. 访问 [share.streamlit.io](https://share.streamlit.io)
2. 使用GitHub账号登录
3. 点击 "New app"
4. 选择你的仓库
5. 主文件路径：`app.py`
6. 点击 "Deploy!"

### 4. **配置环境变量**
在Streamlit Cloud控制台的 "Settings" → "Secrets" 中添加：

```toml
USER_NAME = "your_actual_username"
WS_URL = "wss://agents.dyna.ai/openapi/v1/ws/dialog/"
ROBOT_KEY = "your_actual_robot_key"
ROBOT_TOKEN = "your_actual_robot_token"
```

## 📊 **部署后检查**

### ✅ **应用功能检查**
- [ ] 应用能正常启动
- [ ] 文件上传功能正常
- [ ] 分析功能正常
- [ ] 仪表板显示正常

### ✅ **性能检查**
- [ ] 加载时间合理
- [ ] 内存使用正常
- [ ] 长时间运行稳定

## 🔧 **常见问题解决**

### 1. **模块导入错误**
确保所有依赖都在 `requirements.txt` 中

### 2. **环境变量未找到**
检查 Streamlit Cloud 控制台中的 Secrets 配置

### 3. **文件上传失败**
检查文件大小限制，大文件需要分割处理

### 4. **应用启动慢**
这是正常现象，sklearn等重型库需要时间加载

## 🎉 **部署成功！**

部署完成后，你将获得一个类似这样的URL：
`https://your-app-name.streamlit.app`

---

🔥 **重要提醒**：
1. 不要将 `.env` 或 `secrets.toml` 上传到GitHub
2. 所有敏感信息都在Streamlit Cloud控制台配置
3. 大文件和测试数据不要上传，会影响部署速度 