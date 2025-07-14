# 🧠 增强版LLM分析 - API配置指南

## 🔑 支持的LLM服务

### 1. OpenAI API
```python
config = {
    'provider': 'openai',
    'api_key': 'your-openai-api-key',
    'model': 'gpt-4o-mini',  # 或 gpt-3.5-turbo
    'base_url': 'https://api.openai.com/v1'
}
```

### 2. Azure OpenAI
```python
config = {
    'provider': 'azure',
    'api_key': 'your-azure-key',
    'model': 'gpt-4',
    'base_url': 'https://your-resource.openai.azure.com/',
    'api_version': '2024-02-01'
}
```

### 3. 其他兼容OpenAI的服务
```python
config = {
    'provider': 'openai_compatible',
    'api_key': 'your-api-key',
    'model': 'your-model-name',
    'base_url': 'https://your-service-url/v1'
}
```

## 📝 配置步骤

### 在应用中配置：
1. 打开应用程序
2. 进入 "Analyzer Config" 标签页
3. 填写您的API配置信息
4. 测试连接

### 环境变量配置：
```bash
# 方法1: 创建 .env 文件
OPENAI_API_KEY=your-api-key
OPENAI_MODEL=gpt-4o-mini

# 方法2: 设置环境变量
export OPENAI_API_KEY=your-api-key
export OPENAI_MODEL=gpt-4o-mini
```

## 💰 成本预估

### OpenAI GPT-4o-mini (推荐)
- 输入：$0.15 / 1M tokens
- 输出：$0.60 / 1M tokens
- 100条分析大约：$2-5

### OpenAI GPT-3.5-turbo (经济)
- 输入：$0.50 / 1M tokens  
- 输出：$1.50 / 1M tokens
- 100条分析大约：$3-8

## 🔧 免费/低成本替代方案

### 1. 本地模型 (Ollama)
```bash
# 安装 Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 下载模型
ollama pull llama2:7b

# 配置
config = {
    'provider': 'ollama',
    'model': 'llama2:7b',
    'base_url': 'http://localhost:11434'
}
```

### 2. 免费API服务
- **Hugging Face Inference API** (有免费额度)
- **Google Colab** + 本地模型
- **Groq** (有免费额度)

## ⚠️ 注意事项

1. **数据隐私**: 确保您的测试数据可以发送到第三方API
2. **成本控制**: 设置适当的请求限制
3. **API限制**: 注意速率限制和配额限制
4. **网络连接**: 确保服务器可以访问API端点

## 🧪 测试建议

1. **小批量测试**: 先用10-20条数据测试
2. **质量验证**: 人工检查几个分析结果
3. **成本监控**: 监控API使用量和费用
4. **备份方案**: 准备降级到传统指标的方案 