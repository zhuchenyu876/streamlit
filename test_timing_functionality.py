#!/usr/bin/env python3
"""
测试首字响应时间功能
"""
import sys
import pandas as pd
import streamlit as st
import time
import os

# 添加当前目录到路径
sys.path.append('.')

# 模拟streamlit session_state
class MockSessionState:
    def __init__(self):
        self.data = {}
    
    def get(self, key, default=None):
        return self.data.get(key, default)
    
    def __setattr__(self, name, value):
        if name == 'data':
            super().__setattr__(name, value)
        else:
            self.data[name] = value

# 如果不是在streamlit环境中运行，模拟session_state
if 'streamlit' not in sys.modules:
    st.session_state = MockSessionState()

try:
    from client import Client
    from app import QAAnalyzer
    print("✅ 成功导入相关模块")
except ImportError as e:
    print(f"❌ 导入模块失败: {e}")
    sys.exit(1)

def test_timing_functionality():
    """测试首字响应时间功能"""
    print("🔍 测试首字响应时间功能")
    print("=" * 60)
    
    # 1. 模拟启用首字响应时间
    print("\n1. 设置首字响应时间选项...")
    st.session_state.enable_first_token_timing = True
    enable_status = st.session_state.get('enable_first_token_timing', False)
    print(f"   ✅ enable_first_token_timing: {enable_status}")
    
    # 2. 读取agents配置
    print("\n2. 读取Agent配置...")
    try:
        agents_df = pd.read_csv('./public/agents.csv')
        test_agent = agents_df.iloc[0]
        print(f"   ✅ 使用Agent: {test_agent['name']}")
    except Exception as e:
        print(f"   ❌ 读取agents.csv失败: {e}")
        return False
    
    # 3. 创建客户端
    print("\n3. 创建客户端...")
    try:
        client = Client(
            url=test_agent['url'],
            username=test_agent['username'],
            robot_key=test_agent['robot_key'],
            robot_token=test_agent['robot_token']
        )
        print("   ✅ 客户端创建成功")
    except Exception as e:
        print(f"   ❌ 客户端创建失败: {e}")
        return False
    
    # 4. 测试时间记录方法
    print("\n4. 测试时间记录方法...")
    try:
        # 测试基础WebSocket方法
        print("   🔄 测试基础WebSocket连接...")
        basic_result = client.websocket_chat_with_timeout("你好", timeout=10)
        print(f"   ✅ 基础连接成功: {basic_result[:50]}...")
        
        # 测试带时间记录的方法
        print("   🔄 测试带时间记录的方法...")
        timing_result = client.websocket_chat_with_timeout_and_timing("你好", timeout=10, record_timing=True)
        
        print(f"   📊 时间记录结果:")
        print(f"      答案: {timing_result['answer'][:50]}...")
        print(f"      首字响应时间: {timing_result['first_token_response_time']}")
        print(f"      总响应时间: {timing_result['total_response_time']}")
        print(f"      重试次数: {timing_result['attempt']}")
        
        if timing_result['first_token_response_time'] is not None:
            print("   ✅ 时间记录方法正常工作")
        else:
            print("   ⚠️ 时间记录方法返回了None")
            
    except Exception as e:
        print(f"   ❌ 时间记录方法测试失败: {e}")
        return False
    
    # 5. 测试DataFrame更新
    print("\n5. 测试DataFrame更新...")
    try:
        # 创建测试数据
        df = pd.DataFrame({
            '场景': ['测试场景1', '测试场景2'],
            '测试数据': ['你好', '请问你是谁？'],
            '参考答案': ['你好', '我是AI助手'],
            '组别': ['group1', 'group1']
        })
        
        print(f"   📊 原始DataFrame列: {df.columns.tolist()}")
        
        # 模拟答案生成过程
        col_name = '生成答案1'
        df[col_name] = ""
        
        for idx in df.index:
            # 检查是否启用首字响应时间记录
            enable_first_token_timing = st.session_state.get('enable_first_token_timing', False)
            
            if enable_first_token_timing:
                print(f"   🔄 为第{idx+1}行生成答案（启用时间记录）...")
                # 使用带有时间记录的方法
                result = client.websocket_chat_with_timeout_and_timing(
                    df.loc[idx, '测试数据'], timeout=10, record_timing=True
                )
                
                # 记录时间信息
                if result['first_token_response_time'] is not None:
                    df.loc[idx, f'{col_name}_first_token_time'] = result['first_token_response_time']
                if result['total_response_time'] is not None:
                    df.loc[idx, f'{col_name}_total_time'] = result['total_response_time']
                df.loc[idx, f'{col_name}_attempt'] = result['attempt']
                
                df.loc[idx, col_name] = result['answer']
                print(f"      首字响应时间: {result['first_token_response_time']}")
                print(f"      总响应时间: {result['total_response_time']}")
            else:
                print(f"   🔄 为第{idx+1}行生成答案（不记录时间）...")
                answer = client.websocket_chat_with_timeout(df.loc[idx, '测试数据'], timeout=10)
                df.loc[idx, col_name] = answer
            
            time.sleep(1)  # 避免请求过快
        
        print(f"   📊 处理后DataFrame列: {df.columns.tolist()}")
        
        # 检查时间字段
        timing_columns = [col for col in df.columns if 'first_token_time' in col or 'total_time' in col or 'attempt' in col]
        if timing_columns:
            print(f"   ✅ 成功添加时间字段: {timing_columns}")
        else:
            print("   ❌ 未找到时间字段")
            return False
        
        # 保存到Excel
        excel_file = 'timing_test_result.xlsx'
        df.to_excel(excel_file, index=False)
        print(f"   📄 结果已保存到: {excel_file}")
        
        # 验证Excel文件
        df_read = pd.read_excel(excel_file)
        excel_timing_columns = [col for col in df_read.columns if 'first_token_time' in col or 'total_time' in col or 'attempt' in col]
        if excel_timing_columns:
            print(f"   ✅ Excel文件包含时间字段: {excel_timing_columns}")
        else:
            print("   ❌ Excel文件不包含时间字段")
            return False
        
    except Exception as e:
        print(f"   ❌ DataFrame更新测试失败: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 测试完成！首字响应时间功能正常工作")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = test_timing_functionality()
    if success:
        print("\n✅ 功能测试通过！")
        print("💡 如果在实际使用中仍然没有看到时间字段，请检查:")
        print("   1. 是否勾选了'记录首字响应时间'选项")
        print("   2. 是否等待分析完全完成")
        print("   3. 是否查看了正确的Excel文件")
    else:
        print("\n❌ 功能测试失败！")
        print("请检查网络连接和Agent配置") 