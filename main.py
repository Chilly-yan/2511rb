#!/usr/bin/env python3
import sys
import os
import logging

# 添加src到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.core.system_manager import system
from src.config.settings import config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """主程序"""
    try:
        while True:
            print("\n" + "="*60)
            print("🤖 期货市场智能分析系统")
            print("="*60)
            print("1. 运行每日分析")
            print("2. 获取单个品种数据")
            print("3. 查看分析报告")
            print("4. 系统状态")
            print("5. 退出系统")
            
            choice = input("\n请选择操作 (1-5): ").strip()
            
            if choice == '1':
                # 运行每日分析
                symbols = ["螺纹钢主连", "铁矿石主连", "焦煤主连"]
                results = system.run_daily_analysis(symbols)
                print("✅ 每日分析完成")
                
            elif choice == '2':
                # 获取单个品种数据
                symbol = input("请输入品种名称: ").strip()
                result = system.data_processor.fetch_and_process_symbol(symbol)
                print(f"数据获取结果: {result}")
                
            elif choice == '3':
                # 查看分析报告
                report = system.report_generator.generate_daily_report()
                print(f"📊 分析报告: {report}")
                
            elif choice == '4':
                # 系统状态
                print("🟢 系统运行正常")
                print(f"支持的品种: {config.akshare.supported_symbols}")
                
            elif choice == '5':
                print("👋 感谢使用，再见！")
                break
                
            else:
                print("❌ 无效选择，请重新输入")
                
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断操作")
    except Exception as e:
        print(f"\n❌ 系统错误: {e}")
    finally:
        system.db_manager.close()

if __name__ == "__main__":
    main()