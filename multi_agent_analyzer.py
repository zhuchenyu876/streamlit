#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import streamlit as st
import pandas as pd
import logging
import os
import time
import threading
from datetime import datetime
import concurrent.futures
from typing import List, Dict, Tuple
from app import QAAnalyzer
from client import WebSocketClient

class MultiAgentAnalyzer:
    """多机器人并行测试分析器"""
    
    def __init__(self, agents_configs: List[Dict], analyzer_config: Dict):
        """
        初始化多机器人分析器
        
        Args:
            agents_configs: 机器人配置列表
            analyzer_config: 分析器配置
        """
        self.agents_configs = agents_configs
        self.analyzer_config = analyzer_config
        self.analyzers = {}
        self.results = {}
        self.progress_data = {}
        
        # 为每个机器人创建分析器实例
        for agent_config in agents_configs:
            agent_name = agent_config['name']
            self.analyzers[agent_name] = QAAnalyzer(agent_config, analyzer_config)
            self.progress_data[agent_name] = {'progress': 0.0, 'message': '准备中...', 'status': 'pending'}
    
    def analyze_with_multiple_agents(self, file_path: str, sample_n: int, num_generations: int, 
                                   progress_callback=None, language="auto") -> Dict[str, Tuple]:
        """
        使用多个机器人并行分析同一份数据
        
        Args:
            file_path: 数据文件路径
            sample_n: 样本数量
            num_generations: 生成次数
            progress_callback: 进度回调函数
            language: 语言设置
            
        Returns:
            Dict[str, Tuple]: 每个机器人的分析结果
        """
        logging.info(f"开始多机器人并行分析，机器人数量: {len(self.agents_configs)}")
        
        # 创建线程池执行并行分析
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.agents_configs)) as executor:
            # 提交所有分析任务
            futures = {}
            for agent_name, analyzer in self.analyzers.items():
                future = executor.submit(
                    self._analyze_single_agent,
                    agent_name,
                    analyzer,
                    file_path,
                    sample_n,
                    num_generations,
                    progress_callback,
                    language
                )
                futures[agent_name] = future
            
            # 等待所有任务完成
            for agent_name, future in futures.items():
                try:
                    result = future.result()
                    self.results[agent_name] = result
                    logging.info(f"机器人 {agent_name} 分析完成")
                except Exception as e:
                    logging.error(f"机器人 {agent_name} 分析失败: {str(e)}")
                    self.results[agent_name] = (None, None)
        
        return self.results
    
    def _analyze_single_agent(self, agent_name: str, analyzer: QAAnalyzer, file_path: str, 
                            sample_n: int, num_generations: int, progress_callback=None, language="auto"):
        """
        单个机器人的分析任务
        
        Args:
            agent_name: 机器人名称
            analyzer: 分析器实例
            file_path: 数据文件路径
            sample_n: 样本数量
            num_generations: 生成次数
            progress_callback: 进度回调函数
            language: 语言设置
        """
        def agent_progress_callback(progress, message):
            """为单个机器人包装的进度回调"""
            self.progress_data[agent_name] = {
                'progress': progress,
                'message': message,
                'status': 'running'
            }
            
            if progress_callback:
                # 计算总体进度
                total_progress = sum(data['progress'] for data in self.progress_data.values()) / len(self.progress_data)
                combined_message = f"[{agent_name}] {message}"
                progress_callback(total_progress, combined_message)
            
            # 检查是否需要停止
            if not st.session_state.get('analysis_running', False):
                return False
            
            # 检查是否需要暂停
            if st.session_state.get('analysis_paused', False):
                return False
            
            return True
        
        try:
            # 执行分析
            result = analyzer.analyze_file(file_path, sample_n, num_generations, agent_progress_callback, language)
            self.progress_data[agent_name]['status'] = 'completed'
            return result
        except Exception as e:
            self.progress_data[agent_name]['status'] = 'failed'
            self.progress_data[agent_name]['message'] = f"分析失败: {str(e)}"
            raise e
    
    def get_combined_results(self) -> pd.DataFrame:
        """
        合并所有机器人的分析结果
        
        Returns:
            pd.DataFrame: 合并后的结果DataFrame
        """
        if not self.results:
            return pd.DataFrame()
        
        combined_data = []
        
        # 获取第一个成功的结果作为基础数据
        base_df = None
        for agent_name, (df, _) in self.results.items():
            if df is not None:
                base_df = df.copy()
                break
        
        if base_df is None:
            return pd.DataFrame()
        
        # 重新组织数据结构
        for idx, row in base_df.iterrows():
            combined_row = {
                'ID': idx,
                '场景': row.get('场景', ''),
                '测试数据': row.get('测试数据', ''),
                '参考答案': row.get('参考答案', ''),
                '组别': row.get('组别', ''),
            }
            
            # 添加每个机器人的生成答案和指标
            for agent_name, (df, _) in self.results.items():
                if df is not None and idx < len(df):
                    agent_row = df.iloc[idx]
                    # 为每个机器人添加生成答案
                    for gen_idx in range(1, 4):  # 假设最多3次生成
                        answer_col = f'生成答案{gen_idx}'
                        if answer_col in agent_row:
                            combined_row[f'{agent_name}_{answer_col}'] = agent_row[answer_col]
                    
                    # 添加质量指标
                    for metric in ['语义稳定性', '冗余度', '完整度', '相关度']:
                        if metric in agent_row:
                            combined_row[f'{agent_name}_{metric}'] = agent_row[metric]
                    
                    # 添加错误指标
                    for error_metric in ['语义篡改', '缺失关键信息', '生成无关信息', '包含错误']:
                        if error_metric in agent_row:
                            combined_row[f'{agent_name}_{error_metric}'] = agent_row[error_metric]
            
            combined_data.append(combined_row)
        
        return pd.DataFrame(combined_data)
    
    def get_comparison_summary(self) -> Dict:
        """
        获取机器人对比摘要
        
        Returns:
            Dict: 对比摘要数据
        """
        if not self.results:
            return {}
        
        summary = {}
        
        for agent_name, (df, _) in self.results.items():
            if df is not None:
                # 计算基本统计
                summary[agent_name] = {
                    'total_samples': len(df),
                    'success_rate': (len(df) / len(df)) * 100,  # 简化版本
                    'avg_semantic_stability': df['语义稳定性'].mean() if '语义稳定性' in df.columns else 0,
                    'avg_completeness': df['完整度'].mean() if '完整度' in df.columns else 0,
                    'avg_relevance': df['相关度'].mean() if '相关度' in df.columns else 0,
                    'avg_redundancy': df['冗余度'].mean() if '冗余度' in df.columns else 0,
                    'error_rate': (df['包含错误'] == '是').sum() / len(df) * 100 if '包含错误' in df.columns else 0
                }
        
        return summary
    
    def save_combined_results(self, output_dir: str = "qa_analysis_results") -> str:
        """
        保存合并的分析结果
        
        Args:
            output_dir: 输出目录
            
        Returns:
            str: 输出文件路径
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        agent_names = "_".join([config['name'] for config in self.agents_configs])
        filename = f"multi_agent_analysis_{agent_names}_{timestamp}.csv"
        output_path = os.path.join(output_dir, filename)
        
        # 保存合并结果
        combined_df = self.get_combined_results()
        combined_df.to_csv(output_path, index=False, encoding='utf-8-sig')
        
        logging.info(f"多机器人分析结果已保存到: {output_path}")
        return output_path

class MultiAgentProgressComponents:
    """多机器人进度显示组件"""
    
    @staticmethod
    def show_multi_agent_progress(progress_data: Dict, agent_names: List[str]):
        """
        显示多机器人分析进度
        
        Args:
            progress_data: 进度数据字典
            agent_names: 机器人名称列表
        """
        st.markdown("### 🤖 多机器人分析进度")
        
        # 显示总体进度
        total_progress = sum(data['progress'] for data in progress_data.values()) / len(progress_data)
        st.progress(total_progress)
        
        # 显示每个机器人的进度
        cols = st.columns(len(agent_names))
        
        for idx, agent_name in enumerate(agent_names):
            with cols[idx]:
                data = progress_data.get(agent_name, {'progress': 0, 'message': '等待中...', 'status': 'pending'})
                
                # 状态图标
                status_icons = {
                    'pending': '⏳',
                    'running': '🔄',
                    'completed': '✅',
                    'failed': '❌'
                }
                
                status_icon = status_icons.get(data['status'], '❓')
                
                st.markdown(f"""
                <div style="
                    border: 2px solid {'#4CAF50' if data['status'] == 'completed' else '#2196F3' if data['status'] == 'running' else '#FF9800' if data['status'] == 'pending' else '#F44336'};
                    border-radius: 10px;
                    padding: 15px;
                    margin: 5px 0;
                    text-align: center;
                    background: {'#e8f5e8' if data['status'] == 'completed' else '#e3f2fd' if data['status'] == 'running' else '#fff3e0' if data['status'] == 'pending' else '#ffebee'};
                ">
                    <div style="font-size: 24px; margin-bottom: 10px;">{status_icon}</div>
                    <div style="font-weight: bold; margin-bottom: 5px;">{agent_name}</div>
                    <div style="font-size: 12px; color: #666;">{data['message']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # 进度条
                st.progress(data['progress'])
                st.caption(f"{data['progress']*100:.1f}%")

class MultiAgentResultComponents:
    """多机器人结果显示组件"""
    
    @staticmethod
    def show_comparison_dashboard(summary: Dict, combined_df: pd.DataFrame):
        """
        显示机器人对比仪表板
        
        Args:
            summary: 对比摘要
            combined_df: 合并的结果DataFrame
        """
        st.markdown("### 📊 机器人性能对比")
        
        if not summary:
            st.warning("暂无对比数据")
            return
        
        # 显示对比卡片
        agent_names = list(summary.keys())
        cols = st.columns(len(agent_names))
        
        for idx, agent_name in enumerate(agent_names):
            with cols[idx]:
                data = summary[agent_name]
                
                # 计算总体分数
                quality_score = (data['avg_semantic_stability'] + data['avg_completeness'] + data['avg_relevance']) / 3
                
                st.markdown(f"""
                <div style="
                    border: 2px solid #2196F3;
                    border-radius: 15px;
                    padding: 20px;
                    margin: 10px 0;
                    background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%);
                    text-align: center;
                ">
                    <h3 style="color: #1976D2; margin-bottom: 15px;">🤖 {agent_name}</h3>
                    <div style="font-size: 24px; font-weight: bold; color: #4CAF50; margin-bottom: 10px;">
                        {quality_score:.1f}%
                    </div>
                    <div style="font-size: 14px; color: #666; margin-bottom: 15px;">总体质量分数</div>
                    
                    <div style="text-align: left; font-size: 12px;">
                        <div>📈 语义稳定性: {data['avg_semantic_stability']:.1f}%</div>
                        <div>✅ 完整度: {data['avg_completeness']:.1f}%</div>
                        <div>🎯 相关度: {data['avg_relevance']:.1f}%</div>
                        <div>📝 冗余度: {data['avg_redundancy']:.1f}%</div>
                        <div>❌ 错误率: {data['error_rate']:.1f}%</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # 显示详细对比表格
        st.markdown("### 📋 详细对比数据")
        
        if not combined_df.empty:
            # 让用户选择要显示的列
            available_cols = combined_df.columns.tolist()
            basic_cols = ['ID', '场景', '测试数据', '参考答案']
            
            # 自动检测机器人相关的列
            agent_cols = []
            for agent_name in agent_names:
                agent_specific_cols = [col for col in available_cols if col.startswith(f'{agent_name}_')]
                if agent_specific_cols:
                    agent_cols.extend([f'{agent_name}_生成答案1', f'{agent_name}_语义稳定性', f'{agent_name}_完整度', f'{agent_name}_相关度'])
            
            # 过滤出实际存在的列
            display_cols = [col for col in basic_cols + agent_cols if col in available_cols]
            
            if display_cols:
                st.dataframe(combined_df[display_cols], use_container_width=True, height=400)
            else:
                st.warning("暂无可显示的对比数据")
        
        # 显示最佳表现机器人
        if summary:
            best_agent = max(summary.keys(), key=lambda x: (summary[x]['avg_semantic_stability'] + summary[x]['avg_completeness'] + summary[x]['avg_relevance']) / 3)
            st.success(f"🏆 **最佳表现机器人**: {best_agent} (总体分数: {((summary[best_agent]['avg_semantic_stability'] + summary[best_agent]['avg_completeness'] + summary[best_agent]['avg_relevance']) / 3):.1f}%)")
    
    @staticmethod
    def show_export_options(combined_df: pd.DataFrame, summary: Dict, output_path: str):
        """
        显示导出选项
        
        Args:
            combined_df: 合并的结果DataFrame
            summary: 对比摘要
            output_path: 输出文件路径
        """
        st.markdown("### 📥 导出分析结果")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 导出详细数据"):
                csv_data = combined_df.to_csv(index=False)
                st.download_button(
                    label="⬇️ 下载CSV文件",
                    data=csv_data,
                    file_name=f"multi_agent_detailed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        
        with col2:
            if st.button("📈 导出对比报告"):
                report = MultiAgentResultComponents._generate_comparison_report(summary)
                st.download_button(
                    label="⬇️ 下载对比报告",
                    data=report,
                    file_name=f"multi_agent_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown"
                )
        
        with col3:
            if output_path and os.path.exists(output_path):
                st.success(f"✅ 结果已保存到: {os.path.basename(output_path)}")
            else:
                st.info("💾 结果将自动保存")
    
    @staticmethod
    def _generate_comparison_report(summary: Dict) -> str:
        """生成对比报告"""
        if not summary:
            return "# 多机器人对比报告\n\n暂无数据"
        
        report = f"""# 多机器人对比分析报告

## 📊 测试概览
- **测试时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **参与机器人**: {len(summary)} 个
- **测试机器人**: {', '.join(summary.keys())}

## 🏆 性能排名
"""
        
        # 按总体分数排序
        sorted_agents = sorted(summary.items(), key=lambda x: (x[1]['avg_semantic_stability'] + x[1]['avg_completeness'] + x[1]['avg_relevance']) / 3, reverse=True)
        
        for idx, (agent_name, data) in enumerate(sorted_agents, 1):
            quality_score = (data['avg_semantic_stability'] + data['avg_completeness'] + data['avg_relevance']) / 3
            report += f"""
### {idx}. {agent_name}
- **总体分数**: {quality_score:.1f}%
- **语义稳定性**: {data['avg_semantic_stability']:.1f}%
- **完整度**: {data['avg_completeness']:.1f}%
- **相关度**: {data['avg_relevance']:.1f}%
- **冗余度**: {data['avg_redundancy']:.1f}%
- **错误率**: {data['error_rate']:.1f}%
"""
        
        report += f"""
## 📈 分析结论
- **最佳机器人**: {sorted_agents[0][0]}
- **最高质量分数**: {(sorted_agents[0][1]['avg_semantic_stability'] + sorted_agents[0][1]['avg_completeness'] + sorted_agents[0][1]['avg_relevance']) / 3:.1f}%
- **最低错误率**: {min(data['error_rate'] for _, data in summary.items()):.1f}%

---
*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        return report 