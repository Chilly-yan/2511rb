#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
# 获取项目根目录（当前文件的父目录）
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# 将项目根目录添加到Python路径
sys.path.insert(0, project_root)

import logging
from datetime import datetime, timedelta
from src.models.data_models import InputData
from src.database.repository import FuturesDataRepository
from src.database.database import db_manager



def test_sql():
    """测试调取sql最新数据的逻辑"""
    print("🧪 测试调取sql最新数据的逻辑...")
    
    with db_manager.get_session() as session:
        repo = FuturesDataRepository(session)
        test_result = repo.get_latest_data('螺纹钢主连')
        if test_result is None:
            print('结果为空')
        else:
            print(test_result.trade_date) 

if __name__ == "__main__":
    test_sql()

    

