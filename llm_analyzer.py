import logging
from typing import Dict
import pandas as pd
from tqdm import tqdm
import json
import requests
import time
from requests.exceptions import RequestException, Timeout, ConnectionError

def evluation_chat(question: str, config: Dict, timeout: int = 60, max_retries: int = 3) -> str:
    """
    发送问题到评估聊天端点，带有超时和重试机制。
    
    Args:
        question (str): 要发送的问题。
        config (Dict): 配置参数，包括url、username、robot_key、robot_token。
        timeout (int): 请求超时时间（秒）。
        max_retries (int): 最大重试次数。
        
    Returns:
        str: 响应文本或错误消息。
    """
    url = config.get('url', "https://agents.dyna.ai/openapi/v1/conversation/dialog/")
    headers = {
        'CYBERTRON-ROBOT-KEY': config.get('robot_key', 'f79sd16wABIqwLe%2FzjGeZGDRMUo%3D'),
        'CYBERTRON-ROBOT-TOKEN': config.get('robot_token', 'MTczODkxMDA0MzUwMgp1cjRVVnF4Y0w3Y2hwRmU3RmxFUXFQV05lSGc9'),
        'Content-Type': 'application/json'
    }
    data = {
        "username": config.get('username', "marshall.ting@dyna.ai"),
        "question": question
    }
    
    for attempt in range(max_retries):
        try:
            with requests.Session() as session:
                response = session.post(url, headers=headers, json=data, timeout=timeout)
                response.raise_for_status()
                result = response.json()
                if result.get('code') == '000000':
                    if 'data' in result and 'answer' in result['data']:
                        return result['data']['answer']
                    return str(result.get('data', {}))
                return f"Error code: {result.get('code')}, Message: {result.get('message')}"
        except (RequestException, ValueError, Timeout, ConnectionError) as e:
            logging.error(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # 指数退避
            else:
                return f"Request failed after {max_retries} attempts: {str(e)}"
    return "Failed to get response after multiple attempts"

class LLMAnalyzer:
    def __init__(self, config=None):
        """
        初始化LLMAnalyzer类。
        配置日志记录以跟踪分析过程。
        
        Args:
            config (dict): 分析器配置参数，包括url、username、robot_key、robot_token
        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # 如果没有处理器，添加一个默认的处理器
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        
        # 存储配置
        self.config = config or {}

    def analyze_text_pair(self, reference: str, answer: str) -> Dict:
        """
        分析参考答案和生成答案对。
        
        Args:
            reference (str): 参考答案
            answer (str): 生成答案
            
        Returns:
            Dict: 包含分析结果的字典
        """
        question = f"""
参考答案：{reference}
生成答案：{answer}
"""

        try:
            response = evluation_chat(question, self.config)
            return self._parse_response(response)
        except Exception as e:
            self.logger.error(f"Error analyzing text pair: {str(e)}")
            return self._get_error_result()

    def analyze_dataframe(self, df: pd.DataFrame, ref_col: str, ans_col: str, progress_callback=None, pause_check_callback=None) -> pd.DataFrame:
        """
        分析DataFrame中的所有文本对。
        
        Args:
            df (pd.DataFrame): 输入数据框
            ref_col (str): 参考答案列名
            ans_col (str): 生成答案列名
            progress_callback (callable, optional): 进度回调函数
            pause_check_callback (callable, optional): 暂停检查回调函数
            
        Returns:
            pd.DataFrame: 添加了分析结果的数据框
        """
        results = []
        for idx, row in tqdm(df.iterrows(), total=len(df), desc="分析进度"):
            # Check for pause before processing each item
            if pause_check_callback and not pause_check_callback(0.9, f"正在进行LLM分析: {idx + 1}/{len(df)}"):
                # Analysis was paused, wait until resumed
                import streamlit as st
                while st.session_state.get('analysis_paused', False):
                    time.sleep(1)
                    if not st.session_state.get('analysis_running', False):
                        # Analysis was stopped, return partial results
                        if results:
                            # Add partial results to DataFrame
                            for key in results[0].keys():
                                df[key] = [result[key] for result in results] + [self._get_error_result()[key]] * (len(df) - len(results))
                        return df
            
            result = self.analyze_text_pair(str(row[ref_col]), str(row[ans_col]))
            time.sleep(1)  # 限制请求速率
            results.append(result)
            
            # 每100行记录一次进度
            if (idx + 1) % 100 == 0:
                self.logger.info(f"已完成 {idx + 1}/{len(df)} 行的分析")
            
            # 更新进度回调
            if progress_callback:
                progress_callback(idx + 1, len(df))

        # 将结果添加到DataFrame
        for key in results[0].keys():
            df[key] = [result[key] for result in results]
        
        return df

    def _parse_response(self, response_text: str) -> Dict:
        """解析响应文本"""
        try:
            # 首先尝试直接解析JSON
            return json.loads(response_text)
        except json.JSONDecodeError:
            # JSON解析失败时，使用行解析方法
            result = {}
            lines = response_text.split("\n")
            for line in lines:
                if "语义篡改:" in line:
                    result["语义篡改"] = line.split(":")[1].strip()
                elif "语义篡改说明:" in line:
                    result["语义篡改说明"] = line.split(":")[1].strip()
                elif "缺失关键信息:" in line:
                    result["缺失关键信息"] = line.split(":")[1].strip()
                elif "缺失关键信息说明:" in line:
                    result["缺失关键信息说明"] = line.split(":")[1].strip()
                elif "生成无关信息:" in line:
                    result["生成无关信息"] = line.split(":")[1].strip()
                elif "生成无关信息说明:" in line:
                    result["生成无关信息说明"] = line.split(":")[1].strip()
            return result if result else self._get_error_result()

    def _get_error_result(self) -> Dict:
        """返回错误结果字典"""
        return {
            "语义篡改": "错误",
            "语义篡改说明": "分析过程中发生错误",
            "缺失关键信息": "错误",
            "缺失关键信息说明": "分析过程中发生错误",
            "生成无关信息": "错误",
            "生成无关信息说明": "分析过程中发生错误"
        }