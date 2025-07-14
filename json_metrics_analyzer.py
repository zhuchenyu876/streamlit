#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import pandas as pd
from typing import Dict, List, Tuple, Any
import logging
from difflib import SequenceMatcher
import re

class JSONMetricsAnalyzer:
    """
    专门用于分析JSON格式轮胎查询结果的评估器
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def parse_json_response(self, response_text: str) -> Dict:
        """
        解析JSON响应文本，提取关键信息
        """
        try:
            # 尝试直接解析JSON
            data = json.loads(response_text)
            return {
                'type': data.get('type', ''),
                'products': self._extract_products_from_markdown(data.get('data', '')),
                'description': data.get('desc', ''),
                'total_found': self._extract_total_found(data.get('desc', '')),
                'price_range': self._extract_price_range(data.get('desc', '')),
                'raw_data': data
            }
        except json.JSONDecodeError:
            # 如果不是JSON格式，作为普通文本处理
            return {
                'type': 'text',
                'products': [],
                'description': response_text,
                'total_found': 0,
                'price_range': (0, 0),
                'raw_data': response_text
            }
    
    def _extract_products_from_markdown(self, markdown_data: str) -> List[Dict]:
        """
        从markdown表格中提取产品信息
        """
        products = []
        if not markdown_data:
            return products
            
        lines = markdown_data.split('\\n')
        for line in lines:
            if '|' in line and 'ID Producto' not in line and ':---' not in line:
                parts = [p.strip() for p in line.split('|') if p.strip()]
                if len(parts) >= 4:
                    try:
                        price = int(parts[3].replace('$', '').replace(',', ''))
                        products.append({
                            'id': parts[0],
                            'name': parts[1],
                            'stock': int(parts[2]),
                            'price': price
                        })
                    except ValueError:
                        continue
        return products
    
    def _extract_total_found(self, desc: str) -> int:
        """
        从描述中提取找到的产品总数
        """
        match = re.search(r'encontrados:\s*(\d+)', desc.lower())
        return int(match.group(1)) if match else 0
    
    def _extract_price_range(self, desc: str) -> Tuple[int, int]:
        """
        从描述中提取价格范围
        """
        match = re.search(r'\$(\d+(?:,\d+)?)\s*-\s*\$(\d+(?:,\d+)?)', desc)
        if match:
            min_price = int(match.group(1).replace(',', ''))
            max_price = int(match.group(2).replace(',', ''))
            return (min_price, max_price)
        return (0, 0)
    
    def calculate_json_metrics(self, reference: str, generated: str) -> Dict:
        """
        计算JSON响应的专门指标
        """
        ref_data = self.parse_json_response(reference)
        gen_data = self.parse_json_response(generated)
        
        # 1. 结构一致性
        structure_consistency = self._calculate_structure_consistency(ref_data, gen_data)
        
        # 2. 产品覆盖度
        product_coverage = self._calculate_product_coverage(ref_data, gen_data)
        
        # 3. 价格准确性
        price_accuracy = self._calculate_price_accuracy(ref_data, gen_data)
        
        # 4. 库存准确性
        stock_accuracy = self._calculate_stock_accuracy(ref_data, gen_data)
        
        # 5. 描述相似性
        description_similarity = self._calculate_description_similarity(ref_data, gen_data)
        
        # 6. 格式正确性
        format_correctness = self._calculate_format_correctness(ref_data, gen_data)
        
        return {
            'structure_consistency': structure_consistency,
            'product_coverage': product_coverage,
            'price_accuracy': price_accuracy,
            'stock_accuracy': stock_accuracy,
            'description_similarity': description_similarity,
            'format_correctness': format_correctness,
            'overall_quality': (structure_consistency + product_coverage + price_accuracy + 
                              stock_accuracy + description_similarity + format_correctness) / 6
        }
    
    def _calculate_structure_consistency(self, ref_data: Dict, gen_data: Dict) -> float:
        """
        计算结构一致性（都是JSON格式，都有相同的字段）
        """
        if ref_data['type'] != gen_data['type']:
            return 0.0
            
        ref_fields = set(ref_data.keys())
        gen_fields = set(gen_data.keys())
        
        if len(ref_fields.union(gen_fields)) == 0:
            return 1.0
            
        return len(ref_fields.intersection(gen_fields)) / len(ref_fields.union(gen_fields))
    
    def _calculate_product_coverage(self, ref_data: Dict, gen_data: Dict) -> float:
        """
        计算产品覆盖度（生成答案包含了多少参考答案中的产品）
        """
        ref_products = ref_data.get('products', [])
        gen_products = gen_data.get('products', [])
        
        if not ref_products:
            return 1.0 if not gen_products else 0.0
            
        # 通过产品ID匹配
        ref_ids = {p['id'] for p in ref_products}
        gen_ids = {p['id'] for p in gen_products}
        
        if not ref_ids:
            return 1.0
            
        return len(ref_ids.intersection(gen_ids)) / len(ref_ids)
    
    def _calculate_price_accuracy(self, ref_data: Dict, gen_data: Dict) -> float:
        """
        计算价格准确性
        """
        ref_products = {p['id']: p for p in ref_data.get('products', [])}
        gen_products = {p['id']: p for p in gen_data.get('products', [])}
        
        if not ref_products:
            return 1.0
            
        correct_prices = 0
        total_matches = 0
        
        for product_id in ref_products:
            if product_id in gen_products:
                total_matches += 1
                if ref_products[product_id]['price'] == gen_products[product_id]['price']:
                    correct_prices += 1
                    
        return correct_prices / total_matches if total_matches > 0 else 1.0
    
    def _calculate_stock_accuracy(self, ref_data: Dict, gen_data: Dict) -> float:
        """
        计算库存准确性
        """
        ref_products = {p['id']: p for p in ref_data.get('products', [])}
        gen_products = {p['id']: p for p in gen_data.get('products', [])}
        
        if not ref_products:
            return 1.0
            
        correct_stock = 0
        total_matches = 0
        
        for product_id in ref_products:
            if product_id in gen_products:
                total_matches += 1
                if ref_products[product_id]['stock'] == gen_products[product_id]['stock']:
                    correct_stock += 1
                    
        return correct_stock / total_matches if total_matches > 0 else 1.0
    
    def _calculate_description_similarity(self, ref_data: Dict, gen_data: Dict) -> float:
        """
        计算描述相似性
        """
        ref_desc = ref_data.get('description', '')
        gen_desc = gen_data.get('description', '')
        
        if not ref_desc and not gen_desc:
            return 1.0
        if not ref_desc or not gen_desc:
            return 0.0
            
        return SequenceMatcher(None, ref_desc, gen_desc).ratio()
    
    def _calculate_format_correctness(self, ref_data: Dict, gen_data: Dict) -> float:
        """
        计算格式正确性
        """
        score = 0.0
        
        # 检查是否都是JSON格式
        if ref_data['type'] == 'markdown' and gen_data['type'] == 'markdown':
            score += 0.5
            
        # 检查是否都有产品数据
        if ref_data.get('products') and gen_data.get('products'):
            score += 0.3
            
        # 检查是否都有描述
        if ref_data.get('description') and gen_data.get('description'):
            score += 0.2
            
        return score
    
    def analyze_dataframe(self, df: pd.DataFrame, ref_col: str, gen_col: str) -> pd.DataFrame:
        """
        分析DataFrame中的所有JSON响应对
        """
        results = []
        
        for idx, row in df.iterrows():
            try:
                metrics = self.calculate_json_metrics(str(row[ref_col]), str(row[gen_col]))
                results.append(metrics)
            except Exception as e:
                self.logger.error(f"Error analyzing row {idx}: {str(e)}")
                # 返回默认值
                results.append({
                    'structure_consistency': 0.0,
                    'product_coverage': 0.0,
                    'price_accuracy': 0.0,
                    'stock_accuracy': 0.0,
                    'description_similarity': 0.0,
                    'format_correctness': 0.0,
                    'overall_quality': 0.0
                })
        
        # 将结果添加到DataFrame
        for key in results[0].keys():
            df[f'json_{key}'] = [result[key] for result in results]
            
        return df

if __name__ == "__main__":
    # 测试代码
    analyzer = JSONMetricsAnalyzer()
    
    # 测试数据
    ref_json = '''{"type": "markdown", "data": "| ID Producto | Nombre del Producto | Stock | Precio |\\n|:------------|:--------------------|:------|:-------|\\n| LL-C30210 | 185 65 15 COMPASAL BLAZER HP 88H | 8 | $1142 |\\n", "desc": "🔍 Resultados de búsqueda para neumáticos 185/65R15\\n\\n📊 Encontrados: 1 productos\\n💰 Rango de precios: $1142 - $1142\\n\\n¿Cuál modelo le interesa?"}'''
    
    gen_json = '''{"type": "markdown", "data": "| ID Producto | Nombre del Producto | Stock | Precio |\\n|:------------|:--------------------|:------|:-------|\\n| LL-C30210 | 185 65 15 COMPASAL BLAZER HP 88H | 8 | $1142 |\\n| LL-C29885 | 185 65 R15 92H XL BLACKHAWK HH11 AUTO | 1 | $1156 |\\n", "desc": "🔍 Resultados de búsqueda para neumáticos 185/65R15\\n\\n📊 Encontrados: 6 productos\\n💰 Rango de precios: $1142 - $2030\\n\\n¿Cuál modelo le interesa?"}'''
    
    metrics = analyzer.calculate_json_metrics(ref_json, gen_json)
    print("JSON Metrics Analysis:")
    for key, value in metrics.items():
        print(f"{key}: {value:.3f}") 