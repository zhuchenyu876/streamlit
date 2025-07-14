#!/bin/bash

# 服务器性能优化脚本

echo "🚀 开始优化服务器性能..."

# 1. 优化Nginx配置
echo "⚙️ 优化Nginx配置..."
sudo tee /etc/nginx/nginx.conf > /dev/null << 'EOF'
user www-data;
worker_processes auto;
pid /run/nginx.pid;

events {
    worker_connections 1024;
    use epoll;
    multi_accept on;
}

http {
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    
    # 开启gzip压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    
    # 缓存配置
    open_file_cache max=200000 inactive=20s;
    open_file_cache_valid 30s;
    open_file_cache_min_uses 2;
    open_file_cache_errors on;
    
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    # 日志格式
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';
    
    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log;
    
    include /etc/nginx/conf.d/*.conf;
    include /etc/nginx/sites-enabled/*;
}
EOF

# 2. 优化系统参数
echo "⚙️ 优化系统参数..."
sudo tee -a /etc/sysctl.conf > /dev/null << 'EOF'
# 网络优化
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216
net.ipv4.tcp_rmem = 4096 87380 16777216
net.ipv4.tcp_wmem = 4096 65536 16777216
net.ipv4.tcp_congestion_control = bbr
net.core.netdev_max_backlog = 5000
net.ipv4.tcp_max_syn_backlog = 8192

# 文件描述符限制
fs.file-max = 65535
EOF

sudo sysctl -p

# 3. 设置用户限制
echo "⚙️ 设置用户限制..."
sudo tee -a /etc/security/limits.conf > /dev/null << 'EOF'
* soft nofile 65535
* hard nofile 65535
EOF

# 4. 优化Streamlit配置
echo "⚙️ 优化Streamlit配置..."
mkdir -p ~/.streamlit
cat > ~/.streamlit/config.toml << 'EOF'
[server]
headless = true
port = 8501
address = "127.0.0.1"
maxUploadSize = 200
enableCORS = false
enableXsrfProtection = false
maxMessageSize = 200

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"
EOF

# 5. 创建日志轮转配置
echo "📋 配置日志轮转..."
sudo tee /etc/logrotate.d/llm_agent_test > /dev/null << 'EOF'
/var/log/llm_agent_test.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 root root
    postrotate
        supervisorctl restart llm_agent_test
    endscript
}
EOF

# 6. 重启服务
echo "🔄 重启服务..."
sudo systemctl restart nginx
sudo supervisorctl restart llm_agent_test

echo "✅ 性能优化完成！" 