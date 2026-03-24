# © 2026 MirageShield 团队 版权所有，侵权必究
# 消息队列管理器
import asyncio
import logging
from typing import Dict, Optional, Any

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s:%(funcName)s:%(lineno)d - %(message)s'
)
logger = logging.getLogger('utils.message_queue')

class MessageQueueManager:
    """消息队列管理器"""
    def __init__(self):
        """初始化消息队列管理器"""
        # 为每个智能体创建一个队列
        self.queues: Dict[str, asyncio.Queue] = {}
        # 消息处理任务
        self.tasks: Dict[str, asyncio.Task] = {}
        # 消息处理器
        self.handlers: Dict[str, callable] = {}
        # 运行状态
        self.running = False
        logger.info("消息队列管理器初始化完成")
    
    def register_agent(self, agent_name: str, handler: Optional[callable] = None):
        """注册智能体
        
        Args:
            agent_name: 智能体名称
            handler: 消息处理函数，接收消息作为参数
        """
        if agent_name not in self.queues:
            self.queues[agent_name] = asyncio.Queue()
            logger.info(f"注册智能体: {agent_name}")
        
        if handler:
            self.handlers[agent_name] = handler
            logger.info(f"为智能体 {agent_name} 注册消息处理器")
    
    async def send_message(self, agent_name: str, message: Any):
        """发送消息到指定智能体
        
        Args:
            agent_name: 智能体名称
            message: 消息内容
        """
        if agent_name in self.queues:
            await self.queues[agent_name].put(message)
            logger.debug(f"发送消息到 {agent_name}: {message}")
        else:
            logger.error(f"智能体 {agent_name} 未注册")
    
    async def receive_message(self, agent_name: str) -> Any:
        """接收来自指定智能体的消息
        
        Args:
            agent_name: 智能体名称
        
        Returns:
            消息内容
        """
        if agent_name in self.queues:
            message = await self.queues[agent_name].get()
            logger.debug(f"从 {agent_name} 接收消息: {message}")
            return message
        else:
            logger.error(f"智能体 {agent_name} 未注册")
            return None
    
    async def start_processing(self):
        """开始处理消息"""
        if self.running:
            logger.warning("消息处理已经在运行中")
            return
        
        self.running = True
        logger.info("开始处理消息")
        
        # 为每个注册了处理器的智能体启动一个处理任务
        for agent_name, handler in self.handlers.items():
            if agent_name in self.queues:
                task = asyncio.create_task(self._process_messages(agent_name, handler))
                self.tasks[agent_name] = task
                logger.info(f"为智能体 {agent_name} 启动消息处理任务")
    
    async def stop_processing(self):
        """停止处理消息"""
        if not self.running:
            logger.warning("消息处理已经停止")
            return
        
        self.running = False
        logger.info("停止处理消息")
        
        # 取消所有处理任务
        for agent_name, task in self.tasks.items():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                logger.info(f"智能体 {agent_name} 的消息处理任务已取消")
            except Exception as e:
                logger.error(f"停止智能体 {agent_name} 的消息处理任务时出错: {str(e)}")
        
        self.tasks.clear()
    
    async def _process_messages(self, agent_name: str, handler: callable):
        """处理消息的内部方法
        
        Args:
            agent_name: 智能体名称
            handler: 消息处理函数
        """
        queue = self.queues[agent_name]
        while self.running:
            try:
                # 等待消息，超时为1秒，以便能够响应停止信号
                try:
                    message = await asyncio.wait_for(queue.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    continue
                
                # 处理消息
                await handler(message)
                # 标记消息为已处理
                queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"处理消息时出错: {str(e)}")
    
    def get_queue_size(self, agent_name: str) -> int:
        """获取指定智能体的队列大小
        
        Args:
            agent_name: 智能体名称
        
        Returns:
            队列大小
        """
        if agent_name in self.queues:
            return self.queues[agent_name].qsize()
        else:
            logger.error(f"智能体 {agent_name} 未注册")
            return 0

# 全局消息队列管理器实例
message_queue_manager = MessageQueueManager()
