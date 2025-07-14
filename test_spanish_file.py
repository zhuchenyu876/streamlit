#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import os

def test_spanish_file():
    """全面测试西班牙语多轮对话文件"""
    filename = '轮胎测试数据_西班牙语_多轮对话.csv'
    
    print(f"🔍 测试文件: {filename}")
    print("=" * 60)
    
    # 1. 文件基本信息
    if os.path.exists(filename):
        file_size = os.path.getsize(filename)
        print(f"📄 文件大小: {file_size:,} 字节")
    else:
        print("❌ 文件不存在！")
        return
    
    # 2. 原始文本行数检查
    print("\n📊 原始文本行数:")
    print("-" * 30)
    
    encodings_to_try = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312', 'latin1']
    text_lines = None
    
    for encoding in encodings_to_try:
        try:
            with open(filename, 'r', encoding=encoding) as f:
                text_lines = f.readlines()
            print(f"✅ 文本行数 ({encoding}): {len(text_lines)} 行")
            break
        except Exception as e:
            print(f"❌ {encoding} 编码失败: {e}")
    
    # 3. pandas读取测试
    print(f"\n🐼 Pandas读取测试:")
    print("-" * 30)
    
    for encoding in encodings_to_try:
        try:
            # 标准读取
            df1 = pd.read_csv(filename, encoding=encoding)
            print(f"✅ 标准读取 ({encoding}): {len(df1)} 行")
            
            # 应用程序读取方式
            df2 = pd.read_csv(filename, encoding=encoding, 
                             quoting=1, skipinitialspace=True, 
                             on_bad_lines='skip')
            print(f"📱 应用读取 ({encoding}): {len(df2)} 行")
            
            # 检查行数差异
            if len(df1) != len(df2):
                print(f"⚠️  读取方式差异: 标准{len(df1)}行 vs 应用{len(df2)}行")
                print(f"   可能原因: 文件包含格式问题行")
            
            # 显示列信息
            print(f"   列数: {len(df2.columns)}")
            print(f"   列名: {list(df2.columns)}")
            
            # 检查数据质量
            empty_rows = df2.isnull().all(axis=1).sum()
            duplicate_rows = df2.duplicated().sum()
            print(f"   空行: {empty_rows}")
            print(f"   重复行: {duplicate_rows}")
            
            # 成功读取后跳出循环
            df = df2  # 使用应用程序的读取方式
            break
            
        except Exception as e:
            print(f"❌ Pandas ({encoding}) 失败: {e}")
            df = None
    
    if df is None:
        print("❌ 所有编码读取都失败！")
        return
    
    # 4. 模拟应用程序处理流程
    print(f"\n🎯 模拟应用程序处理:")
    print("-" * 30)
    
    # 检查列名匹配
    possible_column_sets = [
        (['场景', '测试数据', '参考答案'], "中文"),
        (['Pregunta', 'Contenido de Pregunta', 'Respuesta de Referencia'], "西班牙语"),
        (['问题', '问题内容', '参考答案'], "西班牙语混合格式"),
        (['Scene', 'Test Data', 'Reference Answer'], "英语")
    ]
    
    matched_format = None
    for cols, lang_name in possible_column_sets:
        if all(col in df.columns for col in cols):
            matched_format = (cols, lang_name)
            print(f"✅ 匹配格式: {lang_name} - {cols}")
            break
    
    if matched_format is None:
        print("❌ 没有匹配的列名格式！")
        print(f"   实际列名: {list(df.columns)}")
        return
    
    # 5. 数据处理模拟
    selected_columns, format_name = matched_format
    processed_df = df[selected_columns].copy()
    
    print(f"\n📊 数据处理结果:")
    print(f"   原始数据: {len(df)} 行")
    print(f"   提取列后: {len(processed_df)} 行")
    
    # 检查采样逻辑
    sample_sizes = [10, 50, 100]
    for sample_n in sample_sizes:
        if len(processed_df) > sample_n:
            sampled_df = processed_df.sample(n=sample_n, random_state=42)
            print(f"   采样到{sample_n}行: {len(sampled_df)} 行")
        else:
            print(f"   无需采样到{sample_n}行: 数据只有{len(processed_df)}行")
    
    # 6. 显示前几行和后几行数据
    print(f"\n📋 数据内容示例:")
    print("-" * 30)
    print("前3行:")
    for i, (idx, row) in enumerate(processed_df.head(3).iterrows()):
        print(f"  {i+1}. {row.iloc[0][:50]}...")
    
    print("后3行:")
    for i, (idx, row) in enumerate(processed_df.tail(3).iterrows()):
        print(f"  {len(processed_df)-2+i}. {row.iloc[0][:50]}...")
    
    # 7. 结论
    print(f"\n🎯 测试结论:")
    print("=" * 30)
    print(f"📄 文件实际行数: {len(text_lines)} 行 (包含标题)")
    print(f"📊 有效数据行数: {len(df)} 行")
    print(f"🔧 匹配的格式: {format_name}")
    print(f"⚙️  处理后行数: {len(processed_df)} 行")
    
    if len(text_lines) - 1 != len(df):  # 减去标题行
        print(f"⚠️  发现问题: 文本行数与数据行数不匹配")
        print(f"   可能原因: 文件包含空行、格式错误行或编码问题")
    else:
        print(f"✅ 数据读取正常")
    
    return df

if __name__ == "__main__":
    test_spanish_file() 