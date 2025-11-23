import logging
from src.database.database import db_manager
from src.input.data_processor import data_processor
from src.analysis.technical_analyzer import technical_analyzer
from src.output.report_generator import report_generator

logger = logging.getLogger(__name__)

class FuturesAnalysisSystem:
    """期货分析系统主控制器"""
    
    def __init__(self):
        self.db_manager = db_manager
        self.data_processor = data_processor
        self.technical_analyzer = technical_analyzer
        self.report_generator = report_generator
        
        # 初始化系统
        self._initialize_system()
    
    def _initialize_system(self):
        """初始化系统"""
        try:
            # 创建数据库表
            self.db_manager.create_tables()
            logger.info("🚀 期货分析系统初始化完成")
        except Exception as e:
            logger.error(f"❌ 系统初始化失败: {e}")
            raise
    
    def run_daily_analysis(self, symbols: list):
        """运行每日分析"""
        if symbols is None:
            symbols = ["螺纹钢主连", "铁矿石主连", "焦煤主连"]
        
        results = {
            'data_fetch': {},
            'analysis': {},
            'report': {}
        }
        
        # 1. 数据获取
        logger.info("📥 开始数据获取...")
        for symbol in symbols:
            try:
                
                result = self.data_processor.fetch_and_process_symbol(symbol, days=30)
                results['data_fetch'][symbol] = result
            except Exception as e:
                logger.error(f"❌ 数据获取失败: {symbol}, {e}")
                results['data_fetch'][symbol] = {'success': False, 'error': str(e)}
        
        # 2. 技术分析
        logger.info("🔍 开始技术分析...")
        # 这里添加分析逻辑...
        
        # 3. 生成报告
        logger.info("📊 生成分析报告...")
        results['report'] = self.report_generator.generate_daily_report()
        
        logger.info("✅ 每日分析完成")
        return results

# 全局系统实例
system = FuturesAnalysisSystem()