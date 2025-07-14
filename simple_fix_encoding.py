#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import pandas as pd
from pathlib import Path
import shutil

def fix_csv_encoding(file_path):
    """修复CSV文件编码"""
    print(f"\n处理文件: {file_path}")
    
    # 创建备份
    backup_path = str(file_path) + '.backup'
    shutil.copy2(file_path, backup_path)
    print(f"创建备份: {backup_path}")
    
    # 常见编码列表
    encodings_to_try = [
        'utf-8',
        'utf-8-sig',
        'gbk',
        'gb2312',
        'latin-1',
        'cp1252',
        'iso-8859-1'
    ]
    
    content = None
    original_encoding = None
    
    # 尝试读取文件
    for encoding in encodings_to_try:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            original_encoding = encoding
            print(f"✅ 成功读取文件，编码: {encoding}")
            break
        except Exception as e:
            print(f"❌ 编码 {encoding} 失败: {e}")
            continue
    
    if content is None:
        print("❌ 无法读取文件，跳过")
        os.remove(backup_path)
        return False
    
    # 写入UTF-8-BOM格式
    try:
        with open(file_path, 'w', encoding='utf-8-sig', newline='') as f:
            f.write(content)
        print("✅ 成功转换为 UTF-8-BOM")
        
        # 验证转换结果
        df = pd.read_csv(file_path, encoding='utf-8-sig')
        print(f"✅ 验证成功，数据行数: {len(df)}")
        
        # 删除备份
        os.remove(backup_path)
        return True
        
    except Exception as e:
        print(f"❌ 转换失败: {e}")
        # 恢复备份
        shutil.copy2(backup_path, file_path)
        os.remove(backup_path)
        return False

def main():
    """主函数"""
    print("🔧 CSV文件编码修复工具 (简化版)")
    print("=" * 50)
    
    # 获取当前目录下所有csv文件
    csv_files = list(Path('.').glob('*.csv'))
    
    if not csv_files:
        print("当前目录没有CSV文件")
        return
    
    print(f"找到 {len(csv_files)} 个CSV文件:")
    for file in csv_files:
        print(f"  - {file}")
    
    print("\n开始处理...")
    
    success_count = 0
    for csv_file in csv_files:
        try:
            if fix_csv_encoding(csv_file):
                success_count += 1
        except Exception as e:
            print(f"❌ 处理 {csv_file} 时出错: {e}")
    
    print("\n" + "=" * 50)
    print(f"处理完成！成功: {success_count}/{len(csv_files)}")

if __name__ == "__main__":
    main() 