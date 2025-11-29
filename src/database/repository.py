#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_, func, text
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging
from src.models.data_models import InputData, AnalysisResult, TechnicalIndicator

logger = logging.getLogger(__name__)

class BaseRepository:
    """基础仓库类"""
    def __init__(self, db: Session):
        self.db = db

class FuturesDataRepository(BaseRepository):
    """期货数据仓库"""
    
    def create_market_data(self, symbol: str, trade_time: datetime, 
                         open_price: float, high_price: float, low_price: float, 
                         close_price: float, change_amount: Optional[float] = None,
                         change_percent: Optional[float] = None, volume: Optional[int] = None,
                         turnover: Optional[float] = None, open_interest: Optional[int] = None,
                         data_source: str = "akshare") -> InputData:
        """创建市场数据记录"""
        try:
            # 检查是否已存在相同时间的数据
            existing = self.db.query(InputData).filter(
                InputData.symbol == symbol,
                InputData.trade_date == trade_time
            ).first()
            
            if existing:
                logger.warning(f"⚠️ 数据已存在: {symbol} at {trade_time}")
                return existing
            
            # 自动生成symbol_code（取symbol的前2个字符大写）
            symbol_code = symbol[:2].upper() if symbol and len(symbol) >= 2 else symbol
            
            market_data = InputData(
                symbol=symbol,
                symbol_code=symbol_code,  # 自动生成
                trade_date=trade_time,
                open_price=open_price,
                high_price=high_price,
                low_price=low_price,
                close_price=close_price,
                change_amount=change_amount,
                change_percent=change_percent,
                volume=volume,
                turnover=turnover,
                open_interest=open_interest,
                data_source=data_source,
                status="pending"
            )
            
            self.db.add(market_data)
            self.db.flush()
            logger.info(f"✅ 市场数据创建成功: {symbol} at {trade_time}")
            return market_data
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ 创建市场数据失败: {e}")
            raise
    
    def batch_create_market_data(self, data_list: List[Dict]) -> Dict[str, Any]:
        """批量创建市场数据"""
        results = {
            'success': 0, 
            'failed': 0, 
            'ids': [],
            'errors': []
        }
        
        for data in data_list:
            try:
                # 检查必填字段
                required_fields = ['symbol', 'trade_time', 'open_price', 'high_price', 
                                 'low_price', 'close_price']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    error_msg = f"缺少必填字段: {missing_fields}"
                    results['failed'] += 1
                    results['errors'].append({'data': data, 'error': error_msg})
                    continue
                
                # 移除不需要的字段（如symbol_code）
                clean_data = {k: v for k, v in data.items() if k not in ['symbol_code']}
                
                # 创建数据记录
                market_data = self.create_market_data(**clean_data)
                results['success'] += 1
                results['ids'].append(market_data.id)
                
            except Exception as e:
                results['failed'] += 1
                results['errors'].append({'data': data, 'error': str(e)})
                logger.error(f"❌ 批量创建数据失败: {e}")
        
        logger.info(f"📦 批量创建完成: 成功 {results['success']}, 失败 {results['failed']}")
        return results

    
    def get_pending_data(self, limit: int = 10) -> List[InputData]:
        """获取待处理数据"""
        return self.db.query(InputData)\
            .filter(InputData.status == "pending")\
            .order_by(InputData.trade_date.asc())\
            .limit(limit)\
            .all()
    
    def get_symbol_data(self, symbol: str, days: int = 30) -> List[InputData]:
        """获取某品种的历史数据"""
        start_date = datetime.now() - timedelta(days=days)
        
        return self.db.query(InputData)\
            .filter(InputData.symbol == symbol)\
            .filter(InputData.trade_date >= start_date)\
            .order_by(InputData.trade_date.asc())\
            .all()
    
    def get_latest_data(self, symbol: str, limit: int = 1):
        """获取某品种的最新数据"""
        sql_result = self.db.query(InputData)\
            .filter(InputData.symbol == symbol)\
            .order_by(InputData.trade_date.desc())\
            .limit(limit)\
            .first()
        
        if sql_result:
            sql_data = {k:v for k,v in sql_result.__dict__.items() if k != '_sa_instance_state'}
        else:
            sql_data = None
        return sql_data
    
    def update_status(self, data_id: int, status: str) -> bool:
        """更新数据状态"""
        try:
            self.db.query(InputData)\
                .filter(InputData.id == data_id)\
                .update({"status": status})
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ 更新状态失败: {e}")
            return False
    
    def get_market_stats(self) -> Dict[str, Any]:
        """获取市场数据统计"""
        stats = self.db.query(
            InputData.symbol,
            func.count(InputData.id).label('count'),
            func.max(InputData.trade_date).label('latest_time'),
            func.avg(InputData.close_price).label('avg_price')
        ).group_by(InputData.symbol).all()
        
        return {
            'total_count': self.db.query(InputData).count(),
            'symbols_count': len(stats),
            'by_symbol': {
                symbol: {
                    'count': count,
                    'latest_time': latest_time,
                    'avg_price': float(avg_price) if avg_price else 0
                }
                for symbol, count, latest_time, avg_price in stats
            }
        }


class AnalysisResultRepository(BaseRepository):
    """分析结果仓库 - 负责AnalysisResult实体的数据库操作"""
    
    def create_analysis_result(self, input_data_id: int, symbol: str, trend_type: int,
                            suggestion: str, buy_price: Optional[float] = None,
                            target_price: Optional[float] = None, 
                            stop_loss_price: Optional[float] = None,
                            confidence_score: float = 0.0, analysis_method: str = "technical",
                            risk_level: str = "medium", analysis_time_seconds: float = 0.0,
                            is_success: bool = True, error_message: Optional[str] = None) -> AnalysisResult:
        """创建分析结果记录"""
        try:
            result = AnalysisResult(
                input_data_id=input_data_id,
                symbol=symbol,
                trend_type=trend_type,
                suggestion=suggestion,
                buy_price=buy_price,
                target_price=target_price,
                stop_loss_price=stop_loss_price,
                confidence_score=confidence_score,
                analysis_method=analysis_method,
                risk_level=risk_level,
                analysis_time_seconds=analysis_time_seconds,
                is_success=is_success,
                error_message=error_message
            )
            
            self.db.add(result)
            self.db.flush()
            logger.info(f"✅ 分析结果创建成功: {symbol} 趋势{trend_type}")
            return result
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ 创建分析结果失败: {e}")
            raise
    
    def get_recent_results(self, symbol: Optional[str] = None, 
                          limit: int = 10) -> List[AnalysisResult]:
        """获取最近的分析结果"""
        try:
            query = self.db.query(AnalysisResult)\
                .filter(AnalysisResult.is_success == True)\
                .order_by(AnalysisResult.created_at.desc())
            
            if symbol:
                query = query.filter(AnalysisResult.symbol == symbol)
            
            return query.limit(limit).all()
            
        except Exception as e:
            logger.error(f"❌ 获取最近结果失败: {e}")
            return []
    
    def get_buy_suggestions(self, min_confidence: float = 0.7, 
                           days: int = 7) -> List[AnalysisResult]:
        """获取买入建议"""
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            return self.db.query(AnalysisResult)\
                .filter(AnalysisResult.suggestion == "buy")\
                .filter(AnalysisResult.confidence_score >= min_confidence)\
                .filter(AnalysisResult.created_at >= start_date)\
                .filter(AnalysisResult.is_success == True)\
                .order_by(AnalysisResult.confidence_score.desc())\
                .all()
                
        except Exception as e:
            logger.error(f"❌ 获取买入建议失败: {e}")
            return []
    
    def get_sell_suggestions(self, min_confidence: float = 0.7, 
                            days: int = 7) -> List[AnalysisResult]:
        """获取卖出建议"""
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            return self.db.query(AnalysisResult)\
                .filter(AnalysisResult.suggestion == "sell")\
                .filter(AnalysisResult.confidence_score >= min_confidence)\
                .filter(AnalysisResult.created_at >= start_date)\
                .filter(AnalysisResult.is_success == True)\
                .order_by(AnalysisResult.confidence_score.desc())\
                .all()
                
        except Exception as e:
            logger.error(f"❌ 获取卖出建议失败: {e}")
            return []
    
    def get_hold_suggestions(self, min_confidence: float = 0.7, 
                            days: int = 7) -> List[AnalysisResult]:
        """获取持有建议"""
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            return self.db.query(AnalysisResult)\
                .filter(AnalysisResult.suggestion == "hold")\
                .filter(AnalysisResult.confidence_score >= min_confidence)\
                .filter(AnalysisResult.created_at >= start_date)\
                .filter(AnalysisResult.is_success == True)\
                .order_by(AnalysisResult.confidence_score.desc())\
                .all()
                
        except Exception as e:
            logger.error(f"❌ 获取持有建议失败: {e}")
            return []
    
    def get_high_confidence_results(self, min_confidence: float = 0.8, 
                                   days: int = 30) -> List[AnalysisResult]:
        """获取高置信度结果"""
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            return self.db.query(AnalysisResult)\
                .filter(AnalysisResult.confidence_score >= min_confidence)\
                .filter(AnalysisResult.created_at >= start_date)\
                .filter(AnalysisResult.is_success == True)\
                .order_by(AnalysisResult.confidence_score.desc())\
                .all()
                
        except Exception as e:
            logger.error(f"❌ 获取高置信度结果失败: {e}")
            return []
    
    def get_results_by_trend_type(self, trend_type: int, 
                                 days: int = 30) -> List[AnalysisResult]:
        """按趋势类型获取结果"""
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            return self.db.query(AnalysisResult)\
                .filter(AnalysisResult.trend_type == trend_type)\
                .filter(AnalysisResult.created_at >= start_date)\
                .filter(AnalysisResult.is_success == True)\
                .order_by(AnalysisResult.created_at.desc())\
                .all()
                
        except Exception as e:
            logger.error(f"❌ 按趋势类型获取结果失败: {e}")
            return []
    
    def get_results_by_date_range(self, symbol: str, start_date: datetime, 
                                 end_date: datetime) -> List[AnalysisResult]:
        """按日期范围获取结果"""
        try:
            return self.db.query(AnalysisResult)\
                .filter(AnalysisResult.symbol == symbol)\
                .filter(AnalysisResult.created_at >= start_date)\
                .filter(AnalysisResult.created_at <= end_date)\
                .filter(AnalysisResult.is_success == True)\
                .order_by(AnalysisResult.created_at.asc())\
                .all()
        except Exception as e:
            logger.error(f"❌ 按日期范围查询失败: {e}")
            return []
    
    def get_results_by_confidence_range(self, min_confidence: float, 
                                       max_confidence: float) -> List[AnalysisResult]:
        """按置信度范围获取结果"""
        try:
            return self.db.query(AnalysisResult)\
                .filter(AnalysisResult.confidence_score >= min_confidence)\
                .filter(AnalysisResult.confidence_score <= max_confidence)\
                .filter(AnalysisResult.is_success == True)\
                .order_by(AnalysisResult.confidence_score.desc())\
                .all()
        except Exception as e:
            logger.error(f"❌ 按置信度范围查询失败: {e}")
            return []
    
    def get_analysis_stats(self) -> Dict[str, Any]:
        """获取分析结果统计"""
        try:
            # 总体统计
            total_count = self.db.query(AnalysisResult).count()
            success_count = self.db.query(AnalysisResult)\
                .filter(AnalysisResult.is_success == True).count()
            
            # 按建议类型统计
            suggestion_stats = self.db.query(
                AnalysisResult.suggestion,
                func.count(AnalysisResult.id).label('count'),
                func.avg(AnalysisResult.confidence_score).label('avg_confidence')
            ).filter(AnalysisResult.is_success == True)\
             .group_by(AnalysisResult.suggestion).all()
            
            # 按趋势类型统计
            trend_stats = self.db.query(
                AnalysisResult.trend_type,
                func.count(AnalysisResult.id).label('count')
            ).filter(AnalysisResult.is_success == True)\
             .group_by(AnalysisResult.trend_type).all()
            
            # 按风险等级统计
            risk_stats = self.db.query(
                AnalysisResult.risk_level,
                func.count(AnalysisResult.id).label('count')
            ).filter(AnalysisResult.is_success == True)\
             .group_by(AnalysisResult.risk_level).all()
            
            # 按分析方法统计
            method_stats = self.db.query(
                AnalysisResult.analysis_method,
                func.count(AnalysisResult.id).label('count')
            ).filter(AnalysisResult.is_success == True)\
             .group_by(AnalysisResult.analysis_method).all()
            
            # 获取平均值
            avg_confidence_result = self.db.query(
                func.avg(AnalysisResult.confidence_score)
            ).filter(AnalysisResult.is_success == True).scalar()
            
            # 获取最新分析时间
            latest_analysis = self.db.query(
                func.max(AnalysisResult.created_at)
            ).filter(AnalysisResult.is_success == True).scalar()
            
            # 构建结果 - 使用安全转换
            result = {
                'total_count': total_count,
                'success_count': success_count,
                'success_rate': success_count / total_count if total_count > 0 else 0,
                'by_suggestion': {
                    suggestion: {
                        'count': count,
                        'avg_confidence': self._safe_convert_to_float(avg_conf)
                    }
                    for suggestion, count, avg_conf in suggestion_stats
                },
                'by_trend_type': {
                    trend_type: count
                    for trend_type, count in trend_stats
                },
                'by_risk_level': {
                    risk_level: count
                    for risk_level, count in risk_stats
                },
                'by_analysis_method': {
                    method: count
                    for method, count in method_stats
                },
                'avg_confidence': self._safe_convert_to_float(avg_confidence_result),
                'latest_analysis': latest_analysis
            }
            
            return result
            
        except Exception as e:
            logger.error(f"❌ 获取分析统计失败: {e}")
            return {}
    
    def get_symbol_performance(self, symbol: str, days: int = 30) -> Dict[str, Any]:
        """获取品种表现分析"""
        start_date = datetime.now() - timedelta(days=days)
        
        try:
            # 获取该品种的分析结果
            results = self.db.query(AnalysisResult)\
                .filter(AnalysisResult.symbol == symbol)\
                .filter(AnalysisResult.created_at >= start_date)\
                .filter(AnalysisResult.is_success == True)\
                .all()
            
            if not results:
                return {'error': f'没有找到 {symbol} 的分析数据'}
            
            total_signals = len(results)
            
            # 计算平均置信度 - 使用安全方法
            total_confidence = 0.0
            for result in results:
                confidence = self._get_confidence_safe(result)
                total_confidence += confidence
            
            avg_confidence = total_confidence / total_signals if total_signals > 0 else 0
            
            # 按建议类型统计 - 修复字符串比较问题
            buy_signals = []
            sell_signals = []
            hold_signals = []
            
            for result in results:
                # 使用安全的方法获取建议类型
                suggestion = self._get_suggestion_safe(result)
                if suggestion == "buy":
                    buy_signals.append(result)
                elif suggestion == "sell":
                    sell_signals.append(result)
                elif suggestion == "hold":
                    hold_signals.append(result)
            
            # 按趋势类型统计
            trend_counts = {}
            for result in results:
                trend = result.trend_type
                if trend not in trend_counts:
                    trend_counts[trend] = 0
                trend_counts[trend] += 1
            
            # 获取最新信号
            latest_signal = None
            if results:
                latest = results[0]
                latest_signal = {
                    'suggestion': self._get_suggestion_safe(latest),
                    'confidence': self._get_confidence_safe(latest),
                    'trend': latest.trend_type,
                    'time': latest.created_at.strftime('%Y-%m-%d %H:%M:%S')
                }
            
            return {
                'symbol': symbol,
                'period_days': days,
                'total_signals': total_signals,
                'avg_confidence': round(avg_confidence, 4),
                'by_suggestion': {
                    'buy': len(buy_signals),
                    'sell': len(sell_signals),
                    'hold': len(hold_signals)
                },
                'by_trend_type': trend_counts,
                'latest_signal': latest_signal
            }
            
        except Exception as e:
            logger.error(f"❌ 获取品种表现失败: {symbol}, {e}")
            return {'error': str(e)}
    
    def get_daily_summary(self, date: Optional[datetime] = None) -> Dict[str, Any]:
        """获取每日汇总统计 - 修复None类型问题"""
        # 处理None值
        if date is None:
            date = datetime.now()
        
        start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=1)
        
        try:
            # 当日分析结果
            daily_results = self.db.query(AnalysisResult)\
                .filter(AnalysisResult.created_at >= start_date)\
                .filter(AnalysisResult.created_at < end_date)\
                .filter(AnalysisResult.is_success == True)\
                .all()
            
            total_daily = len(daily_results)
            
            if total_daily == 0:
                return {
                    'date': start_date.strftime('%Y-%m-%d'),
                    'total_signals': 0,
                    'message': '当日无分析结果'
                }
            
            # 统计 - 使用安全方法
            buy_count = 0
            sell_count = 0
            hold_count = 0
            high_confidence_count = 0
            total_confidence = 0.0
            
            for result in daily_results:
                # 使用安全的方法获取建议类型
                suggestion = self._get_suggestion_safe(result)
                if suggestion == "buy":
                    buy_count += 1
                elif suggestion == "sell":
                    sell_count += 1
                elif suggestion == "hold":
                    hold_count += 1
                
                # 使用安全方法获取置信度
                confidence = self._get_confidence_safe(result)
                if confidence > 0.8:
                    high_confidence_count += 1
                
                total_confidence += confidence
            
            avg_confidence = total_confidence / total_daily if total_daily > 0 else 0
            
            # 最活跃的品种
            symbol_counts = {}
            for result in daily_results:
                symbol = result.symbol
                if symbol not in symbol_counts:
                    symbol_counts[symbol] = 0
                symbol_counts[symbol] += 1
            
            most_active_symbol = ('N/A', 0)
            if symbol_counts:
                most_active_symbol = max(symbol_counts.items(), key=lambda x: x[1])
            
            return {
                'date': start_date.strftime('%Y-%m-%d'),
                'total_signals': total_daily,
                'buy_signals': buy_count,
                'sell_signals': sell_count,
                'hold_signals': hold_count,
                'high_confidence_signals': high_confidence_count,
                'avg_confidence': round(avg_confidence, 4),
                'most_active_symbol': {
                    'symbol': most_active_symbol[0],
                    'signal_count': most_active_symbol[1]
                },
                'symbols_analyzed': len(symbol_counts)
            }
            
        except Exception as e:
            logger.error(f"❌ 获取每日汇总失败: {e}")
            return {'error': str(e)}
    
    def _get_suggestion_safe(self, result: AnalysisResult) -> str:
        """安全获取建议类型 - 修复ColumnElement问题"""
        try:
            # 方法1：直接访问属性
            if hasattr(result, 'suggestion'):
                suggestion_value = result.suggestion
                if suggestion_value is not None:
                    # 确保返回字符串
                    return str(suggestion_value)
            
            return "hold"  # 默认值
            
        except (TypeError, ValueError, AttributeError) as e:
            logger.warning(f"⚠️ 建议类型获取失败: {e}, 使用默认值'hold'")
            return "hold"
    
    def _get_confidence_safe(self, result: AnalysisResult) -> float:
        """安全获取置信度值 - 修复Column[Unknown]问题"""
        try:
            # 方法1：直接访问属性，避免使用float()包装
            if hasattr(result, 'confidence_score'):
                confidence_value = result.confidence_score
                if confidence_value is not None:
                    # 使用类型检查而不是直接float()
                    if isinstance(confidence_value, (int, float)):
                        return float(confidence_value)
                    else:
                        # 如果是字符串或其他类型，尝试转换
                        return float(str(confidence_value))
            
            return 0.0
            
        except (TypeError, ValueError, AttributeError) as e:
            logger.warning(f"⚠️ 置信度转换失败: {e}, 使用默认值0.0")
            return 0.0
    
    def _safe_convert_to_float(self, value: Any, default: float = 0.0) -> float:
        """安全转换为float - 修复Column[Unknown]问题"""
        try:
            if value is None:
                return default
            
            # 检查类型
            if isinstance(value, (int, float)):
                return float(value)
            elif isinstance(value, str):
                # 字符串转换
                return float(value)
            else:
                # 其他类型先转字符串再转float
                return float(str(value))
                
        except (TypeError, ValueError) as e:
            logger.warning(f"⚠️ 数值转换失败: {value}, 使用默认值{default}")
            return default
    
    def update_result_status(self, result_id: int, is_success: bool, 
                           error_message: Optional[str] = None) -> bool:
        """更新分析结果状态"""
        try:
            self.db.query(AnalysisResult)\
                .filter(AnalysisResult.id == result_id)\
                .update({
                    'is_success': is_success,
                    'error_message': error_message
                })
            self.db.commit()
            logger.info(f"✅ 更新结果状态成功: ID={result_id}, 成功={is_success}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ 更新结果状态失败: {e}")
            return False
    
    def delete_old_results(self, days: int = 365) -> int:
        """删除旧的分析结果（数据清理）"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            deleted_count = self.db.query(AnalysisResult)\
                .filter(AnalysisResult.created_at < cutoff_date)\
                .delete()
            self.db.commit()
            logger.info(f"✅ 删除 {deleted_count} 条旧分析结果")
            return deleted_count
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ 删除旧结果失败: {e}")
            return 0
    
    def get_result_by_id(self, result_id: int) -> Optional[AnalysisResult]:
        """根据ID获取分析结果"""
        try:
            return self.db.query(AnalysisResult)\
                .filter(AnalysisResult.id == result_id)\
                .first()
        except Exception as e:
            logger.error(f"❌ 根据ID获取结果失败: {e}")
            return None
    
    def get_results_by_input_data_id(self, input_data_id: int) -> List[AnalysisResult]:
        """根据输入数据ID获取分析结果"""
        try:
            return self.db.query(AnalysisResult)\
                .filter(AnalysisResult.input_data_id == input_data_id)\
                .order_by(AnalysisResult.created_at.desc())\
                .all()
        except Exception as e:
            logger.error(f"❌ 根据输入数据ID获取结果失败: {e}")
            return []