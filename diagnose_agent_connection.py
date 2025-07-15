#!/usr/bin/env python3
"""
Agent连接诊断工具
"""
import os
import sys
import json
import time
import pandas as pd
import socket
from urllib.parse import urlparse
import ssl
import threading

# 添加当前目录到路径
sys.path.append('.')

try:
    from client import Client
except ImportError:
    print("❌ 无法导入client模块")
    sys.exit(1)

def check_network_connectivity(url):
    """检查网络连接"""
    try:
        parsed = urlparse(url)
        host = parsed.hostname
        port = parsed.port or (443 if parsed.scheme == 'wss' else 80)
        
        # 测试TCP连接
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            return True, f"✅ 网络连接正常 ({host}:{port})"
        else:
            return False, f"❌ 网络连接失败 ({host}:{port})"
    except Exception as e:
        return False, f"❌ 网络检查失败: {str(e)}"

def test_websocket_connection(agent_config):
    """测试WebSocket连接"""
    try:
        client = Client(
            url=agent_config['url'],
            username=agent_config['username'],
            robot_key=agent_config['robot_key'],
            robot_token=agent_config['robot_token']
        )
        
        # 测试简单的连接
        result = client.websocket_chat_with_timeout("你好", timeout=10)
        
        if result and "Request failed" not in result:
            return True, f"✅ WebSocket连接成功，响应: {result[:100]}..."
        else:
            return False, f"❌ WebSocket连接失败: {result}"
            
    except Exception as e:
        return False, f"❌ WebSocket测试失败: {str(e)}"

def diagnose_agent_connection():
    """诊断Agent连接问题"""
    print("=" * 80)
    print("🔍 Agent连接诊断工具")
    print("=" * 80)
    
    # 1. 检查文件结构
    print("\n📁 1. 检查项目文件结构...")
    required_files = [
        'client.py',
        'app.py', 
        'public/agents.csv'
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✅ {file} 存在")
        else:
            print(f"  ❌ {file} 不存在")
    
    # 2. 检查agents.csv
    print("\n📊 2. 检查Agent配置...")
    try:
        agents_df = pd.read_csv('./public/agents.csv')
        print(f"  ✅ 成功读取agents.csv，共有 {len(agents_df)} 个agent配置")
        
        # 显示前3个agent
        print("\n  📋 前3个Agent配置:")
        for i, (_, agent) in enumerate(agents_df.head(3).iterrows()):
            print(f"    {i+1}. {agent['name']} - {agent['description']}")
            print(f"       URL: {agent['url']}")
            print(f"       用户名: {agent['username']}")
            print(f"       Key: {'已配置' if agent['robot_key'] else '未配置'}")
            print(f"       Token: {'已配置' if agent['robot_token'] else '未配置'}")
            print()
            
    except Exception as e:
        print(f"  ❌ 读取agents.csv失败: {str(e)}")
        return
    
    # 3. 测试网络连接
    print("\n🌐 3. 测试网络连接...")
    test_agent = agents_df.iloc[0]  # 使用第一个agent进行测试
    
    network_ok, network_msg = check_network_connectivity(test_agent['url'])
    print(f"  {network_msg}")
    
    if not network_ok:
        print("\n❌ 网络连接失败，请检查:")
        print("  - 网络连接是否正常")
        print("  - 防火墙设置")
        print("  - 代理配置")
        return
    
    # 4. 测试WebSocket连接
    print("\n🔌 4. 测试WebSocket连接...")
    
    # 选择一个agent进行测试
    print(f"  使用Agent: {test_agent['name']}")
    
    ws_ok, ws_msg = test_websocket_connection(test_agent)
    print(f"  {ws_msg}")
    
    if not ws_ok:
        print("\n❌ WebSocket连接失败，可能的原因:")
        print("  - Robot Key或Token错误")
        print("  - 认证信息过期")
        print("  - 用户名错误")
        print("  - 服务器问题")
        
        # 提供解决方案
        print("\n🔧 解决方案:")
        print("  1. 检查Robot Key和Token是否正确")
        print("  2. 确认用户名是否正确")
        print("  3. 尝试重新获取认证信息")
        print("  4. 联系技术支持")
    
    # 5. 环境变量检查
    print("\n⚙️ 5. 检查环境变量...")
    env_vars = ['WS_URL', 'USER_NAME', 'ROBOT_KEY', 'ROBOT_TOKEN']
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            print(f"  ✅ {var}: 已设置")
        else:
            print(f"  ⚠️ {var}: 未设置（可选）")
    
    # 6. 提供使用建议
    print("\n" + "=" * 80)
    print("💡 使用建议")
    print("=" * 80)
    
    if ws_ok:
        print("✅ Agent连接正常！您可以：")
        print("  1. 运行 'streamlit run app.py'")
        print("  2. 在Agent Management标签页选择要使用的Agent")
        print("  3. 在Analysis标签页进行批量分析")
    else:
        print("❌ Agent连接有问题，请按以下步骤排查：")
        print("  1. 检查网络连接")
        print("  2. 验证Robot Key和Token")
        print("  3. 确认用户名正确")
        print("  4. 尝试其他Agent配置")
        print("  5. 如果问题持续，请联系技术支持")
    
    print("\n🔧 快速修复命令:")
    print("  # 启动应用")
    print("  streamlit run app.py")
    print("  # 然后在浏览器中进入 'Agent Management' 标签页")
    print("  # 测试连接或添加新的Agent配置")
    
    print("\n" + "=" * 80)
    print("🎯 诊断完成！")
    print("=" * 80)

if __name__ == "__main__":
    diagnose_agent_connection() 