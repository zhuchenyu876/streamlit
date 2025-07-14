# metrics.py
from typing import Dict, List, Tuple
import numpy as np
from difflib import SequenceMatcher
import jieba
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import logging

def calculate_rouge_l(reference: str, hypothesis: str) -> Dict[str, float]:
    """Calculate ROUGE-L scores
    
    Args:
        reference: Reference text
        hypothesis: Generated text
        
    Returns:
        Dictionary containing precision, recall and F1 scores
    """
    def lcs_length(x: str, y: str) -> int:
        """Calculate Longest Common Subsequence length"""
        return SequenceMatcher(None, x, y).find_longest_match(0, len(x), 0, len(y)).size

    def preprocess_text(text: str) -> str:
        """Preprocess text by converting to lowercase and tokenizing"""
        return ' '.join(jieba.cut(text.lower()))

    try:
        # Preprocess texts
        ref = preprocess_text(reference)
        hyp = preprocess_text(hypothesis)
        
        # Calculate LCS length
        lcs_len = lcs_length(ref, hyp)
        
        # Calculate scores
        precision = lcs_len / len(hyp) if len(hyp) > 0 else 0
        recall = lcs_len / len(ref) if len(ref) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        
        return {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "redundancy": 1 - precision  # 冗余度
        }
    except Exception as e:
        logging.error(f"Error calculating ROUGE-L: {str(e)}")
        return {
            "precision": 0.0,
            "recall": 0.0,
            "f1": 0.0,
            "redundancy": 1.0
        }

def calculate_semantic_similarity(texts: List[str]) -> float:
    """Calculate semantic similarity between multiple texts using TF-IDF and cosine similarity"""
    try:
        # 验证输入
        if not texts or not all(isinstance(t, str) for t in texts):
            logging.warning("Invalid input texts format")
            return 0.0

        # 替换 None 或空字符串
        texts = [str(t) if t is not None else "" for t in texts]
        texts = [t.strip() for t in texts]
        
        # 检查是否所有文本都为空
        if not any(texts):
            logging.warning("All texts are empty")
            return 0.0
            
        # 对文本进行预处理
        processed_texts = []
        for text in texts:
            # 使用jieba分词
            words = jieba.cut(text)
            # 过滤空字符和停用词
            words = [w for w in words if w.strip() and not w.isspace()]
            if words:  # 只添加非空的处理结果
                processed_texts.append(" ".join(words))
                
        if not processed_texts:
            logging.warning("No valid text after processing")
            return 0.0
            
        if len(processed_texts) < 2:
            logging.warning("Not enough valid texts for comparison")
            return 0.0

        # 创建TF-IDF向量
        vectorizer = TfidfVectorizer(
            max_df=1.0,  # 允许所有词
            min_df=0.0,  # 允许低频词
            stop_words=None  # 不使用停用词
        )
        
        try:
            tfidf_matrix = vectorizer.fit_transform(processed_texts)
        except ValueError as e:
            logging.error(f"Error in vectorization: {e}")
            return 0.0

        # 计算相似度
        similarities = cosine_similarity(tfidf_matrix)
        
        # 计算平均相似度（不包括自身相似度）
        n = len(processed_texts)
        total_similarity = 0
        count = 0
        for i in range(n):
            for j in range(i + 1, n):
                total_similarity += similarities[i, j]
                count += 1
                
        return total_similarity / count if count > 0 else 0

    except Exception as e:
        logging.error(f"Error calculating semantic similarity: {str(e)}")
        return 0.0

def normalize_text(text: str) -> str:
    """Normalize text by removing punctuation and whitespace"""
    import string
    if isinstance(text, dict):
        text = text.get('answer', str(text))
    text = str(text)
    return text.translate(str.maketrans('', '', string.punctuation + string.whitespace))