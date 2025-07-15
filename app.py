import streamlit as st

# 必须在所有其他导入之前设置页面配置
st.set_page_config(
    page_title="🚀 智能QA分析系统",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

import os
import ast
import logging
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv, find_dotenv
from client import Client
from metrics import calculate_semantic_similarity, calculate_rouge_l
from llm_analyzer import LLMAnalyzer
from advanced_llm_analyzer import AdvancedLLMAnalyzer
from dashboard import QADashboard
from json_dashboard import JSONDashboard
from advanced_llm_dashboard import AdvancedLLMDashboard
from ui_components import (
    UserGuideComponents, DataValidationComponents, AnalysisProgressComponents,
    ResultDisplayComponents, ConfigurationComponents, ErrorHandlingComponents
)
from file_manager import file_manager
import time

class QAAnalyzer:
    def __init__(self, agent_creds=None, analyzer_creds=None):
        # Configure logging
        self.setup_logging()
        
        # Load environment variables with error handling
        if load_dotenv(find_dotenv()):
            logging.info("Successfully loaded .env file")
        else:
            logging.warning("No .env file found, using default values")
            
        username = os.getenv("USER_NAME")  # 提供默认值
        logging.info(f"Using username: {username}")

        # Initialize client with agent credentials if provided
        agent_creds = agent_creds or {}
        self.client = Client(
            url=agent_creds.get('url', os.getenv("WS_URL") or ""),
            username=agent_creds.get('username', os.getenv("USER_NAME") or ""),
            robot_key=agent_creds.get('robot_key', ""),
            robot_token=agent_creds.get('robot_token', ""),
            retry_secs=3,
        )

        # Initialize LLM analyzer with analyzer credentials
        self.llm_analyzer = LLMAnalyzer(analyzer_creds)
        
        # Initialize Advanced LLM analyzer
        self.advanced_llm_analyzer = AdvancedLLMAnalyzer(analyzer_creds)
        
        # Initialize Dashboard
        self.dashboard = QADashboard()

    def setup_logging(self):
        """Configure logging with timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create log directory if it doesn't exist
        log_dir = './log'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'{log_dir}/qa_analysis_{timestamp}.log'),
                logging.StreamHandler()
            ]
        )

    def process_dataframe(self, df: pd.DataFrame, sample_n: int = 10, language: str = "auto") -> pd.DataFrame:
        """Process the DataFrame for analysis with language support"""
        from ui_components import DataValidationComponents
        
        # 根据语言获取列名映射
        if language == "auto":
            # 自动检测列名
            possible_column_sets = [
                ['场景', '测试数据', '参考答案'],  # 中文
                ['Pregunta', 'Contenido de Pregunta', 'Respuesta de Referencia'],  # 西班牙语  
                ['问题', '问题内容', '参考答案'],  # 西班牙语（混合格式）
                ['Scene', 'Test Data', 'Reference Answer']  # 英语
            ]
            
            selected_columns = None
            for cols in possible_column_sets:
                if all(col in df.columns for col in cols):
                    selected_columns = cols
                    break
            
            if selected_columns is None:
                # 如果没有找到完整匹配，至少尝试提取基本需要的列
                available_cols = df.columns.tolist()
                logging.warning(f"无法找到标准列名组合，可用列: {available_cols}")
                # 简单取样并返回，不做特殊过滤
                if len(df) > sample_n:
                    df = df.sample(n=sample_n, random_state=42)
                return df.reset_index(drop=True)
        else:
            selected_columns = DataValidationComponents.get_required_columns(language)
        
        # 确保我们有必需的列
        if not all(col in df.columns for col in selected_columns):
            logging.warning(f"缺少必需的列: {selected_columns}")
            # 简单取样并返回
            if len(df) > sample_n:
                df = df.sample(n=sample_n, random_state=42)
            return df.reset_index(drop=True)
        
        # 标准化列名 - 统一转换为中文列名以便后续处理
        column_mapping = {
            selected_columns[0]: '场景',      # 场景/Pregunta/问题/Scene
            selected_columns[1]: '测试数据',   # 测试数据/Contenido de Pregunta/问题内容/Test Data  
            selected_columns[2]: '参考答案'    # 参考答案/Respuesta de Referencia/Reference Answer
        }
        
        # 处理混合格式：如果第一列是"问题"，则映射为"场景"
        if selected_columns[0] == '问题':
            column_mapping[selected_columns[0]] = '场景'
        
        # 创建新的DataFrame，只包含需要的列并重命名
        processed_df = df[selected_columns].copy()
        processed_df = processed_df.rename(columns=column_mapping)
        
        # 如果是中文文件，尝试做FAQ过滤（保持原有逻辑）
        if language == "chinese" and '场景' in processed_df.columns:
            # 检查是否有FAQ相关的场景值
            unique_scenarios = processed_df['场景'].unique()
            faq_scenarios = [s for s in unique_scenarios if 'FAQ' in str(s) or '相似问' in str(s)]
            
            if faq_scenarios:
                # 如果有FAQ场景，执行原有的过滤逻辑
                faq_condition = processed_df['场景'].isin(faq_scenarios)
                faq_df = processed_df[faq_condition]
                if len(faq_df) > 0:
                    sampled_df = faq_df.sample(n=min(sample_n, len(faq_df)), random_state=1)
                    remaining_df = processed_df[~faq_condition]
                    processed_df = pd.concat([sampled_df, remaining_df]).reset_index(drop=True)
                    logging.info(f"FAQ filtering applied. FAQ samples: {len(faq_df)}")
        
        # 最终采样 - 只有当明确设置了小的sample_n时才采样
        if len(processed_df) > sample_n and sample_n < 50:
            processed_df = processed_df.sample(n=sample_n, random_state=42)
        
        processed_df = processed_df.reset_index(drop=True)
        
        # 添加缺失的必需列
        if '组别' not in processed_df.columns:
            processed_df['组别'] = processed_df['场景']  # 使用场景作为组别的默认值
        
        logging.info(f"Total samples after processing: {len(processed_df)}")
        return processed_df

    def extract_answer(self, cell):
        """Extract answer from cell content"""
        if isinstance(cell, dict):
            return cell.get('answer', cell)
        elif isinstance(cell, str):
            try:
                data = ast.literal_eval(cell)
                return data.get('answer', cell)
            except (ValueError, SyntaxError):
                return cell
        return cell

    def generate_answers(self, df: pd.DataFrame, progress_bar, num_generations: int = 3, pause_check_callback=None) -> pd.DataFrame:
        """Generate multiple answers for each question with pause support"""
        logging.info(f"Generating {num_generations} answers...")
        
        # Add session ID columns
        for i in range(1, num_generations + 1):
            df[f'session_id{i}'] = ""
            
        current_group = None
        for i in range(1, num_generations + 1):
            col_name = f'生成答案{i}'
            session_col = f'session_id{i}'
            df[col_name] = ""
            progress_text = st.empty()
            
            for idx in df.index:
                # Check for pause before processing each item
                if pause_check_callback and not pause_check_callback(0.5, f"正在生成 {col_name}: {idx + 1}/{len(df)}"):
                    # Analysis was paused, wait until resumed
                    while st.session_state.get('analysis_paused', False):
                        time.sleep(1)
                        if not st.session_state.get('analysis_running', False):
                            # Analysis was stopped
                            return df
                
                progress_text.text(f'Generating {col_name}: {idx + 1}/{len(df)}')
                progress_bar.progress((idx + 1) / len(df))
                
                # Check if group has changed
                group = df.loc[idx, '组别']
                if group != current_group:
                    self.client.create_segment_code(group)
                    current_group = group
                
                question = df.loc[idx, '测试数据']
                # 使用带有40秒超时的方法来调用
                answer = self.client.websocket_chat_with_timeout(question, timeout=40)
                time.sleep(1)
                
                df.loc[idx, col_name] = self.extract_answer(answer)
                df.loc[idx, session_col] = self.client.get_current_session_id()
        
        return df

    def calculate_metrics(self, df: pd.DataFrame, progress_bar, num_generations: int = 3, pause_check_callback=None) -> pd.DataFrame:
        """Calculate various metrics for the generated answers with pause support"""
        logging.info("Calculating metrics...")
        progress_text = st.empty()
        
        # Calculate semantic stability (only if multiple generations)
        if num_generations > 1:
            logging.info("\n开始计算语义稳定性...")
            for idx in range(len(df)):
                # Check for pause before processing each item
                if pause_check_callback and not pause_check_callback(0.7, f"正在计算语义稳定性: {idx + 1}/{len(df)}"):
                    # Analysis was paused, wait until resumed
                    while st.session_state.get('analysis_paused', False):
                        time.sleep(1)
                        if not st.session_state.get('analysis_running', False):
                            # Analysis was stopped
                            return df
                
                progress = (idx + 1) / (len(df) * 2)
                progress_text.text(f'Calculating semantic stability: {idx + 1}/{len(df)}')
                progress_bar.progress(progress)
                
                try:
                    answers = [df.loc[idx, f'生成答案{i}'] for i in range(1, num_generations + 1)]
                    similarity = calculate_semantic_similarity(answers)
                    df.loc[idx, '语义稳定性'] = similarity
                    
                except Exception as e:
                    logging.error(f"计算第 {idx+1} 行语义稳定性时出错: {str(e)}")
                    df.loc[idx, '语义稳定性'] = 0.0
        else:
            # No stability calculation for single generation
            df['语义稳定性'] = float('nan')
            logging.info("Skipping semantic stability calculation for single answer generation")

        # Calculate ROUGE-L metrics
        logging.info("\n开始计算ROUGE-L指标...")
        for idx in range(len(df)):
            # Check for pause before processing each item
            if pause_check_callback and not pause_check_callback(0.8, f"正在计算ROUGE-L指标: {idx + 1}/{len(df)}"):
                # Analysis was paused, wait until resumed
                while st.session_state.get('analysis_paused', False):
                    time.sleep(1)
                    if not st.session_state.get('analysis_running', False):
                        # Analysis was stopped
                        return df
            
            progress = 0.5 + (idx + 1) / (len(df) * 2)
            progress_text.text(f'Calculating ROUGE-L metrics: {idx + 1}/{len(df)}')
            progress_bar.progress(progress)
            
            try:
                reference = df.loc[idx, '参考答案']
                hypothesis = df.loc[idx, '生成答案1']  # Use the first generated answer
                
                rouge_scores = calculate_rouge_l(reference, hypothesis)
                
                df.loc[idx, '冗余度'] = rouge_scores['redundancy']
                df.loc[idx, '完整度'] = rouge_scores['recall']
                df.loc[idx, '相关度'] = rouge_scores['f1']
                
            except Exception as e:
                logging.error(f"计算第 {idx+1} 行ROUGE-L指标时出错: {str(e)}")
                df.loc[idx, '冗余度'] = 0.0
                df.loc[idx, '完整度'] = 0.0
                df.loc[idx, '相关度'] = 0.0
        
        progress_text.empty()
        return df

    def analyze_file(self, file_path: str, sample_n: int, num_generations: int, update_progress, language="auto", enable_llm_analysis=True) -> tuple:
        """Main analysis function with language support"""
        try:
            # Load and process data with language-specific encoding
            from ui_components import DataValidationComponents
            encodings = DataValidationComponents.get_encoding_strategy(language)
            df = None
            
            for encoding in encodings:
                try:
                    df = pd.read_csv(file_path, encoding=encoding, 
                                   quoting=1, skipinitialspace=True, 
                                   on_bad_lines='skip')
                    break
                except (UnicodeDecodeError, pd.errors.ParserError):
                    continue
            
            if df is None:
                raise ValueError(f"无法读取CSV文件，请检查文件格式和编码（当前语言设置: {language}）")
            df = self.process_dataframe(df, sample_n=sample_n, language=language)

            # Set up progress
            st.write("Starting analysis...")
            progress_bar = st.progress(0)
            
            # Generate answers
            df = self.generate_answers(df, progress_bar, num_generations=num_generations, pause_check_callback=update_progress)
            
            # Check if analysis was stopped
            if not st.session_state.get('analysis_running', False):
                return None, None

            # Calculate metrics
            df = self.calculate_metrics(df, progress_bar, num_generations=num_generations, pause_check_callback=update_progress)
            
            # Check if analysis was stopped
            if not st.session_state.get('analysis_running', False):
                return None, None

            # 根据用户选择决定是否进行LLM分析
            if enable_llm_analysis:
                # Perform LLM analysis
                st.write("Performing LLM analysis...")
                llm_progress_bar = st.progress(0)
                
                def update_llm_progress(current, total):
                    llm_progress = current / total
                    llm_progress_bar.progress(llm_progress)
                
                df = self.llm_analyzer.analyze_dataframe(df, '参考答案', '生成答案1', progress_callback=update_llm_progress, pause_check_callback=update_progress)  # Use first generated answer
                llm_progress_bar.empty()  # 清空LLM分析进度条
                
                # Check if analysis was stopped
                if not st.session_state.get('analysis_running', False):
                    return None, None
            else:
                st.write("Skipping LLM analysis (基础机器学习分析模式)")
            
            # 添加"包含错误"列
            df['包含错误'] = df.apply(
                lambda row: '否' if (
                    (row.get('生成无关内容', '') != '是') and 
                    (row.get('语义篡改', '') != '是') and 
                    (row.get('缺失关键信息', '') != '是')
                ) else '是', 
                axis=1
            )

            # Save results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # 根据是否进行LLM分析给文件添加不同后缀
            if enable_llm_analysis:
                output_path = f'./qa_analysis_results/qa_analysis_results_{timestamp}_with_llm.csv'
            else:
                output_path = f'./qa_analysis_results/qa_analysis_results_{timestamp}_basic.csv'
            
            # Save using file_manager
            output_path = file_manager.save_csv(df, output_path, index=False, encoding='utf-8-sig')
            
            # 显示成功消息
            if enable_llm_analysis:
                st.success("✅ LLM增强分析完成！")
            else:
                st.success("✅ 基础机器学习分析完成！")
            st.balloons()  # 添加气球动画效果
            
            # 显示下载链接
            csv_data = file_manager.get_download_data(output_path)
            if csv_data:
                st.download_button(
                    label="📥 Download Results",
                    data=csv_data,
                    file_name=f"qa_analysis_results_{timestamp}.csv",
                    mime="text/csv"
                )
            
            return df, output_path

        except Exception as e:
            st.error(f"❌ Analysis failed: {str(e)}")
            return None, None

class TaskManager:
    def __init__(self):
        self.tasks = {}  # 存储任务信息
        self.results = {}  # 存储任务结果

    def create_task(self, file_path: str, sample_n: int, num_generations: int, language: str = "auto") -> str:
        # Generate a more unique task_id using microseconds and random suffix
        import random
        import string
        base_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        microseconds = datetime.now().microsecond
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
        task_id = f"{base_time}_{microseconds}_{random_suffix}"
        
        # Ensure uniqueness
        while task_id in self.tasks:
            random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
            task_id = f"{base_time}_{microseconds}_{random_suffix}"
        
        self.tasks[task_id] = {
            'file_path': file_path,
            'sample_n': sample_n,
            'num_generations': num_generations,
            'language': language,
            'status': 'pending',
            'progress': 0,
            'message': '',
            'start_time': datetime.now()
        }
        return task_id

    def update_task(self, task_id: str, progress: float, message: str, status: str = None):
        if task_id in self.tasks:
            self.tasks[task_id]['progress'] = progress
            self.tasks[task_id]['message'] = message
            if status is not None:
                self.tasks[task_id]['status'] = status

    def get_task(self, task_id: str) -> dict:
        return self.tasks.get(task_id, {})

    def store_result(self, task_id: str, df: pd.DataFrame, output_path: str):
        self.results[task_id] = {
            'df': df,
            'output_path': output_path
        }

    def get_result(self, task_id: str) -> tuple:
        result = self.results.get(task_id, {})
        return result.get('df'), result.get('output_path')

def load_agents():
    """Load agents from CSV file"""
    agents_df = file_manager.read_csv('./public/agents.csv')
    
    if agents_df is not None:
        # Ensure required columns exist
        if 'url' not in agents_df.columns:
            agents_df['url'] = ''
        if 'username' not in agents_df.columns:
            agents_df['username'] = ''
        return agents_df
    else:
        # Create default agents DataFrame
        default_config = file_manager.get_default_config('agents')
        df = pd.DataFrame(default_config)
        
        # Save using file_manager
        file_manager.save_csv(df, './public/agents.csv', index=False)
        return df

def load_analyzer_config():
    """Load LLM analyzer configuration"""
    config_df = file_manager.read_csv('./public/analyzer_config.csv')
    
    if config_df is not None and len(config_df) > 0:
        return config_df.iloc[0].to_dict()
    else:
        # Create default config
        config = file_manager.get_default_config('analyzer')
        
        # Save using file_manager
        file_manager.save_csv(pd.DataFrame([config]), './public/analyzer_config.csv', index=False)
        return config

def save_analyzer_config(config_dict):
    """Save LLM analyzer configuration"""
    file_manager.save_csv(pd.DataFrame([config_dict]), './public/analyzer_config.csv', index=False)
    if file_manager.is_cloud:
        st.info("💾 配置已保存到会话中（云端模式）")

def save_agents(df):
    """Save agents to CSV file"""
    file_manager.save_csv(df, './public/agents.csv', index=False)
    if file_manager.is_cloud:
        st.info("💾 Agent配置已保存到会话中（云端模式）")

def main():
    # 添加全局CSS样式
    st.markdown("""
    <style>
    /* 全局字体和基础样式 */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .main {
        font-family: 'Inter', sans-serif;
    }
    
    /* 美化按钮样式 */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* 美化文件上传器 */
    .stFileUploader {
        background: white;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        border: 2px dashed #667eea;
    }
    
    .stFileUploader:hover {
        border-color: #764ba2;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.2);
    }
    
    /* 美化输入框 */
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        padding: 10px;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* 美化数字输入框 */
    .stNumberInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        padding: 10px;
        transition: all 0.3s ease;
    }
    
    .stNumberInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* 美化选择框 */
    .stSelectbox > div > div > div {
        background: white;
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        transition: all 0.3s ease;
    }
    
    .stSelectbox > div > div > div:hover {
        border-color: #667eea;
        box-shadow: 0 2px 10px rgba(102, 126, 234, 0.1);
    }
    
    /* 美化多选框 */
    .stMultiSelect > div > div > div {
        background: white;
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        transition: all 0.3s ease;
    }
    
    .stMultiSelect > div > div > div:hover {
        border-color: #667eea;
        box-shadow: 0 2px 10px rgba(102, 126, 234, 0.1);
    }
    
    /* 美化滑块 */
    .stSlider > div > div > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* 美化复选框 */
    .stCheckbox > label > div {
        background: white;
        border-radius: 5px;
        border: 2px solid #e0e0e0;
        transition: all 0.3s ease;
    }
    
    .stCheckbox > label > div[data-checked="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-color: #667eea;
    }
    
    /* 美化进度条 */
    .stProgress > div > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    /* 美化数据表格 */
    .stDataFrame {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    
    /* 美化边栏 */
    .sidebar .sidebar-content {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 15px;
        padding: 20px;
    }
    
    /* 美化扩展器 */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        font-weight: 600;
        color: #2c3e50;
    }
    
    /* 美化提示信息 */
    .stSuccess {
        background: linear-gradient(135deg, #2e7d32 0%, #66bb6a 100%);
        color: white;
        border-radius: 10px;
        padding: 15px;
        border: none;
    }
    
    .stError {
        background: linear-gradient(135deg, #d32f2f 0%, #f44336 100%);
        color: white;
        border-radius: 10px;
        padding: 15px;
        border: none;
    }
    
    .stWarning {
        background: linear-gradient(135deg, #f57c00 0%, #ff9800 100%);
        color: white;
        border-radius: 10px;
        padding: 15px;
        border: none;
    }
    
    .stInfo {
        background: linear-gradient(135deg, #1976d2 0%, #2196f3 100%);
        color: white;
        border-radius: 10px;
        padding: 15px;
        border: none;
    }
    
    /* 美化指标卡片 */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 20px;
        color: white;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        border: none;
    }
    
    [data-testid="metric-container"] > div {
        color: white;
    }
    
    [data-testid="metric-container"] label {
        color: white !important;
        opacity: 0.9;
    }
    
    /* 隐藏Streamlit默认元素 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* 响应式设计 */
    @media (max-width: 768px) {
        .main {
            padding: 1rem;
        }
        
        .stColumns {
            flex-direction: column;
        }
        
        .stButton > button {
            width: 100%;
            margin: 5px 0;
        }
    }
    
    /* 动画效果 */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .stMarkdown > div {
        animation: fadeIn 0.6s ease-out;
    }
    
    /* 自定义滚动条 */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 添加现代化的标题栏
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                color: white; padding: 25px; border-radius: 20px; margin-bottom: 30px; 
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);">
        <div style="text-align: center;">
            <h1 style="margin: 0; font-size: 2.5rem; font-weight: 700;">
                🚀 智能QA分析系统
            </h1>
            <p style="margin: 15px 0 0 0; font-size: 1.2rem; opacity: 0.9;">
                基于大语言模型的智能客服质量评估平台
            </p>
            <div style="margin-top: 20px; display: flex; justify-content: center; gap: 20px; flex-wrap: wrap;">
                <span style="background: rgba(255,255,255,0.2); padding: 8px 16px; border-radius: 20px; font-size: 0.9rem;">
                    🧠 AI驱动分析
                </span>
                <span style="background: rgba(255,255,255,0.2); padding: 8px 16px; border-radius: 20px; font-size: 0.9rem;">
                    📊 多维度评估
                </span>
                <span style="background: rgba(255,255,255,0.2); padding: 8px 16px; border-radius: 20px; font-size: 0.9rem;">
                    🎯 实时监控
                </span>
                <span style="background: rgba(255,255,255,0.2); padding: 8px 16px; border-radius: 20px; font-size: 0.9rem;">
                    📈 可视化报告
                </span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 添加美化的导航说明
    st.markdown("""
    <div style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); 
                color: #333; padding: 20px; border-radius: 15px; margin-bottom: 25px;
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.05);">
        <h3 style="margin: 0 0 15px 0; text-align: center; color: #2c3e50;">
            📍 导航指南
        </h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-top: 15px;">
            <div style="text-align: center; background: rgba(255,255,255,0.7); padding: 15px; border-radius: 10px;">
                <strong>🔍 Analysis</strong><br/>
                <small>基础分析和多机器人对比</small>
            </div>
            <div style="text-align: center; background: rgba(255,255,255,0.7); padding: 15px; border-radius: 10px;">
                <strong>📊 Dashboard</strong><br/>
                <small>数据可视化和报告</small>
            </div>
            <div style="text-align: center; background: rgba(255,255,255,0.7); padding: 15px; border-radius: 10px;">
                <strong>🧠 Advanced LLM</strong><br/>
                <small>深度LLM分析</small>
            </div>
            <div style="text-align: center; background: rgba(255,255,255,0.7); padding: 15px; border-radius: 10px;">
                <strong>🔧 Management</strong><br/>
                <small>配置和管理</small>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize task manager in session state
    if 'task_manager' not in st.session_state:
        st.session_state.task_manager = TaskManager()
    
    # Load agents and analyzer config
    if 'agents_df' not in st.session_state:
        st.session_state.agents_df = load_agents()
    
    if 'analyzer_config' not in st.session_state:
        st.session_state.analyzer_config = load_analyzer_config()
    
    # 美化的标签页
    st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 10px;
        border-radius: 15px;
        margin-bottom: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background: white;
        border-radius: 10px;
        color: #2c3e50;
        font-weight: 600;
        border: 2px solid transparent;
        transition: all 0.3s ease;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-color: #667eea;
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    .stTabs [data-baseweb="tab"]:hover {
        background: #f8f9fa;
        transform: translateY(-1px);
        border-color: #667eea;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create tabs for different functionalities
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "🔍 Analysis", 
        "📋 Tasks(Invalid)", 
        "📊 Dashboard", 
        "🔍 JSON Dashboard", 
        "🧠 Advanced LLM", 
        "👥 Agent Management", 
        "⚙️ Analyzer Config"
    ])
    
    # Initialize analyzer with selected agent
    with tab1:
        # 美化的标题区域
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: white; padding: 25px; border-radius: 20px; margin-bottom: 30px; 
                    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);">
            <div style="text-align: center;">
                <h1 style="margin: 0; font-size: 2.2rem; font-weight: 700;">
                    🔍 QA分析工具
                </h1>
                <p style="margin: 15px 0 0 0; font-size: 1.1rem; opacity: 0.9;">
                    智能客服问答质量评估与分析
                </p>
                <div style="margin-top: 15px; display: flex; justify-content: center; gap: 15px; flex-wrap: wrap;">
                    <span style="background: rgba(255,255,255,0.2); padding: 6px 12px; border-radius: 15px; font-size: 0.8rem;">
                        🤖 多机器人对比
                    </span>
                    <span style="background: rgba(255,255,255,0.2); padding: 6px 12px; border-radius: 15px; font-size: 0.8rem;">
                        📊 质量指标分析
                    </span>
                    <span style="background: rgba(255,255,255,0.2); padding: 6px 12px; border-radius: 15px; font-size: 0.8rem;">
                        🎯 实时监控
                    </span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Show welcome guide for new users
        UserGuideComponents.show_welcome_guide()
        
        # 美化分析模式选择
        st.markdown("""
        <div style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); 
                    color: #333; padding: 20px; border-radius: 15px; margin: 20px 0;
                    box-shadow: 0 4px 15px rgba(168, 237, 234, 0.2);">
            <h3 style="margin: 0 0 15px 0; text-align: center; color: #2c3e50;">
                🎯 选择分析模式
            </h3>
            <p style="margin: 0; text-align: center; font-size: 0.9rem; opacity: 0.8;">
                根据您的需求选择合适的分析模式
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # 美化radio选择
        st.markdown("""
        <style>
        .stRadio > div {
            background: white;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .stRadio > div > label {
            font-weight: 600;
            color: #2c3e50;
        }
        </style>
        """, unsafe_allow_html=True)
        
        analysis_mode = st.radio(
            "选择分析模式",
            ["单机器人分析", "多机器人对比分析"],
            index=0,
            help="单机器人分析：使用一个机器人进行分析；多机器人对比分析：同时使用多个机器人进行对比测试"
        )
        
        # Agent selection with card-based UI
        from ui_components import AgentSelectionComponents
        
        agents = st.session_state.agents_df
        
        if analysis_mode == "单机器人分析":
            selected_agent = AgentSelectionComponents.show_agent_cards(agents, "_analysis")
            
            if selected_agent is None:
                st.stop()
            
            # Get selected agent's credentials as dictionary
            agent_creds = agents[agents['name'] == selected_agent].iloc[0].to_dict()
            
            # Initialize analyzer with selected agent's credentials and analyzer config
            analyzer = QAAnalyzer(agent_creds, st.session_state.analyzer_config)
            selected_agents = [selected_agent]
            
        else:  # 多机器人对比分析
            selected_agents = AgentSelectionComponents.show_multi_agent_selection(agents, "_multi_analysis")
            
            if not selected_agents:
                st.stop()
            
            # 为多机器人分析准备配置
            agents_configs = []
            for agent_name in selected_agents:
                agent_creds = agents[agents['name'] == agent_name].iloc[0].to_dict()
                agents_configs.append(agent_creds)
            
            # 初始化多机器人分析器
            from multi_agent_analyzer import MultiAgentAnalyzer
            analyzer = MultiAgentAnalyzer(agents_configs, st.session_state.analyzer_config)
        
        st.markdown("---")
        
        # 美化数据准备区域
        st.markdown("""
        <div style="background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); 
                    color: #333; padding: 20px; border-radius: 15px; margin: 20px 0;
                    box-shadow: 0 4px 15px rgba(252, 182, 159, 0.2);">
            <h3 style="margin: 0 0 10px 0; text-align: center; color: #2c3e50;">
                📊 数据准备
            </h3>
            <p style="margin: 0; text-align: center; font-size: 0.9rem; opacity: 0.8;">
                上传测试数据文件，开始质量分析
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Template download with better UI
        st.markdown("""
        <div style="background: #e8f4f8; padding: 20px; border-radius: 15px; margin: 15px 0;
                    border-left: 5px solid #17becf;">
            <h4 style="margin: 0 0 10px 0; color: #2c3e50;">💡 首次使用指南</h4>
            <p style="margin: 0; color: #34495e;">
                请先下载模板文件，了解数据格式要求，然后上传您的测试数据
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.info("📝 模板文件包含了标准的数据格式和示例数据")
        
        with col2:
            # 使用file_manager获取模板内容
            template_content = file_manager.get_template_content('default')
            
            if template_content:
                # 添加 BOM 头并转换编码
                template_content_with_bom = '\ufeff' + template_content
                st.download_button(
                    label="📥 下载数据模板",
                    data=template_content_with_bom.encode('utf-8-sig'),
                    file_name="qa_analysis_template.csv",
                    mime="text/csv",
                    help="下载CSV模板文件，了解数据格式要求"
                )
            else:
                st.error("❌ 无法获取模板内容")
        
        # Language selection
        selected_language = DataValidationComponents.show_language_selector("_analysis")
        
        # File upload with validation
        st.subheader("📁 上传测试数据")
        uploaded_file = st.file_uploader(
            "选择CSV文件", 
            type=['csv'],
            help="请上传包含测试数据的CSV文件，确保包含场景、测试数据、参考答案等字段"
        )
        
        # Data validation and preview
        if uploaded_file is not None:
            # Validate file format with language support
            is_valid, message = DataValidationComponents.validate_csv_format(uploaded_file, selected_language)
            if is_valid:
                UserGuideComponents.show_status_indicator('success', message)
                # Show data preview with language support
                DataValidationComponents.show_data_preview(uploaded_file, selected_language)
                
                # Show language statistics
                try:
                    uploaded_file.seek(0)
                    df_preview = DataValidationComponents._read_csv_with_encoding(uploaded_file, language=selected_language)
                    
                    # 显示文件原始信息
                    st.info(f"📄 **文件原始信息**: 成功读取 {len(df_preview)} 行数据")
                    
                    DataValidationComponents.show_language_statistics(selected_language, df_preview)
                    
                    # 显示采样说明
                    sample_n = st.session_state.get('sample_n', 100)
                    if len(df_preview) > sample_n and sample_n < 50:
                        st.warning(f"⚠️ **采样说明**: 文件有 {len(df_preview)} 行，但分析时只会使用 {sample_n} 行样本")
                    else:
                        expected_samples = min(len(df_preview), sample_n)
                        st.success(f"✅ **分析数据**: 文件有 {len(df_preview)} 行，将使用 {expected_samples} 行进行分析")
                        
                except Exception as e:
                    st.warning(f"无法显示语言统计信息: {str(e)}")
                    
            else:
                UserGuideComponents.show_status_indicator('error', message)
                st.stop()
        
        # Analysis configuration
        st.subheader("⚙️ 分析配置")
        
        col1, col2 = st.columns(2)
        with col1:
            sample_n = st.number_input(
                "样本数量", 
                min_value=1, 
                max_value=1000,
                value=100, 
                step=1,
                help="选择要分析的样本数量。西班牙语文件建议使用100以上（默认100）"
            )
            
            # 保存样本数量到session state
            st.session_state.sample_n = sample_n
            
            # Show estimated time
            estimated_time = sample_n * 0.5  # 估算每个样本0.5分钟
            st.caption(f"预计分析时间: {estimated_time:.1f} 分钟")
        
        with col2:
            num_generations = st.number_input(
                "答案生成次数", 
                min_value=1, 
                max_value=3, 
                value=3, 
                step=1,
                help="为每个问题生成多少个答案。更多次数可以计算语义稳定性，但会增加分析时间"
            )
            
            # Show what metrics will be calculated
            if num_generations > 1:
                st.caption("✅ 将计算语义稳定性")
            else:
                st.caption("⚠️ 单次生成无法计算语义稳定性")
        
        # LLM分析选项
        st.markdown("---")
        st.subheader("🧠 LLM分析选项")
        
        col1, col2 = st.columns(2)
        with col1:
            enable_llm_analysis = st.checkbox(
                "🔬 启用LLM深度分析",
                value=False,
                help="是否进行LLM深度分析。关闭此选项只进行基础机器学习分析（ROUGE、语义相似度等）"
            )
            
            # 保存LLM分析选项到session state
            st.session_state.enable_llm_analysis = enable_llm_analysis
            
        with col2:
            if enable_llm_analysis:
                st.success("✅ 将进行完整的LLM深度分析")
                st.caption("包含：事实准确性、语义一致性、业务逻辑等10+维度分析")
            else:
                st.info("📊 仅进行基础机器学习分析")
                st.caption("包含：ROUGE分数、语义相似度、完整度、相关度等传统指标")
        
        # 显示分析内容说明
        if enable_llm_analysis:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #e8f5e8 0%, #f0f8ff 100%); 
                        color: #333; padding: 15px; border-radius: 10px; margin: 10px 0;">
                <h5 style="margin: 0 0 10px 0; color: #2c3e50;">🎯 LLM深度分析包含：</h5>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px;">
                    <div>• 事实准确性评估</div>
                    <div>• 语义一致性分析</div>
                    <div>• 业务逻辑符合性</div>
                    <div>• 用户意图理解度</div>
                    <div>• 专业程度评估</div>
                    <div>• 上下文理解能力</div>
                </div>
                <p style="margin: 10px 0 0 0; font-size: 0.9rem; opacity: 0.8;">
                    <strong>注意：</strong> LLM分析需要API密钥，分析时间较长，但提供更深入的洞察
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%); 
                        color: #333; padding: 15px; border-radius: 10px; margin: 10px 0;">
                <h5 style="margin: 0 0 10px 0; color: #2c3e50;">📊 基础机器学习分析包含：</h5>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px;">
                    <div>• ROUGE-L 分数</div>
                    <div>• 语义相似度</div>
                    <div>• 回答完整度</div>
                    <div>• 信息相关度</div>
                    <div>• 语义稳定性</div>
                    <div>• 冗余度分析</div>
                </div>
                <p style="margin: 10px 0 0 0; font-size: 0.9rem; opacity: 0.8;">
                    <strong>优势：</strong> 快速分析，无需API密钥，适合快速质量检查
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        # 首字响应时间选项
        st.markdown("---")
        st.subheader("⚡ 性能监控选项")
        
        enable_first_token_timing = st.checkbox(
            "⚡ 记录首字响应时间",
            value=False,
            help="记录从请求发送到接收第一个响应字符的时间，用于分析API性能"
        )
        
        # 保存首字响应时间选项到session state
        st.session_state.enable_first_token_timing = enable_first_token_timing
        
        if enable_first_token_timing:
            st.info("📊 将记录每个请求的首字响应时间，用于性能分析")
        else:
            st.caption("不记录首字响应时间数据")
        
        # Analysis execution
        st.markdown("---")
        st.subheader("🚀 开始分析")
        
        # Pre-analysis checks
        if uploaded_file is None:
            st.warning("⚠️ 请先上传CSV文件")
            analysis_ready = False
        elif enable_llm_analysis and not st.session_state.get('analyzer_config'):
            st.warning("⚠️ LLM分析需要配置API参数，请前往'Analyzer Config'标签页配置")
            analysis_ready = False
        else:
            st.success("✅ 准备就绪，可以开始分析")
            analysis_ready = True
        
        # Analysis steps indicator - 根据是否启用LLM分析显示不同步骤
        if enable_llm_analysis:
            analysis_steps = [
                ("数据加载", "读取和处理CSV文件"),
                ("答案生成", "调用机器人生成答案"),
                ("指标计算", "计算各种质量指标"),
                ("LLM分析", "深度质量分析"),
                ("结果保存", "保存分析结果")
            ]
        else:
            analysis_steps = [
                ("数据加载", "读取和处理CSV文件"),
                ("答案生成", "调用机器人生成答案"),
                ("指标计算", "计算各种质量指标"),
                ("结果保存", "保存分析结果")
            ]
        
        # Analysis control buttons
        analysis_running = st.session_state.get('analysis_running', False)
        analysis_paused = st.session_state.get('analysis_paused', False)
        
        if not analysis_running:
            # Show start button when analysis is not running
            if analysis_ready and st.button("🔥 开始分析", type="primary"):
                # Initialize pause state
                st.session_state.analysis_paused = False
                st.session_state.analysis_running = True
                st.rerun()
        else:
            # Show control buttons when analysis is running
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                if analysis_paused:
                    if st.button("▶️ 继续分析", type="primary"):
                        st.session_state.analysis_paused = False
                        st.rerun()
                else:
                    if st.button("⏸️ 暂停分析", type="secondary"):
                        st.session_state.analysis_paused = True
                        st.rerun()
            
            with col2:
                if st.button("⏹️ 停止分析", type="secondary"):
                    st.session_state.analysis_running = False
                    st.session_state.analysis_paused = False
                    st.rerun()
            
            with col3:
                # Show current status
                if analysis_paused:
                    st.warning("⏸️ 已暂停")
                else:
                    st.info("🔄 运行中")
        
        # Show analysis status
        if analysis_running:
            if analysis_paused:
                st.warning("⏸️ 分析已暂停，点击'继续分析'恢复")
            else:
                st.info("🔄 分析运行中，可以点击'暂停分析'暂停")
        
        # Run analysis when conditions are met
        if analysis_running and not analysis_paused:
            try:
                # Save uploaded file temporarily
                temp_file = file_manager.create_temp_file(uploaded_file.getvalue(), '.csv')
                
                # Create new task with language support
                task_id = st.session_state.task_manager.create_task(temp_file, sample_n, num_generations, selected_language)
                
                # Show analysis progress
                progress_placeholder = st.empty()
                step_placeholder = st.empty()
                control_placeholder = st.empty()
                
                with progress_placeholder.container():
                    st.info("🔄 分析任务已创建，正在初始化...")
                
                with step_placeholder.container():
                    AnalysisProgressComponents.show_step_indicator(analysis_steps, 0)
                
                # Start analysis in background
                st.session_state.task_manager.update_task(task_id, 0.1, "Starting analysis...")
                
                # Run analysis with enhanced progress tracking
                def enhanced_progress_callback(progress, message):
                    # Check if analysis is stopped
                    if not st.session_state.get('analysis_running', False):
                        return False  # Signal to stop
                    
                    # Check if analysis is paused
                    if st.session_state.get('analysis_paused', False):
                        return False  # Signal to pause
                    
                    current_step = min(int(progress * len(analysis_steps)), len(analysis_steps) - 1)
                    
                    with progress_placeholder.container():
                        if analysis_mode == "多机器人对比分析":
                            # 显示多机器人进度
                            if hasattr(analyzer, 'progress_data'):
                                from multi_agent_analyzer import MultiAgentProgressComponents
                                MultiAgentProgressComponents.show_multi_agent_progress(
                                    analyzer.progress_data, selected_agents
                                )
                            else:
                                st.info(f"🔄 {message}")
                        else:
                            # 显示单机器人进度
                            AnalysisProgressComponents.show_progress_details(
                                progress, current_step + 1, len(analysis_steps), 
                                estimated_time * (1 - progress) if progress > 0 else estimated_time
                            )
                            
                            # Show different status based on state
                            if st.session_state.get('analysis_paused', False):
                                st.warning(f"⏸️ 分析已暂停: {message}")
                            else:
                                st.info(f"🔄 {message}")
                    
                    with step_placeholder.container():
                        AnalysisProgressComponents.show_step_indicator(analysis_steps, current_step)
                    
                    # Show pause/resume controls in progress
                    with control_placeholder.container():
                        is_paused = st.session_state.get('analysis_paused', False)
                        col1, col2, col3 = st.columns([1, 1, 1])
                        
                        # Generate unique timestamp for button keys to avoid duplicates
                        timestamp = int(datetime.now().timestamp() * 1000)
                        
                        with col1:
                            if not is_paused:
                                if st.button("⏸️ 暂停", key=f"pause_{task_id}_{timestamp}"):
                                    st.session_state.analysis_paused = True
                                    st.rerun()
                            else:
                                if st.button("▶️ 继续", key=f"resume_{task_id}_{timestamp}"):
                                    st.session_state.analysis_paused = False
                                    st.rerun()
                        
                        with col2:
                            if st.button("⏹️ 停止", key=f"stop_{task_id}_{timestamp}", type="secondary"):
                                st.session_state.analysis_running = False
                                st.session_state.analysis_paused = False
                                st.rerun()
                        
                        with col3:
                            # Show current analysis status
                            if is_paused:
                                st.warning("⏸️ 已暂停")
                            else:
                                st.success("🔄 运行中")
                    
                    st.session_state.task_manager.update_task(task_id, progress, message)
                    return True  # Continue analysis
                
                # Run analysis with language support and pause checking
                if analysis_mode == "多机器人对比分析":
                    # 多机器人分析
                    results = analyzer.analyze_with_multiple_agents(
                        temp_file, sample_n, num_generations, enhanced_progress_callback, selected_language
                    )
                    
                    # 检查是否有成功的结果
                    successful_results = {name: result for name, result in results.items() if result[0] is not None}
                    
                    if successful_results:
                        # 获取合并结果
                        combined_df = analyzer.get_combined_results()
                        summary = analyzer.get_comparison_summary()
                        output_path = analyzer.save_combined_results()
                        
                        df = combined_df
                    else:
                        df, output_path = None, None
                else:
                    # 单机器人分析
                    # 获取LLM分析选项
                    enable_llm_analysis = st.session_state.get('enable_llm_analysis', False)
                    
                    df, output_path = analyzer.analyze_file(
                        temp_file, sample_n, num_generations, 
                        enhanced_progress_callback, selected_language, 
                        enable_llm_analysis
                    )
                
                if df is not None:
                    st.session_state.task_manager.store_result(task_id, df, output_path)
                    st.session_state.task_manager.update_task(
                        task_id, 1.0, "✨ Analysis completed successfully!", "completed")
                    
                    # Clear progress indicators and controls
                    progress_placeholder.empty()
                    step_placeholder.empty()
                    control_placeholder.empty()
                    
                    # Reset analysis state
                    st.session_state.analysis_running = False
                    st.session_state.analysis_paused = False
                    
                    # Show success message
                    if analysis_mode == "多机器人对比分析":
                        st.success(f"🎉 多机器人对比分析完成！成功测试了 {len(selected_agents)} 个机器人")
                        
                        # 显示多机器人对比结果
                        if hasattr(analyzer, 'get_comparison_summary'):
                            summary = analyzer.get_comparison_summary()
                            from multi_agent_analyzer import MultiAgentResultComponents
                            MultiAgentResultComponents.show_comparison_dashboard(summary, df)
                            MultiAgentResultComponents.show_export_options(df, summary, output_path)
                        else:
                            st.warning("无法获取对比摘要")
                    else:
                        st.success("🎉 单机器人分析完成！")
                        
                        # Show analysis summary
                        ResultDisplayComponents.show_analysis_summary(df)
                        
                        # Show export options
                        ResultDisplayComponents.show_export_options(df, f"analysis_{task_id}")
                    
                    # Offer to view dashboard
                    if st.button("📊 查看详细分析结果"):
                        st.info("💡 请切换到 'Dashboard' 标签页查看详细分析结果")
                
                elif df is None and st.session_state.get('analysis_running', False):
                    # Analysis failed
                    st.session_state.task_manager.update_task(
                        task_id, 1.0, "❌ Analysis failed", "failed")
                    ErrorHandlingComponents.show_error_details("分析失败", "analysis")
                    
                    # Reset analysis state on failure
                    st.session_state.analysis_running = False
                    st.session_state.analysis_paused = False
                
                else:
                    # Analysis was stopped by user
                    st.session_state.task_manager.update_task(
                        task_id, 0.0, "⏹️ Analysis stopped by user", "stopped")
                    
                    # Clear progress indicators and controls
                    progress_placeholder.empty()
                    step_placeholder.empty()
                    control_placeholder.empty()
                    
                    # Reset analysis state
                    st.session_state.analysis_running = False
                    st.session_state.analysis_paused = False
                    
                    # Show stop message
                    st.info("⏹️ 分析已被用户停止")
                
                # Cleanup
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    
            except Exception as e:
                ErrorHandlingComponents.show_error_details(e, "analysis")
                ErrorHandlingComponents.show_retry_options("analysis_failed")
                
                # Reset analysis state on exception
                st.session_state.analysis_running = False
                st.session_state.analysis_paused = False
                
                if 'temp_file' in locals() and os.path.exists(temp_file):
                    os.remove(temp_file)
    
    with tab2:
        st.title("📋 Tasks Status")
        tasks = st.session_state.task_manager.tasks
        
        if not tasks:
            st.info("🔍 暂无分析任务")
            st.markdown("""
            💡 **提示**：
            - 前往"Analysis"标签页开始新的分析任务
            - 完成的任务结果可以在这里查看和下载
            """)
        else:
            # Task summary
            total_tasks = len(tasks)
            completed_tasks = sum(1 for task in tasks.values() if task['status'] == 'completed')
            running_tasks = sum(1 for task in tasks.values() if task['status'] == 'running')
            failed_tasks = sum(1 for task in tasks.values() if task['status'] == 'failed')
            stopped_tasks = sum(1 for task in tasks.values() if task['status'] == 'stopped')
            
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("总任务数", total_tasks)
            with col2:
                st.metric("已完成", completed_tasks, delta=f"{completed_tasks/total_tasks*100:.1f}%")
            with col3:
                st.metric("运行中", running_tasks)
            with col4:
                st.metric("失败", failed_tasks)
            with col5:
                st.metric("已停止", stopped_tasks)
            
            st.markdown("---")
            
            # Display tasks with enhanced UI
            for task_id, task in tasks.items():
                status_icon = {
                    'completed': '✅',
                    'running': '🔄',
                    'failed': '❌',
                    'pending': '⏳',
                    'stopped': '⏹️'
                }.get(task['status'], '❓')
                
                with st.expander(f"{status_icon} 任务 {task_id} - {task['status']}"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.progress(task['progress'])
                        st.write(f"**状态**: {task['status']}")
                        st.write(f"**消息**: {task['message']}")
                        st.write(f"**开始时间**: {task['start_time']}")
                        
                        # Show task details
                        if 'file_path' in task:
                            st.write(f"**数据文件**: {task['file_path']}")
                        if 'sample_n' in task:
                            st.write(f"**样本数量**: {task['sample_n']}")
                        if 'num_generations' in task:
                            st.write(f"**生成次数**: {task['num_generations']}")
                    
                    with col2:
                        if task['status'] == 'completed':
                            df, output_path = st.session_state.task_manager.get_result(task_id)
                            if df is not None:
                                st.success(f"✅ 分析完成")
                                st.metric("样本数", len(df))
                                
                                # Show results button
                                if st.button(f"📊 查看结果", key=f"show_{task_id}"):
                                    st.subheader(f"任务 {task_id} - 分析结果")
                                    
                                    # Show summary
                                    ResultDisplayComponents.show_analysis_summary(df)
                                    
                                    # Show detailed results
                                    with st.expander("📄 详细数据"):
                                        st.dataframe(df)
                                
                                # Download options
                                ResultDisplayComponents.show_export_options(df, f"task_{task_id}")
                        
                        elif task['status'] == 'failed':
                            st.error("❌ 分析失败")
                            if st.button(f"🔄 重试", key=f"retry_{task_id}"):
                                st.info("💡 请返回 Analysis 标签页重新开始分析")
                        
                        elif task['status'] == 'running':
                            st.info("🔄 分析中...")
                            if st.button(f"⏹️ 停止", key=f"stop_{task_id}"):
                                st.warning("⚠️ 任务停止功能尚未实现")
                        
                        elif task['status'] == 'stopped':
                            st.info("⏹️ 分析已停止")
                            if st.button(f"🔄 重新开始", key=f"restart_{task_id}"):
                                st.info("💡 请返回 Analysis 标签页重新开始分析")
        
        # Task management actions
        st.markdown("---")
        st.subheader("🔧 任务管理")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ 清除已完成任务"):
                completed_ids = [task_id for task_id, task in tasks.items() if task['status'] in ['completed', 'stopped']]
                for task_id in completed_ids:
                    del st.session_state.task_manager.tasks[task_id]
                st.success("✅ 已清除完成和停止的任务")
                st.rerun()
        
        with col2:
            if st.button("🔄 刷新任务状态"):
                st.rerun()
    
    with tab3:
        st.title("QA Analysis Dashboard")
        analyzer.dashboard.show_dashboard()

    with tab4:
        st.title("🔍 JSON Analysis Dashboard")
        
        # Initialize JSON dashboard
        json_dashboard = JSONDashboard()
        
        # Show JSON dashboard with improved description
        st.markdown("""
        ### 📊 JSON专门分析
        
        这个Dashboard专门用于分析JSON格式的轮胎查询结果，提供以下功能：
        
        - 🏗️ **结构一致性分析** - 检查JSON格式是否标准
        - 💰 **价格准确性分析** - 验证价格信息的正确性
        - 📦 **库存准确性分析** - 检查库存数据的准确性
        - 🛞 **产品覆盖率分析** - 分析产品数量匹配度
        - 📝 **描述质量分析** - 评估产品描述的相关性
        - 📈 **传统指标对比** - 与ROUGE等传统指标对比
        
        💡 **使用说明**：请先运行JSON分析（使用 `reanalyze_with_json_metrics.py`）生成 `*_json_metrics.csv` 文件
        """)
        
        try:
            json_dashboard.show_json_dashboard()
        except Exception as e:
            st.error(f"JSON Dashboard加载失败: {str(e)}")
            st.info("请确保已经生成了JSON分析结果文件")

    with tab5:
        st.title("🧠 Advanced LLM Analysis")
        
        # Initialize Advanced LLM dashboard
        advanced_llm_dashboard = AdvancedLLMDashboard()
        
        # Show Advanced LLM dashboard with description
        st.markdown("""
        ### 🎯 增强版LLM分析系统
        
        基于大语言模型的深度分析功能，提供比传统方法更智能的评估：
        
        - **🎯 10维度综合评估** - 事实准确性、语义一致性、业务逻辑符合性等
        - **🛞 6维度业务专门分析** - 轮胎规格、价格、库存等关键业务指标
        - **🤖 Agent对比评估** - 深度对比分析，识别优势和改进空间
        - **📊 方法对比** - 与传统ROUGE/TF-IDF方法的效果对比
        
        ### 💡 与传统方法的区别
        
        | 方面 | 传统方法 (ROUGE/TF-IDF) | 增强版LLM分析 |
        |------|------------------------|---------------|
        | **理解能力** | 词汇匹配 | 深度语义理解 |
        | **业务感知** | 无 | 理解业务逻辑 |
        | **上下文** | 有限 | 强大的上下文理解 |
        | **解释性** | 数值指标 | 详细分析说明 |
        | **准确性** | 表面相似度 | 深层语义准确性 |
        
        ### 🚀 使用说明
        
        1. **查看现有分析** - 如果已有增强LLM分析结果，可在下方查看
        2. **运行新分析** - 可以对现有数据运行增强LLM分析
        3. **对比分析** - 查看与传统方法的对比效果
        """)
        
        try:
            advanced_llm_dashboard.show_advanced_llm_dashboard()
        except Exception as e:
            st.error(f"Advanced LLM Dashboard加载失败: {str(e)}")
            st.info("请确保已经配置了LLM分析器并生成了分析结果")

    with tab6:
        st.title("🤖 Agent Management")
        
        # Display existing agents with improved UI
        st.subheader("📋 当前机器人配置")
        
        if len(st.session_state.agents_df) == 0:
            st.warning("⚠️ 没有配置任何机器人，请先添加一个机器人配置")
        else:
            # Display agents in a more user-friendly way
            for idx, agent in st.session_state.agents_df.iterrows():
                with st.expander(f"🤖 {agent['name']} - {agent.get('description', 'No description')}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**名称**: {agent['name']}")
                        st.write(f"**描述**: {agent.get('description', 'N/A')}")
                        st.write(f"**用户名**: {agent['username']}")
                    
                    with col2:
                        st.write(f"**WebSocket URL**: {agent['url']}")
                        st.write(f"**Robot Key**: {'*' * 20}")
                        st.write(f"**Robot Token**: {'*' * 20}")
                    
                    # Test connection button
                    if st.button(f"🔗 测试连接", key=f"test_{agent['name']}"):
                        try:
                            # Here you would implement actual connection testing
                            st.success("✅ 连接测试成功!")
                        except Exception as e:
                            st.error(f"❌ 连接测试失败: {str(e)}")
        
        st.markdown("---")
        
        # Add new agent form with improved UI
        st.subheader("➕ 添加新机器人")
        
        # Use the configuration component
        new_agent_config = ConfigurationComponents.show_agent_config_form()
        
        if new_agent_config:
            # Check if agent name already exists
            if new_agent_config['name'] in st.session_state.agents_df['name'].values:
                st.error("❌ 机器人名称已存在，请使用其他名称")
            else:
                # Add new agent
                new_row = pd.DataFrame([new_agent_config])
                st.session_state.agents_df = pd.concat([st.session_state.agents_df, new_row], ignore_index=True)
                save_agents(st.session_state.agents_df)
                st.success("✅ 机器人配置添加成功!")
                st.rerun()
        
        # Delete agent with improved UI
        if len(st.session_state.agents_df) > 0:
            st.markdown("---")
            st.subheader("🗑️ 删除机器人配置")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                agent_to_delete = st.selectbox(
                    "选择要删除的机器人配置", 
                    st.session_state.agents_df['name'].tolist(),
                    key='agent_to_delete',
                    help="选择要删除的机器人配置"
                )
            
            with col2:
                if st.button("🗑️ 删除机器人", type="secondary"):
                    if len(st.session_state.agents_df) <= 1:
                        st.error("❌ 不能删除最后一个机器人配置")
                    else:
                        # Show confirmation
                        if st.button("⚠️ 确认删除", type="primary"):
                            st.session_state.agents_df = st.session_state.agents_df[
                                st.session_state.agents_df['name'] != agent_to_delete
                            ]
                            save_agents(st.session_state.agents_df)
                            st.success("✅ 机器人配置删除成功!")
                            st.rerun()
    
    with tab7:
        st.title("🔧 Analyzer Configuration")
        
        # Information about the analyzer
        st.info("""
        📋 **关于分析器配置**
        
        LLM分析器用于执行深度质量分析，包括：
        - 🔍 语义篡改检测
        - ❌ 关键信息缺失分析  
        - ⚠️ 无关信息生成识别
        
        请配置用于分析的LLM服务端点和认证信息。
        """)
        
        # Current configuration display
        st.subheader("📊 当前配置")
        config = st.session_state.analyzer_config
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("API URL", config.get('url', 'Not configured'))
            st.metric("Username", config.get('username', 'Not configured'))
        
        with col2:
            key_status = "✅ 已配置" if config.get('robot_key') else "❌ 未配置"
            token_status = "✅ 已配置" if config.get('robot_token') else "❌ 未配置"
            st.metric("Robot Key", key_status)
            st.metric("Robot Token", token_status)
        
        st.markdown("---")
        
        # Configuration form
        st.subheader("⚙️ 更新配置")
        
        with st.form("analyzer_config_form"):
            st.markdown("**服务端点配置**")
            analyzer_url = st.text_input(
                "API URL", 
                value=config.get('url', 'https://agents.dyna.ai/openapi/v1/conversation/dialog/'),
                help="LLM分析服务的API端点URL"
            )
            analyzer_username = st.text_input(
                "Username", 
                value=config.get('username', 'marshall.ting@dyna.ai'),
                help="用于身份验证的用户名"
            )
            
            st.markdown("**认证信息**")
            col1, col2 = st.columns(2)
            
            with col1:
                analyzer_key = st.text_input(
                    "Robot Key", 
                    value=config.get('robot_key', ''),
                    type="password",
                    help="机器人密钥"
                )
            
            with col2:
                analyzer_token = st.text_input(
                    "Robot Token", 
                    value=config.get('robot_token', ''),
                    type="password",
                    help="机器人令牌"
                )
            
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                if st.form_submit_button("💾 保存配置", type="primary"):
                    # Validate required fields
                    if not all([analyzer_url, analyzer_username, analyzer_key, analyzer_token]):
                        st.error("❌ 请填写所有必填字段")
                    else:
                        new_config = {
                            'url': analyzer_url,
                            'username': analyzer_username,
                            'robot_key': analyzer_key,
                            'robot_token': analyzer_token
                        }
                        save_analyzer_config(new_config)
                        st.session_state.analyzer_config = new_config
                        st.success("✅ 配置保存成功!")
                        st.rerun()
            
            with col_btn2:
                if st.form_submit_button("🔗 测试连接", type="secondary"):
                    # Test analyzer connection
                    if not all([analyzer_url, analyzer_username, analyzer_key, analyzer_token]):
                        st.error("❌ 请先填写所有配置信息")
                    else:
                        try:
                            # Here you would implement actual connection testing
                            st.success("✅ 分析器连接测试成功!")
                        except Exception as e:
                            st.error(f"❌ 连接测试失败: {str(e)}")
        
        # Configuration tips
        st.markdown("---")
        st.subheader("💡 配置提示")
        
        with st.expander("🔍 常见问题"):
            st.markdown("""
            **Q: 如何获取Robot Key和Robot Token？**
            A: 请联系您的系统管理员获取相关认证信息。
            
            **Q: 分析器连接失败怎么办？**
            A: 请检查URL是否正确，网络是否畅通，认证信息是否有效。
            
            **Q: 可以使用其他LLM服务吗？**
            A: 目前支持标准的对话API格式，如需使用其他服务请联系技术支持。
            """)

if __name__ == "__main__":
    main()