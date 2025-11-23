#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Union, Sequence
import logging

logger = logging.getLogger(__name__)

class TechnicalAnalyzer:
    """技术分析器"""
    
    def analyze(self, data: pd.DataFrame, symbol: str) -> Dict[str, Any]:
        """分析数据"""
        try:
            if data is None or data.empty:
                return {"error": "No data available", "success": False}
            
            # 安全获取价格数据
            prices = self._safe_get_prices(data)
            if len(prices) < 5:
                return {"error": "Insufficient data", "success": False}
            
            # 计算技术指标
            indicators = self._calculate_indicators(prices, data)
            
            # 判断趋势
            trend = self._determine_trend(indicators, prices, data)
            
            # 生成交易建议
            suggestion = self._generate_suggestion(trend, indicators, prices)
            
            result = {
                "success": True,
                "symbol": symbol,
                "trend_type": trend,
                "suggestion": suggestion,
                "current_price": float(prices[-1]),  # 确保转换为float
                "indicators": indicators,
                "confidence": self._calculate_confidence(indicators, trend)
            }
            
            logger.info(f"✅ Analysis completed for {symbol}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Analysis error for {symbol}: {e}")
            return {"success": False, "error": str(e)}
    
    def _safe_get_prices(self, data: pd.DataFrame) -> List[float]:
        """安全获取价格列表 - 确保返回List[float]"""
        try:
            # 确保是数值类型并转换为float
            if '收盘' in data.columns:
                prices = data['收盘'].astype(float).tolist()
            elif 'close' in data.columns:
                prices = data['close'].astype(float).tolist()
            else:
                # 尝试使用第一个数值列
                for col in data.columns:
                    if pd.api.types.is_numeric_dtype(data[col]):
                        prices = data[col].astype(float).tolist()
                        break
                else:
                    prices = []
            
            # 过滤掉无效值并确保所有元素都是float
            prices = [float(p) for p in prices if pd.notna(p) and p > 0]
            return prices
            
        except Exception as e:
            logger.error(f"❌ Error getting prices: {e}")
            return []
    
    def _calculate_indicators(self, prices: List[float], data: pd.DataFrame) -> Dict[str, float]:
        """计算技术指标"""
        if len(prices) < 5:
            return {}
        
        try:
            indicators = {
                "ma_5": self._calculate_ma(prices, 5),
                "ma_20": self._calculate_ma(prices, 20),
                "rsi": self._calculate_rsi(prices, 14),
                "macd": self._calculate_macd(prices),
                "price_change": float(prices[-1] - prices[0]) if len(prices) > 1 else 0.0
            }
            
            # 计算布林带
            if len(prices) >= 20:
                bollinger = self._calculate_bollinger(prices, 20)
                indicators.update(bollinger)
            
            return indicators
            
        except Exception as e:
            logger.error(f"❌ Error calculating indicators: {e}")
            return {}
    
    def _calculate_ma(self, prices: List[float], period: int) -> float:
        """计算移动平均线"""
        if len(prices) < period:
            return float(np.mean(prices)) if len(prices) > 0 else 0.0
        return float(np.mean(prices[-period:]))
    
    def _calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """计算RSI指标"""
        if len(prices) < period + 1:
            return 50.0
        
        try:
            # 转换为numpy数组进行计算
            prices_array = np.array(prices, dtype=float)  # 确保是float
            deltas = np.diff(prices_array)
            
            gains = np.where(deltas > 0, deltas, 0.0)
            losses = np.where(deltas < 0, -deltas, 0.0)
            
            # 使用指数移动平均
            avg_gain = self._ema(gains, period)
            avg_loss = self._ema(losses, period)
            
            if avg_loss == 0:
                return 100.0
            
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            return float(rsi)
            
        except Exception as e:
            logger.error(f"❌ RSI calculation error: {e}")
            return 50.0
    
    def _ema(self, values: np.ndarray, period: int) -> float:
        """计算指数移动平均"""
        if len(values) < period:
            return float(np.mean(values)) if len(values) > 0 else 0.0
        
        # 使用pandas的EMA计算
        series = pd.Series(values)
        ema = series.ewm(span=period, adjust=False).mean()
        return float(ema.iloc[-1])
    
    def _calculate_macd(self, prices: List[float]) -> float:
        """计算MACD指标（简化版）"""
        if len(prices) < 26:
            return 0.0
        
        try:
            prices_array = np.array(prices, dtype=float)  # 确保是float
            
            # 计算12日和26日EMA
            ema_12 = self._calculate_ema_series(prices_array, 12)
            ema_26 = self._calculate_ema_series(prices_array, 26)
            
            if len(ema_12) == 0 or len(ema_26) == 0:
                return 0.0
                
            macd_line = ema_12[-1] - ema_26[-1]
            return float(macd_line)
            
        except Exception as e:
            logger.error(f"❌ MACD calculation error: {e}")
            return 0.0
    
    def _calculate_ema_series(self, prices: np.ndarray, period: int) -> np.ndarray:
        """计算EMA序列"""
        if len(prices) < period:
            return np.array([], dtype=float)
        
        ema_values = []
        multiplier = 2.0 / (period + 1.0)  # 确保是float
        ema = float(prices[0])  # 初始值
        
        for price in prices:
            ema = (float(price) - ema) * multiplier + ema
            ema_values.append(ema)
        
        return np.array(ema_values, dtype=float)
    
    def _calculate_bollinger(self, prices: List[float], period: int = 20) -> Dict[str, float]:
        """计算布林带指标"""
        if len(prices) < period:
            return {}
        
        try:
            # 取最近period个价格
            recent_prices = prices[-period:]
            prices_array = np.array(recent_prices, dtype=float)
            
            ma = float(np.mean(prices_array))
            std = float(np.std(prices_array))
            
            return {
                "bollinger_upper": float(ma + 2 * std),
                "bollinger_middle": float(ma),
                "bollinger_lower": float(ma - 2 * std)
            }
        except Exception as e:
            logger.error(f"❌ Bollinger calculation error: {e}")
            return {}
    
    def _determine_trend(self, indicators: Dict[str, float], prices: List[float], data: pd.DataFrame) -> int:
        """判断趋势类型"""
        if not indicators or not prices:
            return 2  # 默认震荡
        
        try:
            current_price = float(prices[-1])
            ma_5 = indicators.get("ma_5", 0.0)
            ma_20 = indicators.get("ma_20", 0.0)
            rsi = indicators.get("rsi", 50.0)
            macd = indicators.get("macd", 0.0)
            
            # 趋势判断逻辑
            bullish_signals = 0
            bearish_signals = 0
            
            # 均线判断
            if current_price > ma_5 > ma_20:
                bullish_signals += 1
            elif current_price < ma_5 < ma_20:
                bearish_signals += 1
            
            # RSI判断
            if rsi > 60.0:
                bullish_signals += 1
            elif rsi < 40.0:
                bearish_signals += 1
            
            # MACD判断
            if macd > 0.0:
                bullish_signals += 1
            elif macd < 0.0:
                bearish_signals += 1
            
            # 综合判断
            if bullish_signals >= 2 and bearish_signals == 0:
                return 1  # 上涨趋势
            elif bearish_signals >= 2 and bullish_signals == 0:
                return 3  # 下跌趋势
            else:
                return 2  # 震荡趋势
                
        except Exception as e:
            logger.error(f"❌ Trend determination error: {e}")
            return 2
    
    def _generate_suggestion(self, trend: int, indicators: Dict[str, float], prices: List[float]) -> str:
        """生成交易建议"""
        if not indicators or not prices:
            return "hold"
        
        try:
            rsi = indicators.get("rsi", 50.0)
            current_price = float(prices[-1])
            
            if trend == 1:  # 上涨趋势
                if rsi < 70.0:  # 未超买
                    return "buy"
                else:
                    return "hold"
            elif trend == 3:  # 下跌趋势
                if rsi > 30.0:  # 未超卖
                    return "sell"
                else:
                    return "hold"
            else:  # 震荡趋势
                return "hold"
                
        except Exception as e:
            logger.error(f"❌ Suggestion generation error: {e}")
            return "hold"
    
    def _calculate_confidence(self, indicators: Dict[str, float], trend: int) -> float:
        """计算置信度"""
        if not indicators:
            return 0.0
        
        try:
            rsi = indicators.get("rsi", 50.0)
            macd = indicators.get("macd", 0.0)
            
            confidence_factors = []
            
            # RSI置信度
            if trend == 1 and rsi > 60.0:
                confidence_factors.append(0.8)
            elif trend == 3 and rsi < 40.0:
                confidence_factors.append(0.8)
            else:
                confidence_factors.append(0.3)
            
            # MACD置信度
            if (trend == 1 and macd > 0.0) or (trend == 3 and macd < 0.0):
                confidence_factors.append(0.7)
            else:
                confidence_factors.append(0.2)
            
            # 均线排列置信度
            ma_5 = indicators.get("ma_5", 0.0)
            ma_20 = indicators.get("ma_20", 0.0)
            if (trend == 1 and ma_5 > ma_20) or (trend == 3 and ma_5 < ma_20):
                confidence_factors.append(0.6)
            
            return float(np.mean(confidence_factors)) if confidence_factors else 0.0
            
        except Exception as e:
            logger.error(f"❌ Confidence calculation error: {e}")
            return 0.0

# 全局分析器实例
technical_analyzer = TechnicalAnalyzer()

def safe_convert_to_float_list(data: Union[pd.Series, List, np.ndarray, Sequence]) -> List[float]:
    """安全转换为浮点数列表 - 确保返回List[float]"""
    try:
        if isinstance(data, pd.Series):
            # 使用astype(float)确保所有元素都是float
            return data.astype(float).dropna().tolist()
        elif isinstance(data, (list, np.ndarray, Sequence)):
            # 使用float()转换每个元素
            return [float(x) for x in data if pd.notna(x) and x is not None]
        else:
            return []
    except (ValueError, TypeError) as e:
        logger.error(f"❌ 类型转换失败: {e}")
        return []

def ensure_float(value: Union[int, float, str]) -> float:
    """确保值为float类型"""
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0

technical_analyzer = TechnicalAnalyzer()