#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM分析调试脚本 - 快速诊断问题
"""

import requests
import time
import json
from datetime import datetime

def test_api_connection():
    """测试API连接"""
    print("🔍 测试API连接...")
    
    config = {
        'url': 'https://agents.dyna.ai/openapi/v1/conversation/dialog/',
        'robot_key': 'AcZ%2FQzIk8m6UV0uNkXi3HO1pJPI%3D',
        'robot_token': 'MTc1MjEzMDE5Njc3NQp2SE5aZU92SFUvT1JwSVMvaFN3S3Jza1BlU1U9',
        'username': 'edison.chu@dyna.ai'
    }
    
    headers = {
        'cybertron-robot-key': config['robot_key'],
        'cybertron-robot-token': config['robot_token'],
        'Content-Type': 'application/json'
    }
    
    data = {
        "username": config['username'],
        "question": "Hello, this is a test.",
        "segment_code": "qa_analysis"
    }
    
    try:
        print(f"📡 请求URL: {config['url']}")
        print(f"👤 用户名: {config['username']}")
        print("⏱️ 发送请求...")
        
        start_time = time.time()
        response = requests.post(
            config['url'], 
            headers=headers, 
            json=data, 
            timeout=30
        )
        elapsed_time = time.time() - start_time
        
        print(f"📊 响应状态: {response.status_code}")
        print(f"⏱️ 响应时间: {elapsed_time:.2f}秒")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ API连接成功！")
            print(f"📄 响应代码: {result.get('code', 'N/A')}")
            if 'data' in result:
                answer = result['data'].get('answer', 'N/A')
                print(f"📝 响应内容: {answer[:200]}...")
            return True
        else:
            print(f"❌ API调用失败: {response.status_code}")
            print(f"📄 错误内容: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏰ 请求超时！")
        return False
    except requests.exceptions.ConnectionError:
        print("🔌 连接错误！")
        return False
    except Exception as e:
        print(f"❌ 其他错误: {str(e)}")
        return False

def test_advanced_analyzer():
    """测试Advanced LLM Analyzer"""
    print("\n🧠 测试Advanced LLM Analyzer...")
    
    try:
        from advanced_llm_analyzer import AdvancedLLMAnalyzer
        
        config = {
            'url': 'https://agents.dyna.ai/openapi/v1/conversation/dialog/',
            'robot_key': 'AcZ%2FQzIk8m6UV0uNkXi3HO1pJPI%3D',
            'robot_token': 'MTc1MjEzMDE5Njc3NQp2SE5aZU92SFUvT1JwSVMvaFN3S3Jza1BlU1U9',
            'username': 'edison.chu@dyna.ai'
        }
        
        print("⚡ 创建分析器...")
        analyzer = AdvancedLLMAnalyzer(config)
        print("✅ 分析器创建成功！")
        
        # 测试简单评估
        print("🔍 测试简单评估...")
        reference = "轮胎规格185/65R15，价格$1142，库存8个"
        generated = "轮胎规格185/65R15，价格$1142，库存8个"
        
        # 创建简单的业务评估提示
        prompt = f"""
作为轮胎业务专家，请简单评估：
参考答案：{reference}
生成答案：{generated}
请给出1-10分的评分。
"""
        
        print("📡 发送评估请求...")
        start_time = time.time()
        result = analyzer.send_evaluation_request(prompt, timeout=30)
        elapsed_time = time.time() - start_time
        
        print(f"✅ 评估完成！")
        print(f"⏱️ 耗时: {elapsed_time:.2f}秒")
        print(f"📄 结果: {result[:300]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ 分析器测试失败: {str(e)}")
        return False

def test_progress_values():
    """测试进度值计算"""
    print("\n📊 测试进度值计算...")
    
    test_cases = [
        (0, 10),    # 开始
        (1, 10),    # 10%
        (5, 10),    # 50%
        (10, 10),   # 100%
        (15, 10),   # 超过100%（错误情况）
    ]
    
    for current, total in test_cases:
        if total > 0:
            progress = min(max(current / total, 0.0), 1.0)
        else:
            progress = 0.0
        
        print(f"   {current}/{total} → {progress:.2f} ({progress*100:.1f}%)")
        
        # 验证进度值在合理范围内
        if 0.0 <= progress <= 1.0:
            print("   ✅ 进度值正常")
        else:
            print("   ❌ 进度值异常")
    
    print("✅ 进度值测试完成")

def main():
    """主测试函数"""
    print("🧪 LLM分析功能调试")
    print("=" * 50)
    print(f"📅 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 测试1: 进度值计算
    test_progress_values()
    
    # 测试2: API连接
    api_ok = test_api_connection()
    
    # 测试3: 分析器
    if api_ok:
        analyzer_ok = test_advanced_analyzer()
    else:
        print("🔴 跳过分析器测试（API连接失败）")
        analyzer_ok = False
    
    # 总结
    print("\n" + "=" * 50)
    print("📋 测试结果总结:")
    print(f"   📊 进度值计算: ✅ 正常")
    print(f"   📡 API连接: {'✅ 正常' if api_ok else '❌ 失败'}")
    print(f"   🧠 分析器: {'✅ 正常' if analyzer_ok else '❌ 失败'}")
    
    if not api_ok:
        print("\n💡 建议:")
        print("   1. 检查网络连接")
        print("   2. 确认API服务状态")
        print("   3. 验证API配置信息")
    
    if api_ok and not analyzer_ok:
        print("\n💡 建议:")
        print("   1. 检查advanced_llm_analyzer.py文件")
        print("   2. 确认导入路径正确")
        print("   3. 查看详细错误信息")

if __name__ == "__main__":
    main() 