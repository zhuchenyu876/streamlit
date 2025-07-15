#!/usr/bin/env python3
"""
诊断首字响应时间功能
"""
import pandas as pd
import os
import sys

def diagnose_timing_feature():
    """诊断首字响应时间功能"""
    print("=" * 60)
    print("🔍 首字响应时间功能诊断工具")
    print("=" * 60)
    
    # 检查1: 文件结构
    print("\n📁 1. 检查文件结构...")
    required_files = ['app.py', 'client.py']
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✅ {file} 存在")
        else:
            print(f"  ❌ {file} 不存在")
    
    # 检查2: 代码实现
    print("\n💻 2. 检查代码实现...")
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            app_content = f.read()
        
        # 检查关键代码
        checks = [
            ('enable_first_token_timing', "复选框变量"),
            ('websocket_chat_with_timeout_and_timing', "时间记录方法调用"),
            ('first_token_time', "首字响应时间字段"),
            ('total_time', "总响应时间字段"),
            ('attempt', "重试次数字段")
        ]
        
        for check, desc in checks:
            if check in app_content:
                print(f"  ✅ {desc}: 已实现")
            else:
                print(f"  ❌ {desc}: 未找到")
                
    except Exception as e:
        print(f"  ❌ 读取app.py失败: {e}")
    
    # 检查3: client.py实现
    print("\n🔌 3. 检查客户端实现...")
    try:
        with open('client.py', 'r', encoding='utf-8') as f:
            client_content = f.read()
        
        client_checks = [
            ('websocket_chat_with_timeout_and_timing', "带超时的时间记录方法"),
            ('websocket_chat_with_timing', "时间记录方法"),
            ('first_token_response_time', "首字响应时间返回"),
            ('total_response_time', "总响应时间返回")
        ]
        
        for check, desc in client_checks:
            if check in client_content:
                print(f"  ✅ {desc}: 已实现")
            else:
                print(f"  ❌ {desc}: 未找到")
                
    except Exception as e:
        print(f"  ❌ 读取client.py失败: {e}")
    
    # 检查4: 模拟数据生成
    print("\n🧪 4. 模拟数据生成测试...")
    try:
        # 创建测试数据
        df = pd.DataFrame({
            '场景': ['测试场景1', '测试场景2'],
            '测试数据': ['你好', '再见'],
            '参考答案': ['你好', '再见']
        })
        
        # 模拟时间记录
        mock_result = {
            'answer': '我是AI助手',
            'first_token_response_time': 0.123,
            'total_response_time': 1.456,
            'attempt': 1
        }
        
        col_name = '生成答案1'
        idx = 0
        
        # 添加时间字段
        if mock_result['first_token_response_time'] is not None:
            df.loc[idx, f'{col_name}_first_token_time'] = mock_result['first_token_response_time']
        if mock_result['total_response_time'] is not None:
            df.loc[idx, f'{col_name}_total_time'] = mock_result['total_response_time']
        df.loc[idx, f'{col_name}_attempt'] = mock_result['attempt']
        
        # 检查结果
        timing_columns = [col for col in df.columns if 'first_token_time' in col or 'total_time' in col or 'attempt' in col]
        
        if timing_columns:
            print(f"  ✅ 时间字段生成成功: {timing_columns}")
            
            # 保存测试Excel
            test_file = 'timing_diagnosis_test.xlsx'
            df.to_excel(test_file, index=False)
            print(f"  ✅ 测试Excel已保存: {test_file}")
            
            # 验证Excel内容
            df_read = pd.read_excel(test_file)
            if any('first_token_time' in col for col in df_read.columns):
                print(f"  ✅ Excel中包含时间字段")
            else:
                print(f"  ❌ Excel中未找到时间字段")
                
        else:
            print(f"  ❌ 时间字段生成失败")
            
    except Exception as e:
        print(f"  ❌ 模拟测试失败: {e}")
    
    # 使用说明
    print("\n" + "=" * 60)
    print("📋 使用说明")
    print("=" * 60)
    print("1. 运行Streamlit应用: streamlit run app.py")
    print("2. 进入Analysis标签页")
    print("3. 在'⚡ 性能监控选项'部分勾选'⚡ 记录首字响应时间'")
    print("4. 确认看到'📊 将记录每个请求的首字响应时间，用于性能分析'")
    print("5. 正常进行批量分析")
    print("6. 在导出的Excel文件中查看时间相关列")
    print("\n预期的Excel列名:")
    print("- 生成答案1_first_token_time (首字响应时间)")
    print("- 生成答案1_total_time (总响应时间)")
    print("- 生成答案1_attempt (重试次数)")
    
    print("\n" + "=" * 60)
    print("🎯 诊断完成！")
    print("=" * 60)

if __name__ == "__main__":
    diagnose_timing_feature() 