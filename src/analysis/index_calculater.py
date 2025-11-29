#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Union, Sequence
from talib import *
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class IndexCalculater:
    """期货综合指数计算器"""

    def __init__(self):
        """
        初始化计算器

        :param data: 包含期货市场数据的DataFrame，必须包含以下列:
                     ['symbol', 'trade_date', 'open_price', 'high_price', 'low_price', 'close_price', 'volume']
        :这里不做日期处理，在前期根据数据内容设定
        """
        # self.data = data

    def calculate_index(self, Tdata: pd.DataFrame) -> List:
        """
        计算全量的量化分析指标
        """
        logger.info(f"开始计算指数" )
        
        data = Tdata['close_price'].values
        index_data = pd.DataFrame()
        index_data['index_date'] = Tdata['trade_date'] # type: ignore
        index_data['symbol'] = Tdata['symbol']

        # 利用talib计算EMA
        index_data['EMA_12'] = EMA(data, timeperiod=12) # type: ignore
        index_data['EMA_26'] = EMA(data, timeperiod=26) # type: ignore

        # 计算RSI
        index_data['RSI_14'] = RSI(data, timeperiod=14) # type: ignore

        # 计算MACD
        macd, macdsignal, macdhist = MACD(data, fastperiod=12, slowperiod=26, signalperiod=9) # type: ignore
        index_data['MACD'] = macd
        index_data['MACD_Signal'] = macdsignal  
        index_data['MACD_Hist'] = macdhist

        # 计算布林带
        upperband, middleband, lowerband = BBANDS(data, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0) # type: ignore
        index_data['BB_Upper'] = upperband
        index_data['BB_Middle'] = middleband
        index_data['BB_Lower'] = lowerband

        index_sql = self._parseResult(index_data)

        return index_sql
    
    def _parseResult(self,data:pd.DataFrame) -> List: 
        index_result = []
        data = data.dropna()
        for _, row in data.iterrows():
            try:
                value_colume = data.iloc[:,2:].columns
                for col in value_colume:
                    index_result.append(
                        {'symbol':row['symbol'],
                        'index_date':row['index_date'],
                        'index_name':col,
                        'index_value':row[col]
                            }
                        )

            except Exception as e:
                logger.error(f"❌ 处理单条数据失败: {row}, 错误: {e}")
                continue
        return index_result



        



