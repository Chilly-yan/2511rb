#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
from src.config.settings import config

logger = logging.getLogger(__name__)

class DatabaseManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """初始化数据库连接"""
        try:
            # 创建数据库引擎
            self.engine = create_engine(
                config.database.database_url,
                poolclass=QueuePool,
                pool_size=config.database.pool_size,
                max_overflow=config.database.max_overflow,
                echo=config.database.echo_sql,
                future=True  # 使用 SQLAlchemy 2.0 风格
            )
            
            # 创建会话工厂
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            # 测试连接
            self._test_connection()
            
            logger.info("✅ PostgreSQL数据库连接成功")
            
        except Exception as e:
            logger.error(f"❌ 数据库连接失败: {e}")
            raise
    
    def _test_connection(self):
        """测试数据库连接"""
        try:
            with self.engine.connect() as conn:
                # 使用 text() 包装 SQL 语句
                conn.execute(text("SELECT 1"))
        except Exception as e:
            logger.error(f"❌ 数据库连接测试失败: {e}")
            raise
    
    @contextmanager
    def get_session(self):
        """获取数据库会话（上下文管理器）"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"❌ 数据库操作失败: {e}")
            raise
        finally:
            session.close()
    
    def create_tables(self):
        """创建数据表"""
        from src.models.data_models import Base
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("✅ 数据表创建成功")
        except Exception as e:
            logger.error(f"❌ 数据表创建失败: {e}")
            raise
    
    def drop_tables(self):
        """删除所有表（仅用于测试）"""
        from src.models.data_models import Base
        try:
            Base.metadata.drop_all(bind=self.engine)
            logger.warning("⚠️ 所有数据表已删除")
        except Exception as e:
            logger.error(f"❌ 删除表失败: {e}")
            raise
    
    def get_table_stats(self):
        """获取表统计信息"""
        stats_sql = text("""
        SELECT 
            table_name,
            table_type,
            row_estimate,
            total_size
        FROM (
            SELECT 
                table_name,
                table_type,
                n_live_tup as row_estimate,
                pg_total_relation_size(quote_ident(table_name)) as total_size
            FROM information_schema.tables t
            LEFT JOIN pg_stat_user_tables s ON s.relname = t.table_name
            WHERE t.table_schema = 'public'
        ) stats
        ORDER BY total_size DESC;
        """)
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(stats_sql)
                return [dict(row._mapping) for row in result]
        except Exception as e:
            logger.error(f"❌ 获取表统计失败: {e}")
            return []
    
    def close(self):
        """关闭数据库连接"""
        if hasattr(self, 'engine'):
            self.engine.dispose()
            logger.info("✅ 数据库连接已关闭")

# 全局数据库管理器实例
db_manager = DatabaseManager()