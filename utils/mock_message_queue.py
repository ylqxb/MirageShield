# © 2026 MirageShield 团队 版权所有，侵权必究
# 模拟消息队列管理器
import asyncio
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s:%(funcName)s:%(lineno)d - %(message)s'
)
logger = logging.getLogger('utils.mock_message_queue')

class MockMessageQueueManager:
    """模拟消息队列管理器"""
    def __init__(self):
        """初始化模拟消息队列管理器"""
        self.queues = {}
        self.handlers = {}
        self.running = False
        logger.info("模拟消息队列管理器初始化完成")
    
    def register_agent(self, agent_name, handler=None):
        """注册智能体"""
        if agent_name not in self.queues:
            self.queues[agent_name] = asyncio.Queue()
            logger.info(f"注册智能体: {agent_name}")
        
        if handler:
            self.handlers[agent_name] = handler
            logger.info(f"为智能体 {agent_name} 注册消息处理器")
    
    async def send_message(self, agent_name, message):
        """发送消息"""
        logger.debug(f"发送消息到 {agent_name}: {message}")
    
    async def receive_message(self, agent_name):
        """接收消息"""
        logger.debug(f"从 {agent_name} 接收消息")
        return None
    
    async def start_processing(self):
        """开始处理消息"""
        if self.running:
            logger.warning("消息处理已经在运行中")
            return
        
        self.running = True
        logger.info("开始处理消息")
    
    async def stop_processing(self):
        """停止处理消息"""
        if not self.running:
            logger.warning("消息处理已经停止")
            return
        
        self.running = False
        logger.info("停止处理消息")
    
    def get_queue_size(self, agent_name):
        """获取队列大小"""
        if agent_name in self.queues:
            return self.queues[agent_name].qsize()
        else:
            logger.error(f"智能体 {agent_name} 未注册")
            return 0
