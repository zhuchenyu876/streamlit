#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
from json_dashboard import JSONDashboard

def test_json_dashboard():
    """测试JSON Dashboard的修复"""
    print("🔍 测试JSON Dashboard...")
    
    # 创建JSON Dashboard实例
    dashboard = JSONDashboard()
    
    # 加载数据
    print("📊 加载JSON指标数据...")
    df = dashboard.load_and_process_df('qa_analysis_results/qa_analysis_results_20250710_123026_json_metrics.csv')
    
    if df.empty:
        print("❌ 数据加载失败")
        return False
    
    print(f"✅ 数据加载成功，共{len(df)}行")
    
    # 检查列名
    print("🔍 检查列名...")
    json_columns = [col for col in df.columns if 'json' in col]
    print(f"📋 找到{len(json_columns)}个JSON相关列:")
    for i, col in enumerate(json_columns[:6]):  # 只显示前6个
        print(f"  {i+1}. {col}")
    
    # 计算指标
    print("🧮 计算JSON指标...")
    metrics = dashboard.calculate_json_metrics(df)
    
    if not metrics:
        print("❌ 指标计算失败")
        return False
    
    print("✅ 指标计算成功")
    
    # 显示关键指标
    print("📈 关键指标结果:")
    key_metrics = [
        'json_structure_consistency_answer1_answer2',
        'json_format_correctness_answer1_answer2',
        'json_price_accuracy_answer1_answer2',
        'json_stock_accuracy_answer1_answer2'
    ]
    
    for metric in key_metrics:
        value = metrics.get(metric, 0)
        print(f"  📊 {metric}: {value:.1f}%")
    
    # 检查是否有非零值
    non_zero_count = sum(1 for metric in key_metrics if metrics.get(metric, 0) > 0)
    
    if non_zero_count > 0:
        print(f"✅ 成功！有{non_zero_count}个指标显示非零值")
        return True
    else:
        print("❌ 所有指标都为0，可能还有问题")
        return False

if __name__ == "__main__":
    success = test_json_dashboard()
    if success:
        print("\n🎉 JSON Dashboard修复测试通过！")
    else:
        print("\n❌ JSON Dashboard修复测试失败") 