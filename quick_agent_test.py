#!/usr/bin/env python3
"""
快速Agent连接测试
"""
import sys
import pandas as pd

sys.path.append('.')

try:
    from client import Client
    print("✅ 成功导入Client模块")
except ImportError as e:
    print(f"❌ 导入Client模块失败: {e}")
    sys.exit(1)

def quick_test():
    """快速测试第一个Agent"""
    print("🚀 快速Agent连接测试")
    print("=" * 50)
    
    try:
        # 读取agents配置
        agents_df = pd.read_csv('./public/agents.csv')
        print(f"📊 找到 {len(agents_df)} 个Agent配置")
        
        # 使用第一个agent进行测试
        test_agent = agents_df.iloc[0]
        print(f"🤖 测试Agent: {test_agent['name']}")
        
        # 创建客户端
        client = Client(
            url=test_agent['url'],
            username=test_agent['username'],
            robot_key=test_agent['robot_key'],
            robot_token=test_agent['robot_token']
        )
        
        print("🔄 发送测试消息...")
        result = client.websocket_chat_with_timeout("你好", timeout=10)
        
        if result and "Request failed" not in result:
            print("✅ 连接成功！")
            print(f"📝 响应: {result[:200]}...")
            return True
        else:
            print("❌ 连接失败！")
            print(f"📝 错误: {result}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False

if __name__ == "__main__":
    success = quick_test()
    if success:
        print("\n🎉 Agent连接正常，可以使用！")
        print("运行: streamlit run app.py")
    else:
        print("\n😞 Agent连接失败")
        print("运行: python diagnose_agent_connection.py 进行详细诊断") 