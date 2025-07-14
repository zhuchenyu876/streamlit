import streamlit as st
import pandas as pd
from datetime import datetime
import os

class UserGuideComponents:
    """用户引导组件类"""
    
    @staticmethod
    def show_welcome_guide():
        """显示欢迎引导页面"""
        if 'show_guide' not in st.session_state:
            st.session_state.show_guide = True
            
        if st.session_state.show_guide:
            # 美化的欢迎信息
            st.markdown("""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        color: white; padding: 25px; border-radius: 20px; margin: 20px 0;
                        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);">
                <div style="text-align: center;">
                    <h2 style="margin: 0; font-size: 2rem; font-weight: 700;">
                        👋 欢迎使用LLM问答质量分析系统！
                    </h2>
                    <p style="margin: 15px 0 0 0; font-size: 1.1rem; opacity: 0.9;">
                        让我们快速了解如何使用这个强大的分析工具
                    </p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # 美化的快速入门指南
            with st.expander("🎯 快速入门指南", expanded=True):
                st.markdown("""
                <div style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); 
                            color: #333; padding: 25px; border-radius: 15px; margin: 15px 0;
                            box-shadow: 0 4px 15px rgba(168, 237, 234, 0.2);">
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">
                        <div style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                            <h3 style="color: #2c3e50; margin: 0 0 15px 0;">📊 第一步：准备测试数据</h3>
                            <ul style="margin: 0; padding-left: 20px; line-height: 1.6;">
                                <li>点击<strong>"📥 下载数据模板"</strong>按钮</li>
                                <li>按照模板格式准备您的测试数据</li>
                                <li>确保包含：场景、测试数据、参考答案等字段</li>
                                <li>支持中文、西班牙语、英语等多种语言</li>
                            </ul>
                        </div>
                        <div style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                            <h3 style="color: #2c3e50; margin: 0 0 15px 0;">🤖 第二步：配置机器人</h3>
                            <ul style="margin: 0; padding-left: 20px; line-height: 1.6;">
                                <li>首次使用请到<strong>"👥 Agent Management"</strong>标签页</li>
                                <li>配置您的机器人API信息</li>
                                <li>输入机器人的URL和认证信息</li>
                                <li>测试连接确保配置正确</li>
                            </ul>
                        </div>
                        <div style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                            <h3 style="color: #2c3e50; margin: 0 0 15px 0;">🚀 第三步：开始分析</h3>
                            <ul style="margin: 0; padding-left: 20px; line-height: 1.6;">
                                <li>上传您的CSV文件</li>
                                <li>设置采样数量（建议从10开始）</li>
                                <li>选择分析模式（单机器人或多机器人对比）</li>
                                <li>点击<strong>"开始分析"</strong>按钮</li>
                            </ul>
                        </div>
                        <div style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                            <h3 style="color: #2c3e50; margin: 0 0 15px 0;">📈 第四步：查看结果</h3>
                            <ul style="margin: 0; padding-left: 20px; line-height: 1.6;">
                                <li>在<strong>"📊 Dashboard"</strong>标签页查看分析结果</li>
                                <li>使用筛选器进行多维度分析</li>
                                <li>查看可视化图表和统计指标</li>
                                <li>导出分析报告和数据</li>
                            </ul>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # 美化的确认按钮
                col1, col2, col3 = st.columns([1, 1, 1])
                with col2:
                    st.markdown("""
                    <div style="text-align: center; margin: 20px 0;">
                        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                    color: white; padding: 15px 30px; border-radius: 25px; 
                                    display: inline-block; cursor: pointer; 
                                    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);">
                            <strong>✅ 我已了解，开始使用</strong>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("我已了解，开始使用", key="start_using"):
                        st.session_state.show_guide = False
                        st.rerun()
    
    @staticmethod
    def show_help_tooltip(help_text, key=None):
        """显示帮助提示"""
        return st.help(help_text) if help_text else None
    
    @staticmethod
    def show_status_indicator(status, message=""):
        """显示状态指示器"""
        status_config = {
            'success': ('✅', 'success', '#2e7d32'),
            'error': ('❌', 'error', '#d32f2f'),
            'warning': ('⚠️', 'warning', '#f57c00'),
            'info': ('ℹ️', 'info', '#1976d2'),
            'running': ('🔄', 'info', '#1976d2')
        }
        
        if status in status_config:
            icon, st_status, color = status_config[status]
            
            # 美化的状态指示器
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, {color}20 0%, {color}10 100%); 
                        color: {color}; padding: 15px; border-radius: 10px; margin: 10px 0;
                        border-left: 4px solid {color};">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 1.2rem;">{icon}</span>
                    <strong>{message}</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    @staticmethod
    def create_metric_card(title, value, description="", delta=None):
        """创建指标卡片"""
        # 美化的指标卡片
        delta_html = ""
        if delta:
            delta_color = "#2e7d32" if delta > 0 else "#d32f2f"
            delta_icon = "📈" if delta > 0 else "📉"
            delta_html = f"""
            <div style="color: {delta_color}; font-size: 0.9rem; margin-top: 5px;">
                {delta_icon} {delta:+.1f}
            </div>
            """
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: white; padding: 20px; border-radius: 15px; margin: 10px 0;
                    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);">
            <h3 style="margin: 0; font-size: 1.2rem; opacity: 0.9;">{title}</h3>
            <h2 style="margin: 10px 0 0 0; font-size: 2rem; font-weight: 700;">{value}</h2>
            {delta_html}
            <p style="margin: 10px 0 0 0; font-size: 0.9rem; opacity: 0.8;">{description}</p>
        </div>
        """, unsafe_allow_html=True)

class DataValidationComponents:
    """数据验证组件类"""
    
    @staticmethod
    def get_language_display_name(language):
        """获取语言的显示名称"""
        language_names = {
            "auto": "🔄 自动检测",
            "chinese": "🇨🇳 中文",
            "spanish": "🇪🇸 西班牙语",
            "english": "🇺🇸 英语"
        }
        return language_names.get(language, language)
    
    @staticmethod
    def show_language_selector(key_suffix=""):
        """显示语言选择器"""
        # 美化的语言选择器标题
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: white; padding: 20px; border-radius: 15px; margin: 15px 0;
                    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);">
            <h3 style="margin: 0; text-align: center; font-size: 1.3rem; font-weight: 600;">
                🌐 选择文件语言
            </h3>
            <p style="margin: 10px 0 0 0; text-align: center; font-size: 0.9rem; opacity: 0.9;">
                正确的语言选择有助于更好地处理您的数据
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # 语言选项
        language_options = {
            "auto": "🔄 自动检测",
            "chinese": "🇨🇳 中文 (Chinese)",
            "spanish": "🇪🇸 西班牙语 (Español)",
            "english": "🇺🇸 英语 (English)"
        }
        
        # 美化的选择区域
        st.markdown("""
        <div style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); 
                    color: #333; padding: 20px; border-radius: 15px; margin: 15px 0;
                    box-shadow: 0 4px 15px rgba(168, 237, 234, 0.2);">
            <h4 style="margin: 0 0 15px 0; text-align: center; color: #2c3e50;">
                🎯 语言配置
            </h4>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # 美化的选择框
            st.markdown("""
            <div style="background: white; padding: 15px; border-radius: 10px; 
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin: 10px 0;">
                <h5 style="margin: 0 0 10px 0; color: #2c3e50;">请选择您的CSV文件语言</h5>
            </div>
            """, unsafe_allow_html=True)
            
            # 使用唯一的key避免冲突
            unique_key = f"selected_language{key_suffix}"
            selected_language = st.selectbox(
                "请选择您的CSV文件语言",
                options=list(language_options.keys()),
                format_func=lambda x: language_options[x],
                key=unique_key,
                help="选择文件语言可以优化编码检测和处理效果",
                label_visibility="collapsed"
            )
        
        with col2:
            # 美化的编码建议
            encoding_suggestions = {
                "auto": "将尝试多种编码",
                "chinese": "建议: GBK, UTF-8",
                "spanish": "建议: UTF-8, UTF-8-sig",
                "english": "建议: UTF-8, ASCII"
            }
            
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                        color: white; padding: 15px; border-radius: 10px; 
                        box-shadow: 0 4px 15px rgba(79, 172, 254, 0.3);">
                <h5 style="margin: 0 0 10px 0; font-size: 1rem;">📝 编码建议</h5>
                <p style="margin: 0; font-size: 0.9rem; opacity: 0.9;">
                    {encoding_suggestions[selected_language]}
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        # 美化的语言相关提示
        language_tips = {
            "auto": "💡 系统将自动检测最佳编码方式",
            "chinese": "💡 中文文件通常使用GBK或UTF-8编码",
            "spanish": "💡 西班牙语文件包含重音符号，建议使用UTF-8编码",
            "english": "💡 英语文件通常使用UTF-8或ASCII编码"
        }
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); 
                    color: #333; padding: 15px; border-radius: 10px; margin: 15px 0;
                    box-shadow: 0 4px 15px rgba(252, 182, 159, 0.2);">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 1.2rem;">💡</span>
                <strong style="color: #2c3e50;">{language_tips[selected_language]}</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        return selected_language
    
    @staticmethod
    def get_encoding_strategy(language):
        """根据语言获取编码检测策略"""
        strategies = {
            "auto": ['utf-8', 'utf-8-sig', 'gbk', 'gb2312', 'latin1'],
            "chinese": ['gbk', 'gb2312', 'utf-8', 'utf-8-sig'],
            "spanish": ['utf-8', 'utf-8-sig', 'latin1', 'iso-8859-1'],
            "english": ['utf-8', 'ascii', 'latin1', 'utf-8-sig']
        }
        return strategies.get(language, strategies["auto"])
    
    @staticmethod
    def _read_csv_with_encoding(uploaded_file, nrows=None, language="auto"):
        """智能编码检测读取CSV文件，增强处理长JSON字符串"""
        encodings = DataValidationComponents.get_encoding_strategy(language)
        
        for encoding in encodings:
            try:
                uploaded_file.seek(0)  # 重置文件指针
                
                # 使用增强的CSV解析参数来处理复杂内容
                df = pd.read_csv(
                    uploaded_file,
                    nrows=nrows,
                    encoding=encoding,
                    quoting=1,  # 严格处理引号
                    skipinitialspace=True,
                    on_bad_lines='skip',
                    dtype=str,  # 强制所有列为字符串，避免类型推断问题
                    keep_default_na=False,  # 不要自动转换空值
                    engine='python'  # 使用Python引擎更好地处理复杂CSV
                )
                
                # 验证读取是否成功
                if len(df.columns) >= 3:  # 至少要有3列
                    return df
                    
            except (UnicodeDecodeError, pd.errors.ParserError) as e:
                # 记录具体错误信息用于调试
                import logging
                logging.warning(f"CSV解析失败 (编码: {encoding}): {str(e)}")
                continue
        
        # 如果所有编码都失败，抛出异常
        raise UnicodeDecodeError("utf-8", b"", 0, 0, "无法识别文件编码，请尝试不同的语言选择或检查文件格式")
    
    @staticmethod
    def get_required_columns(language):
        """根据语言获取必需的列名"""
        column_mappings = {
            "chinese": ['场景', '测试数据', '参考答案'],
            "spanish": ['Pregunta', 'Contenido de Pregunta', 'Respuesta de Referencia'],
            "spanish_mixed": ['问题', '问题内容', '参考答案'],  # 混合格式：中文列名，西班牙语内容
            "english": ['Scene', 'Test Data', 'Reference Answer'],
            "auto": []  # 自动检测时，尝试所有可能的列名组合
        }
        return column_mappings.get(language, column_mappings["chinese"])
    

    
    @staticmethod
    def validate_csv_format(uploaded_file, language="auto"):
        """验证CSV文件格式 - 增强版，支持多种列名格式"""
        if uploaded_file is None:
            return False, "请先上传CSV文件"
        
        try:
            # 智能编码检测
            df = DataValidationComponents._read_csv_with_encoding(uploaded_file, nrows=5, language=language)
            
            # 清理列名，去除可能的编码问题
            clean_columns = []
            for col in df.columns:
                if isinstance(col, str):
                    # 修复常见的编码问题
                    clean_col = col.replace('答�?', '答案').replace('答案案', '答案')
                    clean_columns.append(clean_col)
                else:
                    clean_columns.append(str(col))
            
            df.columns = clean_columns
            
            if language == "auto":
                # 自动检测模式：尝试所有语言的列名组合
                all_possible_columns = [
                    (['场景', '测试数据', '参考答案'], "中文"),
                    (['Pregunta', 'Contenido de Pregunta', 'Respuesta de Referencia'], "西班牙语"),
                    (['问题', '问题内容', '参考答案'], "西班牙语（混合格式）"),
                    (['Scene', 'Test Data', 'Reference Answer'], "英语"),
                    # 添加更多灵活的匹配模式
                    (['场景', '问题内容', '参考答案'], "中文（变体）"),
                    (['问题', '测试数据', '参考答案'], "中文（变体2）")
                ]
                
                matched_format = None
                for required_columns, detected_lang in all_possible_columns:
                    missing_columns = [col for col in required_columns if col not in df.columns]
                    if not missing_columns:
                        matched_format = detected_lang
                        break
                
                if matched_format:
                    return True, f"✅ 检测到{matched_format}文件格式，验证通过"
                
                # 如果精确匹配失败，尝试模糊匹配
                available_cols = list(df.columns)
                
                # 检查是否有包含关键词的列
                key_patterns = {
                    '场景类': ['场景', '问题', 'Scene', 'Pregunta'],
                    '测试数据类': ['测试数据', '问题内容', 'Test Data', 'Contenido'],
                    '参考答案类': ['参考答案', 'Reference', 'Respuesta']
                }
                
                matched_categories = []
                for category, patterns in key_patterns.items():
                    for col in available_cols:
                        if any(pattern in col for pattern in patterns):
                            matched_categories.append(category)
                            break
                
                if len(matched_categories) >= 2:  # 至少匹配两个必要类别
                    return True, f"✅ 检测到兼容的文件格式（模糊匹配），可用列: {', '.join(available_cols[:5])}"
                
                # 最后的错误消息，更加友好
                return False, (f"❌ 文件格式需要调整。当前列名: {', '.join(available_cols[:8])}\n\n"
                             "💡 期望的列名格式（任选其一）:\n"
                             "• 中文: 场景, 测试数据, 参考答案\n"
                             "• 西班牙语: Pregunta, Contenido de Pregunta, Respuesta de Referencia\n"  
                             "• 西班牙语（混合）: 问题, 问题内容, 参考答案\n"
                             "• 英语: Scene, Test Data, Reference Answer\n\n"
                             "🔧 请检查列名是否包含必要的字段")
            else:
                # 特定语言模式 - 增强验证
                required_columns = DataValidationComponents.get_required_columns(language)
                if required_columns is None:
                    required_columns = []
                missing_columns = [col for col in required_columns if col not in df.columns]
                
                if missing_columns:
                    # 尝试模糊匹配
                    available_cols = list(df.columns)
                    fuzzy_matches = []
                    
                    for missing_col in missing_columns:
                        for available_col in available_cols:
                            if missing_col in available_col or available_col in missing_col:
                                fuzzy_matches.append(f"{missing_col} → {available_col}")
                    
                    if fuzzy_matches:
                        return True, f"✅ 检测到相似列名，可能兼容: {', '.join(fuzzy_matches)}"
                    
                    lang_names = {
                        "chinese": "中文",
                        "spanish": "西班牙语", 
                        "english": "英语"
                    }
                    lang_name = lang_names.get(language, language)
                    return False, (f"❌ 缺少{lang_name}必要的列: {', '.join(missing_columns)}\n"
                                 f"📋 当前可用列: {', '.join(available_cols)}")
            
            if len(df) == 0:
                return False, "❌ 文件为空，请检查数据内容"
            
            # 根据语言显示不同的成功消息
            success_messages = {
                "auto": "✅ 文件格式验证通过",
                "chinese": "✅ 中文文件格式验证通过",
                "spanish": "✅ Formato de archivo en español verificado",
                "english": "✅ English file format verified"
            }
            
            return True, success_messages.get(language, success_messages["auto"])
            
        except UnicodeDecodeError as e:
            return False, f"❌ 文件编码错误: 请尝试保存为UTF-8格式 ({str(e)})"
        except Exception as e:
            return False, f"❌ 文件格式错误: {str(e)}"
    
    @staticmethod
    def show_data_preview(uploaded_file, language="auto", max_rows=5):
        """显示数据预览"""
        if uploaded_file is None:
            return
        
        try:
            df = DataValidationComponents._read_csv_with_encoding(uploaded_file, nrows=max_rows, language=language)
            
            # 根据语言显示不同的标题
            preview_titles = {
                "auto": "📊 数据预览",
                "chinese": "📊 数据预览",
                "spanish": "📊 Vista previa de datos",
                "english": "📊 Data Preview"
            }
            
            st.subheader(preview_titles.get(language, preview_titles["auto"]))
            st.dataframe(df)
            
            # 根据语言显示不同的信息
            info_messages = {
                "auto": f"显示前{len(df)}行数据，总计约{len(df) * 20}行（预估）",
                "chinese": f"显示前{len(df)}行数据，总计约{len(df) * 20}行（预估）",
                "spanish": f"Mostrando las primeras {len(df)} filas, aproximadamente {len(df) * 20} filas en total",
                "english": f"Showing first {len(df)} rows, approximately {len(df) * 20} rows total"
            }
            
            st.info(info_messages.get(language, info_messages["auto"]))
            
        except Exception as e:
            # 根据语言显示不同的错误消息
            error_messages = {
                "auto": f"数据预览失败: {str(e)}",
                "chinese": f"数据预览失败: {str(e)}",
                "spanish": f"Error en vista previa: {str(e)}",
                "english": f"Data preview failed: {str(e)}"
            }
            
            st.error(error_messages.get(language, error_messages["auto"]))
    
    @staticmethod
    def show_language_statistics(language, df):
        """显示语言相关的统计信息"""
        if df is None or len(df) == 0:
            return
            
        st.subheader(f"🌐 {DataValidationComponents.get_language_display_name(language)} 文件统计")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("数据行数", len(df))
            
        with col2:
            st.metric("总列数", len(df.columns))
            
        with col3:
            # 计算非空数据比例
            non_empty_ratio = (df.notna().sum().sum() / (len(df) * len(df.columns)) * 100)
            st.metric("数据完整度", f"{non_empty_ratio:.1f}%")
            
        with col4:
            # 根据语言显示特定统计
            if language == "spanish":
                # 计算包含重音符号的行数
                accent_count = 0
                for col in df.select_dtypes(include=['object']).columns:
                    accent_count += df[col].astype(str).str.contains('[áéíóúñü]', case=False, na=False).sum()
                st.metric("包含重音符号", accent_count)
            elif language == "chinese":
                # 计算包含中文字符的行数
                chinese_count = 0
                for col in df.select_dtypes(include=['object']).columns:
                    chinese_count += df[col].astype(str).str.contains('[\u4e00-\u9fff]', na=False).sum()
                st.metric("包含中文字符", chinese_count)
            else:
                # 显示数据大小
                import sys
                data_size = sys.getsizeof(df) / 1024  # KB
                st.metric("数据大小", f"{data_size:.1f} KB")
        
        # 添加详细信息说明
        st.info(f"""
        📋 **文件读取详情**:
        - 成功读取 {len(df)} 行数据
        - 包含 {len(df.columns)} 列
        - 读取使用编码: {DataValidationComponents.get_encoding_strategy(language)[0]}
        - 如果行数与预期不符，可能是文件中包含空行或格式问题
        """)
        
        # 显示列名信息
        with st.expander("🔍 查看列名详情"):
            st.write("**所有列名:**")
            for i, col in enumerate(df.columns, 1):
                st.write(f"{i}. {col}")
            
            # 显示数据类型
            st.write("**数据类型:**")
            for col in df.columns:
                st.write(f"- {col}: {df[col].dtype}")
                
        # 显示前几行数据
        with st.expander("📄 查看前10行数据"):
            st.dataframe(df.head(10))

class AnalysisProgressComponents:
    """分析进度组件类"""
    
    @staticmethod
    def show_progress_details(progress, current_step, total_steps, estimated_time=None):
        """显示详细的进度信息"""
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.progress(progress)
        
        with col2:
            st.metric("进度", f"{current_step}/{total_steps}")
        
        with col3:
            if estimated_time:
                st.metric("预计剩余", f"{estimated_time}分钟")
    
    @staticmethod
    def show_step_indicator(steps, current_step):
        """显示步骤指示器"""
        cols = st.columns(len(steps))
        for i, (step_name, step_desc) in enumerate(steps):
            with cols[i]:
                if i < current_step:
                    st.success(f"✅ {step_name}")
                elif i == current_step:
                    st.info(f"🔄 {step_name}")
                else:
                    st.write(f"⏳ {step_name}")
                st.caption(step_desc)
    
    @staticmethod
    def show_pause_controls(task_id):
        """显示暂停控制按钮"""
        from datetime import datetime
        
        col1, col2 = st.columns([1, 1])
        
        # Generate unique timestamp for button keys to avoid duplicates
        timestamp = int(datetime.now().timestamp() * 1000)
        
        with col1:
            if st.button("⏸️ 暂停分析", key=f"pause_control_{task_id}_{timestamp}"):
                st.session_state.analysis_paused = True
                st.rerun()
        
        with col2:
            if st.button("⏹️ 停止分析", key=f"stop_control_{task_id}_{timestamp}", type="secondary"):
                st.session_state.analysis_running = False
                st.session_state.analysis_paused = False
                st.rerun()
    
    @staticmethod
    def show_analysis_status():
        """显示分析状态"""
        if st.session_state.get('analysis_running', False):
            if st.session_state.get('analysis_paused', False):
                st.warning("⏸️ 分析已暂停")
            else:
                st.info("🔄 分析正在进行中...")
        else:
            st.success("✅ 分析已完成或未开始")

class ResultDisplayComponents:
    """结果展示组件类"""
    
    @staticmethod
    def show_analysis_summary(df):
        """显示分析摘要"""
        if df is None or len(df) == 0:
            return
        
        st.subheader("📈 分析摘要")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("总样本数", len(df))
        
        with col2:
            if '语义稳定性' in df.columns:
                avg_stability = df['语义稳定性'].mean()
                st.metric("平均语义稳定性", f"{avg_stability:.2%}")
        
        with col3:
            if '相关度' in df.columns:
                avg_relevance = df['相关度'].mean()
                st.metric("平均相关度", f"{avg_relevance:.2%}")
        
        with col4:
            if '完整度' in df.columns:
                avg_completeness = df['完整度'].mean()
                st.metric("平均完整度", f"{avg_completeness:.2%}")
    
    @staticmethod
    def show_export_options(df, filename_prefix="analysis_results"):
        """显示导出选项"""
        if df is None:
            return
        
        st.subheader("📤 导出选项")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            csv_data = df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                "📄 导出完整数据 (CSV)",
                csv_data,
                f"{filename_prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        with col2:
            # 导出摘要报告
            summary_data = ResultDisplayComponents._create_summary_report(df)
            st.download_button(
                "📊 导出摘要报告 (CSV)",
                summary_data,
                f"{filename_prefix}_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        with col3:
            # 导出问题数据
            if '语义篡改' in df.columns:
                problem_data = df[df['语义篡改'] == '是'].to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    "⚠️ 导出问题数据 (CSV)",
                    problem_data,
                    f"{filename_prefix}_problems_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
    
    @staticmethod
    def _create_summary_report(df):
        """创建摘要报告"""
        summary = []
        
        # 基本统计
        summary.append(["指标", "数值"])
        summary.append(["总样本数", len(df)])
        
        # 质量指标
        metrics = ['语义稳定性', '相关度', '完整度', '冗余度']
        for metric in metrics:
            if metric in df.columns:
                avg_val = df[metric].mean()
                summary.append([f"平均{metric}", f"{avg_val:.2%}"])
        
        # 问题统计
        problem_metrics = ['语义篡改', '缺失关键信息', '生成无关信息']
        for metric in problem_metrics:
            if metric in df.columns:
                problem_count = len(df[df[metric] == '是'])
                problem_rate = problem_count / len(df) * 100
                summary.append([f"{metric}问题数", problem_count])
                summary.append([f"{metric}问题率", f"{problem_rate:.1f}%"])
        
        return pd.DataFrame(summary).to_csv(index=False, encoding='utf-8-sig')

class AgentSelectionComponents:
    """机器人选择组件类"""
    
    @staticmethod
    def show_agent_cards(agents_df, key_suffix=""):
        """显示机器人卡片选择界面"""
        st.subheader("🤖 选择分析机器人")
        
        if agents_df.empty:
            st.warning("⚠️ 暂无可用机器人，请先在 'Agent Management' 标签页添加机器人配置")
            return None
        
        # 使用session state存储选择的机器人
        session_key = f"selected_agent_card{key_suffix}"
        if session_key not in st.session_state:
            st.session_state[session_key] = agents_df.iloc[0]['name']
        
        # 计算卡片布局
        agents_list = agents_df.to_dict('records')
        cols_per_row = 3
        num_rows = (len(agents_list) + cols_per_row - 1) // cols_per_row
        
        selected_agent = st.session_state[session_key]
        
        # 显示卡片网格
        for row in range(num_rows):
            cols = st.columns(cols_per_row)
            
            for col_idx in range(cols_per_row):
                agent_idx = row * cols_per_row + col_idx
                
                if agent_idx < len(agents_list):
                    agent = agents_list[agent_idx]
                    
                    with cols[col_idx]:
                        # 判断是否为选中状态
                        is_selected = agent['name'] == selected_agent
                        
                        # 显示卡片内容
                        # 安全处理可能的NaN值和空值
                        agent_url = agent.get('url', 'N/A')
                        if not isinstance(agent_url, str) or agent_url in ['N/A', '', 'nan', 'NaN', None] or pd.isna(agent_url):
                            agent_url = 'N/A'
                        else:
                            agent_url = str(agent_url)[:30] + ("..." if len(str(agent_url)) > 30 else "")
                        
                        agent_description = agent.get('description', '暂无描述')
                        if not isinstance(agent_description, str) or agent_description in ['nan', 'NaN', '', None] or pd.isna(agent_description):
                            agent_description = '暂无描述'
                        
                        agent_username = agent.get('username', 'N/A')
                        if not isinstance(agent_username, str) or agent_username in ['nan', 'NaN', '', None] or pd.isna(agent_username):
                            agent_username = 'N/A'
                        
                        # 确保机器人名称不为空
                        agent_name = agent.get('name', 'Unknown')
                        if not isinstance(agent_name, str) or agent_name in ['nan', 'NaN', '', None] or pd.isna(agent_name):
                            agent_name = 'Unknown Robot'
                        
                        # 创建卡片容器
                        if is_selected:
                            # 选中状态 - 蓝色边框
                            st.markdown(f"""
                                <div style="
                                    border: 3px solid #1f77b4;
                                    border-radius: 15px;
                                    padding: 20px;
                                    margin: 10px 0;
                                    background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%);
                                    box-shadow: 0 4px 12px rgba(31, 119, 180, 0.3);
                                    transition: all 0.3s ease;
                                    cursor: pointer;
                                    position: relative;
                                ">
                                    <div style="position: absolute; top: 10px; right: 15px; color: #1f77b4; font-size: 20px;">✓</div>
                                    <h4 style="margin: 0 0 10px 0; color: #333; display: flex; align-items: center;">
                                        🤖 {agent_name}
                                    </h4>
                                    <p style="margin: 5px 0; color: #666; font-size: 14px;">
                                        📝 {agent_description}
                                    </p>
                                    <p style="margin: 5px 0; color: #999; font-size: 12px;">
                                        🌐 {agent_url}
                                    </p>
                                    <p style="margin: 5px 0; color: #999; font-size: 12px;">
                                        👤 {agent_username}
                                    </p>
                                </div>
                            """, unsafe_allow_html=True)
                        else:
                            # 未选中状态 - 灰色边框
                            st.markdown(f"""
                                <div style="
                                    border: 2px solid #e0e0e0;
                                    border-radius: 15px;
                                    padding: 20px;
                                    margin: 10px 0;
                                    background: #fafafa;
                                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                                    transition: all 0.3s ease;
                                    cursor: pointer;
                                ">
                                    <h4 style="margin: 0 0 10px 0; color: #333; display: flex; align-items: center;">
                                        🤖 {agent_name}
                                    </h4>
                                    <p style="margin: 5px 0; color: #666; font-size: 14px;">
                                        📝 {agent_description}
                                    </p>
                                    <p style="margin: 5px 0; color: #999; font-size: 12px;">
                                        🌐 {agent_url}
                                    </p>
                                    <p style="margin: 5px 0; color: #999; font-size: 12px;">
                                        👤 {agent_username}
                                    </p>
                                </div>
                            """, unsafe_allow_html=True)
                        
                        # 点击按钮选择机器人
                        if st.button(
                            f"{'✅ 已选择' if is_selected else '选择此机器人'}", 
                            key=f"select_agent_{agent_name}{key_suffix}",
                            type="primary" if is_selected else "secondary",
                            disabled=is_selected,
                            use_container_width=True
                        ):
                            st.session_state[session_key] = agent['name']
                            st.rerun()
        
        # 显示当前选择的机器人信息
        selected_agent_info = agents_df[agents_df['name'] == selected_agent].iloc[0]
        
        # 安全处理选择的机器人信息中的NaN值
        info_description = selected_agent_info.get('description', '暂无描述')
        if not isinstance(info_description, str) or info_description in ['nan', 'NaN']:
            info_description = '暂无描述'
        
        info_url = selected_agent_info.get('url', 'N/A')
        if not isinstance(info_url, str) or info_url in ['nan', 'NaN']:
            info_url = 'N/A'
        
        info_username = selected_agent_info.get('username', 'N/A')
        if not isinstance(info_username, str) or info_username in ['nan', 'NaN']:
            info_username = 'N/A'
        
        st.markdown("---")
        st.subheader("📋 当前选择的机器人")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.info(f"""
            **🤖 机器人名称**: {selected_agent_info['name']}
            
            **📝 描述**: {info_description}
            
            **🌐 连接地址**: {info_url}
            
            **👤 用户名**: {info_username}
            """)
        
        with col2:
            # 显示连接状态指示器
            st.metric("🔗 连接状态", "待检测", help="分析开始时会自动测试连接")
            
            if st.button("🔧 管理机器人", use_container_width=True):
                st.info("💡 请切换到 'Agent Management' 标签页管理机器人配置")
        
        return selected_agent

    @staticmethod
    def show_multi_agent_selection(agents_df, key_suffix=""):
        """显示多机器人选择界面"""
        st.subheader("🤖 选择多个机器人进行并行测试")
        
        if agents_df.empty:
            st.warning("⚠️ 暂无可用机器人，请先在 'Agent Management' 标签页添加机器人配置")
            return []
        
        # 使用session state存储选择的机器人列表
        session_key = f"selected_agents_multi{key_suffix}"
        if session_key not in st.session_state:
            st.session_state[session_key] = []
        
        # 添加选择模式说明
        st.info("💡 **并行测试模式**: 可以同时选择多个机器人进行对比测试，最多支持3个机器人")
        
        # 计算卡片布局
        agents_list = agents_df.to_dict('records')
        cols_per_row = 3
        num_rows = (len(agents_list) + cols_per_row - 1) // cols_per_row
        
        selected_agents = st.session_state[session_key]
        
        # 显示卡片网格
        for row in range(num_rows):
            cols = st.columns(cols_per_row)
            
            for col_idx in range(cols_per_row):
                agent_idx = row * cols_per_row + col_idx
                
                if agent_idx < len(agents_list):
                    agent = agents_list[agent_idx]
                    
                    with cols[col_idx]:
                        # 判断是否为选中状态
                        is_selected = agent['name'] in selected_agents
                        
                        # 安全处理可能的NaN值和空值
                        agent_url = agent.get('url', 'N/A')
                        if not isinstance(agent_url, str) or agent_url in ['N/A', '', 'nan', 'NaN', None] or pd.isna(agent_url):
                            agent_url = 'N/A'
                        else:
                            agent_url = str(agent_url)[:30] + ("..." if len(str(agent_url)) > 30 else "")
                        
                        agent_description = agent.get('description', '暂无描述')
                        if not isinstance(agent_description, str) or agent_description in ['nan', 'NaN', '', None] or pd.isna(agent_description):
                            agent_description = '暂无描述'
                        
                        agent_username = agent.get('username', 'N/A')
                        if not isinstance(agent_username, str) or agent_username in ['nan', 'NaN', '', None] or pd.isna(agent_username):
                            agent_username = 'N/A'
                        
                        # 确保机器人名称不为空
                        agent_name = agent.get('name', 'Unknown')
                        if not isinstance(agent_name, str) or agent_name in ['nan', 'NaN', '', None] or pd.isna(agent_name):
                            agent_name = 'Unknown Robot'
                        
                        # 创建卡片容器
                        if is_selected:
                            # 选中状态 - 绿色边框
                            st.markdown(f"""
                                <div style="
                                    border: 3px solid #4CAF50;
                                    border-radius: 15px;
                                    padding: 20px;
                                    margin: 10px 0;
                                    background: linear-gradient(135deg, #e8f5e8 0%, #f1f8e9 100%);
                                    box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
                                    transition: all 0.3s ease;
                                    cursor: pointer;
                                    position: relative;
                                ">
                                    <div style="position: absolute; top: 10px; right: 15px; color: #4CAF50; font-size: 20px;">✓</div>
                                    <h4 style="margin: 0 0 10px 0; color: #333; display: flex; align-items: center;">
                                        🤖 {agent_name}
                                    </h4>
                                    <p style="margin: 5px 0; color: #666; font-size: 14px;">
                                        📝 {agent_description}
                                    </p>
                                    <p style="margin: 5px 0; color: #999; font-size: 12px;">
                                        🌐 {agent_url}
                                    </p>
                                    <p style="margin: 5px 0; color: #999; font-size: 12px;">
                                        👤 {agent_username}
                                    </p>
                                </div>
                            """, unsafe_allow_html=True)
                        else:
                            # 未选中状态 - 灰色边框
                            st.markdown(f"""
                                <div style="
                                    border: 2px solid #e0e0e0;
                                    border-radius: 15px;
                                    padding: 20px;
                                    margin: 10px 0;
                                    background: #fafafa;
                                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                                    transition: all 0.3s ease;
                                    cursor: pointer;
                                ">
                                    <h4 style="margin: 0 0 10px 0; color: #333; display: flex; align-items: center;">
                                        🤖 {agent_name}
                                    </h4>
                                    <p style="margin: 5px 0; color: #666; font-size: 14px;">
                                        📝 {agent_description}
                                    </p>
                                    <p style="margin: 5px 0; color: #999; font-size: 12px;">
                                        🌐 {agent_url}
                                    </p>
                                    <p style="margin: 5px 0; color: #999; font-size: 12px;">
                                        👤 {agent_username}
                                    </p>
                                </div>
                            """, unsafe_allow_html=True)
                        
                        # 点击按钮选择/取消选择机器人
                        if is_selected:
                            # 已选中，显示取消选择按钮
                            if st.button(
                                "❌ 取消选择", 
                                key=f"deselect_agent_{agent_name}{key_suffix}",
                                type="secondary",
                                use_container_width=True
                            ):
                                st.session_state[session_key] = [name for name in selected_agents if name != agent['name']]
                                st.rerun()
                        else:
                            # 未选中，显示选择按钮
                            can_select = len(selected_agents) < 3
                            if st.button(
                                f"{'✅ 选择此机器人' if can_select else '❌ 最多选择3个'}", 
                                key=f"select_agent_{agent_name}{key_suffix}",
                                type="primary" if can_select else "secondary",
                                disabled=not can_select,
                                use_container_width=True
                            ):
                                st.session_state[session_key] = selected_agents + [agent['name']]
                                st.rerun()
        
        # 显示当前选择的机器人信息
        if selected_agents:
            st.markdown("---")
            st.subheader(f"📋 已选择的机器人 ({len(selected_agents)}/3)")
            
            # 显示选中的机器人卡片
            cols = st.columns(len(selected_agents))
            
            for idx, agent_name in enumerate(selected_agents):
                agent_info = agents_df[agents_df['name'] == agent_name].iloc[0]
                
                # 安全处理选择的机器人信息中的NaN值
                info_description = agent_info.get('description', '暂无描述')
                if not isinstance(info_description, str) or info_description in ['nan', 'NaN']:
                    info_description = '暂无描述'
                
                info_url = agent_info.get('url', 'N/A')
                if not isinstance(info_url, str) or info_url in ['nan', 'NaN']:
                    info_url = 'N/A'
                
                info_username = agent_info.get('username', 'N/A')
                if not isinstance(info_username, str) or info_username in ['nan', 'NaN']:
                    info_username = 'N/A'
                
                with cols[idx]:
                    st.success(f"""
                    **🤖 {agent_info['name']}**
                    
                    📝 {info_description}
                    
                    🌐 {info_url[:25]}...
                    
                    👤 {info_username}
                    """)
            
            # 显示并行测试说明
            st.info(f"""
            🚀 **并行测试模式**：
            - 将同时向 {len(selected_agents)} 个机器人发送相同的问题
            - 每个机器人的回答将独立生成和评估
            - 结果将自动进行对比分析
            - 预计时间：约 {len(selected_agents)}x 正常分析时间
            """)
            
            # 全部清除按钮
            if st.button("🗑️ 清除所有选择", type="secondary"):
                st.session_state[session_key] = []
                st.rerun()
        
        else:
            st.info("📝 请至少选择一个机器人开始分析")
        
        return selected_agents

    @staticmethod
    def show_compact_agent_selector(agents_df, key_suffix=""):
        """显示紧凑型机器人选择器（用于较小空间）"""
        if agents_df.empty:
            st.warning("⚠️ 暂无可用机器人")
            return None
        
        session_key = f"selected_agent_compact{key_suffix}"
        if session_key not in st.session_state:
            st.session_state[session_key] = agents_df.iloc[0]['name']
        
        agents_list = agents_df.to_dict('records')
        selected_agent = st.session_state[session_key]
        
        # 水平排列的紧凑卡片
        cols = st.columns(min(len(agents_list), 4))
        
        for idx, agent in enumerate(agents_list[:4]):  # 最多显示4个
            with cols[idx]:
                is_selected = agent['name'] == selected_agent
                
                # 紧凑卡片样式
                if is_selected:
                    st.markdown(f"""
                        <div style="
                            border: 2px solid #1f77b4;
                            border-radius: 10px;
                            padding: 10px;
                            text-align: center;
                            background: #e3f2fd;
                            margin: 5px 0;
                        ">
                            <div style="font-size: 16px;">🤖</div>
                            <div style="font-size: 12px; font-weight: bold;">{agent['name']}</div>
                            <div style="color: #1f77b4; font-size: 16px;">✓</div>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                        <div style="
                            border: 1px solid #ddd;
                            border-radius: 10px;
                            padding: 10px;
                            text-align: center;
                            background: #f9f9f9;
                            margin: 5px 0;
                        ">
                            <div style="font-size: 16px;">🤖</div>
                            <div style="font-size: 12px;">{agent['name']}</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                if st.button(
                    "选择", 
                    key=f"compact_select_{agent['name']}{key_suffix}",
                    disabled=is_selected,
                    use_container_width=True
                ):
                    st.session_state[session_key] = agent['name']
                    st.rerun()
        
        return selected_agent

class ConfigurationComponents:
    """配置组件类"""
    
    @staticmethod
    def show_agent_config_form():
        """显示机器人配置表单"""
        st.subheader("🤖 机器人配置")
        
        with st.form("agent_config"):
            st.markdown("**基本信息**")
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("机器人名称", help="用于识别不同的机器人配置")
                url = st.text_input("WebSocket URL", 
                                   value="wss://agents.dyna.ai/openapi/v1/ws/dialog/",
                                   help="机器人的WebSocket连接地址")
            
            with col2:
                description = st.text_input("描述", help="可选，方便记忆该配置的用途")
                username = st.text_input("用户名", help="用于身份验证的用户名")
            
            st.markdown("**认证信息**")
            col3, col4 = st.columns(2)
            
            with col3:
                robot_key = st.text_input("Robot Key", type="password", help="机器人密钥")
            
            with col4:
                robot_token = st.text_input("Robot Token", type="password", help="机器人令牌")
            
            st.markdown("**连接测试**")
            if st.form_submit_button("💾 保存配置"):
                if all([name, url, username, robot_key, robot_token]):
                    return {
                        'name': name,
                        'description': description,
                        'url': url,
                        'username': username,
                        'robot_key': robot_key,
                        'robot_token': robot_token
                    }
                else:
                    st.error("请填写所有必填字段")
                    return None
        
        return None
    
    @staticmethod
    def test_connection(config):
        """测试连接"""
        # 这里应该实现实际的连接测试逻辑
        return True, "连接成功"

class ErrorHandlingComponents:
    """错误处理组件类"""
    
    @staticmethod
    def show_error_details(error, context=""):
        """显示详细的错误信息"""
        st.error(f"❌ 操作失败: {str(error)}")
        
        with st.expander("🔍 错误详情和解决方案"):
            st.code(str(error))
            
            # 提供常见错误的解决方案
            solutions = {
                "WebSocket": "请检查网络连接和机器人配置",
                "CSV": "请检查文件格式和编码",
                "timeout": "请减少样本数量或检查网络连接",
                "permission": "请检查文件权限"
            }
            
            for keyword, solution in solutions.items():
                if keyword.lower() in str(error).lower():
                    st.info(f"💡 建议: {solution}")
                    break 