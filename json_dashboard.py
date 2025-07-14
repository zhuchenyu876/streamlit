#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
import pandas as pd
import streamlit as st
from datetime import datetime
import glob
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import json
from typing import Dict, List, Optional
import re

class JSONDashboard:
    """专门用于分析JSON格式轮胎查询结果的Dashboard"""
    
    def __init__(self):
        # 修正JSON指标列名以匹配实际CSV文件
        self.json_metrics_base = [
            'json_structure_consistency', 'json_format_correctness', 
            'json_price_accuracy', 'json_stock_accuracy', 
            'json_product_coverage', 'json_description_similarity'
        ]
        
        # 实际CSV文件中的列名（包含_answer1_answer2后缀）
        self.json_metrics = [
            'json_structure_consistency_answer1_answer2', 'json_format_correctness_answer1_answer2',
            'json_price_accuracy_answer1_answer2', 'json_stock_accuracy_answer1_answer2',
            'json_product_coverage_answer1_answer2', 'json_description_similarity_answer1_answer2'
        ]
        
        # 单独的answer2指标
        self.json_metrics_answer2 = [
            'json_structure_consistency_answer2', 'json_format_correctness_answer2',
            'json_price_accuracy_answer2', 'json_stock_accuracy_answer2',
            'json_product_coverage_answer2', 'json_description_similarity_answer2'
        ]
        
        self.traditional_metrics = ['语义稳定性', '冗余度', '完整度', '相关度']
        self.data_cache = {}
        
    def load_json_analysis_files(self, pattern='qa_analysis_results/*json_metrics.csv'):
        """加载JSON分析结果文件"""
        os.makedirs('qa_analysis_results', exist_ok=True)
        files = glob.glob(pattern)
        if not files:
            return []
        files.sort(key=os.path.getmtime, reverse=True)
        return files
    
    def load_and_process_df(self, file_path: str) -> pd.DataFrame:
        """加载和处理JSON分析结果文件"""
        if not file_path or file_path == "No analysis files found":
            return pd.DataFrame()
        
        try:
            df = pd.read_csv(file_path, encoding='utf-8-sig')
            return df
        except Exception as e:
            logging.error(f"Error loading file {file_path}: {e}")
            return pd.DataFrame()
    
    def parse_json_response(self, response_text: str) -> Dict:
        """解析JSON响应文本"""
        try:
            if isinstance(response_text, str):
                data = json.loads(response_text)
                return {
                    'type': data.get('type', ''),
                    'has_data': bool(data.get('data', '')),
                    'has_desc': bool(data.get('desc', '')),
                    'product_count': len(self._extract_products_from_markdown(data.get('data', ''))),
                    'price_range': self._extract_price_range(data.get('desc', ''))
                }
        except (json.JSONDecodeError, TypeError):
            return {'type': '', 'has_data': False, 'has_desc': False, 'product_count': 0, 'price_range': (0, 0)}
    
    def _extract_products_from_markdown(self, markdown_text: str) -> List[Dict]:
        """从markdown表格中提取产品信息"""
        products = []
        if not markdown_text:
            return products
        
        lines = markdown_text.split('\\n')
        for line in lines:
            if '|' in line and 'ID Producto' not in line and ':---' not in line:
                parts = [p.strip() for p in line.split('|') if p.strip()]
                if len(parts) >= 4:
                    try:
                        price = float(re.sub(r'[^\d.]', '', parts[3]))
                        products.append({
                            'id': parts[0],
                            'name': parts[1],
                            'stock': int(parts[2]) if parts[2].isdigit() else 0,
                            'price': price
                        })
                    except (ValueError, IndexError):
                        continue
        return products
    
    def _extract_price_range(self, desc_text: str) -> tuple:
        """从描述中提取价格范围"""
        if not desc_text:
            return (0, 0)
        
        prices = re.findall(r'\$(\d+)', desc_text)
        if prices:
            price_values = [int(p) for p in prices]
            return (min(price_values), max(price_values))
        return (0, 0)
    
    def calculate_json_metrics(self, df: pd.DataFrame) -> Dict:
        """计算JSON专门指标"""
        if df.empty:
            return {}
        
        total_samples = len(df)
        metrics = {}
        
        # 计算JSON专门指标
        for metric in self.json_metrics:
            if metric in df.columns:
                series = df[metric]
                numeric_series = pd.to_numeric(series, errors='coerce').fillna(0)
                metrics[metric] = numeric_series.mean() * 100  # 转换为百分比
        
        # 计算传统指标对比
        for metric in self.traditional_metrics:
            if metric in df.columns:
                values = pd.to_numeric(df[metric], errors='coerce').fillna(0)
                metrics[f'traditional_{metric}'] = values.mean() * 100
        
        # 计算产品数量统计
        if '参考答案' in df.columns and '生成答案1' in df.columns:
            ref_products = []
            gen_products = []
            
            for idx, row in df.iterrows():
                ref_parsed = self.parse_json_response(row.get('参考答案', ''))
                gen_parsed = self.parse_json_response(row.get('生成答案1', ''))
                
                ref_products.append(ref_parsed['product_count'])
                gen_products.append(gen_parsed['product_count'])
            
            metrics['avg_ref_products'] = np.mean(ref_products) if ref_products else 0
            metrics['avg_gen_products'] = np.mean(gen_products) if gen_products else 0
            metrics['product_count_diff'] = metrics['avg_gen_products'] - metrics['avg_ref_products']
        
        metrics['total_samples'] = total_samples
        return metrics
    
    def show_json_metric_card(self, title: str, value: float, unit: str = "%", 
                             color: str = "blue", icon: str = "📊", 
                             comparison_value: Optional[float] = None):
        """显示JSON指标卡片"""
        if isinstance(value, (int, float)):
            if unit == "%":
                display_value = f"{value:.1f}%"
            else:
                display_value = f"{value:.1f}{unit}"
        else:
            display_value = str(value)
        
        # 颜色选择
        color_map = {
            "blue": ("#E3F2FD", "#2196F3"),
            "green": ("#E8F5E8", "#4CAF50"),
            "red": ("#FFEBEE", "#F44336"),
            "orange": ("#FFF3E0", "#FF9800"),
            "purple": ("#F3E5F5", "#9C27B0")
        }
        
        bg_color, border_color = color_map.get(color, color_map["blue"])
        
        # 对比信息
        comparison_text = ""
        if comparison_value is not None:
            diff = value - comparison_value
            if diff > 0:
                comparison_text = f"<div style='color: #4CAF50; font-size: 12px;'>↑ +{diff:.1f}% vs传统</div>"
            elif diff < 0:
                comparison_text = f"<div style='color: #F44336; font-size: 12px;'>↓ {diff:.1f}% vs传统</div>"
            else:
                comparison_text = f"<div style='color: #9E9E9E; font-size: 12px;'>= 相同</div>"
        
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
            {comparison_text}
        </div>
        """, unsafe_allow_html=True)
    
    def show_json_overview_cards(self, metrics: Dict):
        """显示JSON专门指标总览卡片"""
        st.markdown("### 📊 JSON专门指标总览")
        
        # 第一行：结构和格式指标
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            self.show_json_metric_card(
                "结构一致性", 
                metrics.get('json_structure_consistency_answer1_answer2', 0), 
                "%", 
                "blue", 
                "🏗️"
            )
        
        with col2:
            self.show_json_metric_card(
                "格式正确性", 
                metrics.get('json_format_correctness_answer1_answer2', 0), 
                "%", 
                "green", 
                "✅"
            )
        
        with col3:
            self.show_json_metric_card(
                "价格准确性", 
                metrics.get('json_price_accuracy_answer1_answer2', 0), 
                "%", 
                "orange", 
                "💰"
            )
        
        with col4:
            self.show_json_metric_card(
                "库存准确性", 
                metrics.get('json_stock_accuracy_answer1_answer2', 0), 
                "%", 
                "purple", 
                "📦"
            )
        
        # 第二行：内容和产品指标
        st.markdown("### 🎯 内容质量指标")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            self.show_json_metric_card(
                "产品覆盖率", 
                metrics.get('json_product_coverage_answer1_answer2', 0), 
                "%", 
                "blue", 
                "🛞"
            )
        
        with col2:
            self.show_json_metric_card(
                "描述相似度", 
                metrics.get('json_description_similarity_answer1_answer2', 0), 
                "%", 
                "green", 
                "📝"
            )
        
        with col3:
            self.show_json_metric_card(
                "参考产品数", 
                metrics.get('avg_ref_products', 0), 
                "个", 
                "orange", 
                "🎯"
            )
        
        with col4:
            self.show_json_metric_card(
                "生成产品数", 
                metrics.get('avg_gen_products', 0), 
                "个", 
                "purple", 
                "🔄"
            )
        
        # 第三行：对比指标
        st.markdown("### 📈 传统指标对比")
        col1, col2, col3, col4 = st.columns(4)
        
        traditional_metrics_display = [
            ('语义稳定性', 'traditional_语义稳定性', 'blue', '🔄'),
            ('冗余度', 'traditional_冗余度', 'red', '🔄'),
            ('完整度', 'traditional_完整度', 'green', '✅'),
            ('相关度', 'traditional_相关度', 'orange', '🎯')
        ]
        
        cols = [col1, col2, col3, col4]
        for i, (title, key, color, icon) in enumerate(traditional_metrics_display):
            with cols[i]:
                self.show_json_metric_card(
                    title, 
                    metrics.get(key, 0), 
                    "%", 
                    color, 
                    icon
                )
    
    def create_json_comparison_chart(self, metrics: Dict):
        """创建JSON指标与传统指标对比图表"""
        st.markdown("### 📊 JSON指标 vs 传统指标对比")
        
        # 准备数据
        json_metrics_data = {
            '结构一致性': metrics.get('json_structure_consistency_answer1_answer2', 0),
            '格式正确性': metrics.get('json_format_correctness_answer1_answer2', 0),
            '价格准确性': metrics.get('json_price_accuracy_answer1_answer2', 0),
            '库存准确性': metrics.get('json_stock_accuracy_answer1_answer2', 0),
            '产品覆盖率': metrics.get('json_product_coverage_answer1_answer2', 0),
            '描述相似度': metrics.get('json_description_similarity_answer1_answer2', 0)
        }
        
        traditional_metrics_data = {
            '语义稳定性': metrics.get('traditional_语义稳定性', 0),
            '冗余度': metrics.get('traditional_冗余度', 0),
            '完整度': metrics.get('traditional_完整度', 0),
            '相关度': metrics.get('traditional_相关度', 0)
        }
        
        # 创建对比图表
        col1, col2 = st.columns(2)
        
        with col1:
            fig1 = go.Figure()
            fig1.add_trace(go.Bar(
                x=list(json_metrics_data.keys()),
                y=list(json_metrics_data.values()),
                name='JSON专门指标',
                marker_color='#2196F3'
            ))
            fig1.update_layout(
                title='JSON专门指标表现',
                xaxis_title='指标类型',
                yaxis_title='分数 (%)',
                yaxis=dict(range=[0, 100])
            )
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(
                x=list(traditional_metrics_data.keys()),
                y=list(traditional_metrics_data.values()),
                name='传统指标',
                marker_color='#FF9800'
            ))
            fig2.update_layout(
                title='传统指标表现',
                xaxis_title='指标类型',
                yaxis_title='分数 (%)',
                yaxis=dict(range=[0, 100])
            )
            st.plotly_chart(fig2, use_container_width=True)
    
    def create_product_analysis_chart(self, df: pd.DataFrame):
        """创建产品数量分析图表"""
        st.markdown("### 🛞 产品数量分析")
        
        if df.empty or '参考答案' not in df.columns or '生成答案1' not in df.columns:
            st.warning("缺少必要的数据列进行产品分析")
            return
        
        # 提取产品数量数据
        ref_products = []
        gen_products = []
        scenarios = []
        
        for idx, row in df.iterrows():
            ref_parsed = self.parse_json_response(row.get('参考答案', ''))
            gen_parsed = self.parse_json_response(row.get('生成答案1', ''))
            
            ref_products.append(ref_parsed['product_count'])
            gen_products.append(gen_parsed['product_count'])
            scenarios.append(row.get('场景', f'样本{idx+1}'))
        
        # 创建产品数量对比图表
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=list(range(len(ref_products))),
            y=ref_products,
            mode='lines+markers',
            name='参考答案产品数',
            line=dict(color='#4CAF50'),
            marker=dict(size=8)
        ))
        fig.add_trace(go.Scatter(
            x=list(range(len(gen_products))),
            y=gen_products,
            mode='lines+markers',
            name='生成答案产品数',
            line=dict(color='#F44336'),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title='产品数量对比（参考答案 vs 生成答案）',
            xaxis_title='样本编号',
            yaxis_title='产品数量',
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 统计信息
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "平均参考产品数",
                f"{np.mean(ref_products):.1f}",
                f"范围: {min(ref_products)}-{max(ref_products)}"
            )
        
        with col2:
            st.metric(
                "平均生成产品数",
                f"{np.mean(gen_products):.1f}",
                f"范围: {min(gen_products)}-{max(gen_products)}"
            )
        
        with col3:
            diff = np.mean(gen_products) - np.mean(ref_products)
            st.metric(
                "平均差异",
                f"{diff:+.1f}",
                f"{'过多' if diff > 0 else '过少' if diff < 0 else '相等'}"
            )
    
    def create_json_format_analysis(self, df: pd.DataFrame):
        """创建JSON格式分析"""
        st.markdown("### 🔧 JSON格式详细分析")
        
        if df.empty:
            st.warning("没有数据可供分析")
            return
        
        # 分析JSON格式问题
        format_issues = {
            '结构完整性': 0,
            '数据表格格式': 0,
            '描述字段存在': 0,
            '价格格式正确': 0,
            '产品ID格式': 0
        }
        
        total_samples = len(df)
        
        for idx, row in df.iterrows():
            # 分析生成答案1
            gen_answer = row.get('生成答案1', '')
            if gen_answer:
                try:
                    data = json.loads(gen_answer)
                    
                    # 检查结构完整性
                    if 'type' in data and 'data' in data and 'desc' in data:
                        format_issues['结构完整性'] += 1
                    
                    # 检查数据表格格式
                    if data.get('data') and '| ID Producto |' in data.get('data', ''):
                        format_issues['数据表格格式'] += 1
                    
                    # 检查描述字段
                    if data.get('desc') and len(data.get('desc', '')) > 50:
                        format_issues['描述字段存在'] += 1
                    
                    # 检查价格格式
                    if '$' in data.get('data', ''):
                        format_issues['价格格式正确'] += 1
                    
                    # 检查产品ID格式
                    if 'LL-' in data.get('data', '') or 'C' in data.get('data', ''):
                        format_issues['产品ID格式'] += 1
                        
                except json.JSONDecodeError:
                    continue
        
        # 转换为百分比
        format_percentages = {k: (v/total_samples)*100 for k, v in format_issues.items()}
        
        # 创建格式分析图表
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=list(format_percentages.keys()),
            y=list(format_percentages.values()),
            marker_color=['#4CAF50' if v >= 80 else '#FF9800' if v >= 60 else '#F44336' 
                         for v in format_percentages.values()],
            text=[f'{v:.1f}%' for v in format_percentages.values()],
            textposition='auto'
        ))
        
        fig.update_layout(
            title='JSON格式质量分析',
            xaxis_title='格式检查项',
            yaxis_title='通过率 (%)',
            yaxis=dict(range=[0, 100])
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 显示详细统计
        st.markdown("#### 📋 格式检查详情")
        
        col1, col2 = st.columns(2)
        
        with col1:
            for item, percentage in list(format_percentages.items())[:3]:
                if percentage >= 80:
                    st.success(f"✅ {item}: {percentage:.1f}%")
                elif percentage >= 60:
                    st.warning(f"⚠️ {item}: {percentage:.1f}%")
                else:
                    st.error(f"❌ {item}: {percentage:.1f}%")
        
        with col2:
            for item, percentage in list(format_percentages.items())[3:]:
                if percentage >= 80:
                    st.success(f"✅ {item}: {percentage:.1f}%")
                elif percentage >= 60:
                    st.warning(f"⚠️ {item}: {percentage:.1f}%")
                else:
                    st.error(f"❌ {item}: {percentage:.1f}%")
    
    def show_json_dashboard(self):
        """显示JSON分析Dashboard"""
        # 现代化的标题区域
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: white; padding: 30px; border-radius: 20px; margin-bottom: 30px;
                    box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);">
            <div style="text-align: center;">
                <h1 style="margin: 0; font-size: 2.5rem; font-weight: 700;">
                    🔍 JSON格式分析Dashboard
                </h1>
                <p style="margin: 15px 0 0 0; font-size: 1.2rem; opacity: 0.9;">
                    专门分析JSON格式轮胎查询结果
                </p>
                <div style="margin-top: 20px; display: flex; justify-content: center; gap: 20px; flex-wrap: wrap;">
                    <span style="background: rgba(255,255,255,0.2); padding: 8px 16px; border-radius: 20px; font-size: 0.9rem;">
                        🏗️ 结构分析
                    </span>
                    <span style="background: rgba(255,255,255,0.2); padding: 8px 16px; border-radius: 20px; font-size: 0.9rem;">
                        💰 价格验证
                    </span>
                    <span style="background: rgba(255,255,255,0.2); padding: 8px 16px; border-radius: 20px; font-size: 0.9rem;">
                        📦 库存分析
                    </span>
                    <span style="background: rgba(255,255,255,0.2); padding: 8px 16px; border-radius: 20px; font-size: 0.9rem;">
                        🛞 产品匹配
                    </span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 功能说明区域
        st.markdown("""
        <div style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); 
                    color: #333; padding: 20px; border-radius: 15px; margin: 20px 0;
                    box-shadow: 0 4px 15px rgba(168, 237, 234, 0.2);">
            <h3 style="margin: 0 0 15px 0; text-align: center; color: #2c3e50;">
                📊 JSON专门分析功能
            </h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; margin-top: 15px;">
                <div style="text-align: center; background: rgba(255,255,255,0.7); padding: 15px; border-radius: 10px;">
                    <strong>🏗️ 结构一致性</strong><br/>
                    <small>检查JSON格式标准化</small>
                </div>
                <div style="text-align: center; background: rgba(255,255,255,0.7); padding: 15px; border-radius: 10px;">
                    <strong>💰 价格准确性</strong><br/>
                    <small>验证价格信息正确性</small>
                </div>
                <div style="text-align: center; background: rgba(255,255,255,0.7); padding: 15px; border-radius: 10px;">
                    <strong>📦 库存准确性</strong><br/>
                    <small>检查库存数据准确性</small>
                </div>
                <div style="text-align: center; background: rgba(255,255,255,0.7); padding: 15px; border-radius: 10px;">
                    <strong>🛞 产品覆盖率</strong><br/>
                    <small>分析产品数量匹配度</small>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 文件选择区域
        st.markdown("""
        <div style="background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); 
                    color: #333; padding: 20px; border-radius: 15px; margin: 20px 0;
                    box-shadow: 0 4px 15px rgba(252, 182, 159, 0.2);">
            <h3 style="margin: 0 0 10px 0; text-align: center; color: #2c3e50;">
                📁 选择分析文件
            </h3>
            <p style="margin: 0; text-align: center; font-size: 0.9rem; opacity: 0.8;">
                选择包含JSON指标的分析结果文件
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        files = self.load_json_analysis_files()
        if not files:
            st.markdown("""
            <div style="text-align: center; padding: 60px; 
                        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                        color: white; border-radius: 20px; margin: 30px 0;
                        box-shadow: 0 8px 25px rgba(240, 147, 251, 0.3);">
                <h2 style="margin: 0 0 15px 0; font-size: 2rem;">⚠️ 没有找到JSON分析结果</h2>
                <p style="margin: 0; font-size: 1.1rem; opacity: 0.9;">
                    请先运行JSON分析，生成 *_json_metrics.csv 文件
                </p>
                <div style="margin-top: 25px; background: rgba(255,255,255,0.2); 
                            padding: 15px; border-radius: 15px; display: inline-block;">
                    <span style="font-size: 1rem;">💡 运行 reanalyze_with_json_metrics.py 生成数据</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            return
        
        # 美化的文件选择器
        st.markdown("""
        <div style="background: white; padding: 20px; border-radius: 15px; 
                    box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin: 20px 0;">
            <h4 style="margin: 0 0 15px 0; color: #2c3e50; text-align: center;">
                📄 选择分析结果文件
            </h4>
        </div>
        """, unsafe_allow_html=True)
        
        # 文件选择器
        selected_file = st.selectbox(
            "选择分析结果文件",
            files,
            format_func=lambda x: f"📄 {os.path.basename(x)} ({datetime.fromtimestamp(os.path.getmtime(x)).strftime('%Y-%m-%d %H:%M')})",
            label_visibility="collapsed"
        )
        
        if not selected_file:
            st.stop()
        
        # 加载数据
        df = self.load_and_process_df(selected_file)
        
        if df.empty:
            st.error("❌ 无法加载数据或数据为空")
            return
        
        # 美化的数据基本信息
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: white; padding: 20px; border-radius: 15px; margin: 20px 0;
                    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);">
            <h3 style="margin: 0 0 15px 0; text-align: center;">
                📊 数据基本信息
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                        color: white; padding: 20px; border-radius: 15px; text-align: center;
                        box-shadow: 0 4px 15px rgba(79, 172, 254, 0.3);">
                <h2 style="margin: 0; font-size: 2rem;">{}</h2>
                <p style="margin: 5px 0 0 0; font-size: 1rem; opacity: 0.9;">总样本数</p>
            </div>
            """.format(len(df)), unsafe_allow_html=True)
        
        with col2:
            unique_scenarios = df['场景'].nunique() if '场景' in df.columns else 0
            st.markdown("""
            <div style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); 
                        color: white; padding: 20px; border-radius: 15px; text-align: center;
                        box-shadow: 0 4px 15px rgba(250, 112, 154, 0.3);">
                <h2 style="margin: 0; font-size: 2rem;">{}</h2>
                <p style="margin: 5px 0 0 0; font-size: 1rem; opacity: 0.9;">场景类型</p>
            </div>
            """.format(unique_scenarios), unsafe_allow_html=True)
        
        with col3:
            file_size = os.path.getsize(selected_file) / 1024  # KB
            st.markdown("""
            <div style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); 
                        color: #333; padding: 20px; border-radius: 15px; text-align: center;
                        box-shadow: 0 4px 15px rgba(168, 237, 234, 0.3);">
                <h2 style="margin: 0; font-size: 2rem;">{:.1f} KB</h2>
                <p style="margin: 5px 0 0 0; font-size: 1rem; opacity: 0.8;">文件大小</p>
            </div>
            """.format(file_size), unsafe_allow_html=True)
        
        # 计算指标
        metrics = self.calculate_json_metrics(df)
        
        # 显示总览卡片
        self.show_json_overview_cards(metrics)
        
        # 显示对比图表
        self.create_json_comparison_chart(metrics)
        
        # 显示产品分析
        self.create_product_analysis_chart(df)
        
        # 显示格式分析
        self.create_json_format_analysis(df)
        
        # 数据详情
        st.markdown("### 📄 数据详情")
        
        # 显示选项
        col1, col2 = st.columns(2)
        
        with col1:
            show_all_columns = st.checkbox("显示所有列", value=False)
        
        with col2:
            max_rows = st.slider("最大显示行数", 5, 50, 20)
        
        # 选择要显示的列
        if show_all_columns:
            display_df = df.head(max_rows)
        else:
            # 只显示关键列
            key_columns = ['场景', '测试数据', '参考答案', '生成答案1']
            json_metric_columns = [col for col in df.columns if col.startswith('json_')]
            display_columns = key_columns + json_metric_columns
            display_columns = [col for col in display_columns if col in df.columns]
            display_df = df[display_columns].head(max_rows)
        
        st.dataframe(display_df, use_container_width=True)
        
        # 下载选项
        st.markdown("### 📥 导出选项")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 生成分析报告"):
                report = self.generate_json_analysis_report(metrics, df)
                st.markdown(report)
        
        with col2:
            csv_data = df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📁 下载CSV数据",
                data=csv_data,
                file_name=f"json_analysis_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    def generate_json_analysis_report(self, metrics: Dict, df: pd.DataFrame) -> str:
        """生成JSON分析报告"""
        report = f"""
## 📊 JSON格式分析报告

### 📋 基本信息
- **分析时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **总样本数**: {metrics.get('total_samples', 0)}
- **分析类型**: JSON格式专门分析

### 🎯 JSON专门指标表现

#### 📐 结构和格式指标
- **结构一致性**: {metrics.get('json_structure_consistency', 0):.1f}%
- **格式正确性**: {metrics.get('json_format_correctness', 0):.1f}%
- **价格准确性**: {metrics.get('json_price_accuracy', 0):.1f}%
- **库存准确性**: {metrics.get('json_stock_accuracy', 0):.1f}%

#### 📝 内容质量指标
- **产品覆盖率**: {metrics.get('json_product_coverage', 0):.1f}%
- **描述相似度**: {metrics.get('json_description_similarity', 0):.1f}%

#### 🛞 产品数量分析
- **平均参考产品数**: {metrics.get('avg_ref_products', 0):.1f}个
- **平均生成产品数**: {metrics.get('avg_gen_products', 0):.1f}个
- **数量差异**: {metrics.get('product_count_diff', 0):+.1f}个

### 📈 传统指标对比
- **语义稳定性**: {metrics.get('traditional_语义稳定性', 0):.1f}%
- **冗余度**: {metrics.get('traditional_冗余度', 0):.1f}%
- **完整度**: {metrics.get('traditional_完整度', 0):.1f}%
- **相关度**: {metrics.get('traditional_相关度', 0):.1f}%

### 🔍 关键发现

#### ✅ 优势领域
"""
        
        # 找出表现最好的指标
        json_metrics_values = {
            '结构一致性': metrics.get('json_structure_consistency', 0),
            '格式正确性': metrics.get('json_format_correctness', 0),
            '价格准确性': metrics.get('json_price_accuracy', 0),
            '库存准确性': metrics.get('json_stock_accuracy', 0),
            '产品覆盖率': metrics.get('json_product_coverage', 0),
            '描述相似度': metrics.get('json_description_similarity', 0)
        }
        
        # 排序找出最好的指标
        sorted_metrics = sorted(json_metrics_values.items(), key=lambda x: x[1], reverse=True)
        
        for metric, value in sorted_metrics[:3]:
            if value >= 80:
                report += f"- **{metric}**: {value:.1f}% (优秀)\n"
            elif value >= 60:
                report += f"- **{metric}**: {value:.1f}% (良好)\n"
        
        report += "\n#### ⚠️ 需要改进的领域\n"
        
        for metric, value in sorted_metrics[-3:]:
            if value < 60:
                report += f"- **{metric}**: {value:.1f}% (需要改进)\n"
        
        # 产品数量分析
        product_diff = metrics.get('product_count_diff', 0)
        if abs(product_diff) > 5:
            report += f"\n#### 🛞 产品数量问题\n"
            if product_diff > 0:
                report += f"- 生成的产品数量过多，平均超出参考答案 {product_diff:.1f} 个产品\n"
                report += f"- 建议：优化产品筛选逻辑，提高查询精确性\n"
            else:
                report += f"- 生成的产品数量不足，平均少于参考答案 {abs(product_diff):.1f} 个产品\n"
                report += f"- 建议：检查产品查询覆盖范围\n"
        
        report += f"""

### 📊 总体评估

JSON专门分析显示了传统ROUGE指标无法捕捉的关键问题：
- 产品数量匹配度是影响用户体验的关键因素
- 价格和库存准确性对业务至关重要
- 结构一致性保证了系统的可靠性

### 💡 改进建议

1. **优化产品查询逻辑**：确保返回的产品数量符合预期
2. **加强数据验证**：提高价格和库存信息的准确性
3. **规范化输出格式**：确保JSON结构的一致性
4. **增强描述质量**：提高产品描述的相关性和准确性

---
*本报告基于JSON专门分析指标生成，更适合评估结构化数据的质量*
"""
        
        return report

# 主函数
def main():
    """主函数，用于测试JSON Dashboard"""
    dashboard = JSONDashboard()
    dashboard.show_json_dashboard()

if __name__ == "__main__":
    main() 