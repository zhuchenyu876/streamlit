#!/usr/bin/env python3
"""
调试首字响应时间功能问题
"""
import sys
import pandas as pd
import os
import glob
from datetime import datetime, timedelta

sys.path.append('.')

def debug_timing_issue():
    """调试首字响应时间功能问题"""
    print("🐛 调试首字响应时间功能问题")
    print("=" * 60)
    
    # 1. 检查最近的Excel文件
    print("\n1. 检查最近的Excel文件...")
    excel_files = glob.glob("*.xlsx")
    if excel_files:
        # 按修改时间排序
        excel_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        print(f"   📄 找到 {len(excel_files)} 个Excel文件:")
        
        for i, file in enumerate(excel_files[:5]):  # 显示最近5个
            mod_time = datetime.fromtimestamp(os.path.getmtime(file))
            print(f"      {i+1}. {file} (修改时间: {mod_time.strftime('%Y-%m-%d %H:%M:%S')})")
    else:
        print("   ❌ 当前目录没有找到Excel文件")
        return
    
    # 2. 检查最新Excel文件的列结构
    print("\n2. 检查最新Excel文件的列结构...")
    latest_file = excel_files[0]
    try:
        df = pd.read_excel(latest_file)
        print(f"   📊 {latest_file} 包含 {len(df)} 行数据")
        print(f"   📋 列名: {df.columns.tolist()}")
        
        # 检查时间相关列
        timing_columns = [col for col in df.columns if 'first_token_time' in col or 'total_time' in col or 'attempt' in col]
        if timing_columns:
            print(f"   ✅ 找到时间相关列: {timing_columns}")
            
            # 显示时间数据样例
            for col in timing_columns:
                sample_data = df[col].dropna().head(3)
                if not sample_data.empty:
                    print(f"      {col}: {sample_data.tolist()}")
        else:
            print("   ❌ 没有找到时间相关列")
            
    except Exception as e:
        print(f"   ❌ 读取Excel文件失败: {e}")
        return
    
    # 3. 检查可能的原因
    print("\n3. 可能的原因分析...")
    
    # 检查session_state相关的代码
    print("   🔍 检查代码实现...")
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查关键功能是否存在
        checks = [
            ('enable_first_token_timing', '首字响应时间选项'),
            ('websocket_chat_with_timeout_and_timing', '时间记录方法'),
            ('first_token_time', '首字响应时间字段'),
            ('total_time', '总响应时间字段')
        ]
        
        for check, desc in checks:
            if check in content:
                print(f"      ✅ {desc}: 已实现")
            else:
                print(f"      ❌ {desc}: 未找到")
                
    except Exception as e:
        print(f"   ❌ 检查代码失败: {e}")
    
    # 4. 提供解决方案
    print("\n4. 解决方案建议...")
    print("   💡 请按以下步骤排查:")
    print("      1. 确认已经勾选了'记录首字响应时间'选项")
    print("      2. 确认看到了'将记录每个请求的首字响应时间'的提示")
    print("      3. 等待分析完全完成（不要中途停止）")
    print("      4. 检查导出的Excel文件是否是最新的")
    print("      5. 尝试重新运行分析")
    
    # 5. 快速验证
    print("\n5. 快速验证建议...")
    print("   🚀 运行以下命令进行验证:")
    print("      python test_timing_functionality.py")
    print("   🔧 如果仍有问题，运行:")
    print("      python diagnose_agent_connection.py")
    
    print("\n" + "=" * 60)
    print("🎯 调试完成！")
    print("=" * 60)

if __name__ == "__main__":
    debug_timing_issue() 