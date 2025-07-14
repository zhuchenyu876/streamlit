#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from typing import Dict, List, Optional, Tuple
import pandas as pd
from tqdm import tqdm
import json
import requests
import time
from requests.exceptions import RequestException, Timeout, ConnectionError
import numpy as np
from datetime import datetime
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor, as_completed
import uuid

# 🧠 增强版LLM分析器 - 支持模拟模式和真实API
# 
# 模式说明：
# 1. DEMO_MODE = True  -> 使用模拟数据演示功能（无需API Key）
# 2. DEMO_MODE = False -> 使用真实LLM API分析（需要配置API Key）

import os
import json
import random
import asyncio
import aiohttp
from typing import Dict, List, Any, Optional
from datetime import datetime

# 🎯 模拟模式开关 - 设置为True可无需API体验功能
DEMO_MODE = True  # 设置为 False 以使用真实API

# 🔧 支持的LLM服务提供商
SUPPORTED_PROVIDERS = {
    'openai': {
        'name': 'OpenAI',
        'models': ['gpt-4o-mini', 'gpt-3.5-turbo', 'gpt-4'],
        'default_model': 'gpt-4o-mini'
    },
    'azure': {
        'name': 'Azure OpenAI',
        'models': ['gpt-4', 'gpt-35-turbo'],
        'default_model': 'gpt-4'
    },
    'ollama': {
        'name': 'Ollama (本地)',
        'models': ['llama2:7b', 'llama2:13b', 'codellama:7b'],
        'default_model': 'llama2:7b'
    }
}

class AdvancedLLMAnalyzer:
    """
    增强版LLM分析器，提供多维度准确性评估和agent评测功能
    """
    
    def __init__(self, config=None):
        """
        初始化增强版LLM分析器
        
        Args:
            config (dict): 分析器配置参数
        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        
        self.config = config or {}
        
        # 定义评估维度
        self.evaluation_dimensions = {
            'factual_accuracy': '事实准确性',
            'semantic_consistency': '语义一致性', 
            'business_logic_compliance': '业务逻辑符合性',
            'response_completeness': '回答完整性',
            'information_relevance': '信息相关性',
            'language_quality': '语言质量',
            'user_intent_fulfillment': '用户意图满足度',
            'technical_accuracy': '技术准确性',
            'context_understanding': '上下文理解',
            'professional_tone': '专业程度'
        }
        
        # 轮胎业务专门的评估维度
        self.tire_business_dimensions = {
            'tire_spec_accuracy': '轮胎规格准确性',
            'price_accuracy': '价格准确性',
            'stock_accuracy': '库存准确性',
            'brand_consistency': '品牌一致性',
            'service_info_accuracy': '服务信息准确性',
            'sales_process_compliance': '销售流程符合性'
        }

    def create_evaluation_prompt(self, reference: str, generated: str, evaluation_type: str = "comprehensive") -> str:
        """
        创建评估提示词
        
        Args:
            reference (str): 参考答案
            generated (str): 生成答案
            evaluation_type (str): 评估类型 ('comprehensive', 'tire_business', 'agent_comparison')
            
        Returns:
            str: 评估提示词
        """
        if evaluation_type == "comprehensive":
            return f"""
作为一个专业的AI质量评估专家，请对以下轮胎销售对话进行全面的质量评估。

**参考答案（标准答案）：**
{reference}

**生成答案（待评估答案）：**
{generated}

**评估要求：**
请从以下10个维度对生成答案进行评估，每个维度打分0-10分，并提供详细说明：

1. **事实准确性** (0-10分)：信息是否准确无误
2. **语义一致性** (0-10分)：语义是否与参考答案一致
3. **业务逻辑符合性** (0-10分)：是否符合轮胎销售业务逻辑
4. **回答完整性** (0-10分)：回答是否完整，没有遗漏关键信息
5. **信息相关性** (0-10分)：信息是否与用户问题相关
6. **语言质量** (0-10分)：语言表达是否清晰、专业
7. **用户意图满足度** (0-10分)：是否满足用户的实际需求
8. **技术准确性** (0-10分)：技术细节是否准确
9. **上下文理解** (0-10分)：是否正确理解对话上下文
10. **专业程度** (0-10分)：是否体现专业的销售服务水平

**特别关注：**
- 如果是JSON格式回答，检查JSON结构是否正确
- 轮胎规格信息（如185/65R15）是否准确
- 价格信息是否正确
- 库存信息是否准确
- 品牌信息是否一致

**输出格式：**
请严格按照以下JSON格式输出评估结果：

{{
    "factual_accuracy": {{"score": X, "explanation": "详细说明"}},
    "semantic_consistency": {{"score": X, "explanation": "详细说明"}},
    "business_logic_compliance": {{"score": X, "explanation": "详细说明"}},
    "response_completeness": {{"score": X, "explanation": "详细说明"}},
    "information_relevance": {{"score": X, "explanation": "详细说明"}},
    "language_quality": {{"score": X, "explanation": "详细说明"}},
    "user_intent_fulfillment": {{"score": X, "explanation": "详细说明"}},
    "technical_accuracy": {{"score": X, "explanation": "详细说明"}},
    "context_understanding": {{"score": X, "explanation": "详细说明"}},
    "professional_tone": {{"score": X, "explanation": "详细说明"}},
    "overall_score": X,
    "overall_assessment": "总体评估说明",
    "key_issues": ["主要问题1", "主要问题2"],
    "recommendations": ["改进建议1", "改进建议2"]
}}
"""
        
        elif evaluation_type == "tire_business":
            return f"""
作为轮胎销售业务专家，请专门评估以下轮胎销售对话的业务准确性。

**参考答案（标准答案）：**
{reference}

**生成答案（待评估答案）：**
{generated}

**专业业务评估要求：**
请从以下6个轮胎业务专门维度进行评估，每个维度打分0-10分：

1. **轮胎规格准确性** (0-10分)：轮胎规格信息是否准确
2. **价格准确性** (0-10分)：价格信息是否准确
3. **库存准确性** (0-10分)：库存信息是否准确
4. **品牌一致性** (0-10分)：品牌信息是否一致
5. **服务信息准确性** (0-10分)：安装、配送等服务信息是否准确
6. **销售流程符合性** (0-10分)：是否符合Grupo Magno的销售流程

**输出格式：**
{{
    "tire_spec_accuracy": {{"score": X, "explanation": "详细说明"}},
    "price_accuracy": {{"score": X, "explanation": "详细说明"}},
    "stock_accuracy": {{"score": X, "explanation": "详细说明"}},
    "brand_consistency": {{"score": X, "explanation": "详细说明"}},
    "service_info_accuracy": {{"score": X, "explanation": "详细说明"}},
    "sales_process_compliance": {{"score": X, "explanation": "详细说明"}},
    "business_overall_score": X,
    "business_assessment": "业务评估说明"
}}
"""
        
        elif evaluation_type == "agent_comparison":
            return f"""
作为AI Agent评估专家，请对这两个答案进行深度对比分析。

**参考答案（基准答案）：**
{reference}

**生成答案（待评估答案）：**
{generated}

**Agent对比评估要求：**
请从以下角度进行深度对比分析：

1. **答案质量对比**：哪个答案更好，为什么？
2. **准确性对比**：哪个答案更准确，具体差异在哪里？
3. **用户体验对比**：哪个答案用户体验更好？
4. **业务价值对比**：哪个答案更有商业价值？
5. **改进空间分析**：生成答案还有哪些改进空间？

**输出格式：**
{{
    "quality_comparison": "质量对比分析",
    "accuracy_comparison": "准确性对比分析", 
    "user_experience_comparison": "用户体验对比分析",
    "business_value_comparison": "业务价值对比分析",
    "improvement_suggestions": ["改进建议1", "改进建议2"],
    "winner": "reference/generated/tie",
    "confidence_level": "high/medium/low",
    "detailed_analysis": "详细分析说明"
}}
"""
        
        else:
            return self.create_evaluation_prompt(reference, generated, "comprehensive")

    def send_evaluation_request(self, prompt: str, timeout: int = 120, max_retries: int = 3) -> str:
        """
        发送评估请求到API - 优化504错误处理
        
        Args:
            prompt (str): 评估提示
            timeout (int): 超时时间（秒）- 增加到120秒应对504错误
            max_retries (int): 最大重试次数 - 保持3次
            
        Returns:
            str: API响应结果
        """
        
        for attempt in range(max_retries):
            try:
                # 记录请求开始
                self.logger.info(f"发送API请求 (尝试 {attempt + 1}/{max_retries})")
                
                response = requests.post(
                    self.config['url'],
                    json={
                        'username': self.config['username'],
                        'question': prompt,
                        'segment_code': str(uuid.uuid4())
                    },
                    timeout=timeout,
                    headers={
                        'cybertron-robot-key': self.config['robot_key'],
                        'cybertron-robot-token': self.config['robot_token'],
                        'Content-Type': 'application/json'
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('code') == '000000':
                        if 'data' in result and 'answer' in result['data']:
                            content = result['data']['answer']
                            self.logger.info(f"API请求成功 (尝试 {attempt + 1})")
                            return content
                        else:
                            content = str(result.get('data', {}))
                            self.logger.info(f"API请求成功 (尝试 {attempt + 1})")
                            return content
                    else:
                        error_msg = result.get('message', 'Unknown error')
                        self.logger.warning(f"API返回错误: {error_msg}")
                        raise Exception(f"API错误: {error_msg}")
                else:
                    self.logger.warning(f"HTTP错误: {response.status_code}")
                    raise Exception(f"HTTP错误: {response.status_code}")
                    
            except requests.exceptions.Timeout:
                self.logger.warning(f"尝试 {attempt + 1} 失败: 请求超时 ({timeout}秒)")
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 3  # 504错误增加等待时间
                    self.logger.info(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    raise Exception(f"API请求超时，已重试 {max_retries} 次")
                    
            except requests.exceptions.ConnectionError as e:
                self.logger.warning(f"尝试 {attempt + 1} 失败: 连接错误 - {str(e)}")
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 5  # 连接错误等待更长时间
                    self.logger.info(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    raise Exception(f"API连接失败，已重试 {max_retries} 次")
                    
            except Exception as e:
                self.logger.warning(f"尝试 {attempt + 1} 失败: {str(e)}")
                
                # 504错误特殊处理
                if "504" in str(e):
                    self.logger.warning("检测到504网关超时错误")
                    if attempt < max_retries - 1:
                        wait_time = (attempt + 1) * 5  # 504错误等待更长时间
                        self.logger.info(f"504错误重试策略：等待 {wait_time} 秒后重试...")
                        time.sleep(wait_time)
                    else:
                        raise Exception(f"504网关超时，已重试 {max_retries} 次。建议：1) 减少样本数量 2) 使用更简单的分析类型")
                else:
                    if attempt < max_retries - 1:
                        wait_time = (attempt + 1) * 3
                        self.logger.info(f"等待 {wait_time} 秒后重试...")
                        time.sleep(wait_time)
                    else:
                        raise Exception(f"API请求失败: {str(e)}")
        
        raise Exception(f"所有重试都失败了，请检查网络连接和API服务状态")

    def parse_evaluation_result(self, result_text: str, evaluation_type: str = "comprehensive") -> Dict:
        """
        解析评估结果
        
        Args:
            result_text (str): 评估结果文本
            evaluation_type (str): 评估类型
            
        Returns:
            Dict: 解析后的评估结果
        """
        try:
            # 尝试直接解析JSON
            if result_text.strip().startswith('{') and result_text.strip().endswith('}'):
                return json.loads(result_text)
            
            # 如果不是纯JSON，尝试提取JSON部分
            import re
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            
            # 解析失败，返回错误结果
            return self._get_error_evaluation_result(evaluation_type)
            
        except json.JSONDecodeError:
            self.logger.error(f"Failed to parse evaluation result: {result_text}")
            return self._get_error_evaluation_result(evaluation_type)

    def _get_error_evaluation_result(self, evaluation_type: str = "comprehensive") -> Dict:
        """
        获取错误评估结果
        
        Args:
            evaluation_type (str): 评估类型
            
        Returns:
            Dict: 错误评估结果
        """
        if evaluation_type == "comprehensive":
            return {
                "factual_accuracy": {"score": 0, "explanation": "评估失败"},
                "semantic_consistency": {"score": 0, "explanation": "评估失败"},
                "business_logic_compliance": {"score": 0, "explanation": "评估失败"},
                "response_completeness": {"score": 0, "explanation": "评估失败"},
                "information_relevance": {"score": 0, "explanation": "评估失败"},
                "language_quality": {"score": 0, "explanation": "评估失败"},
                "user_intent_fulfillment": {"score": 0, "explanation": "评估失败"},
                "technical_accuracy": {"score": 0, "explanation": "评估失败"},
                "context_understanding": {"score": 0, "explanation": "评估失败"},
                "professional_tone": {"score": 0, "explanation": "评估失败"},
                "overall_score": 0,
                "overall_assessment": "评估过程中发生错误",
                "key_issues": ["评估失败"],
                "recommendations": ["重新评估"]
            }
        elif evaluation_type == "tire_business":
            return {
                "tire_spec_accuracy": {"score": 0, "explanation": "评估失败"},
                "price_accuracy": {"score": 0, "explanation": "评估失败"},
                "stock_accuracy": {"score": 0, "explanation": "评估失败"},
                "brand_consistency": {"score": 0, "explanation": "评估失败"},
                "service_info_accuracy": {"score": 0, "explanation": "评估失败"},
                "sales_process_compliance": {"score": 0, "explanation": "评估失败"},
                "business_overall_score": 0,
                "business_assessment": "评估过程中发生错误"
            }
        elif evaluation_type == "agent_comparison":
            return {
                "quality_comparison": "评估失败",
                "accuracy_comparison": "评估失败",
                "user_experience_comparison": "评估失败", 
                "business_value_comparison": "评估失败",
                "improvement_suggestions": ["重新评估"],
                "winner": "unknown",
                "confidence_level": "low",
                "detailed_analysis": "评估过程中发生错误"
            }
        else:
            return {"error": "Unknown evaluation type"}

    def comprehensive_analyze(self, reference: str, generated: str) -> Dict:
        """
        全面分析单个答案对
        
        Args:
            reference (str): 参考答案
            generated (str): 生成答案
            
        Returns:
            Dict: 全面分析结果
        """
        # 1. 综合评估
        comprehensive_prompt = self.create_evaluation_prompt(reference, generated, "comprehensive")
        comprehensive_result = self.send_evaluation_request(comprehensive_prompt)
        comprehensive_analysis = self.parse_evaluation_result(comprehensive_result, "comprehensive")
        
        # 2. 业务专门评估
        business_prompt = self.create_evaluation_prompt(reference, generated, "tire_business")
        business_result = self.send_evaluation_request(business_prompt)
        business_analysis = self.parse_evaluation_result(business_result, "tire_business")
        
        # 3. Agent对比评估
        comparison_prompt = self.create_evaluation_prompt(reference, generated, "agent_comparison")
        comparison_result = self.send_evaluation_request(comparison_prompt)
        comparison_analysis = self.parse_evaluation_result(comparison_result, "agent_comparison")
        
        # 合并结果
        return {
            "comprehensive_analysis": comprehensive_analysis,
            "business_analysis": business_analysis,
            "comparison_analysis": comparison_analysis,
            "analysis_timestamp": datetime.now().isoformat()
        }

    def batch_analyze_dataframe(self, df: pd.DataFrame, ref_col: str, gen_col: str, 
                              analysis_type: str = "comprehensive",
                              progress_callback=None, pause_check_callback=None) -> pd.DataFrame:
        """
        批量分析DataFrame
        
        Args:
            df (pd.DataFrame): 数据框
            ref_col (str): 参考答案列名
            gen_col (str): 生成答案列名
            analysis_type (str): 分析类型
            progress_callback: 进度回调
            pause_check_callback: 暂停检查回调
            
        Returns:
            pd.DataFrame: 添加了分析结果的数据框
        """
        results = []
        
        for idx, row in tqdm(df.iterrows(), total=len(df), desc=f"执行{analysis_type}分析"):
            # 先更新进度（显示当前正在处理的样本）
            if progress_callback:
                progress_callback(idx, len(df))
            
            # 检查暂停
            if pause_check_callback and not pause_check_callback(0.95, f"正在执行增强LLM分析: {idx + 1}/{len(df)}"):
                import streamlit as st
                while st.session_state.get('analysis_paused', False):
                    time.sleep(1)
                    if not st.session_state.get('analysis_running', False):
                        # 分析被停止，返回部分结果
                        if results:
                            self._add_partial_results_to_df(df, results, analysis_type)
                        return df
            
            try:
                # 记录开始处理
                self.logger.info(f"开始处理样本 {idx + 1}/{len(df)}")
                
                if analysis_type == "comprehensive":
                    result = self.comprehensive_analyze(str(row[ref_col]), str(row[gen_col]))
                elif analysis_type == "business_only":
                    prompt = self.create_evaluation_prompt(str(row[ref_col]), str(row[gen_col]), "tire_business")
                    result_text = self.send_evaluation_request(prompt)
                    result = self.parse_evaluation_result(result_text, "tire_business")
                elif analysis_type == "comparison_only":
                    prompt = self.create_evaluation_prompt(str(row[ref_col]), str(row[gen_col]), "agent_comparison")
                    result_text = self.send_evaluation_request(prompt)
                    result = self.parse_evaluation_result(result_text, "agent_comparison")
                else:
                    result = self.comprehensive_analyze(str(row[ref_col]), str(row[gen_col]))
                
                results.append(result)
                
                # 记录完成处理
                self.logger.info(f"完成处理样本 {idx + 1}/{len(df)}")
                
            except Exception as e:
                # 处理API错误
                self.logger.error(f"处理样本 {idx + 1} 时发生错误: {str(e)}")
                
                # 添加错误结果
                error_result = self._get_error_evaluation_result(analysis_type)
                results.append(error_result)
                
                # 如果是严重错误，考虑停止分析
                if "timeout" in str(e).lower() or "connection" in str(e).lower():
                    self.logger.error(f"检测到严重错误，停止分析: {str(e)}")
                    break
            
            # 控制请求频率
            time.sleep(0.5) # 减少请求间隔
            
            # 更新进度（显示已完成的样本）
            if progress_callback:
                progress_callback(idx + 1, len(df))
            
            # 每10行记录一次进度
            if (idx + 1) % 10 == 0:
                self.logger.info(f"已完成增强LLM分析 {idx + 1}/{len(df)} 行")
        
        # 添加结果到DataFrame
        self._add_results_to_df(df, results, analysis_type)
        
        return df

    def _add_results_to_df(self, df: pd.DataFrame, results: List[Dict], analysis_type: str):
        """
        将分析结果添加到DataFrame
        
        Args:
            df (pd.DataFrame): 数据框
            results (List[Dict]): 分析结果列表
            analysis_type (str): 分析类型
        """
        if analysis_type == "comprehensive":
            for i, result in enumerate(results):
                # 综合分析结果
                comp_analysis = result.get('comprehensive_analysis', {})
                for dim, chinese_name in self.evaluation_dimensions.items():
                    if dim in comp_analysis:
                        df.loc[i, f'llm_{dim}_score'] = comp_analysis[dim].get('score', 0)
                        df.loc[i, f'llm_{dim}_explanation'] = comp_analysis[dim].get('explanation', '')
                
                df.loc[i, 'llm_overall_score'] = comp_analysis.get('overall_score', 0)
                df.loc[i, 'llm_overall_assessment'] = comp_analysis.get('overall_assessment', '')
                
                # 业务分析结果
                bus_analysis = result.get('business_analysis', {})
                for dim, chinese_name in self.tire_business_dimensions.items():
                    if dim in bus_analysis:
                        df.loc[i, f'llm_business_{dim}_score'] = bus_analysis[dim].get('score', 0)
                        df.loc[i, f'llm_business_{dim}_explanation'] = bus_analysis[dim].get('explanation', '')
                
                df.loc[i, 'llm_business_overall_score'] = bus_analysis.get('business_overall_score', 0)
                
                # 对比分析结果
                comp_analysis = result.get('comparison_analysis', {})
                df.loc[i, 'llm_comparison_winner'] = comp_analysis.get('winner', 'unknown')
                df.loc[i, 'llm_comparison_confidence'] = comp_analysis.get('confidence_level', 'low')
                df.loc[i, 'llm_detailed_analysis'] = comp_analysis.get('detailed_analysis', '')

    def _add_partial_results_to_df(self, df: pd.DataFrame, results: List[Dict], analysis_type: str):
        """
        添加部分结果到DataFrame（当分析被中断时）
        
        Args:
            df (pd.DataFrame): 数据框
            results (List[Dict]): 部分分析结果
            analysis_type (str): 分析类型
        """
        self._add_results_to_df(df, results, analysis_type)
        
        # 为未完成的行添加默认值
        for i in range(len(results), len(df)):
            if analysis_type == "comprehensive":
                for dim in self.evaluation_dimensions.keys():
                    df.loc[i, f'llm_{dim}_score'] = 0
                    df.loc[i, f'llm_{dim}_explanation'] = '分析被中断'
                
                df.loc[i, 'llm_overall_score'] = 0
                df.loc[i, 'llm_overall_assessment'] = '分析被中断'

    def generate_analysis_report(self, df: pd.DataFrame) -> Dict:
        """
        生成分析报告
        
        Args:
            df (pd.DataFrame): 包含分析结果的数据框
            
        Returns:
            Dict: 分析报告
        """
        report = {
            "总样本数": len(df),
            "分析时间": datetime.now().isoformat(),
            "综合评估结果": {},
            "业务评估结果": {},
            "对比评估结果": {},
            "改进建议": []
        }
        
        # 综合评估统计
        for dim in self.evaluation_dimensions.keys():
            col_name = f'llm_{dim}_score'
            if col_name in df.columns:
                scores = pd.to_numeric(df[col_name], errors='coerce').fillna(0)
                report["综合评估结果"][dim] = {
                    "平均分": scores.mean(),
                    "最高分": scores.max(),
                    "最低分": scores.min(),
                    "标准差": scores.std()
                }
        
        # 业务评估统计
        for dim in self.tire_business_dimensions.keys():
            col_name = f'llm_business_{dim}_score'
            if col_name in df.columns:
                scores = pd.to_numeric(df[col_name], errors='coerce').fillna(0)
                report["业务评估结果"][dim] = {
                    "平均分": scores.mean(),
                    "最高分": scores.max(),
                    "最低分": scores.min(),
                    "标准差": scores.std()
                }
        
        # 对比评估统计
        if 'llm_comparison_winner' in df.columns:
            winner_counts = df['llm_comparison_winner'].value_counts()
            report["对比评估结果"] = {
                "reference获胜": winner_counts.get('reference', 0),
                "generated获胜": winner_counts.get('generated', 0),
                "平局": winner_counts.get('tie', 0),
                "未知": winner_counts.get('unknown', 0)
            }
        
        return report

if __name__ == "__main__":
    # 测试代码
    config = {
        'url': 'https://agents.dyna.ai/openapi/v1/conversation/dialog/',
        'username': 'marshall.ting@dyna.ai',
        'robot_key': 'f79sd16wABIqwLe%2FzjGeZGDRMUo%3D',
        'robot_token': 'MTczODkxMDA0MzUwMgp1cjRVVnF4Y0w3Y2hwRmU3RmxFUXFQV05lSGc9'
    }
    
    analyzer = AdvancedLLMAnalyzer(config)
    
    # 测试数据
    reference = '{"type": "markdown", "data": "| ID Producto | Nombre del Producto | Stock | Precio |\\n|:------------|:--------------------|:------|:-------|\\n| LL-C30210 | 185 65 15 COMPASAL BLAZER HP 88H | 8 | $1142 |\\n", "desc": "🔍 Resultados de búsqueda\\n\\n📊 Encontrados: 1 productos\\n💰 Precio: $1142\\n\\n¿Cuál modelo le interesa?"}'
    generated = '{"type": "markdown", "data": "| ID Producto | Nombre del Producto | Stock | Precio |\\n|:------------|:--------------------|:------|:-------|\\n| LL-C30210 | 185 65 15 COMPASAL BLAZER HP 88H | 8 | $1142 |\\n", "desc": "🔍 Resultados de búsqueda\\n\\n📊 Encontrados: 1 productos\\n💰 Precio: $1142\\n\\n¿Cuál modelo le interesa?"}'
    
    # 执行分析
    result = analyzer.comprehensive_analyze(reference, generated)
    print("增强LLM分析结果:")
    print(json.dumps(result, indent=2, ensure_ascii=False)) 