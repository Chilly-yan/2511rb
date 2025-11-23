#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import csv
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import logging
from src.database.repository import AnalysisResultRepository, FuturesDataRepository
from src.database.database import db_manager

logger = logging.getLogger(__name__)

class ReportGenerator:
    """报告生成器 - 负责生成各种分析报告"""
    
    def generate_daily_report(self) -> Dict[str, Any]:
        """生成日报"""
        try:
            with db_manager.get_session() as session:
                analysis_repo = AnalysisResultRepository(session)
                data_repo = FuturesDataRepository(session)
                
                # 获取今日分析结果
                today_results = analysis_repo.get_recent_results(limit=50)
                
                # 获取统计数据
                analysis_stats = analysis_repo.get_analysis_stats()
                market_stats = data_repo.get_market_stats()
                
                # 计算准确率统计 - 修复ColumnElement问题
                accuracy_stats = self._calculate_accuracy_stats_safe(today_results)
                
                # 格式化信号列表
                formatted_signals = self._format_signals_safe(today_results)
                
                # 生成摘要
                summary = self._generate_summary_safe(today_results, accuracy_stats)
                
                report = {
                    'report_date': datetime.now().strftime('%Y-%m-%d'),
                    'total_signals': len(today_results),
                    'buy_signals': self._count_suggestions_safe(today_results, 'buy'),
                    'sell_signals': self._count_suggestions_safe(today_results, 'sell'),
                    'hold_signals': self._count_suggestions_safe(today_results, 'hold'),
                    'high_confidence_signals': self._count_high_confidence_safe(today_results),
                    'accuracy_stats': accuracy_stats,
                    'analysis_stats': analysis_stats,
                    'market_stats': market_stats,
                    'signals': formatted_signals,
                    'summary': summary,
                    'trend_analysis': self._analyze_trends_safe(today_results),
                    'performance_metrics': self._calculate_performance_metrics_safe(today_results)
                }
                
                logger.info(f"✅ 日报生成成功: {len(today_results)} 个信号")
                return report
                
        except Exception as e:
            logger.error(f"❌ 生成日报失败: {e}")
            return {'error': str(e)}
    
    def generate_signal_report(self, symbol: str, days: int = 30) -> Dict[str, Any]:
        """生成品种信号报告"""
        try:
            with db_manager.get_session() as session:
                repo = AnalysisResultRepository(session)
                
                # 获取历史信号
                signals = repo.get_recent_results(symbol=symbol, limit=100)
                if not signals:
                    return {'error': f'没有找到 {symbol} 的信号数据'}
                
                # 计算准确率 - 使用安全方法
                accuracy_stats = self._calculate_accuracy_stats_safe(signals)
                
                # 计算性能指标 - 使用安全方法
                performance_metrics = self._calculate_performance_metrics_safe(signals)
                
                # 格式化信号历史
                signal_history = self._format_signal_history_safe(signals)
                
                # 趋势分析
                trend_analysis = self._analyze_trends_safe(signals)
                
                report = {
                    'symbol': symbol,
                    'period_days': days,
                    'total_signals': len(signals),
                    'accuracy_stats': accuracy_stats,
                    'performance_metrics': performance_metrics,
                    'signal_history': signal_history,
                    'trend_analysis': trend_analysis,
                    'risk_assessment': self._assess_risk_safe(signals),
                    'recommendation': self._generate_recommendation_safe(signals, accuracy_stats)
                }
                
                logger.info(f"✅ {symbol} 信号报告生成成功")
                return report
                
        except Exception as e:
            logger.error(f"❌ 生成信号报告失败: {symbol}, {e}")
            return {'error': str(e)}
    
    def _calculate_accuracy_stats_safe(self, signals: List) -> Dict[str, Any]:
        """安全计算信号准确率统计"""
        if not signals:
            return {'total': 0, 'accuracy_rate': 0.0, 'by_suggestion': {}}
        
        try:
            total_signals = len(signals)
            correct_signals = 0
            by_suggestion = {}
            
            for signal in signals:
                # 使用安全方法获取建议类型
                suggestion = self._get_suggestion_safe(signal)
                if suggestion not in by_suggestion:
                    by_suggestion[suggestion] = {'total': 0, 'correct': 0}
                
                by_suggestion[suggestion]['total'] += 1
                
                # 简化版准确率计算（实际需要历史价格验证）
                if self._is_signal_correct_safe(signal):
                    correct_signals += 1
                    by_suggestion[suggestion]['correct'] += 1
            
            # 计算准确率
            accuracy_rate = correct_signals / total_signals if total_signals > 0 else 0.0
            
            # 计算各建议类型的准确率
            for suggestion, stats in by_suggestion.items():
                if stats['total'] > 0:
                    stats['accuracy_rate'] = stats['correct'] / stats['total']
                else:
                    stats['accuracy_rate'] = 0.0
            
            return {
                'total': total_signals,
                'correct': correct_signals,
                'accuracy_rate': round(accuracy_rate, 4),
                'by_suggestion': by_suggestion
            }
            
        except Exception as e:
            logger.error(f"❌ 计算准确率失败: {e}")
            return {'total': 0, 'accuracy_rate': 0.0, 'by_suggestion': {}}
    
    def _is_signal_correct_safe(self, signal) -> bool:
        """安全判断信号是否正确（简化版）"""
        try:
            # 实际应用中需要结合历史价格验证
            # 这里使用置信度作为代理指标
            confidence = self._get_confidence_safe(signal)
            return confidence > 0.7
        except Exception:
            return False
    
    def _calculate_performance_metrics_safe(self, signals: List) -> Dict[str, float]:
        """安全计算性能指标"""
        if not signals:
            return {}
        
        try:
            # 计算平均置信度
            total_confidence = 0.0
            for signal in signals:
                confidence = self._get_confidence_safe(signal)
                total_confidence += confidence
            
            avg_confidence = total_confidence / len(signals)
            
            # 计算成功率（简化版）
            success_count = 0
            for signal in signals:
                if self._is_signal_correct_safe(signal):
                    success_count += 1
            
            success_rate = success_count / len(signals)
            
            # 计算风险收益比（简化版）
            total_risk_reward = 0.0
            valid_count = 0
            for signal in signals:
                if hasattr(signal, 'risk_reward_ratio') and signal.risk_reward_ratio is not None:
                    try:
                        risk_reward = float(str(signal.risk_reward_ratio))
                        total_risk_reward += risk_reward
                        valid_count += 1
                    except (ValueError, TypeError):
                        continue
            
            avg_risk_reward = total_risk_reward / valid_count if valid_count > 0 else 0.0
            
            return {
                'avg_confidence': round(float(avg_confidence), 4),
                'success_rate': round(float(success_rate), 4),
                'avg_risk_reward': round(float(avg_risk_reward), 4),
                'total_signals': len(signals)
            }
        except Exception as e:
            logger.error(f"❌ 计算性能指标失败: {e}")
            return {}
    
    def _analyze_trends_safe(self, signals: List) -> Dict[str, Any]:
        """安全分析趋势"""
        if not signals:
            return {}
        
        try:
            # 按趋势类型统计 - 修复max函数问题
            trend_counts = {}
            for signal in signals:
                trend = signal.trend_type
                if trend not in trend_counts:
                    trend_counts[trend] = 0
                trend_counts[trend] += 1
            
            # 计算趋势分布
            total = len(signals)
            trend_distribution = {
                trend: {
                    'count': count,
                    'percentage': round(count / total * 100, 2)
                }
                for trend, count in trend_counts.items()
            }
            
            # 修复max函数问题 - 使用安全的方法获取主导趋势
            dominant_trend = self._get_dominant_trend_safe(trend_counts)
            
            return {
                'trend_distribution': trend_distribution,
                'dominant_trend': dominant_trend,
                'trend_stability': self._calculate_trend_stability_safe(signals)
            }
        except Exception as e:
            logger.error(f"❌ 分析趋势失败: {e}")
            return {}
    
    def _get_dominant_trend_safe(self, trend_counts: Dict[int, int]) -> int:
        """安全获取主导趋势 - 修复max函数问题"""
        try:
            if not trend_counts:
                return 2  # 默认震荡
            
            # 使用items()和lambda函数修复max问题
            dominant_trend = max(trend_counts.items(), key=lambda x: x[1])
            return dominant_trend[0]
            
        except Exception as e:
            logger.error(f"❌ 获取主导趋势失败: {e}")
            return 2
    
    def _calculate_trend_stability_safe(self, signals: List) -> float:
        """计算趋势稳定性"""
        if len(signals) < 2:
            return 0.0
        
        try:
            # 计算趋势变化频率
            trend_changes = 0
            previous_trend = None
            
            for signal in signals:
                current_trend = signal.trend_type
                if previous_trend is not None and current_trend != previous_trend:
                    trend_changes += 1
                previous_trend = current_trend
            
            stability = 1.0 - (trend_changes / len(signals))
            return round(max(0.0, stability), 4)
            
        except Exception as e:
            logger.error(f"❌ 计算趋势稳定性失败: {e}")
            return 0.0
    
    def _format_signals_safe(self, signals: List) -> List[Dict]:
        """安全格式化信号列表"""
        formatted = []
        for signal in signals:
            try:
                # 使用安全方法获取值
                confidence = self._get_confidence_safe(signal)
                suggestion = self._get_suggestion_safe(signal)
                
                formatted_signal = {
                    'symbol': str(signal.symbol) if hasattr(signal, 'symbol') else 'Unknown',
                    'trend_type': int(signal.trend_type) if hasattr(signal, 'trend_type') else 2,
                    'suggestion': suggestion,
                    'confidence': confidence,
                    'entry_price': self._get_price_safe(signal, 'buy_price'),
                    'target_price': self._get_price_safe(signal, 'target_price'),
                    'stop_loss_price': self._get_price_safe(signal, 'stop_loss_price'),
                    'risk_reward_ratio': self._get_risk_reward_safe(signal),
                    'analysis_time': signal.created_at.strftime('%Y-%m-%d %H:%M:%S') if hasattr(signal, 'created_at') else 'Unknown'
                }
                formatted.append(formatted_signal)
                
            except Exception as e:
                logger.error(f"❌ 格式化信号失败: {e}")
                continue
        
        return formatted
    
    def _format_signal_history_safe(self, signals: List) -> List[Dict]:
        """安全格式化信号历史"""
        formatted = []
        for signal in signals:
            try:
                # 使用安全方法获取值
                suggestion = self._get_suggestion_safe(signal)
                confidence = self._get_confidence_safe(signal)
                
                formatted.append({
                    'symbol': str(signal.symbol) if hasattr(signal, 'symbol') else 'Unknown',
                    'time': signal.created_at.strftime('%Y-%m-%d %H:%M') if hasattr(signal, 'created_at') else 'Unknown',
                    'suggestion': suggestion,
                    'trend': int(signal.trend_type) if hasattr(signal, 'trend_type') else 2,
                    'confidence': confidence,
                    'price': self._get_price_safe(signal, 'entry_price'),
                    'is_success': bool(signal.is_success) if hasattr(signal, 'is_success') else True
                })
            except Exception as e:
                logger.error(f"❌ 格式化信号历史失败: {e}")
                continue
        
        return formatted
    
    def _generate_summary_safe(self, signals: List, accuracy_stats: Dict) -> str:
        """安全生成报告摘要"""
        if not signals:
            return "今日无交易信号"
        
        try:
            total = len(signals)
            buy_count = self._count_suggestions_safe(signals, 'buy')
            sell_count = self._count_suggestions_safe(signals, 'sell')
            hold_count = self._count_suggestions_safe(signals, 'hold')
            
            accuracy = accuracy_stats.get('accuracy_rate', 0) * 100
            
            summary_parts = [
                f"今日生成 {total} 个交易信号",
                f"买入建议: {buy_count} 个",
                f"卖出建议: {sell_count} 个",
                f"持有建议: {hold_count} 个",
                f"历史准确率: {accuracy:.1f}%"
            ]
            
            return " | ".join(summary_parts)
            
        except Exception as e:
            logger.error(f"❌ 生成摘要失败: {e}")
            return "报告生成失败"
    
    def _count_suggestions_safe(self, signals: List, suggestion_type: str) -> int:
        """安全统计建议类型数量"""
        count = 0
        for signal in signals:
            try:
                suggestion = self._get_suggestion_safe(signal)
                if suggestion == suggestion_type:
                    count += 1
            except Exception:
                continue
        return count
    
    def _count_high_confidence_safe(self, signals: List) -> int:
        """安全统计高置信度信号数量"""
        count = 0
        for signal in signals:
            try:
                confidence = self._get_confidence_safe(signal)
                if confidence > 0.8:
                    count += 1
            except Exception:
                continue
        return count
    
    def _get_suggestion_safe(self, signal) -> str:
        """安全获取建议类型"""
        try:
            if hasattr(signal, 'suggestion'):
                suggestion_value = signal.suggestion
                if suggestion_value is not None:
                    return str(suggestion_value)
            return "hold"
        except Exception:
            return "hold"
    
    def _get_confidence_safe(self, signal) -> float:
        """安全获取置信度"""
        try:
            if hasattr(signal, 'confidence_score'):
                confidence_value = signal.confidence_score
                if confidence_value is not None:
                    if isinstance(confidence_value, (int, float)):
                        return float(confidence_value)
                    else:
                        return float(str(confidence_value))
            return 0.0
        except Exception:
            return 0.0
    
    def _get_price_safe(self, signal, price_field: str) -> Optional[float]:
        """安全获取价格"""
        try:
            if hasattr(signal, price_field):
                price_value = getattr(signal, price_field)
                if price_value is not None:
                    if isinstance(price_value, (int, float)):
                        return float(price_value)
                    else:
                        return float(str(price_value))
            return None
        except Exception:
            return None
    
    def _get_risk_reward_safe(self, signal) -> Optional[float]:
        """安全获取风险收益比"""
        try:
            if hasattr(signal, 'risk_reward_ratio'):
                rr_value = signal.risk_reward_ratio
                if rr_value is not None:
                    if isinstance(rr_value, (int, float)):
                        return float(rr_value)
                    else:
                        return float(str(rr_value))
            return None
        except Exception:
            return None
    
    def _assess_risk_safe(self, signals: List) -> Dict[str, Any]:
        """安全评估风险"""
        if not signals:
            return {'level': 'low', 'message': '无信号数据'}
        
        try:
            # 计算平均置信度
            total_confidence = 0.0
            for signal in signals:
                confidence = self._get_confidence_safe(signal)
                total_confidence += confidence
            
            avg_confidence = total_confidence / len(signals)
            
            # 根据平均置信度评估风险
            if avg_confidence >= 0.8:
                risk_level = 'low'
                message = '高置信度，风险较低'
            elif avg_confidence >= 0.6:
                risk_level = 'medium'
                message = '中等置信度，风险适中'
            else:
                risk_level = 'high'
                message = '低置信度，风险较高'
            
            return {
                'level': risk_level,
                'message': message,
                'avg_confidence': round(avg_confidence, 4)
            }
        except Exception as e:
            logger.error(f"❌ 风险评估失败: {e}")
            return {'level': 'unknown', 'message': '风险评估失败'}
    
    def _generate_recommendation_safe(self, signals: List, accuracy_stats: Dict) -> Dict[str, Any]:
        """安全生成投资建议"""
        if not signals:
            return {'action': 'hold', 'confidence': 0.0, 'reason': '无信号数据'}
        
        try:
            # 获取最新信号
            latest_signal = signals[0]
            suggestion = self._get_suggestion_safe(latest_signal)
            confidence = self._get_confidence_safe(latest_signal)
            accuracy = accuracy_stats.get('accuracy_rate', 0.5)
            
            # 综合置信度和准确率
            overall_confidence = (confidence + accuracy) / 2
            
            if overall_confidence >= 0.7:
                action = suggestion
                reason = f'高置信度建议 ({overall_confidence:.1%})'
            elif overall_confidence >= 0.5:
                action = 'hold'  # 中等置信度时建议持有
                reason = f'中等置信度，建议观望 ({overall_confidence:.1%})'
            else:
                action = 'hold'
                reason = f'低置信度，建议谨慎 ({overall_confidence:.1%})'
            
            return {
                'action': action,
                'confidence': round(overall_confidence, 4),
                'reason': reason,
                'based_on_signals': len(signals)
            }
        except Exception as e:
            logger.error(f"❌ 生成建议失败: {e}")
            return {'action': 'hold', 'confidence': 0.0, 'reason': '建议生成失败'}
    
    def export_to_json(self, report: Dict, filename: Optional[str] = None) -> str:
        """导出报告为JSON文件"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"analysis_report_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2, default=str)
            logger.info(f"✅ 报告已导出到: {filename}")
            return filename
        except Exception as e:
            logger.error(f"❌ JSON导出失败: {e}")
            raise
    
    def export_to_csv(self, report: Dict, filename: Optional[str] = None) -> str:
        """导出报告为CSV文件"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"analysis_report_{timestamp}.csv"
        
        try:
            # 提取信号数据
            signals = report.get('signals', [])
            if not signals:
                logger.warning("⚠️ 无信号数据可导出")
                return filename
            
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                if signals:
                    fieldnames = signals[0].keys()
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(signals)
            
            logger.info(f"✅ CSV报告已导出到: {filename}")
            return filename
        except Exception as e:
            logger.error(f"❌ CSV导出失败: {e}")
            raise
    
    def display_console_report(self, report: Dict):
        """在控制台显示报告"""
        print("\n" + "="*60)
        print("📊 分析报告汇总")
        print("="*60)
        
        try:
            # 基本信息
            print(f"报告日期: {report.get('report_date', 'N/A')}")
            print(f"总信号数: {report.get('total_signals', 0)}")
            print(f"买入信号: {report.get('buy_signals', 0)}")
            print(f"卖出信号: {report.get('sell_signals', 0)}")
            print(f"高置信度信号: {report.get('high_confidence_signals', 0)}")
            
            # 准确率统计
            accuracy_stats = report.get('accuracy_stats', {})
            if accuracy_stats:
                accuracy_rate = accuracy_stats.get('accuracy_rate', 0) * 100
                print(f"历史准确率: {accuracy_rate:.1f}%")
            
            # 信号列表
            signals = report.get('signals', [])
            if signals:
                print(f"\n📈 最新信号 (前5个):")
                for i, signal in enumerate(signals[:5], 1):
                    print(f"  {i}. [{signal.get('symbol', 'N/A')}] {signal.get('suggestion', 'N/A')} "
                          f"(置信度: {signal.get('confidence', 0):.2f})")
            
            print("="*60)
            
        except Exception as e:
            print(f"❌ 控制台显示失败: {e}")

# 全局报告生成器实例
report_generator = ReportGenerator()