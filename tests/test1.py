#!/usr/bin/env python3
import sys
import os
import logging

# 添加src到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.input.data_processor import data_processor
from src.data_fetcher.akshare_client import akshare_client

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_akshare_client():
    """测试akshare客户端"""
    print("🧪 测试akshare客户端...")
    
    try:
        # 测试支持的品种
        symbols = akshare_client.get_supported_symbols()
        print(f"✅ 支持的品种: {symbols[:5]}...")  # 只显示前5个
        
        # 测试单个品种
        symbol = "螺纹钢主连"
        if akshare_client.validate_symbol(symbol):
            print(f"✅ 品种验证通过: {symbol}")
            
            # 获取数据
            df = akshare_client.get_futures_recent_data(symbol, days=7)
            print(f"✅ 获取数据成功: {len(df)} 条记录")
            print(f"数据列名: {df.columns.tolist()}")
            if not df.empty:
                print(f"数据样例:\n{df.head(2)}")
        else:
            print(f"❌ 不支持的品种: {symbol}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def test_data_processor():
    """测试数据处理器"""
    print("\n🧪 测试数据处理器...")
    
    try:
        symbol = "螺纹钢主连"
        result = data_processor.fetch_and_process_symbol(symbol, days=7)
        print(f"✅ 数据处理结果: {result}")
        
    except Exception as e:
        print(f"❌ 数据处理测试失败: {e}")

if __name__ == "__main__":
    test_akshare_client()
    test_data_processor()