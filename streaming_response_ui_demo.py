"""
流式响应UI演示
展示如何在前端界面中启用流式响应和首字响应时间功能
"""

import streamlit as st
import pandas as pd
import time
from ui_components import StreamingResponseMetricsComponents, ResultDisplayComponents
from advanced_llm_analyzer import AdvancedLLMAnalyzer

def main():
    st.set_page_config(
        page_title="流式响应UI演示",
        page_icon="🚀",
        layout="wide"
    )
    
    st.title("🚀 流式响应和首字响应时间UI演示")
    
    st.markdown("""
    此演示展示了如何在前端界面中启用流式响应功能，包括：
    - ⚡ 首字响应时间测量
    - ⏱️ 总响应时间记录
    - 🔄 API重试次数统计
    - 📊 性能指标可视化
    - 💡 性能优化建议
    """)
    
    # 创建示例数据
    @st.cache_data
    def create_sample_data():
        """创建示例数据，包含流式响应指标"""
        data = {
            '场景': [f'测试场景{i+1}' for i in range(10)],
            '参考答案': [f'参考答案{i+1}' for i in range(10)],
            '生成答案1': [f'生成答案{i+1}' for i in range(10)],
            'llm_first_token_response_time': [
                0.234, 0.567, 0.123, 0.789, 0.345,
                0.678, 0.234, 0.567, 0.123, 0.789
            ],
            'llm_total_response_time': [
                2.345, 3.678, 1.234, 4.567, 2.890,
                3.456, 2.345, 3.678, 1.234, 4.567
            ],
            'llm_api_attempt': [1, 1, 2, 1, 1, 3, 1, 1, 2, 1],
            'llm_overall_score': [85, 92, 78, 88, 90, 76, 89, 91, 84, 87]
        }
        return pd.DataFrame(data)
    
    # 显示功能说明
    st.header("🔧 功能配置")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("✅ 当前实现的功能")
        st.markdown("""
        - **🚀 流式响应选项** - 在LLM分析设置中可启用
        - **⚡ 首字响应时间** - 测量从请求到第一个字符的时间
        - **⏱️ 总响应时间** - 完整请求响应时间
        - **🔄 API重试次数** - 记录请求重试情况
        - **📊 性能指标面板** - 可视化展示性能数据
        - **💡 智能建议** - 基于性能数据的优化建议
        """)
    
    with col2:
        st.subheader("🎯 使用方法")
        st.markdown("""
        1. 在**分析配置**中启用 "🧠 LLM深度分析"
        2. 勾选 "🚀 启用流式响应" 选项
        3. 开始分析，系统会自动记录时间指标
        4. 在结果页面查看 "🚀 详细流式响应指标"
        5. 根据性能建议优化配置
        """)
    
    # 显示示例数据
    st.header("📊 示例数据展示")
    
    sample_df = create_sample_data()
    
    # 使用新的UI组件显示分析摘要
    ResultDisplayComponents.show_analysis_summary(sample_df)
    
    # 显示原始数据
    st.subheader("📋 原始数据")
    st.dataframe(sample_df)
    
    # 配置说明
    st.header("⚙️ 配置说明")
    
    st.markdown("""
    ### 在 `app.py` 中的配置：
    
    ```python
    # LLM分析选项
    enable_llm_analysis = st.checkbox("🧠 启用LLM深度分析", value=False)
    
    if enable_llm_analysis:
        # 流式响应选项
        enable_streaming = st.checkbox(
            "🚀 启用流式响应",
            value=False,
            help="启用流式响应可以测量首字响应时间，更好地评估API性能"
        )
        
        if enable_streaming:
            st.info("📊 将记录首字响应时间和总响应时间")
    ```
    
    ### 在分析器中的调用：
    
    ```python
    # 检查是否启用流式响应
    use_streaming = st.session_state.get('enable_streaming', False)
    
    # 调用分析器
    result_df = analyzer.batch_analyze_dataframe(
        df, '参考答案', '生成答案1', 'comprehensive',
        use_streaming=use_streaming  # 传递流式响应参数
    )
    ```
    
    ### 结果数据格式：
    
    启用流式响应后，结果DataFrame会包含以下额外列：
    - `llm_first_token_response_time`: 首字响应时间（秒）
    - `llm_total_response_time`: 总响应时间（秒）
    - `llm_api_attempt`: API重试次数
    """)
    
    # 性能基准
    st.header("🎯 性能基准")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "🚀 首字响应时间",
            "< 1.0s",
            delta="优秀",
            delta_color="normal"
        )
        st.caption("从请求开始到接收第一个字符")
    
    with col2:
        st.metric(
            "⏱️ 总响应时间",
            "< 10.0s",
            delta="满意",
            delta_color="normal"
        )
        st.caption("完整请求响应时间")
    
    with col3:
        st.metric(
            "🔄 API重试次数",
            "= 1",
            delta="理想",
            delta_color="normal"
        )
        st.caption("首次成功率 > 95%")
    
    # 使用说明
    st.header("📖 使用说明")
    
    with st.expander("🔍 详细使用步骤"):
        st.markdown("""
        1. **启用功能**：
           - 在分析配置中启用 "🧠 LLM深度分析"
           - 勾选 "🚀 启用流式响应" 选项
        
        2. **开始分析**：
           - 系统会自动使用流式响应方式
           - 记录每个请求的首字响应时间和总响应时间
        
        3. **查看结果**：
           - 在分析摘要中查看平均时间指标
           - 点击 "🚀 详细流式响应指标" 查看详细分析
        
        4. **性能优化**：
           - 根据性能建议调整配置
           - 监控首字响应时间和重试次数
        
        5. **数据导出**：
           - 所有时间指标都会保存在结果文件中
           - 可用于进一步的性能分析
        """)
    
    # 技术细节
    with st.expander("🔧 技术实现细节"):
        st.markdown("""
        ### 流式响应实现：
        
        ```python
        def send_evaluation_request_streaming(self, prompt: str) -> Dict:
            request_start_time = time.time()
            
            # 发送流式请求
            response = requests.post(url, json=data, stream=True)
            
            first_byte_time = None
            full_content = ""
            
            # 逐块读取响应
            for chunk in response.iter_content(chunk_size=1):
                if chunk:
                    if first_byte_time is None:
                        first_byte_time = time.time()
                        first_token_response_time = first_byte_time - request_start_time
                    full_content += chunk
            
            total_response_time = time.time() - request_start_time
            
            return {
                'content': full_content,
                'first_token_response_time': first_token_response_time,
                'total_response_time': total_response_time
            }
        ```
        
        ### UI组件集成：
        
        ```python
        class StreamingResponseMetricsComponents:
            @staticmethod
            def show_streaming_metrics(df):
                # 显示首字响应时间分布
                # 显示总响应时间分析
                # 显示API重试统计
                # 显示性能优化建议
        ```
        """)

if __name__ == "__main__":
    main() 