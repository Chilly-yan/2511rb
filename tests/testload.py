#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import logging

# 添加src到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from models.data_models import InputData
from src.database.database import db_manager
from src.database.repository import FuturesDataRepository
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_repository_fix():
    """测试仓库修复"""
    print("🧪 测试仓库修复...")
    
    try:
        # 初始化数据库
        db_manager.create_tables()
        
        # 测试创建数据
        with db_manager.get_session() as session:
            repo = FuturesDataRepository(session)
            
            # 测试单个数据创建
            market_data = repo.create_market_data(
                symbol="rebar",
                trade_time=datetime.now(),
                open_price=100.0,
                high_price=105.0,
                low_price=98.0,
                close_price=102.0,
                volume=1000000,
                data_source="test"
            )
            
            print(f"✅ 单个数据创建成功: ID={market_data.id}, Symbol={market_data.symbol}, SymbolCode={market_data.symbol_code}")
            
            # 测试批量数据创建
            test_data = [
                {
                    'symbol': 'iron_ore',
                    'trade_time': datetime.now(),
                    'open_price': 150.0,
                    'high_price': 155.0,
                    'low_price': 148.0,
                    'close_price': 152.0,
                    'volume': 500000
                },
                {
                    'symbol': 'coking_coal',
                    'trade_time': datetime.now(),
                    'open_price': 200.0,
                    'high_price': 205.0,
                    'low_price': 198.0,
                    'close_price': 202.0,
                    'volume': 300000
                }
            ]
            
            batch_result = repo.batch_create_market_data(test_data)
            print(f"✅ 批量数据创建结果: {batch_result}")
            
            # 验证数据
            all_data = session.query(InputData).all()
            print(f"✅ 数据库中共有 {len(all_data)} 条记录")
            for data in all_data:
                print(f"   - {data.symbol} ({data.symbol_code}): {data.close_price}")
        
        print("🎉 仓库修复测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_repository_fix()