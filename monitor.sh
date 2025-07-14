#!/bin/bash

# 系统监控脚本

echo "📊 LLM客服质量分析系统 - 状态监控"
echo "=================================="

# 1. 检查系统资源
echo "💻 系统资源状态:"
echo "CPU使用率: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | sed 's/%us,//')"
echo "内存使用: $(free -h | grep Mem | awk '{print $3"/"$2}')"
echo "磁盘使用: $(df -h / | tail -1 | awk '{print $5}')"

# 2. 检查服务状态
echo ""
echo "🔧 服务状态:"
echo "Nginx: $(sudo systemctl is-active nginx)"
echo "Supervisor: $(sudo systemctl is-active supervisor)"
echo "Streamlit: $(sudo supervisorctl status llm_agent_test | awk '{print $2}')"

# 3. 检查端口
echo ""
echo "🌐 端口状态:"
echo "HTTP (80): $(sudo netstat -tlnp | grep :80 | wc -l) 个连接"
echo "HTTPS (443): $(sudo netstat -tlnp | grep :443 | wc -l) 个连接"
echo "Streamlit (8501): $(sudo netstat -tlnp | grep :8501 | wc -l) 个连接"

# 4. 检查日志
echo ""
echo "📋 最近错误日志:"
echo "Nginx错误:"
sudo tail -n 5 /var/log/nginx/error.log 2>/dev/null || echo "  无错误日志"
echo "Streamlit错误:"
sudo tail -n 5 /var/log/llm_agent_test.log | grep -i error || echo "  无错误日志"

# 5. 检查SSL证书
echo ""
echo "🔐 SSL证书状态:"
if command -v certbot &> /dev/null; then
    sudo certbot certificates 2>/dev/null | grep -E "(Certificate Name|Expiry Date)" || echo "  未找到证书"
else
    echo "  Certbot未安装"
fi

# 6. 检查网络连接
echo ""
echo "🌍 网络连接测试:"
if ping -c 1 8.8.8.8 &> /dev/null; then
    echo "  外网连接: ✅ 正常"
else
    echo "  外网连接: ❌ 异常"
fi

# 7. 性能指标
echo ""
echo "📈 性能指标:"
echo "负载平均: $(uptime | awk -F'load average:' '{print $2}')"
echo "运行时间: $(uptime | awk -F'up ' '{print $2}' | awk -F',' '{print $1}')"
echo "活跃连接: $(sudo netstat -an | grep ESTABLISHED | wc -l)"

# 8. 磁盘空间警告
echo ""
echo "⚠️  磁盘空间警告:"
df -h | awk 'NR>1 {
    gsub(/%/, "", $5)
    if ($5 > 80) 
        print "  " $6 ": " $5 "% 使用率过高!"
}'

echo ""
echo "=================================="
echo "监控完成 - $(date)" 