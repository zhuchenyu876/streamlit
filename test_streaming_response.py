"""
流式响应测试 - 首字响应时间测量
测试批量分析中的流式响应功能和首字响应时间指标
"""

import pandas as pd
import time
import json
from advanced_llm_analyzer import AdvancedLLMAnalyzer


def create_test_data():
    """创建测试数据"""
    test_data = {
        '场景': [
            '轮胎规格询问',
            '轮胎价格查询',
            '轮胎库存查询'
        ],
        '参考答案': [
            '您询问的轮胎规格是185/65R15，这是一款适合紧凑型轿车的轮胎。',
            '该轮胎的价格是$1142，目前有库存。',
            '该轮胎规格的库存数量为15个，可以满足您的需求。'
        ],
        '生成答案1': [
            '185/65R15轮胎适合紧凑型轿车，质量可靠。',
            '价格为$1142，库存充足。',
            '库存15个，可购买。'
        ]
    }
    return pd.DataFrame(test_data)


def test_streaming_vs_normal_response():
    """测试流式响应和普通响应的性能差异"""
    
    # 配置信息
    config = {
        'url': 'https://agents.dyna.ai/api/v1/chat/completions',
        'username': 'test_user',
        'robot_key': 'your_robot_key',
        'robot_token': 'your_robot_token'
    }
    
    # 创建分析器
    analyzer = AdvancedLLMAnalyzer(config)
    
    # 创建测试数据
    test_df = create_test_data()
    
    print("🚀 流式响应 vs 普通响应性能测试")
    print("="*50)
    
    # 测试1：普通响应（原有方式）
    print("\n📊 测试1: 普通响应方式")
    print("-" * 30)
    
    start_time = time.time()
    
    try:
        result_normal = analyzer.batch_analyze_dataframe(
            test_df.copy(), 
            '参考答案', 
            '生成答案1',
            'comprehensive',
            use_streaming=False
        )
        
        normal_time = time.time() - start_time
        print(f"✅ 普通响应完成")
        print(f"⏱️ 总耗时: {normal_time:.2f}秒")
        print(f"📊 平均每样本: {normal_time/len(test_df):.2f}秒")
        
    except Exception as e:
        print(f"❌ 普通响应测试失败: {str(e)}")
        result_normal = None
        normal_time = None
    
    # 测试2：流式响应（新方式）
    print("\n📈 测试2: 流式响应方式")
    print("-" * 30)
    
    start_time = time.time()
    
    try:
        result_streaming = analyzer.batch_analyze_dataframe(
            test_df.copy(), 
            '参考答案', 
            '生成答案1',
            'comprehensive',
            use_streaming=True
        )
        
        streaming_time = time.time() - start_time
        print(f"✅ 流式响应完成")
        print(f"⏱️ 总耗时: {streaming_time:.2f}秒")
        print(f"📊 平均每样本: {streaming_time/len(test_df):.2f}秒")
        
        # 分析首字响应时间
        first_token_times = []
        total_response_times = []
        
        for idx, row in result_streaming.iterrows():
            if 'llm_first_token_response_time' in result_streaming.columns:
                ft_time = row.get('llm_first_token_response_time')
                if ft_time is not None:
                    first_token_times.append(ft_time)
            
            if 'llm_total_response_time' in result_streaming.columns:
                tr_time = row.get('llm_total_response_time')
                if tr_time is not None:
                    total_response_times.append(tr_time)
        
        if first_token_times:
            avg_first_token = sum(first_token_times) / len(first_token_times)
            print(f"🚀 平均首字响应时间: {avg_first_token:.3f}秒")
            print(f"🏃 最快首字响应: {min(first_token_times):.3f}秒")
            print(f"🐌 最慢首字响应: {max(first_token_times):.3f}秒")
        
        if total_response_times:
            avg_total = sum(total_response_times) / len(total_response_times)
            print(f"⏱️ 平均总响应时间: {avg_total:.3f}秒")
            
    except Exception as e:
        print(f"❌ 流式响应测试失败: {str(e)}")
        result_streaming = None
        streaming_time = None
    
    # 性能对比
    print("\n📈 性能对比")
    print("="*50)
    
    if normal_time and streaming_time:
        if streaming_time < normal_time:
            improvement = ((normal_time - streaming_time) / normal_time) * 100
            print(f"🎉 流式响应更快 {improvement:.1f}%")
        else:
            slowdown = ((streaming_time - normal_time) / normal_time) * 100
            print(f"⚠️ 流式响应较慢 {slowdown:.1f}%")
    
    return result_normal, result_streaming


def analyze_streaming_metrics(df):
    """分析流式响应指标"""
    print("\n📊 流式响应指标分析")
    print("="*50)
    
    # 检查时间指标列
    time_columns = [col for col in df.columns if 'time' in col.lower()]
    
    if time_columns:
        print(f"📋 可用时间指标: {time_columns}")
        
        for col in time_columns:
            values = df[col].dropna()
            if len(values) > 0:
                print(f"\n📊 {col}:")
                print(f"  平均值: {values.mean():.3f}秒")
                print(f"  最小值: {values.min():.3f}秒")
                print(f"  最大值: {values.max():.3f}秒")
                print(f"  标准差: {values.std():.3f}秒")
    else:
        print("⚠️ 没有找到时间指标列")
    
    # 检查API重试次数
    retry_columns = [col for col in df.columns if 'attempt' in col.lower()]
    if retry_columns:
        for col in retry_columns:
            values = df[col].dropna()
            if len(values) > 0:
                print(f"\n🔄 {col}:")
                print(f"  平均重试次数: {values.mean():.1f}")
                print(f"  最多重试次数: {values.max()}")


def main():
    """主测试函数"""
    print("🧪 流式响应和首字响应时间测试")
    print("="*50)
    
    # 运行测试
    result_normal, result_streaming = test_streaming_vs_normal_response()
    
    # 分析流式响应指标
    if result_streaming is not None:
        analyze_streaming_metrics(result_streaming)
    
    # 保存结果
    if result_streaming is not None:
        result_streaming.to_csv('streaming_response_test_results.csv', index=False, encoding='utf-8')
        print(f"\n💾 流式响应测试结果已保存到: streaming_response_test_results.csv")
    
    print("\n✅ 测试完成!")


if __name__ == "__main__":
    main() 