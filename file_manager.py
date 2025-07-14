#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import pandas as pd
import streamlit as st
from typing import Dict, List, Optional, Union
from datetime import datetime
import tempfile
import shutil
from pathlib import Path

class FileManager:
    """
    统一的文件管理器，处理本地和Streamlit Cloud环境的文件操作差异
    """
    
    def __init__(self):
        self.is_cloud = self._detect_cloud_environment()
        self.temp_dir = None
        self._setup_environment()
    
    def _detect_cloud_environment(self) -> bool:
        """检测是否运行在Streamlit Cloud环境中"""
        # 检查典型的Streamlit Cloud环境变量
        cloud_indicators = [
            'STREAMLIT_CLOUD',
            'STREAMLIT_SHARING',
            '/mount/src/' in os.getcwd(),
            '/home/adminuser/venv/' in os.environ.get('VIRTUAL_ENV', ''),
        ]
        return any(cloud_indicators)
    
    def _setup_environment(self):
        """设置环境相关的配置"""
        if self.is_cloud:
            # 在云端环境中，使用临时目录
            self.temp_dir = tempfile.mkdtemp()
            st.info("🌐 检测到云端环境，文件将存储在临时空间中")
        else:
            # 本地环境，使用标准目录
            self.temp_dir = None
    
    def ensure_directory(self, path: str) -> str:
        """确保目录存在，返回实际可用的路径"""
        if self.is_cloud:
            # 云端环境：创建临时目录
            if self.temp_dir:
                cloud_path = os.path.join(self.temp_dir, os.path.basename(path))
                os.makedirs(cloud_path, exist_ok=True)
                return cloud_path
            else:
                return path
        else:
            # 本地环境：正常创建目录
            try:
                os.makedirs(path, exist_ok=True)
                return path
            except (OSError, PermissionError):
                # 如果无法创建，使用临时目录
                temp_path = os.path.join(tempfile.gettempdir(), os.path.basename(path))
                os.makedirs(temp_path, exist_ok=True)
                return temp_path
    
    def save_csv(self, df: pd.DataFrame, file_path: str, **kwargs) -> str:
        """保存CSV文件，处理环境差异"""
        try:
            # 确保目录存在
            directory = os.path.dirname(file_path)
            if directory:
                actual_dir = self.ensure_directory(directory)
                actual_path = os.path.join(actual_dir, os.path.basename(file_path))
            else:
                actual_path = file_path
            
            # 保存文件
            df.to_csv(actual_path, **kwargs)
            
            if self.is_cloud:
                # 在云端环境中，同时保存到session state
                self._save_to_session_state(actual_path, df)
            
            return actual_path
            
        except (OSError, PermissionError) as e:
            # 如果无法保存文件，仅保存到session state
            st.warning(f"⚠️ 无法保存文件到磁盘: {str(e)}")
            self._save_to_session_state(file_path, df)
            return file_path
    
    def read_csv(self, file_path: str, **kwargs) -> Optional[pd.DataFrame]:
        """读取CSV文件，处理环境差异"""
        try:
            # 首先尝试从实际文件路径读取
            return pd.read_csv(file_path, **kwargs)
        except FileNotFoundError:
            # 如果文件不存在，尝试从session state读取
            return self._read_from_session_state(file_path)
    
    def file_exists(self, file_path: str) -> bool:
        """检查文件是否存在"""
        if os.path.exists(file_path):
            return True
        # 检查session state
        return self._exists_in_session_state(file_path)
    
    def get_file_list(self, pattern: str) -> List[str]:
        """获取文件列表，支持通配符"""
        import glob
        files = []
        
        # 获取实际文件
        try:
            files.extend(glob.glob(pattern))
        except Exception:
            pass
        
        # 获取session state中的文件
        if 'file_storage' in st.session_state:
            for stored_path in st.session_state['file_storage'].keys():
                if self._match_pattern(stored_path, pattern):
                    files.append(stored_path)
        
        return sorted(set(files), reverse=True)
    
    def _save_to_session_state(self, file_path: str, df: pd.DataFrame):
        """保存数据到session state"""
        if 'file_storage' not in st.session_state:
            st.session_state['file_storage'] = {}
        
        st.session_state['file_storage'][file_path] = {
            'data': df,
            'timestamp': datetime.now(),
            'type': 'csv'
        }
    
    def _read_from_session_state(self, file_path: str) -> Optional[pd.DataFrame]:
        """从session state读取数据"""
        if 'file_storage' in st.session_state:
            stored_data = st.session_state['file_storage'].get(file_path)
            if stored_data and stored_data['type'] == 'csv':
                return stored_data['data']
        return None
    
    def _exists_in_session_state(self, file_path: str) -> bool:
        """检查文件是否存在于session state中"""
        if 'file_storage' in st.session_state:
            return file_path in st.session_state['file_storage']
        return False
    
    def _match_pattern(self, file_path: str, pattern: str) -> bool:
        """简单的通配符匹配"""
        import fnmatch
        return fnmatch.fnmatch(file_path, pattern)
    
    def get_download_data(self, file_path: str) -> Optional[str]:
        """获取文件的下载数据"""
        try:
            # 尝试从实际文件读取
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8-sig') as f:
                    return f.read()
        except Exception:
            pass
        
        # 从session state读取
        df = self._read_from_session_state(file_path)
        if df is not None:
            return df.to_csv(index=False, encoding='utf-8-sig')
        
        return None
    
    def create_temp_file(self, content: bytes, suffix: str = '.csv') -> str:
        """创建临时文件"""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        temp_file.write(content)
        temp_file.close()
        return temp_file.name
    
    def cleanup_temp_files(self):
        """清理临时文件"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
            except Exception:
                pass
    
    def get_default_config(self, config_type: str) -> Dict:
        """获取默认配置"""
        if config_type == 'agents':
            return {
                'name': ['futu路线1', 'futu路线2'],
                'description': ['富途问答机器人路线1', '富途问答机器人路线2'],
                'url': [
                    'wss://agents.dyna.ai/openapi/v1/ws/dialog/',
                    'wss://agents.dyna.ai/openapi/v1/ws/dialog/'
                ],
                'username': ['your_username', 'your_username'],
                'robot_key': [
                    'X3qi%2FBbsvlmDWGyUBZBhaNi4bDk%3D',
                    'aAPeava4nCrSSMpN%2F9SxHhtjgt4%3D'
                ],
                'robot_token': [
                    'MTczNjEzMTY4NzM0NwpQVHgxb3NYMWxDNnYyVVMrZzZ2UStUR1QwelU9',
                    'MTczOTQyMDQ6NDUzMgowblpwWVRIWHQ0M2RGN3ErSEJzNDF0RmNUQkU9'
                ]
            }
        elif config_type == 'analyzer':
            return {
                'url': 'https://agents.dyna.ai/openapi/v1/conversation/dialog/',
                'robot_key': 'f79sd16wABIqwLe%2FzjGeZGDRMUo%3D',
                'robot_token': 'MTczODkxMDA0MzUwMgp1cjRVVnF4Y0w3Y2hwRmU3RmxFUXFQV05lSGc9',
                'username': 'marshall.ting@dyna.ai'
            }
        else:
            return {}
    
    def get_template_content(self, template_type: str = 'default') -> str:
        """获取模板内容"""
        if template_type == 'default':
            # 默认模板内容
            template_content = """场景,测试数据,参考答案
场景1,这是一个测试问题,这是参考答案
场景2,另一个测试问题,另一个参考答案
"""
            return template_content
        else:
            return ""

# 创建全局文件管理器实例
file_manager = FileManager() 