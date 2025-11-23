#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import time
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class AkshareClient:
    """akshare期货数据客户端"""
    
    # 品种映射表
    SYMBOL_MAPPING = {
        "螺纹钢主连": "RB", "铁矿石主连": "I", "焦煤主连": "JM", "焦炭主连": "J",
        "甲醇主连": "MA", "PTA主连": "TA", "豆粕主连": "M", "豆油主连": "Y",
        "棕榈油主连": "P", "白糖主连": "SR", "棉花主连": "CF", "沪铜主连": "CU",
        "沪铝主连": "AL", "黄金主连": "AU", "原油主连": "SC"
    }
    
    def __init__(self, rate_limit_delay=1.0):
        self.rate_limit_delay = rate_limit_delay
        self.last_request_time = 0
    
    def _rate_limit(self):
        """API调用频率限制"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def get_futures_daily_data(self, symbol: str, period: str = "daily", 
                              start_date: Optional[str] = None, 
                              end_date: Optional[str] = None) -> pd.DataFrame:
        """获取期货日线数据"""
        try:
            self._rate_limit()
            
            logger.info(f"📊 获取期货数据: {symbol}")
            
            # 处理日期参数 - 确保不是 None
            if start_date is None:
                start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
            
            if end_date is None:
                end_date = datetime.now().strftime("%Y%m%d")
            
            # 调用akshare API
            df = ak.futures_hist_em(
                symbol=symbol,
                period=period,
                start_date=start_date,  # 现在确保是字符串
                end_date=end_date       # 现在确保是字符串
            )
            
            if df.empty:
                logger.warning(f"⚠️ 未获取到数据: {symbol}")
                return df
            
            logger.info(f"✅ 成功获取 {symbol} 数据，共 {len(df)} 条记录")
            return df
            
        except Exception as e:
            logger.error(f"❌ 获取期货数据失败: {symbol}, 错误: {e}")
            raise

        
    def get_futures_full_data(self, symbol:str, period: str = "daily", start_date:Optional[str] = None, end_date:Optional[str] = None) :
        """获取目标品种全量数据信息"""
        if start_date is None or end_date is None:
            df = ak.futures_hist_em(symbol=symbol, period= period)
        else:
            df = ak.futures_hist_em(symbol=symbol, period= period, start_date= start_date, end_date= end_date)

        if df.empty:
            logger.warning(f"⚠️ 未获取到数据: {symbol}")
            return df
        
        logger.info(f"成功获取{symbol}数据")
        return df         

    def get_futures_recent_data(self, symbol: str, days: int = 30) -> pd.DataFrame:
        """获取最近N天的期货数据（简化方法）"""

        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y%m%d")
        end_date = datetime.now().strftime("%Y%m%d")
        
        return self.get_futures_daily_data(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date
        )
    
    def get_symbol_code(self, symbol: str) -> str:
        """获取品种代码"""
        return self.SYMBOL_MAPPING.get(symbol, symbol)
    
    def validate_symbol(self, symbol: str) -> bool:
        """验证品种是否支持"""
        return symbol in self.SYMBOL_MAPPING.keys()
    
    def get_supported_symbols(self) -> List[str]:
        """获取支持的品种列表"""
        return list(self.SYMBOL_MAPPING.keys())

# 全局客户端实例
akshare_client = AkshareClient()