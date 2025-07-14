#!/usr/bin/env python3
"""
LLM质量分析系统启动脚本
一键启动脚本，包含环境检查、依赖安装和应用启动功能
"""

import os
import sys
import subprocess
import pkg_resources
import platform
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    print("🐍 检查Python版本...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python版本过低，需要Python 3.8及以上版本")
        print(f"   当前版本: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python版本检查通过: {version.major}.{version.minor}.{version.micro}")
    return True

def check_dependencies():
    """检查依赖是否安装"""
    print("📦 检查依赖包...")
    
    required_packages = [
        'streamlit',
        'pandas',
        'scikit-learn',
        'jieba',
        'requests',
        'python-dotenv',
        'plotly',
        'tqdm'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            pkg_resources.get_distribution(package)
            print(f"   ✅ {package}")
        except pkg_resources.DistributionNotFound:
            print(f"   ❌ {package} (未安装)")
            missing_packages.append(package)
    
    return missing_packages

def install_dependencies(missing_packages):
    """安装缺失的依赖"""
    if not missing_packages:
        return True
    
    print(f"\n📥 需要安装 {len(missing_packages)} 个依赖包...")
    
    # 询问用户是否自动安装
    response = input("是否自动安装缺失的依赖包? (y/n): ")
    if response.lower() not in ['y', 'yes', '是']:
        print("❌ 用户取消安装，程序退出")
        return False
    
    # 安装依赖
    for package in missing_packages:
        print(f"   📦 安装 {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"   ✅ {package} 安装成功")
        except subprocess.CalledProcessError:
            print(f"   ❌ {package} 安装失败")
            return False
    
    return True

def check_project_structure():
    """检查项目结构"""
    print("📁 检查项目结构...")
    
    required_files = [
        'app.py',
        'client.py',
        'llm_analyzer.py',
        'dashboard.py',
        'metrics.py',
        'ui_components.py',
        'requirements.txt'
    ]
    
    required_dirs = [
        'public',
        'log',
        'qa_analysis_results'
    ]
    
    missing_files = []
    missing_dirs = []
    
    # 检查文件
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
            print(f"   ❌ {file} (缺失)")
        else:
            print(f"   ✅ {file}")
    
    # 检查目录
    for dir in required_dirs:
        if not os.path.exists(dir):
            missing_dirs.append(dir)
            print(f"   ❌ {dir}/ (缺失)")
        else:
            print(f"   ✅ {dir}/")
    
    # 创建缺失的目录
    if missing_dirs:
        print("\n📁 创建缺失的目录...")
        for dir in missing_dirs:
            os.makedirs(dir, exist_ok=True)
            print(f"   ✅ 创建 {dir}/")
    
    return len(missing_files) == 0

def create_default_configs():
    """创建默认配置文件"""
    print("⚙️ 检查配置文件...")
    
    # 创建默认的agents.csv
    agents_file = "public/agents.csv"
    if not os.path.exists(agents_file):
        print(f"   📝 创建默认的 {agents_file}")
        import pandas as pd
        default_agents = pd.DataFrame({
            'name': ['default'],
            'description': ['默认机器人配置'],
            'url': ['wss://agents.dyna.ai/openapi/v1/ws/dialog/'],
            'username': ['your_username'],
            'robot_key': ['your_robot_key'],
            'robot_token': ['your_robot_token']
        })
        default_agents.to_csv(agents_file, index=False)
        print(f"   ✅ 默认配置已创建，请在应用中更新实际的配置信息")
    
    # 创建默认的analyzer_config.csv
    analyzer_config_file = "public/analyzer_config.csv"
    if not os.path.exists(analyzer_config_file):
        print(f"   📝 创建默认的 {analyzer_config_file}")
        import pandas as pd
        default_config = pd.DataFrame({
            'url': ['https://agents.dyna.ai/openapi/v1/conversation/dialog/'],
            'username': ['your_username'],
            'robot_key': ['your_robot_key'],
            'robot_token': ['your_robot_token']
        })
        default_config.to_csv(analyzer_config_file, index=False)
        print(f"   ✅ 默认配置已创建，请在应用中更新实际的配置信息")
    
    # 创建.env模板
    env_file = ".env"
    if not os.path.exists(env_file):
        print(f"   📝 创建环境变量模板 {env_file}")
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write("""# LLM质量分析系统环境变量配置
# 请根据实际情况修改以下配置

# 用户信息
USER_NAME=your_username

# WebSocket连接URL
WS_URL=wss://agents.dyna.ai/openapi/v1/ws/dialog/

# 机器人认证信息
ROBOT_KEY=your_robot_key
ROBOT_TOKEN=your_robot_token
""")
        print(f"   ✅ 环境变量模板已创建，请编辑 {env_file} 文件配置实际参数")

def get_streamlit_command():
    """获取Streamlit启动命令"""
    # 尝试不同的启动方式
    commands = [
        [sys.executable, "-m", "streamlit", "run", "app.py"],
        ["streamlit", "run", "app.py"],
        ["python", "-m", "streamlit", "run", "app.py"],
        ["python3", "-m", "streamlit", "run", "app.py"]
    ]
    
    for cmd in commands:
        try:
            # 测试命令是否可用
            result = subprocess.run(cmd + ["--help"], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=5)
            if result.returncode == 0:
                return cmd
        except (subprocess.TimeoutExpired, FileNotFoundError):
            continue
    
    return None

def start_application():
    """启动应用"""
    print("🚀 启动应用...")
    
    # 获取启动命令
    cmd = get_streamlit_command()
    if not cmd:
        print("❌ 无法找到Streamlit命令，请确保已正确安装Streamlit")
        return False
    
    # 添加启动参数
    cmd.extend([
        "--server.port", "8501",
        "--server.address", "0.0.0.0",
        "--server.headless", "true"
    ])
    
    print(f"   命令: {' '.join(cmd)}")
    print("\n🌐 应用将在以下地址启动:")
    print("   本地访问: http://localhost:8501")
    print("   网络访问: http://0.0.0.0:8501")
    print("\n⚠️  首次启动可能需要一些时间，请耐心等待...")
    print("   启动完成后，请在浏览器中访问上述地址")
    
    try:
        subprocess.run(cmd)
        return True
    except KeyboardInterrupt:
        print("\n👋 用户手动停止应用")
        return True
    except Exception as e:
        print(f"❌ 启动失败: {str(e)}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("🔍 LLM质量分析系统 - 启动脚本")
    print("=" * 60)
    
    # 检查Python版本
    if not check_python_version():
        sys.exit(1)
    
    # 检查依赖
    missing_packages = check_dependencies()
    if missing_packages:
        if not install_dependencies(missing_packages):
            sys.exit(1)
    
    # 检查项目结构
    if not check_project_structure():
        print("❌ 项目文件不完整，请检查文件是否存在")
        sys.exit(1)
    
    # 创建默认配置
    create_default_configs()
    
    print("\n✅ 所有检查完成，准备启动应用...")
    print("\n💡 使用提示:")
    print("   1. 首次使用请到 'Agent Management' 页面配置机器人")
    print("   2. 可以下载数据模板了解输入格式")
    print("   3. 建议从小样本开始测试（如10-50个样本）")
    print("   4. 按 Ctrl+C 可以停止应用")
    
    print("\n" + "=" * 60)
    
    # 启动应用
    if not start_application():
        sys.exit(1)

if __name__ == "__main__":
    main() 