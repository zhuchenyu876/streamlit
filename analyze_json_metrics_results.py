#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def analyze_json_metrics_results():
    """
    分析JSON专门指标的结果
    """
    # 读取数据
    df = pd.read_csv('qa_analysis_results/qa_analysis_results_20250710_123026_json_metrics.csv')
    
    print("🔍 JSON专门指标分析报告")
    print("=" * 50)
    
    # 基本信息
    print(f"📊 总测试样本数: {len(df)}")
    print(f"📋 场景类型分布:")
    scenario_counts = df['场景'].value_counts()
    for scenario, count in scenario_counts.items():
        print(f"  • {scenario}: {count}个")
    
    print("\n🎯 指标详细分析:")
    
    # 分析JSON相关指标
    json_metrics = [
        'json_structure_consistency_answer1_answer2', 
        'json_product_coverage_answer1_answer2',
        'json_price_accuracy_answer1_answer2', 
        'json_stock_accuracy_answer1_answer2',
        'json_description_similarity_answer1_answer2', 
        'json_format_correctness_answer1_answer2',
        'json_overall_quality_answer1_answer2'
    ]
    
    # 只分析包含三个参数的查询（JSON格式回复）
    json_queries = df[df['场景'] == 'Consulta tres parámetros']
    
    if len(json_queries) > 0:
        print(f"\n📋 三参数查询（JSON格式）分析 ({len(json_queries)}个样本):")
        
        for metric in json_metrics:
            if metric in json_queries.columns:
                values = json_queries[metric].dropna()
                if len(values) > 0:
                    avg_val = values.mean()
                    metric_name = metric.replace('json_', '').replace('_answer1_answer2', '')
                    print(f"  • {metric_name}: {avg_val:.3f}")
    
    # 分析传统指标在JSON数据上的表现
    print(f"\n📋 传统指标在JSON数据上的表现:")
    traditional_metrics = ['语义稳定性', '冗余度', '完整度', '相关度']
    
    for metric in traditional_metrics:
        if metric in df.columns:
            values = df[metric].dropna()
            if len(values) > 0:
                avg_val = values.mean()
                print(f"  • {metric}: {avg_val:.3f}")
    
    # 对比分析
    print(f"\n🔍 问题诊断:")
    
    # 1. 参考答案 vs 生成答案数量对比
    ref_with_json = df[df['参考答案'].str.contains('type.*markdown', na=False)]
    gen_with_json = df[df['生成答案1'].str.contains('type.*markdown', na=False)]
    
    print(f"  • 参考答案包含JSON格式: {len(ref_with_json)}个")
    print(f"  • 生成答案包含JSON格式: {len(gen_with_json)}个")
    
    # 2. 产品数量对比
    if len(json_queries) > 0:
        print(f"\n📊 产品数量对比（三参数查询）:")
        
        # 分析参考答案中的产品数量
        ref_product_counts = []
        gen_product_counts = []
        
        for idx, row in json_queries.iterrows():
            ref_answer = str(row['参考答案'])
            gen_answer = str(row['生成答案1'])
            
            # 计算参考答案中的产品数量
            ref_products = ref_answer.count('|') - ref_answer.count('|:')
            if ref_products > 0:
                ref_products = ref_products - 1  # 减去表头
            
            # 计算生成答案中的产品数量
            gen_products = gen_answer.count('|') - gen_answer.count('|:')
            if gen_products > 0:
                gen_products = gen_products - 1  # 减去表头
            
            ref_product_counts.append(max(0, ref_products))
            gen_product_counts.append(max(0, gen_products))
        
        avg_ref_products = np.mean(ref_product_counts)
        avg_gen_products = np.mean(gen_product_counts)
        
        print(f"  • 参考答案平均产品数: {avg_ref_products:.1f}")
        print(f"  • 生成答案平均产品数: {avg_gen_products:.1f}")
        print(f"  • 产品数量差异: {abs(avg_gen_products - avg_ref_products):.1f}")
    
    # 3. 价格分析
    print(f"\n💰 价格准确性分析:")
    price_accuracy = json_queries['json_price_accuracy_answer1_answer2'].dropna()
    if len(price_accuracy) > 0:
        print(f"  • 价格准确性: {price_accuracy.mean():.3f}")
        print(f"  • 价格完全准确的比例: {(price_accuracy == 1.0).mean():.1%}")
    
    # 4. 格式一致性分析
    print(f"\n📋 格式一致性分析:")
    format_correctness = json_queries['json_format_correctness_answer1_answer2'].dropna()
    if len(format_correctness) > 0:
        print(f"  • 格式正确性: {format_correctness.mean():.3f}")
        print(f"  • 格式完全正确的比例: {(format_correctness == 1.0).mean():.1%}")
    
    # 5. 整体质量分析
    print(f"\n🎯 整体质量分析:")
    overall_quality = json_queries['json_overall_quality_answer1_answer2'].dropna()
    if len(overall_quality) > 0:
        print(f"  • JSON整体质量: {overall_quality.mean():.3f}")
        print(f"  • 高质量（>0.8）比例: {(overall_quality > 0.8).mean():.1%}")
        print(f"  • 中等质量（0.5-0.8）比例: {((overall_quality >= 0.5) & (overall_quality <= 0.8)).mean():.1%}")
        print(f"  • 低质量（<0.5）比例: {(overall_quality < 0.5).mean():.1%}")
    
    # 6. 传统指标 vs JSON指标对比
    print(f"\n📊 传统指标 vs JSON专门指标对比:")
    
    # 传统指标
    traditional_quality = 1 - df['冗余度'].mean()  # 1 - 冗余度作为质量指标
    semantic_stability = df['语义稳定性'].mean()
    
    print(f"  • 传统质量指标（1-冗余度）: {traditional_quality:.3f}")
    print(f"  • 语义稳定性: {semantic_stability:.3f}")
    
    if len(overall_quality) > 0:
        print(f"  • JSON专门质量指标: {overall_quality.mean():.3f}")
        print(f"  • 指标一致性: {'良好' if abs(traditional_quality - overall_quality.mean()) < 0.3 else '存在差异'}")
    
    print(f"\n🔍 结论和建议:")
    print("=" * 30)
    
    # 生成结论
    if len(overall_quality) > 0:
        json_avg_quality = overall_quality.mean()
        if json_avg_quality > 0.7:
            print("✅ JSON格式回复整体质量较好")
        elif json_avg_quality > 0.5:
            print("⚠️  JSON格式回复质量中等，需要优化")
        else:
            print("❌ JSON格式回复质量较低，需要重点改进")
    
    # 产品覆盖率分析
    product_coverage = json_queries['json_product_coverage_answer1_answer2'].dropna()
    if len(product_coverage) > 0:
        low_coverage = (product_coverage == 0.0).mean()
        if low_coverage > 0.5:
            print("❌ 产品覆盖率过低，生成答案缺少产品信息")
        else:
            print("✅ 产品覆盖率良好")
    
    # 价格准确性分析
    if len(price_accuracy) > 0:
        high_price_accuracy = (price_accuracy == 1.0).mean()
        if high_price_accuracy > 0.8:
            print("✅ 价格信息准确性很高")
        else:
            print("⚠️  价格信息准确性需要提升")
    
    # 格式一致性分析
    if len(format_correctness) > 0:
        high_format_correctness = (format_correctness == 1.0).mean()
        if high_format_correctness > 0.8:
            print("✅ JSON格式一致性很高")
        else:
            print("⚠️  JSON格式一致性需要改进")
    
    print(f"\n💡 改进建议:")
    print("  1. 优化产品查询逻辑，确保返回完整的产品列表")
    print("  2. 标准化JSON格式，确保参考答案和生成答案格式一致")
    print("  3. 改进价格和库存信息的准确性验证")
    print("  4. 优化产品描述的语义相似度计算")
    print("  5. 建议使用JSON专门指标而非传统ROUGE指标评估JSON格式回复")

if __name__ == "__main__":
    analyze_json_metrics_results() 