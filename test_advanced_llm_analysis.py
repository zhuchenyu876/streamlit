#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced LLM Analysis 测试脚本
用于验证和调试LLM分析功能
"""

import sys
import time
import json
import pandas as pd
import requests
from datetime import datetime
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LLMAnalysisTester:
    def __init__(self):
        """初始化测试器"""
        # 使用默认配置
        self.config = {
            'url': 'https://agents.dyna.ai/openapi/v1/conversation/dialog/',
            'robot_key': 'AcZ%2FQzIk8m6UV0uNkXi3HO1pJPI%3D',
            'robot_token': 'MTc1MjEzMDE5Njc3NQp2SE5aZU92SFUvT1JwSVMvaFN3S3Jza1BlU1U9',
            'username': 'edison.chu@dyna.ai'
        }
        
        print("🚀 Advanced LLM Analysis 测试器初始化完成")
        print(f"📡 API URL: {self.config['url']}")
        print(f"👤 用户名: {self.config['username']}")
        print("-" * 60)
    
    def test_api_connection(self):
        """测试API连接"""
        print("\n🔍 测试1: API连接测试")
        
        test_prompt = "请回答：你好，这是一个测试。"
        
        try:
            start_time = time.time()
            result = self.send_simple_request(test_prompt)
            elapsed_time = time.time() - start_time
            
            print(f"✅ API连接成功！")
            print(f"⏱️ 响应时间: {elapsed_time:.2f}秒")
            print(f"📄 响应内容: {result[:200]}...")
            return True
            
        except Exception as e:
            print(f"❌ API连接失败: {str(e)}")
            return False
    
    def test_analysis_performance(self):
        """测试分析性能"""
        print("\n🔍 测试2: 分析性能测试")
        
        # 创建测试数据
        test_data = {
            'reference': '{"type": "markdown", "data": "| ID | 产品 | 库存 | 价格 |\\n|:---|:-----|:-----|:-----|\\n| LL-C30210 | 185/65R15 COMPASAL BLAZER HP 88H | 8 | $1142 |\\n", "desc": "找到1个产品，价格$1142"}',
            'generated': '{"type": "markdown", "data": "| ID | 产品 | 库存 | 价格 |\\n|:---|:-----|:-----|:-----|\\n| LL-C30210 | 185/65R15 COMPASAL BLAZER HP 88H | 8 | $1142 |\\n", "desc": "找到1个产品，价格$1142"}'
        }
        
        # 测试不同类型的分析
        analysis_types = [
            ("comprehensive", "全面分析"),
            ("tire_business", "业务分析"),
            ("agent_comparison", "对比分析")
        ]
        
        results = {}
        
        for analysis_type, chinese_name in analysis_types:
            print(f"\n🧠 测试 {chinese_name} ({analysis_type})...")
            
            try:
                start_time = time.time()
                
                # 创建提示词
                prompt = self.create_evaluation_prompt(
                    test_data['reference'], 
                    test_data['generated'], 
                    analysis_type
                )
                
                # 发送请求
                result = self.send_simple_request(prompt)
                elapsed_time = time.time() - start_time
                
                results[analysis_type] = {
                    'success': True,
                    'time': elapsed_time,
                    'result_length': len(result),
                    'result_preview': result[:300] + "..." if len(result) > 300 else result
                }
                
                print(f"✅ {chinese_name} 成功！")
                print(f"⏱️ 耗时: {elapsed_time:.2f}秒")
                print(f"📄 结果长度: {len(result)} 字符")
                
            except Exception as e:
                results[analysis_type] = {
                    'success': False,
                    'error': str(e),
                    'time': 0
                }
                print(f"❌ {chinese_name} 失败: {str(e)}")
        
        return results
    
    def test_batch_analysis(self, sample_size=3):
        """测试批量分析"""
        print(f"\n🔍 测试3: 批量分析测试 ({sample_size}个样本)")
        
        # 创建测试DataFrame
        test_df = pd.DataFrame({
            '场景': [f'测试场景{i+1}' for i in range(sample_size)],
            '参考答案': [f'这是参考答案{i+1}，包含轮胎规格185/65R15，价格$1142' for i in range(sample_size)],
            '生成答案1': [f'这是生成答案{i+1}，包含轮胎规格185/65R15，价格$1142' for i in range(sample_size)]
        })
        
        print(f"📊 测试数据: {len(test_df)} 行")
        
        try:
            # 导入分析器
            from advanced_llm_analyzer import AdvancedLLMAnalyzer
            
            # 创建分析器
            analyzer = AdvancedLLMAnalyzer(self.config)
            
            # 定义进度回调
            def progress_callback(current, total):
                progress = (current / total) * 100
                print(f"📈 进度: {current}/{total} ({progress:.1f}%)")
            
            # 执行分析
            start_time = time.time()
            result_df = analyzer.batch_analyze_dataframe(
                test_df, 
                '参考答案', 
                '生成答案1',
                'comprehensive',
                progress_callback=progress_callback
            )
            total_time = time.time() - start_time
            
            print(f"✅ 批量分析成功！")
            print(f"⏱️ 总耗时: {total_time:.2f}秒")
            print(f"📊 平均每样本: {total_time/sample_size:.2f}秒")
            print(f"📄 结果列数: {len(result_df.columns)}")
            
            # 显示结果列
            llm_columns = [col for col in result_df.columns if col.startswith('llm_')]
            print(f"🧠 LLM分析列: {len(llm_columns)} 个")
            
            return True
            
        except Exception as e:
            print(f"❌ 批量分析失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def send_simple_request(self, prompt, timeout=30):
        """发送简单请求"""
        url = self.config['url']
        headers = {
            'cybertron-robot-key': self.config['robot_key'],
            'cybertron-robot-token': self.config['robot_token'],
            'Content-Type': 'application/json'
        }
        data = {
            "username": self.config['username'],
            "question": prompt,
            "segment_code": "qa_analysis"
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=timeout)
        response.raise_for_status()
        result = response.json()
        
        if result.get('code') == '000000':
            if 'data' in result and 'answer' in result['data']:
                return result['data']['answer']
            return str(result.get('data', {}))
        else:
            raise Exception(f"API Error: {result.get('code')} - {result.get('message')}")
    
    def create_evaluation_prompt(self, reference: str, generated: str, evaluation_type: str = "comprehensive") -> str:
        """创建评估提示词"""
        if evaluation_type == "comprehensive":
            return f"""
作为AI质量评估专家，请对以下答案进行评估：

参考答案：{reference}
生成答案：{generated}

请从以下维度评估（0-10分）：
1. 事实准确性
2. 语义一致性
3. 业务逻辑符合性
4. 回答完整性
5. 信息相关性

请用JSON格式返回评估结果。
"""
        elif evaluation_type == "tire_business":
            return f"""
作为轮胎业务专家，请评估以下答案的业务准确性：

参考答案：{reference}
生成答案：{generated}

请从轮胎业务角度评估：
1. 轮胎规格准确性
2. 价格准确性
3. 库存准确性

请用JSON格式返回结果。
"""
        elif evaluation_type == "agent_comparison":
            return f"""
请对比以下两个答案的质量：

参考答案：{reference}
生成答案：{generated}

请分析：
1. 哪个答案更好
2. 具体差异在哪里
3. 改进建议

请用JSON格式返回对比结果。
"""
        else:
            return self.create_evaluation_prompt(reference, generated, "comprehensive")
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🎯 开始运行 Advanced LLM Analysis 完整测试")
        print("=" * 60)
        
        # 测试1: API连接
        connection_ok = self.test_api_connection()
        if not connection_ok:
            print("\n❌ API连接失败，无法继续测试")
            return False
        
        # 测试2: 分析性能
        performance_results = self.test_analysis_performance()
        
        # 测试3: 批量分析
        batch_ok = self.test_batch_analysis(sample_size=2)
        
        # 生成测试报告
        print("\n📋 测试报告总结")
        print("=" * 60)
        print(f"✅ API连接测试: {'通过' if connection_ok else '失败'}")
        
        if performance_results:
            for analysis_type, result in performance_results.items():
                status = "通过" if result['success'] else "失败"
                time_info = f"({result['time']:.2f}秒)" if result['success'] else f"({result.get('error', '未知错误')})"
                print(f"✅ {analysis_type}分析: {status} {time_info}")
        
        print(f"✅ 批量分析测试: {'通过' if batch_ok else '失败'}")
        
        # 性能建议
        if performance_results:
            avg_time = sum(r['time'] for r in performance_results.values() if r['success']) / len([r for r in performance_results.values() if r['success']])
            print(f"\n💡 性能分析:")
            print(f"   平均单次API调用时间: {avg_time:.2f}秒")
            print(f"   10个样本全面分析预计时间: {10 * 3 * avg_time:.0f}秒")
            print(f"   50个样本全面分析预计时间: {50 * 3 * avg_time:.0f}秒")
        
        return True

def main():
    """主函数"""
    print("🧪 Advanced LLM Analysis 功能测试脚本")
    print("📅 测试时间:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    try:
        tester = LLMAnalysisTester()
        tester.run_all_tests()
        
    except KeyboardInterrupt:
        print("\n⏹️ 用户中断测试")
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 