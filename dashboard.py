import os
import logging
import pandas as pd
import streamlit as st
from datetime import datetime
import glob
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from file_manager import file_manager

class QADashboard:
    def __init__(self):
        self.metrics = ['语义稳定性', '冗余度', '完整度', '相关度']
        self.binary_metrics = ['语义篡改', '缺失关键信息', '生成无关信息']
        self.data_cache = {}  # Cache for loaded datasets
        
    def load_csv_files(self, pattern='qa_analysis_results/*.csv'):
        """Load all QA analysis result files"""
        # Create qa_analysis_results directory if it doesn't exist
        os.makedirs('qa_analysis_results', exist_ok=True)
        
        files = glob.glob(pattern)
        if not files:
            return []
        files.sort(key=os.path.getmtime, reverse=True)
        return files

    def load_and_process_df(self, file_path, language="auto"):
        """Load and process a single CSV file with language support"""
        if not file_path or file_path == "No analysis files found":
            # Return empty DataFrame with expected columns
            return pd.DataFrame(columns=['场景', '子场景', '数据来源', '是否多轮', '组别', 
                                       '测试数据', '参考答案', '生成答案1', '生成答案2', '生成答案3',
                                       '语义稳定性', '冗余度', '完整度', '相关度'])
        
        # 根据语言获取编码策略
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
        
        return df

    def count_request_failures(self, row):
        """Count Request failures in generated answers"""
        count = 0
        error_patterns = ['Request failed', 'System busy']  # 添加错误模式
        columns = row.index.tolist()
        answer_columns = [col for col in columns if col.startswith('生成答案')]
        for col in answer_columns:
            if col in columns and isinstance(row[col], str):
                if any(pattern in row[col] for pattern in error_patterns):
                    count += 1
        return count

    def calculate_metrics(self, df, filters=None):
        """Calculate metrics based on filtered data"""
        # Create an explicit copy at the start
        df = df.copy()
        
        if filters:
            for col, value in filters.items():
                if value:
                    df = df[df[col] == value]

        total_samples = len(df)
        if total_samples == 0:
            return {}

        # 转换百分比字符串为浮点数
        def convert_percentage(value):
            if pd.isna(value):
                return 0.0
            if isinstance(value, str):
                try:
                    # 移除百分号并转换为浮点数
                    return float(value.strip('%'))
                except ValueError:
                    return 0.0
            return float(value)

        # Use .loc to assign new column
        df.loc[:, 'failure_count'] = df.apply(self.count_request_failures, axis=1)
        total_failures = df['failure_count'].sum()
        failure_rate = total_failures / (total_samples * 3) * 100

        # 计算百分比指标
        metric_means = {}
        for metric in self.metrics:
            if metric in df.columns:
                # 转换数据并计算平均值
                values = df[metric].apply(convert_percentage)
                metric_means[metric] = values.mean()
        
        binary_rates = {}
        for metric in self.binary_metrics:
            if metric in df.columns:
                true_count = df[df[metric] == '是'].shape[0]
                binary_rates[f'{metric}率'] = (true_count / total_samples) * 100
            else:
                binary_rates[f'{metric}率'] = 0
        
        # 添加包含错误率
        if '包含错误' in df.columns:
            error_count = df[df['包含错误'] == '是'].shape[0]
            binary_rates['包含错误率'] = (error_count / total_samples) * 100

        return {
            'total_samples': total_samples,
            'total_failures': total_failures,
            'failure_rate': failure_rate,
            **metric_means,
            **binary_rates
        }

    def show_metric_card(self, title, value, unit="", color="blue", icon="📊"):
        """显示指标卡片"""
        if isinstance(value, (int, float)):
            if unit == "%":
                display_value = f"{value:.1f}%"
            else:
                display_value = f"{value:.1f}{unit}"
        else:
            display_value = str(value)
        
        # 根据指标类型选择颜色
        if color == "blue":
            bg_color = "#E3F2FD"
            border_color = "#2196F3"
        elif color == "green":
            bg_color = "#E8F5E8"
            border_color = "#4CAF50"
        elif color == "red":
            bg_color = "#FFEBEE"
            border_color = "#F44336"
        elif color == "orange":
            bg_color = "#FFF3E0"
            border_color = "#FF9800"
        else:
            bg_color = "#F5F5F5"
            border_color = "#9E9E9E"
        
        st.markdown(f"""
        <div style="
            background-color: {bg_color};
            border: 2px solid {border_color};
            border-radius: 10px;
            padding: 20px;
            margin: 5px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        ">
            <div style="font-size: 24px; margin-bottom: 10px;">{icon}</div>
            <div style="font-size: 28px; font-weight: bold; color: {border_color}; margin-bottom: 5px;">
                {display_value}
            </div>
            <div style="font-size: 14px; color: #666; font-weight: 500;">
                {title}
            </div>
        </div>
        """, unsafe_allow_html=True)

    def show_overview_cards(self, metrics):
        """显示总览卡片"""
        st.markdown("### 📊 总览指标")
        
        # 第一行：基本统计
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            self.show_metric_card(
                "总样本数", 
                metrics.get('total_samples', 0), 
                "个", 
                "blue", 
                "📋"
            )
        
        with col2:
            self.show_metric_card(
                "请求失败数", 
                metrics.get('total_failures', 0), 
                "次", 
                "red", 
                "❌"
            )
        
        with col3:
            self.show_metric_card(
                "失败率", 
                metrics.get('failure_rate', 0), 
                "%", 
                "orange", 
                "⚠️"
            )
        
        with col4:
            # 计算总体质量分数
            quality_score = (
                metrics.get('语义稳定性', 0) + 
                metrics.get('完整度', 0) + 
                metrics.get('相关度', 0)
            ) / 3
            self.show_metric_card(
                "质量分数", 
                quality_score, 
                "%", 
                "green", 
                "⭐"
            )
        
        # 第二行：质量指标
        st.markdown("### 📈 质量指标")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            self.show_metric_card(
                "语义稳定性", 
                metrics.get('语义稳定性', 0), 
                "%", 
                "blue", 
                "🔄"
            )
        
        with col2:
            self.show_metric_card(
                "完整度", 
                metrics.get('完整度', 0), 
                "%", 
                "green", 
                "✅"
            )
        
        with col3:
            self.show_metric_card(
                "相关度", 
                metrics.get('相关度', 0), 
                "%", 
                "green", 
                "🎯"
            )
        
        with col4:
            self.show_metric_card(
                "冗余度", 
                100 - metrics.get('冗余度', 0), 
                "%", 
                "orange", 
                "📝"
            )

    def create_quality_radar_chart(self, metrics):
        """创建质量雷达图"""
        categories = ['语义稳定性', '完整度', '相关度', '冗余度']
        values = [metrics.get(cat, 0) for cat in categories]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='质量指标',
            line=dict(color='#2196F3', width=2),
            fillcolor='rgba(33, 150, 243, 0.3)'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    ticksuffix='%'
                )
            ),
            showlegend=True,
            title="质量指标雷达图",
            title_x=0.5,
            height=400
        )
        
        return fig

    def create_scene_performance_chart(self, df):
        """创建场景性能图表"""
        if '场景' not in df.columns:
            return None
        
        # 计算每个场景的平均指标
        scene_metrics = []
        for scene in df['场景'].unique():
            scene_df = df[df['场景'] == scene]
            scene_data = {
                '场景': scene,
                '样本数': len(scene_df),
                '语义稳定性': scene_df['语义稳定性'].mean() if '语义稳定性' in scene_df.columns else 0,
                '完整度': scene_df['完整度'].mean() if '完整度' in scene_df.columns else 0,
                '相关度': scene_df['相关度'].mean() if '相关度' in scene_df.columns else 0,
            }
            scene_metrics.append(scene_data)
        
        scene_df = pd.DataFrame(scene_metrics)
        
        # 创建条形图
        fig = px.bar(
            scene_df.head(10),  # 只显示前10个场景
            x='场景',
            y=['语义稳定性', '完整度', '相关度'],
            title="各场景质量指标对比",
            labels={'value': '分数 (%)', 'variable': '指标类型'},
            color_discrete_map={
                '语义稳定性': '#2196F3',
                '完整度': '#4CAF50',
                '相关度': '#FF9800'
            }
        )
        
        fig.update_layout(
            xaxis_title="场景",
            yaxis_title="分数 (%)",
            height=400,
            xaxis_tickangle=-45
        )
        
        return fig

    def create_error_distribution_chart(self, df):
        """创建错误分布图表"""
        error_columns = ['语义篡改', '缺失关键信息', '生成无关信息']
        error_counts = {}
        
        for col in error_columns:
            if col in df.columns:
                error_counts[col] = (df[col] == '是').sum()
            else:
                error_counts[col] = 0
        
        if not any(error_counts.values()):
            return None
        
        fig = go.Figure(data=[
            go.Bar(
                x=list(error_counts.keys()),
                y=list(error_counts.values()),
                marker_color=['#F44336', '#FF9800', '#9C27B0']
            )
        ])
        
        fig.update_layout(
            title="错误类型分布",
            xaxis_title="错误类型",
            yaxis_title="错误数量",
            height=400
        )
        
        return fig

    def show_interactive_filters(self, df):
        """显示交互式过滤器"""
        st.markdown("### 🔍 智能过滤器")
        
        # 创建更美观的过滤器布局
        with st.expander("📋 高级过滤选项", expanded=True):
            filters = {}
            
            # 第一行过滤器
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if '场景' in df.columns:
                    scene_values = ['全部'] + sorted(df['场景'].unique().tolist())
                    selected_scene = st.selectbox('🎯 场景', scene_values, key='scene_filter')
                    filters['场景'] = selected_scene if selected_scene != '全部' else ''
                else:
                    st.info("场景列不存在")
                    filters['场景'] = ''
            
            with col2:
                if '数据来源' in df.columns:
                    source_values = ['全部'] + sorted(df['数据来源'].unique().tolist())
                    selected_source = st.selectbox('📊 数据来源', source_values, key='source_filter')
                    filters['数据来源'] = selected_source if selected_source != '全部' else ''
                else:
                    st.info("数据来源列不存在")
                    filters['数据来源'] = ''
            
            with col3:
                if '组别' in df.columns:
                    group_values = ['全部'] + sorted(df['组别'].unique().tolist())
                    selected_group = st.selectbox('👥 组别', group_values, key='group_filter')
                    filters['组别'] = selected_group if selected_group != '全部' else ''
                else:
                    st.info("组别列不存在")
                    filters['组别'] = ''
            
            # 第二行过滤器
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # 质量分数过滤
                quality_range = st.slider(
                    '📈 质量分数范围', 
                    0.0, 100.0, (0.0, 100.0), 
                    step=5.0,
                    help="根据平均质量分数过滤数据"
                )
            
            with col2:
                # 错误过滤
                show_errors_only = st.checkbox('❌ 仅显示有错误的数据', help="只显示包含错误的样本")
            
            with col3:
                # 失败请求过滤
                show_failures_only = st.checkbox('⚠️ 仅显示失败请求', help="只显示有请求失败的样本")
        
        return filters, quality_range, show_errors_only, show_failures_only

    def apply_filters(self, df, filters, quality_range, show_errors_only, show_failures_only):
        """应用过滤器"""
        filtered_df = df.copy()
        
        # 应用基本过滤器
        for col, value in filters.items():
            if value and col in filtered_df.columns:
                filtered_df = filtered_df[filtered_df[col] == value]
        
        # 应用质量分数过滤
        if '语义稳定性' in filtered_df.columns and '完整度' in filtered_df.columns and '相关度' in filtered_df.columns:
            def calculate_quality_score(row):
                score = (
                    float(str(row['语义稳定性']).strip('%')) + 
                    float(str(row['完整度']).strip('%')) + 
                    float(str(row['相关度']).strip('%'))
                ) / 3
                return score
            
            filtered_df['质量分数'] = filtered_df.apply(calculate_quality_score, axis=1)
            filtered_df = filtered_df[
                (filtered_df['质量分数'] >= quality_range[0]) & 
                (filtered_df['质量分数'] <= quality_range[1])
            ]
        
        # 应用错误过滤
        if show_errors_only and '包含错误' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['包含错误'] == '是']
        
        # 应用失败请求过滤
        if show_failures_only:
            filtered_df['has_failure'] = filtered_df.apply(
                lambda row: self.count_request_failures(row) > 0, axis=1
            )
            filtered_df = filtered_df[filtered_df['has_failure'] == True]
        
        return filtered_df

    def get_example_file(self):
        """Get the example file path"""
        example_path = "futu_test_data_v1.csv"
        if os.path.exists(example_path):
            try:
                with open(example_path, 'rb') as f:
                    return f.read()
            except Exception as e:
                logging.error(f"Error reading example file: {str(e)}")
                return None
        return None

    def show_dashboard(self, df=None):
        """显示美化后的仪表板"""
        # 现代化的页面标题
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: white; padding: 30px; border-radius: 20px; margin-bottom: 30px;
                    box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);">
            <div style="text-align: center;">
                <h1 style="margin: 0; font-size: 2.8rem; font-weight: 700;">
                    🎯 智能QA分析仪表板
                </h1>
                <p style="margin: 15px 0 0 0; font-size: 1.3rem; opacity: 0.9;">
                    实时监控机器人问答质量
                </p>
                <div style="margin-top: 20px; display: flex; justify-content: center; gap: 20px; flex-wrap: wrap;">
                    <span style="background: rgba(255,255,255,0.2); padding: 8px 16px; border-radius: 20px; font-size: 0.9rem;">
                        📊 数据可视化
                    </span>
                    <span style="background: rgba(255,255,255,0.2); padding: 8px 16px; border-radius: 20px; font-size: 0.9rem;">
                        📈 趋势分析
                    </span>
                    <span style="background: rgba(255,255,255,0.2); padding: 8px 16px; border-radius: 20px; font-size: 0.9rem;">
                        🔍 深度洞察
                    </span>
                    <span style="background: rgba(255,255,255,0.2); padding: 8px 16px; border-radius: 20px; font-size: 0.9rem;">
                        📋 报告生成
                    </span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        files = self.load_csv_files()
        
        if not files:
            st.markdown("""
            <div style="text-align: center; padding: 60px; 
                        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                        color: white; border-radius: 20px; margin: 30px 0;
                        box-shadow: 0 8px 25px rgba(240, 147, 251, 0.3);">
                <h2 style="margin: 0 0 15px 0; font-size: 2rem;">📊 暂无分析数据</h2>
                <p style="margin: 0; font-size: 1.1rem; opacity: 0.9;">
                    请先运行一次分析以生成数据
                </p>
                <div style="margin-top: 25px; background: rgba(255,255,255,0.2); 
                            padding: 15px; border-radius: 15px; display: inline-block;">
                    <span style="font-size: 1rem;">💡 前往 Analysis 标签页开始分析</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            return None
        
        # 美化文件选择和语言设置区域
        st.markdown("""
        <div style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); 
                    color: #333; padding: 20px; border-radius: 15px; margin: 20px 0;
                    box-shadow: 0 4px 15px rgba(168, 237, 234, 0.2);">
            <h3 style="margin: 0 0 10px 0; text-align: center; color: #2c3e50;">
                🔧 配置选项
            </h3>
            <p style="margin: 0; text-align: center; font-size: 0.9rem; opacity: 0.8;">
                选择要分析的数据文件和语言设置
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # 文件选择和语言设置
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown("""
            <div style="background: white; padding: 15px; border-radius: 10px; 
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin: 10px 0;">
                <h4 style="margin: 0 0 10px 0; color: #2c3e50;">📁 选择分析文件</h4>
            </div>
            """, unsafe_allow_html=True)
            
            # 美化文件选择
            file_options = [f"📊 {os.path.basename(f)} ({datetime.fromtimestamp(os.path.getmtime(f)).strftime('%Y-%m-%d %H:%M')})" for f in files]
            selected_index = st.selectbox('选择分析文件', file_options, label_visibility='collapsed')
            selected_file = files[file_options.index(selected_index)]
        
        with col2:
            st.markdown("""
            <div style="background: white; padding: 15px; border-radius: 10px; 
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin: 10px 0;">
                <h4 style="margin: 0 0 10px 0; color: #2c3e50;">🌐 语言设置</h4>
            </div>
            """, unsafe_allow_html=True)
            
            from ui_components import DataValidationComponents
            selected_language = DataValidationComponents.show_language_selector("_dashboard")
        
        # 加载数据
        if df is None:
            df = self.load_and_process_df(selected_file, selected_language)
            
            # 如果没有"包含错误"列，添加该列
            if '包含错误' not in df.columns and not df.empty:
                df['包含错误'] = df.apply(
                    lambda row: '否' if (
                        (row.get('生成无关内容', '') != '是') and 
                        (row.get('语义篡改', '') != '是') and 
                        (row.get('缺失关键信息', '') != '是')
                    ) else '是', 
                    axis=1
                )
        
        if df is None or df.empty:
            st.error("📊 数据加载失败，请检查文件格式")
            return None
        
        # 显示交互式过滤器
        filters, quality_range, show_errors_only, show_failures_only = self.show_interactive_filters(df)
        
        # 应用过滤器
        filtered_df = self.apply_filters(df, filters, quality_range, show_errors_only, show_failures_only)
        
        # 显示过滤结果
        st.markdown(f"### 📊 数据概览 ({len(filtered_df)}/{len(df)} 条记录)")
        
        # 计算指标
        metrics = self.calculate_metrics(filtered_df)
        
        if not metrics:
            st.warning("📊 没有数据可以分析")
            return None
        
        # 显示总览卡片
        self.show_overview_cards(metrics)
        
        # 显示图表
        st.markdown("---")
        st.markdown("### 📈 可视化分析")
        
        # 第一行图表
        col1, col2 = st.columns(2)
        
        with col1:
            # 雷达图
            radar_fig = self.create_quality_radar_chart(metrics)
            st.plotly_chart(radar_fig, use_container_width=True)
        
        with col2:
            # 错误分布图
            error_fig = self.create_error_distribution_chart(filtered_df)
            if error_fig:
                st.plotly_chart(error_fig, use_container_width=True)
            else:
                st.info("🎉 没有检测到错误数据")
        
        # 第二行图表
        if '场景' in filtered_df.columns:
            scene_fig = self.create_scene_performance_chart(filtered_df)
            if scene_fig:
                st.plotly_chart(scene_fig, use_container_width=True)
        
        # 详细数据表
        st.markdown("---")
        st.markdown("### 📋 详细数据")
        
        # 选择要显示的列
        available_columns = filtered_df.columns.tolist()
        default_columns = ['场景', '测试数据', '参考答案', '生成答案1', '语义稳定性', '完整度', '相关度', '包含错误']
        display_columns = [col for col in default_columns if col in available_columns]
        
        if display_columns:
            # 创建美化的数据表
            display_df = filtered_df[display_columns].copy()
            
            # 格式化数据
            for col in display_df.columns:
                if col in ['语义稳定性', '完整度', '相关度', '冗余度']:
                    display_df[col] = display_df[col].apply(
                        lambda x: f"{float(str(x).strip('%')):.1f}%" if pd.notna(x) else "N/A"
                    )
            
            st.dataframe(
                display_df,
                use_container_width=True,
                height=400
            )
        else:
            st.warning("📊 没有可显示的列")
        
        # 导出功能
        st.markdown("---")
        st.markdown("### 📥 导出数据")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 导出当前数据为CSV"):
                csv_data = filtered_df.to_csv(index=False)
                st.download_button(
                    label="⬇️ 下载CSV文件",
                    data=csv_data,
                    file_name=f"filtered_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        
        with col2:
            if st.button("📈 导出分析报告"):
                report = self.generate_analysis_report(metrics, filtered_df)
                st.download_button(
                    label="⬇️ 下载分析报告",
                    data=report,
                    file_name=f"analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown"
                )
        
        with col3:
            st.info("💡 提示：使用过滤器来精确分析特定场景的表现")
        
        return filtered_df
    
    def generate_analysis_report(self, metrics, df):
        """生成分析报告"""
        report = f"""# QA分析报告
        
## 📊 总体概览
- **总样本数**: {metrics.get('total_samples', 0)}
- **请求失败数**: {metrics.get('total_failures', 0)}
- **失败率**: {metrics.get('failure_rate', 0):.1f}%
- **质量分数**: {(metrics.get('语义稳定性', 0) + metrics.get('完整度', 0) + metrics.get('相关度', 0)) / 3:.1f}%

## 📈 质量指标
- **语义稳定性**: {metrics.get('语义稳定性', 0):.1f}%
- **完整度**: {metrics.get('完整度', 0):.1f}%
- **相关度**: {metrics.get('相关度', 0):.1f}%
- **冗余度**: {metrics.get('冗余度', 0):.1f}%

## ❌ 错误分析
- **语义篡改率**: {metrics.get('语义篡改率', 0):.1f}%
- **缺失关键信息率**: {metrics.get('缺失关键信息率', 0):.1f}%
- **生成无关信息率**: {metrics.get('生成无关信息率', 0):.1f}%

## 📋 场景分析
"""
        
        if '场景' in df.columns:
            scene_stats = df.groupby('场景').size().sort_values(ascending=False)
            report += "\n### 场景分布\n"
            for scene, count in scene_stats.head(10).items():
                report += f"- {scene}: {count} 个样本\n"
        
        report += f"\n---\n*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
        
        return report

    def create_trend_chart(self, files):
        """Create trend chart for multiple files"""
        if len(files) < 2:
            return None
        
        trends = []
        for file in files[-10:]:  # Last 10 files
            try:
                df = self.load_and_process_df(file)
                if df.empty:
                    continue
                
                metrics = self.calculate_metrics(df)
                file_date = datetime.fromtimestamp(os.path.getmtime(file))
                
                trends.append({
                    'Date': file_date,
                    'File': os.path.basename(file),
                    '语义稳定性': metrics.get('语义稳定性', 0),
                    '完整度': metrics.get('完整度', 0),
                    '相关度': metrics.get('相关度', 0),
                    '失败率': metrics.get('failure_rate', 0)
                })
            except Exception as e:
                logging.error(f"Error processing file {file}: {str(e)}")
                continue
        
        if not trends:
            return None
        
        trend_df = pd.DataFrame(trends)
        
        fig = go.Figure()
        
        colors = ['#2196F3', '#4CAF50', '#FF9800', '#F44336']
        metrics_to_plot = ['语义稳定性', '完整度', '相关度', '失败率']
        
        for i, metric in enumerate(metrics_to_plot):
            fig.add_trace(go.Scatter(
                x=trend_df['Date'],
                y=trend_df[metric],
                mode='lines+markers',
                name=metric,
                line=dict(color=colors[i], width=3),
                marker=dict(size=8)
            ))
        
        fig.update_layout(
            title='历史趋势分析',
            xaxis_title='时间',
            yaxis_title='分数 (%)',
            hovermode='x unified',
            height=500
        )
        
        return fig