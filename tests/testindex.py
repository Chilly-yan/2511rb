import sys
import os
import logging

# 添加src到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.models.data_models import InputData
from src.database.database import db_manager
# from src.database.repository import FuturesDataRepository
from datetime import datetime
from src.analysis.index_calculater import IndexCalculater

import numpy as np
import pandas as pd

def test_load():
    session = db_manager.SessionLocal()
    dataResult = pd.read_sql(session.query(InputData).statement, session.bind)
    print(dataResult['close_price'])
    icer = IndexCalculater()
    print(icer.calculate_index(dataResult))

if __name__ == "__main__":
    test_load()


