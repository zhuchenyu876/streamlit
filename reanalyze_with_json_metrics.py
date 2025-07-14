#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from json_metrics_analyzer import JSONMetricsAnalyzer
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def reanalyze_csv_with_json_metrics(input_file: str, output_file: str):
    """
    使用新的JSON专门指标重新分析CSV文件
    """
    try:
        # 读取CSV文件
        logger.info(f"正在读取文件: {input_file}")
        df = pd.read_csv(input_file)
        logger.info(f"成功读取 {len(df)} 行数据")
        
        # 检查必要的列
        required_columns = ['参考答案', '生成答案1', '生成答案2']
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"缺少必要的列: {col}")
        
        # 创建JSON分析器
        analyzer = JSONMetricsAnalyzer()
        
        # 分析生成答案1 vs 参考答案
        logger.info("开始分析生成答案1...")
        df_with_metrics1 = analyzer.analyze_dataframe(df, '参考答案', '生成答案1')
        
        # 重命名列以区分答案1和答案2
        metrics_columns = [col for col in df_with_metrics1.columns if col.startswith('json_')]
        for col in metrics_columns:
            df_with_metrics1[col + '_answer1'] = df_with_metrics1[col]
            df_with_metrics1.drop(col, axis=1, inplace=True)
        
        # 分析生成答案2 vs 参考答案
        logger.info("开始分析生成答案2...")
        df_with_metrics2 = analyzer.analyze_dataframe(df, '参考答案', '生成答案2')
        
        # 重命名列以区分答案1和答案2
        metrics_columns = [col for col in df_with_metrics2.columns if col.startswith('json_')]
        for col in metrics_columns:
            df_with_metrics2[col + '_answer2'] = df_with_metrics2[col]
            df_with_metrics2.drop(col, axis=1, inplace=True)
        
        # 合并结果
        logger.info("合并分析结果...")
        
        # 获取answer1的指标列
        answer1_metrics = [col for col in df_with_metrics1.columns if col.endswith('_answer1')]
        answer2_metrics = [col for col in df_with_metrics2.columns if col.endswith('_answer2')]
        
        # 将answer2的指标添加到answer1的dataframe中
        for col in answer2_metrics:
            df_with_metrics1[col] = df_with_metrics2[col]
        
        # 计算两个答案之间的一致性
        logger.info("计算答案间一致性...")
        consistency_metrics = []
        
        base_metric_names = ['structure_consistency', 'product_coverage', 'price_accuracy', 
                           'stock_accuracy', 'description_similarity', 'format_correctness', 
                           'overall_quality']
        
        for metric in base_metric_names:
            col1 = f'json_{metric}_answer1'
            col2 = f'json_{metric}_answer2'
            
            if col1 in df_with_metrics1.columns and col2 in df_with_metrics1.columns:
                # 计算一致性 (1 - 两个答案指标的差异)
                consistency = 1 - abs(df_with_metrics1[col1] - df_with_metrics1[col2])
                df_with_metrics1[f'consistency_{metric}'] = consistency
        
        # 计算综合指标
        logger.info("计算综合指标...")
        
        # 平均质量分数
        answer1_quality_col = None
        answer2_quality_col = None
        
        for col in df_with_metrics1.columns:
            if col.endswith('_overall_quality_answer1'):
                answer1_quality_col = col
            elif col.endswith('_overall_quality_answer2'):
                answer2_quality_col = col
        
        if answer1_quality_col and answer2_quality_col:
            df_with_metrics1['average_quality'] = (
                df_with_metrics1[answer1_quality_col] + 
                df_with_metrics1[answer2_quality_col]
            ) / 2
        
        # 答案稳定性（两个答案的一致性）
        consistency_cols = [col for col in df_with_metrics1.columns if col.startswith('consistency_')]
        if consistency_cols:
            df_with_metrics1['answer_stability'] = df_with_metrics1[consistency_cols].mean(axis=1)
        
        # 保存结果
        logger.info(f"保存结果到: {output_file}")
        df_with_metrics1.to_csv(output_file, index=False, encoding='utf-8')
        
        # 输出统计信息
        logger.info("=== 分析结果统计 ===")
        logger.info(f"总样本数: {len(df_with_metrics1)}")
        
        if 'average_quality' in df_with_metrics1.columns:
            logger.info(f"平均质量分数: {df_with_metrics1['average_quality'].mean():.3f}")
            logger.info(f"质量分数标准差: {df_with_metrics1['average_quality'].std():.3f}")
        
        if 'answer_stability' in df_with_metrics1.columns:
            logger.info(f"答案稳定性: {df_with_metrics1['answer_stability'].mean():.3f}")
            logger.info(f"稳定性标准差: {df_with_metrics1['answer_stability'].std():.3f}")
        
        # 统计各个指标的表现
        for metric in base_metric_names:
            col1 = f'json_{metric}_answer1'
            col2 = f'json_{metric}_answer2'
            
            if col1 in df_with_metrics1.columns and col2 in df_with_metrics1.columns:
                avg1 = df_with_metrics1[col1].mean()
                avg2 = df_with_metrics1[col2].mean()
                logger.info(f"{metric}: Answer1={avg1:.3f}, Answer2={avg2:.3f}")
        
        logger.info("重新分析完成!")
        return df_with_metrics1
        
    except Exception as e:
        logger.error(f"分析过程中发生错误: {str(e)}")
        raise

if __name__ == "__main__":
    # 使用最新的分析结果文件
    input_file = "qa_analysis_results/qa_analysis_results_20250710_123026.csv"
    output_file = "qa_analysis_results/qa_analysis_results_20250710_123026_json_metrics.csv"
    
    try:
        result_df = reanalyze_csv_with_json_metrics(input_file, output_file)
        print(f"成功完成重新分析，结果保存到: {output_file}")
        print(f"处理了 {len(result_df)} 行数据")
        
        # 显示前几行的关键指标
        print("\n=== 前5行关键指标预览 ===")
        key_columns = ['场景', 'average_quality', 'answer_stability']
        if all(col in result_df.columns for col in key_columns):
            print(result_df[key_columns].head())
        
    except Exception as e:
        print(f"执行失败: {str(e)}") 