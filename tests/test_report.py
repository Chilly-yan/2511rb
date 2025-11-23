#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import logging
from datetime import datetime, timedelta

# 添加src到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.database.database import db_manager
from src.output.report_generator import ReportGenerator

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def test_report_generator_fixed():
    """测试修复后的ReportGenerator"""
    print("🧪 测试修复后的ReportGenerator...")
    
    try:
        # 初始化数据库
        db_manager.create_tables()
        
        # 创建报告生成器实例
        reporter = ReportGenerator()
        
        # 测试1：生成日报
        print("📊 测试日报生成...")
        daily_report = reporter.generate_daily_report()
        print(f"✅ 日报生成成功: {len(daily_report.get('signals', []))} 个信号")
        
        # 测试2：生成信号报告
        print("📈 测试信号报告...")
        signal_report = reporter.generate_signal_report("test_symbol", days=30)
        print(f"✅ 信号报告生成成功")
        
        # 测试3：测试安全方法
        print("🛡️ 测试安全方法...")
        
        # 创建测试数据
        class MockSignal:
            def __init__(self, suggestion, confidence, trend):
                self.suggestion = suggestion
                self.confidence_score = confidence
                self.trend_type = trend
                self.symbol = "test"
                self.is_success = True
        
        test_signals = [
            MockSignal("buy", 0.85, 1),
            MockSignal("sell", 0.75, 3),
            MockSignal("hold", 0.65, 2)
        ]
        
        # 测试安全统计
        buy_count = reporter._count_suggestions_safe(test_signals, 'buy')
        sell_count = reporter._count_suggestions_safe(test_signals, 'sell')
        hold_count = reporter._count_suggestions_safe(test_signals, 'hold')
        
        print(f"✅ 买入信号: {buy_count}")
        print(f"✅ 卖出信号: {sell_count}")
        print(f"✅ 持有信号: {hold_count}")
        
        # 测试趋势分析
        trend_counts = {1: 5, 2: 3, 3: 2}
        dominant_trend = reporter._get_dominant_trend_safe(trend_counts)
        print(f"✅ 主导趋势: {dominant_trend}")
        
        # 测试4：控制台显示
        print("🖥️ 测试控制台显示...")
        reporter.display_console_report(daily_report)
        
        # 测试5：导出功能
        print("💾 测试导出功能...")
        json_file = reporter.export_to_json(daily_report, "test_report.json")
        print(f"✅ JSON导出成功: {json_file}")
        
        print("🎉 ReportGenerator修复测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_report_generator_fixed()