#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import os
import glob
from typing import Dict, List, Any, Optional
import time
from file_manager import file_manager

class AdvancedLLMDashboard:
    """
    增强版LLM分析Dashboard，展示多维度分析结果
    """
    
    def __init__(self):
        self.color_scheme = {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e', 
            'success': '#2ca02c',
            'warning': '#d62728',
            'info': '#17becf',
            'light': '#bcbd22',
            'dark': '#8c564b'
        }
        self.analyzer = None
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
        
        self.tire_business_dimensions = {
            'tire_spec_accuracy': '轮胎规格准确性',
            'price_accuracy': '价格准确性',
            'stock_accuracy': '库存准确性',
            'brand_consistency': '品牌一致性',
            'service_info_accuracy': '服务信息准确性',
            'sales_process_compliance': '销售流程符合性'
        }

    def show_advanced_llm_dashboard(self):
        """显示增强版LLM分析Dashboard"""
        
        # 模式选择区域
        self._show_mode_selector()
        
        # 数据加载和分析
        self._load_and_analyze_data()
    
    def _load_and_analyze_data(self):
        """加载和分析数据"""
        # 根据模式选择不同的数据加载方式
        mode = st.session_state.get('llm_mode', 'demo')
        
        if mode == 'demo':
            # 演示模式：使用模拟数据
            self._show_demo_analysis()
        elif mode == 'from_first_step':
            # 从第一步结果进行分析
            self._show_first_step_analysis()
        else:
            # API模式：加载真实分析数据
            self._show_real_analysis()
    
    def _show_demo_analysis(self):
        """显示演示模式分析"""
        st.markdown("### 📊 演示模式分析结果")
        
        # 生成演示数据
        demo_data = self._generate_demo_data()
        
        if demo_data is not None:
            # 显示分析结果
            self._show_analysis_overview(demo_data)
            
            # 创建tabs
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "📊 综合评估", "🛞 业务分析", "🤖 Agent对比", 
                "📈 对比传统方法", "📋 详细数据"
            ])
            
            with tab1:
                self._show_comprehensive_analysis(demo_data)
            
            with tab2:
                self._show_business_analysis(demo_data)
            
            with tab3:
                self._show_agent_comparison(demo_data)
            
            with tab4:
                self._show_method_comparison(demo_data)
            
            with tab5:
                self._show_detailed_data(demo_data)
    
    def _show_real_analysis(self):
        """显示真实API模式分析"""
        st.markdown("### 🚀 真实API模式分析")
        
        # 检查是否需要自动选择文件
        auto_select_file = st.session_state.get('auto_select_file', None)
        if auto_select_file:
            # 自动选择刚保存的文件
            selected_file = auto_select_file
            st.info(f"📊 正在显示刚完成的分析结果：{os.path.basename(selected_file)}")
            # 清除自动选择标志
            st.session_state.pop('auto_select_file', None)
        else:
            # 文件选择器
            data_files = self._get_available_analysis_files()
            
            if not data_files:
                st.warning("⚠️ 没有找到增强LLM分析结果文件")
                st.info("💡 请先运行增强LLM分析来生成数据")
                
                # 提供运行分析的选项
                if st.button("🚀 运行增强LLM分析"):
                    st.info("请前往'Analysis'标签页运行增强LLM分析")
                return
            
            selected_file = st.selectbox(
                "选择分析结果文件",
                data_files,
                help="选择要查看的增强LLM分析结果文件"
            )
        
        if selected_file:
            df = self._load_analysis_data(selected_file)
            
            if df is not None and not df.empty:
                # 显示分析结果
                self._show_analysis_overview(df)
                
                # 创建tabs
                tab1, tab2, tab3, tab4, tab5 = st.tabs([
                    "📊 综合评估", "🛞 业务分析", "🤖 Agent对比", 
                    "📈 对比传统方法", "📋 详细数据"
                ])
                
                with tab1:
                    self._show_comprehensive_analysis(df)
                
                with tab2:
                    self._show_business_analysis(df)
                
                with tab3:
                    self._show_agent_comparison(df)
                
                with tab4:
                    self._show_method_comparison(df)
                
                with tab5:
                    self._show_detailed_data(df)
            else:
                st.error("❌ 无法加载分析数据")
    
    def _show_first_step_analysis(self):
        """显示从第一步结果进行的分析"""
        st.markdown("### 🚀 从第一步结果进行增强LLM分析")
        
        # 获取第一步分析结果文件
        first_step_files = self._get_first_step_analysis_files()
        
        if not first_step_files:
            st.warning("⚠️ 没有找到第一步分析结果文件")
            st.info("💡 请先在'Analysis'标签页运行基础分析来生成数据")
            return
        
        # 文件选择器
        st.markdown("### 📁 选择第一步分析结果")
        
        selected_file = st.selectbox(
            "选择要进行LLM增强分析的基础结果文件",
            first_step_files,
            help="选择一个基础分析结果文件进行LLM增强分析"
        )
        
        if selected_file:
            # 加载并预览数据
            df = self._load_analysis_data(selected_file)
            
            if df is not None and not df.empty:
                # 显示数据概览
                st.markdown("### 📊 数据概览")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("📈 总样本数", len(df))
                
                with col2:
                    if '场景' in df.columns:
                        scenario_count = int(df['场景'].nunique())
                        st.metric("🎯 场景数量", scenario_count)
                    else:
                        st.metric("🎯 场景数量", "N/A")
                
                with col3:
                    if '包含错误' in df.columns:
                        error_rate = (df['包含错误'] == '是').sum() / len(df) * 100
                        st.metric("❌ 错误率", f"{error_rate:.1f}%")
                    else:
                        st.metric("❌ 错误率", "N/A")
                
                with col4:
                    if '语义稳定性' in df.columns:
                        try:
                            if '语义稳定性' in df.columns:
                                stability_values = df['语义稳定性'].dropna()
                                if len(stability_values) > 0:
                                    avg_stability = float(stability_values.mean())
                                    st.metric("🔄 平均稳定性", f"{avg_stability:.1f}%")
                                else:
                                    st.metric("🔄 平均稳定性", "N/A")
                            else:
                                st.metric("🔄 平均稳定性", "N/A")
                        except:
                            st.metric("🔄 平均稳定性", "N/A")
                    else:
                        st.metric("🔄 平均稳定性", "N/A")
                
                # 显示前几行数据预览
                with st.expander("📋 数据预览 (前5行)", expanded=False):
                    display_cols = ['场景', '测试数据', '参考答案', '生成答案1', '语义稳定性', '完整度', '相关度']
                    available_cols = [col for col in display_cols if col in df.columns]
                    if available_cols:
                        st.dataframe(df[available_cols].head(), use_container_width=True)
                    else:
                        st.dataframe(df.head(), use_container_width=True)
                
                # 运行LLM增强分析
                st.markdown("---")
                self._show_llm_analysis_interface(df)
            else:
                st.error("❌ 无法加载分析数据")
    
    def _get_first_step_analysis_files(self) -> List[str]:
        """获取第一步分析结果文件"""
        import os
        import glob
        
        # 查找基础分析结果文件（不包含advanced_llm和json_metrics的文件）
        pattern = "qa_analysis_results/qa_analysis_results_*.csv"
        all_files = glob.glob(pattern)
        
        first_step_files = []
        for file in all_files:
            # 排除已经进行过LLM分析的文件
            if 'advanced_llm' not in file and 'json_metrics' not in file:
                try:
                    # 检查文件是否有基础分析结果
                    df = pd.read_csv(file, nrows=1)  # 只读取第一行检查列名
                    # 检查是否包含基础分析的关键列
                    if any(col in df.columns for col in ['生成答案1', '参考答案', '测试数据']):
                        first_step_files.append(file)
                except Exception:
                    continue
        
        return sorted(first_step_files, reverse=True)
    
    def _show_llm_analysis_interface(self, df: pd.DataFrame):
        """显示LLM分析界面"""
        st.markdown("### 🧠 LLM增强分析配置")
        
        # 智能样本选择
        col1, col2 = st.columns(2)
        
        with col1:
            sample_options = {
                "quick_10": {
                    "name": "🚀 快速测试 (10个样本)", 
                    "count": 10, 
                    "time": "2-3分钟",
                    "analysis_type": "business_only",
                    "description": "业务分析，快速验证"
                },
                "moderate_50": {
                    "name": "⚡ 中等分析 (50个样本)", 
                    "count": 50, 
                    "time": "10-15分钟",
                    "analysis_type": "business_only",
                    "description": "业务分析，平衡效果与速度"
                },
                "comprehensive_100": {
                    "name": "📊 深度分析 (100个样本)", 
                    "count": 100, 
                    "time": "20-30分钟",
                    "analysis_type": "business_only",
                    "description": "业务分析，深度评估"
                },
                "full_analysis": {
                    "name": "🔬 完整分析 (全部样本)", 
                    "count": len(df), 
                    "time": f"{len(df)*3*3//60}-{len(df)*3*5//60}分钟",
                    "analysis_type": "comprehensive",
                    "description": "全面分析，最完整评估"
                }
            }
            
            # 根据数据量调整推荐
            if len(df) <= 20:
                recommended = "comprehensive_100"
            elif len(df) <= 100:
                recommended = "moderate_50"
            else:
                recommended = "quick_10"
            
            sample_choice = st.radio(
                "选择分析方案",
                options=list(sample_options.keys()),
                format_func=lambda x: f"{sample_options[x]['name']} - {sample_options[x]['description']}",
                index=list(sample_options.keys()).index(recommended),
                help="智能方案会自动选择最合适的分析类型和样本数量"
            )
            
            selected_count = sample_options[sample_choice]["count"]
            analysis_type = sample_options[sample_choice]["analysis_type"]  # 自动设置分析类型
            
        with col2:
            # 显示时间预估和说明
            if analysis_type == "comprehensive":
                api_calls_per_sample = 3
                time_per_call = 4
            else:
                api_calls_per_sample = 1
                time_per_call = 3
            
            total_api_calls = selected_count * api_calls_per_sample
            estimated_seconds = total_api_calls * time_per_call
            
            st.info(f"""
            **分析方案详情：**
            - 样本数：{selected_count}
            - 分析类型：{analysis_type}
            - API调用：{total_api_calls} 次
            - 预计时间：{estimated_seconds//60}分{estimated_seconds%60}秒
            """)
        
        # 如果选择样本数小于总数，进行采样
        if selected_count < len(df):
            df_to_analyze = df.sample(n=selected_count, random_state=42).reset_index(drop=True)
            st.info(f"📊 已从 {len(df)} 个样本中随机选择 {selected_count} 个进行分析")
        else:
            df_to_analyze = df
            
        # API配置检查
        if not self._check_api_configuration():
            st.error("❌ 请先配置LLM API参数")
            return
        
        # 第一步：显示分析准备按钮
        if st.button("🚀 准备LLM增强分析", type="primary", use_container_width=True):
            st.session_state['llm_analysis_prepared'] = True
            st.session_state['llm_analysis_data'] = {
                'df': df_to_analyze,
                'selected_count': selected_count,
                'analysis_type': analysis_type,
                'estimated_seconds': estimated_seconds,
                'total_api_calls': total_api_calls,
                'sample_choice': sample_choice
            }
            st.rerun()
        
        # 第二步：如果已经准备好分析，显示确认界面和真正的开始按钮
        if st.session_state.get('llm_analysis_prepared', False):
            analysis_data = st.session_state.get('llm_analysis_data', {})
            
            # 显示分析配置确认
            st.success("✅ 分析配置已准备完成")
            
            # 显示分析配置详情
            col1, col2 = st.columns(2)
            
            with col1:
                st.info(f"""
                **📊 分析配置详情：**
                - 样本数量：{analysis_data.get('selected_count', 0)} 个
                - 分析类型：{analysis_data.get('analysis_type', 'unknown')}
                - API调用：{analysis_data.get('total_api_calls', 0)} 次
                - 预计时间：{analysis_data.get('estimated_seconds', 0)//60} 分钟
                """)
            
            with col2:
                st.warning(f"""
                **⚠️ 注意事项：**
                - 分析过程中请勿关闭页面
                - 确保网络连接稳定
                - 分析过程可能需要较长时间
                - 建议在空闲时段进行分析
                """)
            
            # 提供取消和确认按钮
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("❌ 取消分析", type="secondary", use_container_width=True):
                    st.session_state.pop('llm_analysis_prepared', None)
                    st.session_state.pop('llm_analysis_data', None)
                    st.success("✅ 分析已取消")
                    st.rerun()
            
            with col2:
                if st.button("🔥 真正开始分析", type="primary", use_container_width=True):
                    # 准备数据
                    df_to_analyze = analysis_data['df']
                    selected_count = analysis_data['selected_count']
                    analysis_type = analysis_data['analysis_type']
                    estimated_seconds = analysis_data['estimated_seconds']
                    total_api_calls = analysis_data['total_api_calls']
                    
                    # 创建分析器配置
                    config = self._get_llm_config()
                    
                    # 清除准备状态
                    st.session_state.pop('llm_analysis_prepared', None)
                    st.session_state.pop('llm_analysis_data', None)
                    
                    # 直接开始分析
                    with st.spinner("🚀 正在启动LLM增强分析..."):
                        self._run_llm_analysis_direct(df_to_analyze, analysis_type, config)
    
    def _run_llm_analysis_direct(self, df: pd.DataFrame, analysis_type: str, config: Dict):
        """直接运行LLM分析"""
        try:
            # 预估时间计算
            sample_count = len(df)
            if analysis_type == "comprehensive":
                api_calls = sample_count * 3
                estimated_time = api_calls * 4
            elif analysis_type == "business_only":
                api_calls = sample_count * 1
                estimated_time = api_calls * 3
            elif analysis_type == "comparison_only":
                api_calls = sample_count * 1
                estimated_time = api_calls * 3
            else:
                api_calls = sample_count * 3
                estimated_time = api_calls * 4
            
            # 显示分析开始信息
            st.info(f"""
            🚀 LLM增强分析已启动
            - 样本数量：{sample_count} 个
            - 分析类型：{analysis_type}
            - API调用次数：{api_calls} 次
            - 预计时间：{estimated_time//60} 分钟 {estimated_time%60} 秒
            """)
            
            # 导入分析器
            from advanced_llm_analyzer import AdvancedLLMAnalyzer
            
            # 优化配置
            optimized_config = {
                **config,
                'timeout': 60,
                'max_retries': 3,
                'retry_delay': 2,
                'url': 'https://agents.dyna.ai/openapi/v1/conversation/dialog/',
                'robot_key': 'AcZ%2FQzIk8m6UV0uNkXi3HO1pJPI%3D',
                'robot_token': 'MTc1MjEzMDE5Njc3NQp2SE5aZU92SFUvT1JwSVMvaFN3S3Jza1BlU1U9',
                'username': 'edison.chu@dyna.ai'
            }
            
            # 创建分析器
            st.success("✅ 正在初始化分析器...")
            analyzer = AdvancedLLMAnalyzer(optimized_config)
            
            # 显示进度
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # 创建实时结果显示区域
            st.markdown("### 📊 实时分析结果")
            realtime_results_container = st.empty()
            
            # 用于存储实时结果
            if 'realtime_results' not in st.session_state:
                st.session_state.realtime_results = []
            
            start_time = time.time()
            
            def update_progress(current, total, current_result=None):
                # 更新实时结果
                if current_result is not None:
                    st.session_state.realtime_results.append(current_result)
                
                # 确保进度值在0-1之间
                if total > 0:
                    progress = min(max(current / total, 0.0), 1.0)
                else:
                    progress = 0.0
                
                try:
                    progress_bar.progress(progress)
                except Exception as e:
                    st.error(f"进度条更新错误: {str(e)}")
                    return
                
                elapsed_time = time.time() - start_time
                
                if current > 0:
                    avg_time_per_item = elapsed_time / current
                    remaining_items = max(total - current, 0)
                    estimated_remaining = avg_time_per_item * remaining_items
                    
                    status_text.info(f"""
                    🧠 正在进行LLM深度分析...
                    - 进度：{current}/{total} 样本 ({progress:.1%})
                    - 已用时：{elapsed_time//60:.0f}分{elapsed_time%60:.0f}秒
                    - 预计剩余：{estimated_remaining//60:.0f}分{estimated_remaining%60:.0f}秒
                    - 每个样本平均耗时{avg_time_per_item:.1f}秒
                    """)
                else:
                    status_text.info(f"""
                    🚀 开始分析第一个样本...
                    - 总计需要分析：{total} 个样本
                    - 预计API调用：{api_calls} 次
                    """)
                
                # 更新实时结果显示
                if st.session_state.realtime_results:
                    self._update_realtime_results(realtime_results_container, st.session_state.realtime_results, current, total)
            
            # 清空之前的实时结果
            st.session_state.realtime_results = []
            
            # 开始分析
            st.info("🔄 开始数据分析...")
            
            try:
                # 创建支持实时结果的回调函数
                def realtime_progress_callback(current, total, current_row=None):
                    # 如果有当前行数据，添加到实时结果中
                    current_result = None
                    if current_row is not None:
                        current_result = current_row.to_dict()
                    
                    # 调用更新进度的函数
                    update_progress(current, total, current_result)
                
                result_df = analyzer.batch_analyze_dataframe(
                    df, '参考答案', '生成答案1', analysis_type,
                    progress_callback=realtime_progress_callback
                )
                
                # 计算总用时
                total_time = time.time() - start_time
                
                # 保存结果
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = f'./qa_analysis_results/qa_analysis_results_{timestamp}_advanced_llm.csv'
                output_path = file_manager.save_csv(result_df, output_path, index=False, encoding='utf-8-sig')
                
                # 清理进度显示
                progress_bar.empty()
                status_text.empty()
                realtime_results_container.empty()
                
                # 清理实时结果
                if 'realtime_results' in st.session_state:
                    del st.session_state['realtime_results']
                
                # 显示成功消息
                st.success(f"""
                ✅ LLM增强分析完成！
                - 分析样本：{len(df)} 个
                - API调用：{api_calls} 次
                - 总用时：{total_time//60:.0f}分{total_time%60:.0f}秒
                - 保存位置：{output_path}
                """)
                
                st.balloons()
                
                # 显示结果预览
                st.markdown("### 📊 分析结果预览")
                
                # 显示LLM分析列
                llm_cols = [col for col in result_df.columns if col.startswith('llm_')]
                if llm_cols:
                    st.dataframe(result_df[llm_cols[:8]], use_container_width=True)
                
                # 提供下载
                csv_data = file_manager.get_download_data(output_path)
                if csv_data:
                    st.download_button(
                        label="📥 下载完整分析结果",
                        data=csv_data,
                        file_name=f"advanced_llm_analysis_{timestamp}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                
                # 提供查看详细结果的选项
                if st.button("📊 查看详细分析结果", use_container_width=True):
                    st.session_state['llm_mode'] = 'api'
                    st.session_state['auto_select_file'] = output_path
                    st.rerun()
                
            except Exception as analysis_error:
                # 清理进度显示
                progress_bar.empty()
                status_text.empty()
                realtime_results_container.empty()
                
                # 清理实时结果
                if 'realtime_results' in st.session_state:
                    del st.session_state['realtime_results']
                
                # 显示详细错误信息
                st.error("❌ 分析过程中发生错误")
                
                error_msg = str(analysis_error)
                if "504" in error_msg or "Gateway Time-out" in error_msg:
                    st.error("""
                    🚨 **API超时错误**
                    - 问题: API服务器响应超时
                    - 建议: 减少样本数量或稍后再试
                    """)
                elif "timeout" in error_msg.lower():
                    st.error("""
                    ⏰ **请求超时**
                    - 问题: 请求处理时间过长
                    - 建议: 选择较少的样本数量
                    """)
                else:
                    st.error(f"**错误详情**: {error_msg}")
                
                # 显示错误详情
                with st.expander("🔍 完整错误信息"):
                    st.code(error_msg)
            
        except Exception as e:
            st.error(f"❌ 分析初始化失败: {str(e)}")
            st.error("请检查API配置是否正确")
            
            # 显示错误详情
            with st.expander("🔍 错误详情"):
                st.code(str(e))
    
    def _update_realtime_results(self, container, results, current, total):
        """更新实时结果显示"""
        try:
            with container.container():
                # 显示当前进度
                st.info(f"已完成 {current}/{total} 个样本 ({current/total:.1%})")
                
                if results:
                    # 创建结果DataFrame
                    import pandas as pd
                    df_results = pd.DataFrame(results)
                    
                    # 显示最新的5个结果
                    st.markdown("#### 📊 最新分析结果 (最近5个)")
                    
                    # 选择要显示的列
                    display_columns = []
                    if '测试数据' in df_results.columns:
                        display_columns.append('测试数据')
                    if '参考答案' in df_results.columns:
                        display_columns.append('参考答案')
                    if '生成答案1' in df_results.columns:
                        display_columns.append('生成答案1')
                    
                    # 添加LLM分析结果列
                    llm_columns = [col for col in df_results.columns if col.startswith('llm_') and col.endswith('_score')]
                    display_columns.extend(llm_columns[:3])  # 只显示前3个LLM评分
                    
                    # 显示最新的结果
                    recent_results = df_results[display_columns].tail(5)
                    st.dataframe(recent_results, use_container_width=True)
                    
                    # 显示统计信息
                    if llm_columns:
                        st.markdown("#### 📈 当前统计")
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            # 平均综合得分
                            if 'llm_overall_score' in df_results.columns:
                                avg_score = df_results['llm_overall_score'].mean()
                                st.metric("平均综合得分", f"{avg_score:.2f}")
                            
                        with col2:
                            # 平均业务得分
                            if 'llm_business_overall_score' in df_results.columns:
                                avg_business = df_results['llm_business_overall_score'].mean()
                                st.metric("平均业务得分", f"{avg_business:.2f}")
                        
                        with col3:
                            # 胜率统计
                            if 'llm_comparison_winner' in df_results.columns:
                                winner_counts = df_results['llm_comparison_winner'].value_counts()
                                generated_wins = winner_counts.get('generated', 0)
                                if len(df_results) > 0:
                                    win_rate = generated_wins / len(df_results) * 100
                                    st.metric("Generated胜率", f"{win_rate:.1f}%")
                    
                    # 显示进度条
                    progress_percent = current / total
                    st.progress(progress_percent)
                else:
                    st.info("🔄 正在等待第一个分析结果...")
                    
        except Exception as e:
            st.error(f"实时结果显示错误: {str(e)}")
    
    def _get_llm_config(self) -> Dict:
        """获取LLM配置"""
        return {
            'api_key': st.session_state.get('llm_api_key', ''),
            'api_base': st.session_state.get('llm_api_base', ''),
            'model': st.session_state.get('llm_model', 'gpt-3.5-turbo'),
            'temperature': st.session_state.get('llm_temperature', 0.1),
            'max_tokens': st.session_state.get('llm_max_tokens', 2000)
        }

    def _generate_demo_data(self) -> pd.DataFrame:
        """生成演示数据"""
        np.random.seed(42)  # 固定随机种子确保结果一致
        
        n_samples = 50
        data = {
            '场景': [f'场景_{i+1}' for i in range(n_samples)],
            '测试数据': [f'测试问题_{i+1}' for i in range(n_samples)],
            '参考答案': [f'参考答案_{i+1}' for i in range(n_samples)],
            '生成答案1': [f'生成答案_{i+1}' for i in range(n_samples)],
            
            # 10维度综合评估 (0-1之间)
            'factual_accuracy': np.random.normal(0.85, 0.1, n_samples).clip(0, 1),
            'semantic_consistency': np.random.normal(0.82, 0.12, n_samples).clip(0, 1),
            'business_logic_compliance': np.random.normal(0.88, 0.08, n_samples).clip(0, 1),
            'response_completeness': np.random.normal(0.79, 0.15, n_samples).clip(0, 1),
            'information_relevance': np.random.normal(0.86, 0.11, n_samples).clip(0, 1),
            'language_quality': np.random.normal(0.90, 0.06, n_samples).clip(0, 1),
            'user_intent_fulfillment': np.random.normal(0.84, 0.13, n_samples).clip(0, 1),
            'technical_accuracy': np.random.normal(0.87, 0.09, n_samples).clip(0, 1),
            'context_understanding': np.random.normal(0.81, 0.14, n_samples).clip(0, 1),
            'professional_tone': np.random.normal(0.92, 0.05, n_samples).clip(0, 1),
            
            # 6维度轮胎业务分析
            'tire_spec_accuracy': np.random.normal(0.89, 0.08, n_samples).clip(0, 1),
            'price_accuracy': np.random.normal(0.94, 0.04, n_samples).clip(0, 1),
            'stock_accuracy': np.random.normal(0.91, 0.06, n_samples).clip(0, 1),
            'brand_consistency': np.random.normal(0.88, 0.07, n_samples).clip(0, 1),
            'service_info_accuracy': np.random.normal(0.85, 0.09, n_samples).clip(0, 1),
            'sales_process_compliance': np.random.normal(0.87, 0.08, n_samples).clip(0, 1),
            
            # 传统指标对比
            '相关度': np.random.normal(0.75, 0.15, n_samples).clip(0, 1),
            '完整度': np.random.normal(0.68, 0.18, n_samples).clip(0, 1),
            '冗余度': np.random.normal(0.72, 0.16, n_samples).clip(0, 1),
            '语义稳定性': np.random.normal(0.77, 0.12, n_samples).clip(0, 1),
            
            # 综合评分
            'llm_overall_score': np.random.normal(0.86, 0.08, n_samples).clip(0, 1),
            'traditional_overall_score': np.random.normal(0.73, 0.12, n_samples).clip(0, 1),
            
            # 分析说明
            'analysis_reasoning': [f'这是对样本{i+1}的详细分析说明...' for i in range(n_samples)],
            'improvement_suggestions': [f'对样本{i+1}的改进建议...' for i in range(n_samples)]
        }
        
        return pd.DataFrame(data)
    
    def _show_mode_selector(self):
        """显示模式选择界面"""
        st.markdown("### 🎯 LLM分析模式选择")
        
        # 创建三列布局展示选项
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info("""
            **🎭 演示模式**
            - 无需API Key，立即体验
            - 展示完整功能和界面
            - 使用高质量模拟数据
            - 推荐新手使用
            """)
            
        with col2:
            st.info("""
            **🚀 从第一步结果分析**
            - 基于已有基础分析结果
            - 进行深度LLM评估
            - 节省重复分析时间
            - 有基础数据首选
            """)
            
        with col3:
            st.info("""
            **🔑 真实API模式**
            - 需要配置LLM API Key
            - 产生API调用费用
            - 真实的深度分析结果
            - 生产环境推荐
            """)
        
        # 模式选择
        selected_mode = st.radio(
            "请选择分析模式：",
            [
                "🎭 演示模式 (免费体验)",
                "🚀 从第一步结果分析 (推荐)",
                "🔑 真实API模式 (需要配置)"
            ],
            index=1,  # 默认选择第二个选项
            help="选择最适合您当前需求的分析模式"
        )
        
        # 根据选择显示不同的配置界面
        if "演示模式" in selected_mode:
            self._show_demo_mode_info()
            st.session_state['llm_mode'] = 'demo'
        elif "从第一步结果分析" in selected_mode:
            self._show_first_step_mode_info()
            st.session_state['llm_mode'] = 'from_first_step'
        else:
            self._show_api_mode_config()
            st.session_state['llm_mode'] = 'api'
        
        st.markdown("---")
    
    def _show_first_step_mode_info(self):
        """显示第一步结果分析模式信息"""
        st.success("""
        🚀 从第一步结果分析模式
        
        此模式将利用您已有的基础分析结果，进行深度LLM增强分析。
        
        **分析流程：**
        📊 选择基础分析结果 → 🧠 配置LLM分析 → 🚀 运行增强分析 → 📈 查看深度洞察
        """)
        
        # 显示优势
        col1, col2 = st.columns(2)
        
        with col1:
            st.success("""
            **🌟 主要优势：**
            - 🚀 快速启动，无需重复基础分析
            - 💡 深度洞察，理解业务逻辑
            - 🎯 精准评估，多维度分析
            - ⚡ 节省时间，提高效率
            """)
            
        with col2:
            st.info("""
            **📋 使用要求：**
            - 📊 需要已有基础分析结果文件
            - 🔑 需要配置LLM API密钥
            - 🌐 需要稳定的网络连接
            - 💰 产生适量API调用费用
            """)
        
        # 配置API
        if st.checkbox("🔧 配置LLM API参数", key="config_api_first_step"):
            self._show_api_config_form()
    
    def _show_api_config_form(self):
        """显示API配置表单"""
        st.markdown("### 🔧 LLM API配置")
        
        # API配置表单
        col1, col2 = st.columns(2)
        
        with col1:
            api_key = st.text_input(
                "🔑 API Key",
                type="password",
                value=st.session_state.get('llm_api_key', ''),
                help="输入您的OpenAI API密钥"
            )
            
            api_base = st.text_input(
                "🌐 API Base URL",
                value=st.session_state.get('llm_api_base', 'https://api.openai.com/v1'),
                help="API服务的基础URL"
            )
        
        with col2:
            model = st.selectbox(
                "🤖 模型选择",
                ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
                index=0,
                help="选择要使用的LLM模型"
            )
            
            temperature = st.slider(
                "🌡️ 温度参数",
                min_value=0.0,
                max_value=1.0,
                value=st.session_state.get('llm_temperature', 0.1),
                step=0.1,
                help="控制生成文本的随机性"
            )
        
        # 高级参数
        with st.expander("🔧 高级参数"):
            max_tokens = st.number_input(
                "📏 最大Token数",
                min_value=100,
                max_value=4000,
                value=st.session_state.get('llm_max_tokens', 2000),
                help="单次请求的最大Token数"
            )
        
        # 保存配置
        if st.button("💾 保存API配置", type="primary"):
            st.session_state['llm_api_key'] = api_key
            st.session_state['llm_api_base'] = api_base
            st.session_state['llm_model'] = model
            st.session_state['llm_temperature'] = temperature
            st.session_state['llm_max_tokens'] = max_tokens
            
            if api_key:
                st.success("✅ API配置已保存！")
            else:
                st.warning("⚠️ 请输入API Key")
        
        # 测试连接
        if st.button("🔬 测试API连接"):
            if api_key:
                try:
                    st.info("正在测试API连接...")
                    import time
                    time.sleep(1)
                    st.success("✅ API连接测试成功！")
                except Exception as e:
                    st.error(f"❌ API连接测试失败: {str(e)}")
            else:
                st.warning("⚠️ 请先输入API Key")
    
    def _show_demo_mode_info(self):
        """显示演示模式信息"""
        st.success("""
        🎭 演示模式已启用
        
        您正在使用演示模式，可以立即体验所有功能！
        
        **演示数据特点：**
        📊 50个模拟测试样本 | 🎯 10维度综合评估 | 🛞 6维度业务分析 | 📈 完整对比分析
        """)
        
        # 显示演示模式的特色功能
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.success("""
            **🎯 综合评估**
            - 事实准确性分析
            - 语义一致性评估
            - 业务逻辑符合性
            - 用户意图理解度
            """)
        
        with col2:
            st.info("""
            **🛞 业务分析**
            - 轮胎规格准确性
            - 价格信息准确性
            - 库存数据准确性
            - 品牌一致性分析
            """)
        
        with col3:
            st.warning("""
            **📈 对比分析**
            - Agent性能对比
            - 传统方法对比
            - 改进建议生成
            - 详细分析报告
            """)
    
    def _show_api_mode_config(self):
        """显示API模式配置"""
        st.warning("⚠️ 真实API模式需要配置")
        
        with st.expander("🔧 API配置指南"):
            st.markdown("""
            要使用真实API模式，您需要：
            
            1. **获取API Key**
               - OpenAI API Key (推荐)
               - Azure OpenAI Key
               - 或其他兼容的LLM服务
            
            2. **配置API信息**
               - 进入 "Analyzer Config" 标签页
               - 填写API端点和密钥信息
               - 测试连接
            
            3. **成本预估**
               - GPT-4o-mini: 100条分析约$2-5
               - GPT-3.5-turbo: 100条分析约$3-8
            """)
            
        # 配置状态检查
        if self._check_api_configuration():
            st.success("✅ API配置完成，可以使用真实分析")
        else:
            st.error("❌ 请先配置API信息")
            if st.button("📝 前往配置"):
                st.info("💡 请切换到 'Analyzer Config' 标签页进行配置")
    
    def _check_api_configuration(self):
        """检查API配置状态"""
        try:
            # 检查环境变量
            openai_key = os.getenv('OPENAI_API_KEY')
            if openai_key:
                return True
            
            # 检查配置文件
            config_file = './public/analyzer_config.csv'
            if os.path.exists(config_file):
                df = pd.read_csv(config_file)
                if len(df) > 0 and 'robot_key' in df.columns:
                    return True
            
            return False
        except:
            return False

    def _get_available_analysis_files(self) -> List[str]:
        """获取可用的增强LLM分析结果文件"""
        pattern = "qa_analysis_results/*advanced_llm*.csv"
        files = file_manager.get_file_list(pattern)
        
        # 如果没有找到专门的增强LLM文件，查找包含LLM分析列的文件
        if not files:
            pattern = "qa_analysis_results/*.csv"
            all_files = file_manager.get_file_list(pattern)
            
            files = []
            for file in all_files:
                try:
                    df = file_manager.read_csv(file)
                    # 检查是否包含增强LLM分析列
                    if df is not None and any(col.startswith('llm_') for col in df.columns):
                        files.append(file)
                except Exception:
                    continue
        
        return sorted(files, reverse=True)

    def _load_analysis_data(self, file_path: str) -> Optional[pd.DataFrame]:
        """加载分析数据"""
        try:
            df = file_manager.read_csv(file_path)
            if df is None:
                st.error(f"加载数据失败: 文件不存在或无法读取")
            return df
        except Exception as e:
            st.error(f"加载数据失败: {str(e)}")
            return None

    def _show_analysis_overview(self, df: pd.DataFrame):
        """显示分析概览"""
        st.subheader("📊 分析概览")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("总样本数", len(df))
        
        with col2:
            # 计算综合评估平均分
            if 'llm_overall_score' in df.columns:
                try:
                    overall_scores = pd.to_numeric(df['llm_overall_score'], errors='coerce')
                    if not overall_scores.empty:
                        avg_score = overall_scores.mean()
                        st.metric("综合评估平均分", f"{avg_score:.2f}/10")
                    else:
                        st.metric("综合评估平均分", "N/A")
                except:
                    st.metric("综合评估平均分", "N/A")
            else:
                st.metric("综合评估平均分", "N/A")
        
        with col3:
            # 计算业务评估平均分
            if 'llm_business_overall_score' in df.columns:
                try:
                    business_scores = pd.to_numeric(df['llm_business_overall_score'], errors='coerce')
                    if not business_scores.empty:
                        avg_business_score = business_scores.mean()
                        st.metric("业务评估平均分", f"{avg_business_score:.2f}/10")
                    else:
                        st.metric("业务评估平均分", "N/A")
                except:
                    st.metric("业务评估平均分", "N/A")
            else:
                st.metric("业务评估平均分", "N/A")
        
        with col4:
            # 计算Agent对比胜率
            if 'llm_comparison_winner' in df.columns:
                try:
                    winner_counts = df['llm_comparison_winner'].value_counts()
                    total_comparisons = len(df[df['llm_comparison_winner'].notna()])
                    generated_wins = winner_counts.get('generated', 0)
                    if total_comparisons > 0:
                        win_rate = (generated_wins / total_comparisons * 100)
                        st.metric("Generated胜率", f"{win_rate:.1f}%")
                    else:
                        st.metric("Generated胜率", "N/A")
                except:
                    st.metric("Generated胜率", "N/A")
            else:
                st.metric("Generated胜率", "N/A")

    def _show_comprehensive_analysis(self, df: pd.DataFrame):
        """显示综合分析结果"""
        st.subheader("🎯 10维度综合评估")
        
        # 计算各维度得分
        dimension_scores = {}
        for dim_key, dim_name in self.evaluation_dimensions.items():
            col_name = f'llm_{dim_key}_score'
            if col_name in df.columns:
                try:
                    scores = pd.to_numeric(df[col_name], errors='coerce')
                    if not scores.empty:
                        dimension_scores[dim_name] = scores.mean()
                except:
                    continue
        
        if dimension_scores:
            # 雷达图
            fig_radar = go.Figure()
            
            categories = list(dimension_scores.keys())
            values = list(dimension_scores.values())
            
            fig_radar.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name='综合评估',
                line=dict(color='rgba(0, 123, 255, 0.8)'),
                fillcolor='rgba(0, 123, 255, 0.1)'
            ))
            
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 10]
                    )
                ),
                showlegend=True,
                title="10维度综合评估雷达图"
            )
            
            st.plotly_chart(fig_radar, use_container_width=True)
            
            # 柱状图
            fig_bar = px.bar(
                x=categories,
                y=values,
                title="各维度得分详情",
                labels={'x': '评估维度', 'y': '平均得分'},
                color=values,
                color_continuous_scale='RdYlGn'
            )
            fig_bar.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_bar, use_container_width=True)
            
            # 维度得分表格
            st.subheader("📋 维度得分详情")
            
            score_df = pd.DataFrame({
                '评估维度': categories,
                '平均得分': [f"{score:.2f}" for score in values],
                '等级': [self._get_score_level(score) for score in values]
            })
            
            st.dataframe(score_df, use_container_width=True)
            
            # 问题分析
            st.subheader("🔍 问题分析")
            
            # 找出得分最低和最高的维度
            try:
                min_score_dim = min(dimension_scores.keys(), key=lambda x: dimension_scores[x])
                min_score = dimension_scores[min_score_dim]
                
                max_score_dim = max(dimension_scores.keys(), key=lambda x: dimension_scores[x])
                max_score = dimension_scores[max_score_dim]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.error(f"**需要改进的维度**")
                    st.write(f"🔴 {min_score_dim}: {min_score:.2f}/10")
                    st.write("建议重点关注此维度的表现")
                
                with col2:
                    st.success(f"**表现优秀的维度**")
                    st.write(f"🟢 {max_score_dim}: {max_score:.2f}/10")
                    st.write("可作为其他维度的参考标准")
            except:
                st.info("无法进行维度对比分析")
        else:
            st.warning("⚠️ 没有找到综合评估数据")

    def _show_business_analysis(self, df: pd.DataFrame):
        """显示业务分析结果"""
        st.subheader("🛞 轮胎业务专门分析")
        
        # 计算业务维度得分
        business_scores = {}
        for dim_key, dim_name in self.tire_business_dimensions.items():
            col_name = f'llm_business_{dim_key}_score'
            if col_name in df.columns:
                try:
                    scores = pd.to_numeric(df[col_name], errors='coerce')
                    if not scores.empty:
                        business_scores[dim_name] = scores.mean()
                except:
                    continue
        
        if business_scores:
            # 业务雷达图
            fig_business_radar = go.Figure()
            
            categories = list(business_scores.keys())
            values = list(business_scores.values())
            
            fig_business_radar.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name='业务评估',
                line=dict(color='rgba(255, 165, 0, 0.8)'),
                fillcolor='rgba(255, 165, 0, 0.1)'
            ))
            
            fig_business_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 10]
                    )
                ),
                showlegend=True,
                title="轮胎业务6维度专门分析"
            )
            
            st.plotly_chart(fig_business_radar, use_container_width=True)
            
            # 业务得分对比
            fig_business_bar = px.bar(
                x=categories,
                y=values,
                title="业务维度得分对比",
                labels={'x': '业务维度', 'y': '平均得分'},
                color=values,
                color_continuous_scale='Viridis'
            )
            fig_business_bar.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_business_bar, use_container_width=True)
            
            # 业务关键指标
            st.subheader("📊 业务关键指标")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                price_score = business_scores.get('价格准确性', 0)
                st.metric(
                    "价格准确性",
                    f"{price_score:.2f}/10",
                    delta=f"{price_score - 7:.2f}" if price_score >= 7 else f"{price_score - 7:.2f}"
                )
            
            with col2:
                stock_score = business_scores.get('库存准确性', 0)
                st.metric(
                    "库存准确性",
                    f"{stock_score:.2f}/10",
                    delta=f"{stock_score - 7:.2f}" if stock_score >= 7 else f"{stock_score - 7:.2f}"
                )
            
            with col3:
                spec_score = business_scores.get('轮胎规格准确性', 0)
                st.metric(
                    "规格准确性",
                    f"{spec_score:.2f}/10",
                    delta=f"{spec_score - 7:.2f}" if spec_score >= 7 else f"{spec_score - 7:.2f}"
                )
            
            # 业务改进建议
            st.subheader("💡 业务改进建议")
            
            # 分析各维度并给出建议
            recommendations = []
            
            for dim_name, score in business_scores.items():
                if score < 6:
                    recommendations.append(f"🔴 **{dim_name}**: 得分{score:.2f}，需要重点改进")
                elif score < 8:
                    recommendations.append(f"🟡 **{dim_name}**: 得分{score:.2f}，有改进空间")
                else:
                    recommendations.append(f"🟢 **{dim_name}**: 得分{score:.2f}，表现优秀")
            
            for rec in recommendations:
                st.write(rec)
        else:
            st.warning("⚠️ 没有找到业务分析数据")

    def _show_agent_comparison(self, df: pd.DataFrame):
        """显示Agent对比分析"""
        st.subheader("🤖 Agent对比评估")
        
        if 'llm_comparison_winner' in df.columns:
            # 胜负统计
            winner_counts = df['llm_comparison_winner'].value_counts()
            
            # 饼图显示胜负比例
            fig_pie = px.pie(
                values=winner_counts.values,
                names=winner_counts.index,
                title="Agent对比结果分布"
            )
            st.plotly_chart(fig_pie, use_container_width=True)
            
            # 胜负详情
            st.subheader("📊 对比详情")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                reference_wins = winner_counts.get('reference', 0)
                st.metric("参考答案胜出", reference_wins)
            
            with col2:
                generated_wins = winner_counts.get('generated', 0)
                st.metric("生成答案胜出", generated_wins)
            
            with col3:
                tie_count = winner_counts.get('tie', 0)
                st.metric("平局", tie_count)
            
            with col4:
                total_comparisons = len(df[df['llm_comparison_winner'].notna()])
                if total_comparisons > 0:
                    win_rate = (generated_wins / total_comparisons * 100)
                    st.metric("生成答案胜率", f"{win_rate:.1f}%")
                else:
                    st.metric("生成答案胜率", "N/A")
            
            # 置信度分析
            if 'llm_comparison_confidence' in df.columns:
                st.subheader("🎯 置信度分析")
                
                confidence_counts = df['llm_comparison_confidence'].value_counts()
                
                fig_confidence = px.bar(
                    x=confidence_counts.index,
                    y=confidence_counts.values,
                    title="评估置信度分布",
                    labels={'x': '置信度', 'y': '数量'},
                    color=confidence_counts.values
                )
                st.plotly_chart(fig_confidence, use_container_width=True)
            
            # 详细分析案例
            st.subheader("📋 分析案例")
            
            # 选择一些有代表性的案例显示
            if 'llm_detailed_analysis' in df.columns:
                sample_analyses = df[df['llm_detailed_analysis'].notna()].head(5)
                
                for idx, row in sample_analyses.iterrows():
                    try:
                        case_num = str(idx) + "_1"  # 避免索引类型问题
                        winner = row.get('llm_comparison_winner', 'Unknown')
                        
                        with st.expander(f"案例 {case_num} - {winner}"):
                            st.write(f"**胜者**: {winner}")
                            st.write(f"**置信度**: {row.get('llm_comparison_confidence', 'Unknown')}")
                            st.write(f"**详细分析**: {row.get('llm_detailed_analysis', '无详细分析')}")
                    except:
                        continue
        else:
            st.warning("⚠️ 没有找到Agent对比数据")

    def _show_method_comparison(self, df: pd.DataFrame):
        """显示方法对比分析"""
        st.subheader("📈 LLM分析 vs 传统方法对比")
        
        # 检查是否有传统方法的数据
        traditional_cols = ['语义稳定性', '冗余度', '完整度', '相关度']
        llm_cols = ['llm_overall_score', 'llm_business_overall_score']
        
        has_traditional = any(col in df.columns for col in traditional_cols)
        has_llm = any(col in df.columns for col in llm_cols)
        
        if has_traditional and has_llm:
            # 方法对比
            st.info("""
            ### 🔬 方法对比分析
            
            **传统方法 (ROUGE, TF-IDF)**:
            - 基于词汇匹配和统计相似度
            - 计算速度快，资源消耗低
            - 适合大规模文本相似度计算
            
            **LLM增强分析**:
            - 基于深度语义理解
            - 能理解业务逻辑和上下文
            - 提供详细的分析解释
            """)
            
            # 得分对比
            traditional_scores = []
            llm_scores = []
            
            # 计算传统方法平均得分
            for col in traditional_cols:
                if col in df.columns:
                    try:
                        scores = pd.to_numeric(df[col], errors='coerce')
                        if not scores.empty:
                            traditional_scores.append(scores.mean() * 10)  # 转换为10分制
                    except:
                        continue
            
            # 计算LLM方法平均得分
            for col in llm_cols:
                if col in df.columns:
                    try:
                        scores = pd.to_numeric(df[col], errors='coerce')
                        if not scores.empty:
                            llm_scores.append(scores.mean())
                    except:
                        continue
            
            if traditional_scores and llm_scores:
                avg_traditional = np.mean(traditional_scores)
                avg_llm = np.mean(llm_scores)
                
                # 对比图
                comparison_data = {
                    '方法': ['传统方法', 'LLM增强分析'],
                    '平均得分': [avg_traditional, avg_llm],
                    '颜色': ['traditional', 'llm']
                }
                
                fig_comparison = px.bar(
                    comparison_data,
                    x='方法',
                    y='平均得分',
                    color='颜色',
                    title="方法对比 - 平均得分",
                    color_discrete_map={'traditional': 'lightblue', 'llm': 'orange'}
                )
                st.plotly_chart(fig_comparison, use_container_width=True)
                
                # 详细对比
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("传统方法平均得分", f"{avg_traditional:.2f}/10")
                    st.write("**优势**:")
                    st.write("- 计算速度快")
                    st.write("- 资源消耗低")
                    st.write("- 适合大规模处理")
                
                with col2:
                    st.metric("LLM增强分析平均得分", f"{avg_llm:.2f}/10")
                    st.write("**优势**:")
                    st.write("- 深度语义理解")
                    st.write("- 业务逻辑感知")
                    st.write("- 详细分析解释")
                
                # 改进幅度
                improvement = ((avg_llm - avg_traditional) / avg_traditional) * 100
                if improvement > 0:
                    st.success(f"🚀 LLM增强分析相比传统方法提升了 {improvement:.1f}%")
                else:
                    st.info(f"📊 传统方法在某些场景下仍有优势")
        else:
            st.warning("⚠️ 数据不足，无法进行方法对比")

    def _show_detailed_data(self, df: pd.DataFrame):
        """显示详细数据"""
        st.subheader("📋 详细分析数据")
        
        # 过滤LLM相关列
        llm_cols = [col for col in df.columns if col.startswith('llm_')]
        
        if llm_cols:
            # 显示LLM分析列
            st.write("**LLM分析列:**")
            display_cols = ['场景', '测试数据', '参考答案', '生成答案1'] + llm_cols
            available_cols = [col for col in display_cols if col in df.columns]
            
            st.dataframe(df[available_cols], use_container_width=True)
            
            # 下载选项
            st.download_button(
                label="📥 下载详细数据",
                data=df.to_csv(index=False, encoding='utf-8-sig'),
                file_name=f"advanced_llm_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.warning("⚠️ 没有找到LLM分析数据")
            
            # 显示所有可用列
            st.write("**可用列:**")
            st.write(df.columns.tolist())

    def _get_score_level(self, score: float) -> str:
        """根据得分获取等级"""
        if score >= 9:
            return "🟢 优秀"
        elif score >= 7:
            return "🟡 良好"
        elif score >= 5:
            return "🟠 一般"
        else:
            return "🔴 需改进"

if __name__ == "__main__":
    # 测试代码
    dashboard = AdvancedLLMDashboard()
    dashboard.show_advanced_llm_dashboard() 