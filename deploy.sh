#!/bin/bash

# LLM客服质量分析系统 - 阿里云部署脚本
# 使用方法: ./deploy.sh your-domain.com your-server-ip

set -e

DOMAIN=$1
SERVER_IP=$2
PROJECT_PATH="/opt/llm_agent_test"

if [ -z "$DOMAIN" ] || [ -z "$SERVER_IP" ]; then
    echo "使用方法: ./deploy.sh your-domain.com your-server-ip"
    exit 1
fi

echo "🚀 开始部署 LLM客服质量分析系统到阿里云..."
echo "域名: $DOMAIN"
echo "服务器IP: $SERVER_IP"

# 1. 更新系统
echo "📦 更新系统包..."
sudo apt update && sudo apt upgrade -y

# 2. 安装必要软件
echo "📦 安装必要软件..."
sudo apt install -y python3 python3-pip python3-venv git nginx supervisor ufw certbot python3-certbot-nginx

# 3. 创建项目目录
echo "📁 创建项目目录..."
sudo mkdir -p $PROJECT_PATH
sudo chown $USER:$USER $PROJECT_PATH
cd $PROJECT_PATH

# 4. 创建Python虚拟环境
echo "🐍 配置Python环境..."
python3 -m venv .venv
source .venv/bin/activate
pip install streamlit pandas scikit-learn jieba requests tqdm plotly python-dotenv

# 5. 创建Streamlit配置
echo "⚙️ 配置Streamlit..."
mkdir -p ~/.streamlit
cat > ~/.streamlit/config.toml << EOF
[server]
headless = true
port = 8501
address = "127.0.0.1"
maxUploadSize = 200

[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
EOF

# 6. 配置Nginx
echo "🌐 配置Nginx..."
sudo tee /etc/nginx/sites-available/llm_agent_test > /dev/null << EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    
    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
        proxy_read_timeout 86400;
    }
    
    location /static {
        alias $PROJECT_PATH/static;
        expires 30d;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/llm_agent_test /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# 7. 配置Supervisor
echo "🔄 配置进程管理..."
sudo tee /etc/supervisor/conf.d/llm_agent_test.conf > /dev/null << EOF
[program:llm_agent_test]
command=$PROJECT_PATH/.venv/bin/streamlit run app.py --server.port 8501 --server.address 127.0.0.1 --server.headless true
directory=$PROJECT_PATH
user=$USER
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/llm_agent_test.log
environment=PATH="$PROJECT_PATH/.venv/bin"
EOF

sudo supervisorctl reread
sudo supervisorctl update

# 8. 配置防火墙
echo "🔒 配置防火墙..."
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw --force enable

# 9. 配置SSL证书
echo "🔐 配置SSL证书..."
sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN

# 10. 设置自动续期
echo "🔄 设置证书自动续期..."
(crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet") | crontab -

echo "✅ 部署完成!"
echo "🌐 您可以通过以下地址访问应用:"
echo "   https://$DOMAIN"
echo "   https://www.$DOMAIN"
echo ""
echo "📊 监控命令:"
echo "   sudo supervisorctl status llm_agent_test"
echo "   sudo tail -f /var/log/llm_agent_test.log"
echo "   sudo systemctl status nginx"
echo ""
echo "🔧 管理命令:"
echo "   sudo supervisorctl restart llm_agent_test  # 重启应用"
echo "   sudo systemctl restart nginx              # 重启Nginx"
echo "   sudo certbot certificates                 # 查看证书状态" 