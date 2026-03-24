# © 2026 MirageShield 团队 版权所有，侵权必究
# 本项目已申请发明专利，未经许可禁止商用
# 数据同步模块
import threading
import json
import logging
import time
import hashlib
from datetime import datetime
from enum import Enum

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s:%(funcName)s:%(lineno)d - %(message)s'
)
logger = logging.getLogger('network.data_sync')

class SyncStatus(Enum):
    """同步状态枚举"""
    IDLE = "idle"          # 空闲
    SYNCING = "syncing"      # 同步中
    COMPLETED = "completed"   # 已完成
    FAILED = "failed"        # 失败
    CONFLICT = "conflict"     # 冲突

class DataSyncManager:
    def __init__(self, communication_manager=None, data_pool=None):
        """初始化数据同步管理器"""
        self.communication_manager = communication_manager
        self.data_pool = data_pool
        self.sync_tasks = {}
        self.sync_status = {}
        self.data_hashes = {}
        self.lock = threading.RLock()
        self.running = False
        self.gossip_thread = None
        
        # Gossip协议参数
        self.gossip_interval = 10  # 秒
        self.gossip_nodes = 3      # 每次gossip的节点数
        self.sync_timeout = 30     # 同步超时时间（秒）
    
    def start(self):
        """启动数据同步服务"""
        if self.running:
            logger.warning("数据同步服务已经在运行")
            return
        
        self.running = True
        
        # 启动Gossip线程
        self.gossip_thread = threading.Thread(target=self._gossip_loop, daemon=True)
        self.gossip_thread.start()
        
        logger.info("数据同步服务已启动")
    
    def stop(self):
        """停止数据同步服务"""
        self.running = False
        if self.gossip_thread:
            self.gossip_thread.join(timeout=5)
        logger.info("数据同步服务已停止")
    
    def _gossip_loop(self):
        """Gossip协议循环"""
        while self.running:
            try:
                # 获取所有节点
                nodes = self._get_available_nodes()
                if len(nodes) > 1:
                    # 随机选择几个节点进行gossip
                    selected_nodes = self._select_gossip_nodes(nodes, self.gossip_nodes)
                    for node in selected_nodes:
                        self._gossip_with_node(node)
                time.sleep(self.gossip_interval)
            except Exception as e:
                logger.error(f"Gossip循环出错: {str(e)}")
                time.sleep(self.gossip_interval)
    
    def _get_available_nodes(self):
        """获取可用节点列表"""
        # 这里可以从局域网发现模块获取节点列表
        # 暂时返回一个空列表
        return []
    
    def _select_gossip_nodes(self, nodes, count):
        """选择要进行gossip的节点"""
        import random
        if len(nodes) <= count:
            return nodes
        return random.sample(nodes, count)
    
    def _gossip_with_node(self, node):
        """与节点进行gossip"""
        try:
            node_id = f"{node['ip']}:{node['port']}"
            
            # 发送本地数据哈希
            local_hashes = self._get_local_data_hashes()
            gossip_message = {
                'type': 'gossip',
                'hashes': local_hashes,
                'timestamp': datetime.now().isoformat()
            }
            
            success = self.communication_manager.send_message(node_id, gossip_message)
            if success:
                logger.debug(f"与节点 {node_id} 进行gossip成功")
        except Exception as e:
            logger.error(f"与节点进行gossip时出错: {str(e)}")
    
    def _get_local_data_hashes(self):
        """获取本地数据哈希"""
        hashes = {}
        if self.data_pool:
            # 从数据池获取数据列表
            data_list = self.data_pool.list_data()
            for data_info in data_list:
                data_id = data_info['data_id']
                # 获取数据内容并计算哈希
                data = self.data_pool.retrieve_data(data_id, 'prober')
                if data:
                    data_str = json.dumps(data, sort_keys=True)
                    data_hash = hashlib.sha256(data_str.encode('utf-8')).hexdigest()
                    hashes[data_id] = data_hash
        return hashes
    
    def sync_with_node(self, node_id, data_ids=None):
        """与指定节点同步数据"""
        sync_id = f"sync_{node_id}_{datetime.now().timestamp()}"
        
        with self.lock:
            self.sync_tasks[sync_id] = {
                'sync_id': sync_id,
                'node_id': node_id,
                'data_ids': data_ids,
                'status': SyncStatus.SYNCING.value,
                'start_time': datetime.now().isoformat(),
                'end_time': None,
                'error': None
            }
        
        # 启动同步线程
        sync_thread = threading.Thread(
            target=self._sync_with_node,
            args=(sync_id, node_id, data_ids),
            daemon=True
        )
        sync_thread.start()
        
        return sync_id
    
    def _sync_with_node(self, sync_id, node_id, data_ids):
        """执行与节点的同步"""
        try:
            # 获取远程数据哈希
            remote_hashes = self._get_remote_data_hashes(node_id)
            local_hashes = self._get_local_data_hashes()
            
            # 确定需要同步的数据
            to_sync = []
            
            if data_ids:
                # 同步指定的数据
                for data_id in data_ids:
                    if data_id not in local_hashes or local_hashes[data_id] != remote_hashes.get(data_id):
                        to_sync.append(data_id)
            else:
                # 同步所有不同的数据
                for data_id, remote_hash in remote_hashes.items():
                    if data_id not in local_hashes or local_hashes[data_id] != remote_hash:
                        to_sync.append(data_id)
            
            # 同步数据
            for data_id in to_sync:
                success = self._sync_data(node_id, data_id)
                if not success:
                    raise Exception(f"同步数据 {data_id} 失败")
            
            # 同步完成
            with self.lock:
                if sync_id in self.sync_tasks:
                    self.sync_tasks[sync_id]['status'] = SyncStatus.COMPLETED.value
                    self.sync_tasks[sync_id]['end_time'] = datetime.now().isoformat()
            
            logger.info(f"与节点 {node_id} 的同步完成，同步了 {len(to_sync)} 个数据")
        except Exception as e:
            logger.error(f"与节点同步时出错: {str(e)}")
            with self.lock:
                if sync_id in self.sync_tasks:
                    self.sync_tasks[sync_id]['status'] = SyncStatus.FAILED.value
                    self.sync_tasks[sync_id]['error'] = str(e)
                    self.sync_tasks[sync_id]['end_time'] = datetime.now().isoformat()
    
    def _get_remote_data_hashes(self, node_id):
        """获取远程节点的数据哈希"""
        # 发送请求获取远程数据哈希
        request_message = {
            'type': 'get_data_hashes',
            'timestamp': datetime.now().isoformat()
        }
        
        # 这里需要实现异步接收响应的逻辑
        # 暂时返回空字典
        return {}
    
    def _sync_data(self, node_id, data_id):
        """同步指定的数据"""
        try:
            # 请求远程数据
            request_message = {
                'type': 'get_data',
                'data_id': data_id,
                'timestamp': datetime.now().isoformat()
            }
            
            # 这里需要实现异步接收响应的逻辑
            # 暂时模拟成功
            time.sleep(0.5)
            
            # 假设我们收到了数据
            # 这里应该是从远程节点获取的数据
            remote_data = {"key": "value"}
            
            # 存储数据
            if self.data_pool:
                self.data_pool.store_data(remote_data, 'synced_data', 'prober')
            
            return True
        except Exception as e:
            logger.error(f"同步数据时出错: {str(e)}")
            return False
    
    def resolve_conflict(self, data_id, conflict_data):
        """解决数据冲突"""
        try:
            # 这里实现冲突解决逻辑
            # 例如：基于时间戳、版本号等
            logger.info(f"解决数据 {data_id} 的冲突")
            return True
        except Exception as e:
            logger.error(f"解决冲突时出错: {str(e)}")
            return False
    
    def get_sync_status(self, sync_id):
        """获取同步状态"""
        with self.lock:
            return self.sync_tasks.get(sync_id)
    
    def get_all_sync_tasks(self):
        """获取所有同步任务"""
        with self.lock:
            return list(self.sync_tasks.values())
    
    def cancel_sync(self, sync_id):
        """取消同步任务"""
        with self.lock:
            if sync_id in self.sync_tasks:
                self.sync_tasks[sync_id]['status'] = SyncStatus.FAILED.value
                self.sync_tasks[sync_id]['error'] = "同步被取消"
                self.sync_tasks[sync_id]['end_time'] = datetime.now().isoformat()
                return True
            return False
    
    def cleanup_completed_tasks(self, hours=24):
        """清理已完成的同步任务"""
        current_time = datetime.now()
        tasks_to_remove = []
        
        with self.lock:
            for sync_id, task in self.sync_tasks.items():
                if task['status'] in [SyncStatus.COMPLETED.value, SyncStatus.FAILED.value]:
                    end_time = datetime.fromisoformat(task['end_time'])
                    if (current_time - end_time).total_seconds() > hours * 3600:
                        tasks_to_remove.append(sync_id)
            
            for sync_id in tasks_to_remove:
                del self.sync_tasks[sync_id]
        
        if tasks_to_remove:
            logger.info(f"清理了 {len(tasks_to_remove)} 个已完成的同步任务")

if __name__ == "__main__":
    # 测试代码
    import time
    
    # 模拟通信管理器
    class MockCommunicationManager:
        def send_message(self, client_id, message):
            # 模拟发送成功
            time.sleep(0.1)
            return True
    
    # 模拟数据池
    class MockDataPool:
        def list_data(self):
            return [{'data_id': 'test1'}, {'data_id': 'test2'}]
        
        def retrieve_data(self, data_id, agent_name):
            return {"key": "value"}
        
        def store_data(self, data, data_type, agent_name):
            return f"data_{datetime.now().timestamp()}"
    
    comm_manager = MockCommunicationManager()
    data_pool = MockDataPool()
    sync_manager = DataSyncManager(comm_manager, data_pool)
    sync_manager.start()
    
    try:
        # 测试同步
        sync_id = sync_manager.sync_with_node('127.0.0.1:5001')
        print(f"开始同步，同步ID: {sync_id}")
        
        # 监控同步状态
        while True:
            status = sync_manager.get_sync_status(sync_id)
            if status:
                print(f"状态: {status['status']}")
                if status['status'] in [SyncStatus.COMPLETED.value, SyncStatus.FAILED.value]:
                    break
            time.sleep(1)
        
        # 获取所有同步任务
        tasks = sync_manager.get_all_sync_tasks()
        print(f"所有同步任务: {tasks}")
    except KeyboardInterrupt:
        sync_manager.stop()
        print("测试结束")
