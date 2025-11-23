#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from dataclasses import dataclass
from typing import List

@dataclass
class DatabaseConfig:
    """数据库配置"""
    host: str = os.getenv("PG_HOST", "localhost")
    port: int = int(os.getenv("PG_PORT", "5432"))
    user: str = os.getenv("PG_USER", "postgres")
    password: str = os.getenv("PG_PASSWORD", "ying11233")
    database: str = os.getenv("PG_DATABASE", "analysis_system")
    pool_size: int = 10
    max_overflow: int = 20
    echo_sql: bool = False
    
    @property
    def database_url(self):
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"

@dataclass
class AkshareConfig:
    """akshare配置"""
    rate_limit_delay: float = 1.0  # API调用间隔(秒)
    default_days: int = 30         # 默认获取天数
    supported_symbols: List[str] = None # type: ignore
    
    def __post_init__(self):
        if self.supported_symbols is None:
            self.supported_symbols = [
                "螺纹钢主连", "铁矿石主连", "焦煤主连", "焦炭主连",
                "甲醇主连", "PTA主连", "豆粕主连", "豆油主连",
                "棕榈油主连", "白糖主连", "棉花主连", "沪铜主连",
                "沪铝主连", "黄金主连", "原油主连"
            ]

@dataclass
class AnalysisConfig:
    """分析配置"""
    batch_size: int = 10
    max_workers: int = 4
    timeout: int = 30
    min_confidence: float = 0.7

@dataclass
class TradingConfig:
    """交易配置"""
    stop_loss_percent: float = 0.02  # 止损比例 2%
    take_profit_percent: float = 0.05  # 止盈比例 5%
    risk_level: str = "medium"  # 风险等级

class Config:
    def __init__(self):
        self.database = DatabaseConfig()
        self.akshare = AkshareConfig()
        self.analysis = AnalysisConfig()
        self.trading = TradingConfig()

config = Config()