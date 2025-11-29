#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean, DECIMAL, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class InputData(Base):
    """期货市场数据表"""
    __tablename__ = "futures_data"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(50), nullable=False)                      # 品种名称
    symbol_code = Column(String(20), default="")               # 品种代码(RB, I, JM等)
    trade_date = Column(DateTime, nullable=False)                  # 交易日期
    open_price = Column(DECIMAL(15, 4), nullable=False)            # 开盘价
    high_price = Column(DECIMAL(15, 4), nullable=False)           # 最高价
    low_price = Column(DECIMAL(15, 4), nullable=False)             # 最低价
    close_price = Column(DECIMAL(15, 4), nullable=False)          # 收盘价
    change_amount = Column(DECIMAL(15, 4))                         # 涨跌额
    change_percent = Column(DECIMAL(8, 4))                          # 涨跌幅(%)
    volume = Column(BigInteger)                                     # 成交量
    turnover = Column(DECIMAL(20, 4))                              # 成交额
    open_interest = Column(BigInteger)                             # 持仓量
    
    # 系统字段
    data_source = Column(String(100), default="akshare")
    status = Column(String(20), default="pending")                 # pending/processing/processed/error
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class FuturnsIndex(Base):
    """期货综合指数表"""
    __tablename__ = "futures_index"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(50), nullable=False)                      # 品种名称
    index_date = Column(DateTime, nullable=False)                    # 指数日期
    index_name = Column(String(100), nullable=False)                 # 指数名称
    index_value = Column(DECIMAL(15, 4), nullable=False)            # 指数值
    
    # 系统字段
    data_source = Column(String(100), default="calculated")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AnalysisResult(Base):
    """分析结果表"""
    __tablename__ = "analysis_results"
    
    id = Column(Integer, primary_key=True, index=True)
    futures_data_id = Column(Integer, nullable=False)              # 关联的期货数据ID
    symbol = Column(String(50), nullable=False)                    # 品种名称
    symbol_code = Column(String(20), nullable=False)                # 品种代码
    
    # 分析结果
    trend_type = Column(Integer, nullable=False)                    # 趋势类型 1:上涨, 2:震荡, 3:下跌
    suggestion = Column(String(20), nullable=False)                # 建议: buy/sell/hold
    signal_strength = Column(DECIMAL(5, 4), default=0.0)           # 信号强度 0-1
    
    # 交易建议
    entry_price = Column(DECIMAL(15, 4))                            # 建议入场价
    target_price = Column(DECIMAL(15, 4))                          # 目标价(止盈)
    stop_loss_price = Column(DECIMAL(15, 4))                       # 止损价
    risk_reward_ratio = Column(DECIMAL(8, 4))                      # 风险收益比
    
    # 技术指标
    ma_5 = Column(DECIMAL(15, 4))                                  # 5日均线
    ma_20 = Column(DECIMAL(15, 4))                                 # 20日均线
    rsi = Column(DECIMAL(8, 4))                                    # RSI指标
    macd = Column(DECIMAL(15, 4))                                 # MACD值
    bollinger_upper = Column(DECIMAL(15, 4))                        # 布林线上轨
    bollinger_lower = Column(DECIMAL(15, 4))                       # 布林线下轨
    
    # 系统字段
    confidence_score = Column(DECIMAL(5, 4), default=0.0)         # 置信度
    analysis_method = Column(String(50), default="technical")      # 分析方法
    risk_level = Column(String(20), default="medium")              # 风险等级
    is_success = Column(Boolean, default=True)                     # 分析是否成功
    error_message = Column(Text)                                   # 错误信息
    analysis_time = Column(DECIMAL(10, 4))                         # 分析耗时(秒)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class TechnicalIndicator(Base):
    """交易信号表"""
    __tablename__ = "trading_signals"
    
    id = Column(Integer, primary_key=True, index=True)
    analysis_result_id = Column(Integer, nullable=False)            # 关联的分析结果ID
    symbol = Column(String(50), nullable=False)                    # 品种名称
    signal_type = Column(String(20), nullable=False)               # 信号类型: buy/sell
    signal_time = Column(DateTime, nullable=False)                # 信号时间
    price = Column(DECIMAL(15, 4), nullable=False)                # 信号价格
    strength = Column(DECIMAL(5, 4), default=0.0)                 # 信号强度
    is_active = Column(Boolean, default=True)                      # 信号是否有效
    expired_at = Column(DateTime)                                 # 信号过期时间
    created_at = Column(DateTime(timezone=True), server_default=func.now())