#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import List

# 添加src到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_type_safety():
    """测试类型安全"""
    print("🧪 测试类型安全...")
    
    try:
        from src.analysis.technical_analyzer import TechnicalAnalyzer, safe_convert_to_float_list
        
        # 测试混合类型数据
        mixed_data = [100, 102.5, 98, 101.3, 105]  # int和float混合
        print(f"📊 原始数据: {mixed_data} (类型: {[type(x) for x in mixed_data]})")
        
        # 转换为List[float]
        float_list = safe_convert_to_float_list(mixed_data)
        print(f"📊 转换后: {float_list} (类型: {[type(x) for x in float_list]})")
        
        # 验证类型
        assert all(isinstance(x, float) for x in float_list), "❌ 类型转换失败"
        print("✅ 类型安全测试通过")
        
        return True
        
    except Exception as e:
        print(f"❌ 类型安全测试失败: {e}")
        return False

def test_technical_analyzer():
    """测试技术分析器"""
    print("\n🧪 测试技术分析器...")
    
    try:
        from src.analysis.technical_analyzer import TechnicalAnalyzer
        
        # 创建测试数据（包含int和float混合）
        dates = pd.date_range(start='2024-01-01', end='2024-01-20', freq='D')
        test_data = pd.DataFrame({
            '日期': dates,
            '开盘': [100 + i*2 for i in range(len(dates))],  # int
            '最高': [105.5 + i*2 for i in range(len(dates))],  # float
            '最低': [98 + i*2 for i in range(len(dates))],     # int
            '收盘': [102.3 + i*2 for i in range(len(dates))],  # float
            '成交量': [1000000 + i*10000 for i in range(len(dates))],
            '成交额': [100000000.5 + i*1000000 for i in range(len(dates))]  # float
        })
        
        print(f"📊 测试数据: {len(test_data)} 条记录")
        
        # 创建分析器实例
        analyzer = TechnicalAnalyzer()
        
        # 测试分析
        result = analyzer.analyze(test_data, "test_symbol")
        print(f"✅ 分析结果: {result}")
        
        if result.get('success'):
            print(f"📈 趋势类型: {result['trend_type']}")
            print(f"💡 交易建议: {result['suggestion']}")
            print(f"🎯 置信度: {result['confidence']:.2f}")
            print(f"💰 当前价格: {result['current_price']} (类型: {type(result['current_price'])})")
            
            # 验证所有指标都是float
            indicators = result['indicators']
            for key, value in indicators.items():
                print(f"📊 {key}: {value} (类型: {type(value)})")
                assert isinstance(value, float), f"❌ {key} 不是float类型"
        
        print("✅ 技术分析器测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_type_safety()
    test_technical_analyzer()