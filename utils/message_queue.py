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

class MockMessageQueueManager:
    """模拟消息队列管理器"""
    def register_agent(self, agent_name, handler=None):
        logger.warning(f"消息队列不可用，跳过注册智能体: {agent_name}")
    
    def send_message(self, agent_name, message):
        logger.warning(f"消息队列不可用，无法发送消息到 {agent_name}")
        return False
    
    def receive_message(self, agent_name):
        logger.warning(f"消息队列不可用，无法接收来自 {agent_name} 的消息")
        return None
    
    async def start_processing(self):
        logger.warning("消息队列不可用，跳过启动处理")
    
    async def stop_processing(self):
        logger.warning("消息队列不可用，跳过停止处理")
    
    def get_queue_status(self):
        return {"status": "unavailable", "queues": {}}
    
    def get_message_stats(self):
        return {"total_messages": 0, "processed_messages": 0, "failed_messages": 0}
    
    def get_health_status(self):
        return {"status": "unavailable", "message": "Mock message queue manager"}

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
        # 消息统计
        self.message_stats = {
            'total_messages': 0,
            'processed_messages': 0,
            'failed_messages': 0,
            'start_time': None
        }
        # 队列状态
        self.queue_status = {}
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
            # 增加消息统计
            self.message_stats['total_messages'] += 1
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
        # 设置开始时间
        import time
        self.message_stats['start_time'] = time.time()
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
                try:
                    await handler(message)
                    # 增加处理成功统计
                    self.message_stats['processed_messages'] += 1
                except Exception as e:
                    # 增加处理失败统计
                    self.message_stats['failed_messages'] += 1
                    logger.error(f"处理消息时出错: {str(e)}")
                finally:
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
    
    def get_queue_status(self):
        """获取所有队列的状态
        
        Returns:
            队列状态字典
        """
        status = {}
        for agent_name, queue in self.queues.items():
            status[agent_name] = {
                'queue_size': queue.qsize(),
                'task_running': agent_name in self.tasks,
                'handler_registered': agent_name in self.handlers
            }
        return status
    
    def get_message_stats(self):
        """获取消息统计信息
        
        Returns:
            消息统计字典
        """
        import time
        stats = self.message_stats.copy()
        if stats['start_time']:
            uptime = time.time() - stats['start_time']
            stats['uptime'] = uptime
            if uptime > 0:
                stats['messages_per_second'] = stats['total_messages'] / uptime
        return stats
    
    def get_health_status(self):
        """获取消息队列健康状态
        
        Returns:
            健康状态字典
        """
        status = {
            'running': self.running,
            'queue_status': self.get_queue_status(),
            'message_stats': self.get_message_stats(),
            'agents': list(self.queues.keys()),
            'tasks': list(self.tasks.keys()),
            'handlers': list(self.handlers.keys())
        }
        
        # 检查健康状态
        healthy = True
        issues = []
        
        # 检查是否有队列积压
        for agent_name, queue_info in status['queue_status'].items():
            if queue_info['queue_size'] > 100:
                healthy = False
                issues.append(f"队列 {agent_name} 积压严重: {queue_info['queue_size']} 条消息")
            
            if queue_info['handler_registered'] and not queue_info['task_running']:
                healthy = False
                issues.append(f"智能体 {agent_name} 注册了处理器但任务未运行")
        
        # 检查消息处理失败率
        total_processed = status['message_stats']['processed_messages'] + status['message_stats']['failed_messages']
        if total_processed > 0:
            failure_rate = status['message_stats']['failed_messages'] / total_processed
            if failure_rate > 0.1:
                healthy = False
                issues.append(f"消息处理失败率过高: {failure_rate:.2f}")
        
        status['healthy'] = healthy
        status['issues'] = issues
        return status

# 全局消息队列管理器实例
message_queue_manager = MessageQueueManager()
