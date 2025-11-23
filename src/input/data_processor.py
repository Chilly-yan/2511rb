#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
from src.data_fetcher.akshare_client import akshare_client
from src.database.repository import FuturesDataRepository
from src.database.database import db_manager

logger = logging.getLogger(__name__)

class DataProcessor:
    """数据处理器"""
    
    def __init__(self):
        self.akshare_client = akshare_client
    
    def fetch_and_process_symbol(self, symbol: str, days: int = 30) -> Dict[str, Any]:
        """获取并处理单个品种数据"""
        try:
            # 验证品种
            if not self.akshare_client.validate_symbol(symbol):
                return {'success': False, 'error': f'不支持的品种: {symbol}'}
            
            # 获取数据
            df = self.akshare_client.get_futures_recent_data(symbol, days)
            
            if df.empty:
                return {'success': False, 'error': '数据为空'}
            
            # 处理数据
            processed_data = self._process_akshare_data(df, symbol)
            
            if not processed_data:
                return {'success': False, 'error': '数据处理失败'}
            
            # 存储到数据库
            with db_manager.get_session() as session:
                repo = FuturesDataRepository(session)
                result = repo.batch_create_market_data(processed_data)
                result['symbol'] = symbol
                return result
                
        except Exception as e:
            logger.error(f"❌ 处理品种数据失败: {symbol}, 错误: {e}")
            return {'success': False, 'error': str(e)}
    
    def _process_akshare_data(self, df: pd.DataFrame, symbol: str) -> List[Dict[str, Any]]:
        """处理akshare数据格式"""
        processed_data = []
        
        for _, row in df.iterrows():
            try:
                # 解析日期
                trade_date = self._parse_date(row['时间'])
                
                # 只传递create_market_data方法支持的字段
                data = {
                    'symbol': symbol,
                    'trade_time': trade_date,
                    'open_price': float(row['开盘']),
                    'high_price': float(row['最高']),
                    'low_price': float(row['最低']),
                    'close_price': float(row['收盘']),
                    'data_source': 'akshare'
                }
                
                # 可选字段
                if '成交量' in row and pd.notna(row['成交量']):
                    data['volume'] = int(row['成交量'])
                
                if '成交额' in row and pd.notna(row['成交额']):
                    data['turnover'] = float(row['成交额'])
                
                if '持仓量' in row and pd.notna(row['持仓量']):
                    data['open_interest'] = int(row['持仓量'])
                
                # 涨跌幅字段
                if '涨跌' in row and pd.notna(row['涨跌']):
                    data['change_amount'] = float(row['涨跌'])
                
                if '涨跌幅' in row and pd.notna(row['涨跌幅']):
                    data['change_percent'] = float(row['涨跌幅'])
                
                processed_data.append(data)
                
            except Exception as e:
                logger.error(f"❌ 处理单条数据失败: {row}, 错误: {e}")
                continue
        
        return processed_data
    
    def _parse_date(self, date_str: str) -> datetime:
        """解析日期字符串"""
        try:
            return datetime.strptime(str(date_str), '%Y-%m-%d')
        except ValueError:
            return pd.to_datetime(date_str).to_pydatetime()
    
    
    def batch_process_symbols(self, symbols: List[str], days: int = 30) -> Dict[str, Any]:
        """批量处理多个品种数据"""
        results = {
            'total_symbols': len(symbols),
            'success_count': 0,
            'failed_count': 0,
            'details': {}
        }
        
        for symbol in symbols:
            try:
                result = self.fetch_and_process_symbol(symbol, days)
                results['details'][symbol] = result
                
                if result.get('success', False):
                    results['success_count'] += 1
                else:
                    results['failed_count'] += 1
                    
            except Exception as e:
                results['details'][symbol] = {'success': False, 'error': str(e)}
                results['failed_count'] += 1
        
        logger.info(f"📦 批量处理完成: 成功 {results['success_count']}/{results['total_symbols']}")
        return results

# 全局数据处理器实例
data_processor = DataProcessor()