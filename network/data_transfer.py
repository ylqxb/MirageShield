# © 2026 MirageShield 团队 版权所有，侵权必究
# 本项目已申请发明专利，未经许可禁止商用
# 数据传输管理模块
import threading
import json
import logging
import time
from datetime import datetime
from enum import Enum

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s:%(funcName)s:%(lineno)d - %(message)s'
)
logger = logging.getLogger('network.data_transfer')

class TransferStatus(Enum):
    """传输状态枚举"""
    PENDING = "pending"      # 待传输
    TRANSFERRING = "transferring"  # 传输中
    COMPLETED = "completed"    # 已完成
    FAILED = "failed"        # 失败
    PAUSED = "paused"        # 暂停

class DataTransferManager:
    def __init__(self, communication_manager=None):
        """初始化数据传输管理器"""
        self.communication_manager = communication_manager
        self.transfers = {}
        self.lock = threading.RLock()
        self.transfer_threads = {}
    
    def send_data(self, target_node, data_id, data, chunk_size=1024 * 1024):
        """发送数据到目标节点"""
        if not self.communication_manager:
            logger.error("通信管理器未初始化")
            return None
        
        # 生成传输ID
        transfer_id = f"{data_id}_{datetime.now().timestamp()}"
        
        # 初始化传输状态
        with self.lock:
            self.transfers[transfer_id] = {
                'transfer_id': transfer_id,
                'data_id': data_id,
                'target_node': target_node,
                'status': TransferStatus.PENDING.value,
                'total_size': len(str(data)),
                'transferred_size': 0,
                'start_time': datetime.now().isoformat(),
                'end_time': None,
                'error': None,
                'retries': 0,
                'max_retries': 3
            }
        
        # 启动传输线程
        transfer_thread = threading.Thread(
            target=self._transfer_data,
            args=(transfer_id, data, chunk_size),
            daemon=True
        )
        transfer_thread.start()
        self.transfer_threads[transfer_id] = transfer_thread
        
        return transfer_id
    
    def _transfer_data(self, transfer_id, data, chunk_size):
        """执行数据传输"""
        try:
            # 更新状态为传输中
            with self.lock:
                if transfer_id in self.transfers:
                    self.transfers[transfer_id]['status'] = TransferStatus.TRANSFERRING.value
            
            # 获取传输信息
            with self.lock:
                transfer_info = self.transfers[transfer_id].copy()
            
            target_node = transfer_info['target_node']
            data_id = transfer_info['data_id']
            
            # 检查目标节点是否已连接
            connections = self.communication_manager.get_connections()
            if target_node not in connections:
                # 尝试连接目标节点
                ip, port = target_node.split(':')
                connection_id = self.communication_manager.connect_to_node(ip, int(port))
                if not connection_id:
                    with self.lock:
                        if transfer_id in self.transfers:
                            self.transfers[transfer_id]['status'] = TransferStatus.FAILED.value
                            self.transfers[transfer_id]['error'] = "无法连接到目标节点"
                            self.transfers[transfer_id]['end_time'] = datetime.now().isoformat()
                    return
            
            # 转换数据为字符串
            if isinstance(data, dict) or isinstance(data, list):
                data_str = json.dumps(data)
            else:
                data_str = str(data)
            
            # 分块传输
            total_size = len(data_str)
            transferred_size = 0
            chunk_index = 0
            
            while transferred_size < total_size:
                # 检查传输是否被暂停
                with self.lock:
                    if transfer_id in self.transfers and self.transfers[transfer_id]['status'] == TransferStatus.PAUSED.value:
                        # 等待传输继续
                        while transfer_id in self.transfers and self.transfers[transfer_id]['status'] == TransferStatus.PAUSED.value:
                            time.sleep(1)
                        if transfer_id not in self.transfers:
                            return
                
                # 计算当前块大小
                current_chunk_size = min(chunk_size, total_size - transferred_size)
                chunk_data = data_str[transferred_size:transferred_size + current_chunk_size]
                
                # 构建传输消息
                transfer_message = {
                    'type': 'data_transfer',
                    'data_id': data_id,
                    'transfer_id': transfer_id,
                    'chunk_index': chunk_index,
                    'total_chunks': (total_size + chunk_size - 1) // chunk_size,
                    'chunk_data': chunk_data,
                    'total_size': total_size,
                    'timestamp': datetime.now().isoformat()
                }
                
                # 发送数据
                success = self.communication_manager.send_message(target_node, transfer_message)
                if not success:
                    # 重试
                    with self.lock:
                        if transfer_id in self.transfers:
                            self.transfers[transfer_id]['retries'] += 1
                            if self.transfers[transfer_id]['retries'] >= self.transfers[transfer_id]['max_retries']:
                                self.transfers[transfer_id]['status'] = TransferStatus.FAILED.value
                                self.transfers[transfer_id]['error'] = "传输失败，达到最大重试次数"
                                self.transfers[transfer_id]['end_time'] = datetime.now().isoformat()
                                return
                    time.sleep(1)  # 等待后重试
                    continue
                
                # 更新传输进度
                transferred_size += current_chunk_size
                chunk_index += 1
                
                with self.lock:
                    if transfer_id in self.transfers:
                        self.transfers[transfer_id]['transferred_size'] = transferred_size
            
            # 传输完成
            with self.lock:
                if transfer_id in self.transfers:
                    self.transfers[transfer_id]['status'] = TransferStatus.COMPLETED.value
                    self.transfers[transfer_id]['end_time'] = datetime.now().isoformat()
            
            logger.info(f"数据传输完成: {transfer_id}")
        except Exception as e:
            logger.error(f"数据传输出错: {str(e)}")
            with self.lock:
                if transfer_id in self.transfers:
                    self.transfers[transfer_id]['status'] = TransferStatus.FAILED.value
                    self.transfers[transfer_id]['error'] = str(e)
                    self.transfers[transfer_id]['end_time'] = datetime.now().isoformat()
        finally:
            # 清理线程引用
            if transfer_id in self.transfer_threads:
                del self.transfer_threads[transfer_id]
    
    def get_transfer_status(self, transfer_id):
        """获取传输状态"""
        with self.lock:
            return self.transfers.get(transfer_id)
    
    def get_all_transfers(self):
        """获取所有传输"""
        with self.lock:
            return list(self.transfers.values())
    
    def pause_transfer(self, transfer_id):
        """暂停传输"""
        with self.lock:
            if transfer_id in self.transfers:
                self.transfers[transfer_id]['status'] = TransferStatus.PAUSED.value
                return True
            return False
    
    def resume_transfer(self, transfer_id):
        """恢复传输"""
        with self.lock:
            if transfer_id in self.transfers:
                self.transfers[transfer_id]['status'] = TransferStatus.TRANSFERRING.value
                return True
            return False
    
    def cancel_transfer(self, transfer_id):
        """取消传输"""
        with self.lock:
            if transfer_id in self.transfers:
                self.transfers[transfer_id]['status'] = TransferStatus.FAILED.value
                self.transfers[transfer_id]['error'] = "传输被取消"
                self.transfers[transfer_id]['end_time'] = datetime.now().isoformat()
                return True
            return False
    
    def cleanup_completed_transfers(self, hours=24):
        """清理已完成的传输记录"""
        current_time = datetime.now()
        transfers_to_remove = []
        
        with self.lock:
            for transfer_id, transfer_info in self.transfers.items():
                if transfer_info['status'] in [TransferStatus.COMPLETED.value, TransferStatus.FAILED.value]:
                    end_time = datetime.fromisoformat(transfer_info['end_time'])
                    if (current_time - end_time).total_seconds() > hours * 3600:
                        transfers_to_remove.append(transfer_id)
            
            for transfer_id in transfers_to_remove:
                del self.transfers[transfer_id]
        
        if transfers_to_remove:
            logger.info(f"清理了 {len(transfers_to_remove)} 个已完成的传输记录")
    
    def get_transfer_statistics(self):
        """获取传输统计信息"""
        with self.lock:
            total_transfers = len(self.transfers)
            completed_transfers = sum(1 for t in self.transfers.values() if t['status'] == TransferStatus.COMPLETED.value)
            failed_transfers = sum(1 for t in self.transfers.values() if t['status'] == TransferStatus.FAILED.value)
            transferring_transfers = sum(1 for t in self.transfers.values() if t['status'] == TransferStatus.TRANSFERRING.value)
            
            total_size = sum(t['total_size'] for t in self.transfers.values())
            transferred_size = sum(t['transferred_size'] for t in self.transfers.values())
            
            return {
                'total_transfers': total_transfers,
                'completed_transfers': completed_transfers,
                'failed_transfers': failed_transfers,
                'transferring_transfers': transferring_transfers,
                'total_size': total_size,
                'transferred_size': transferred_size,
                'transfer_rate': transferred_size / total_size * 100 if total_size > 0 else 0
            }

if __name__ == "__main__":
    # 测试代码
    import time
    
    # 模拟通信管理器
    class MockCommunicationManager:
        def get_connections(self):
            return ['127.0.0.1:5001']
        
        def connect_to_node(self, ip, port):
            return f"{ip}:{port}"
        
        def send_message(self, client_id, message):
            # 模拟发送成功
            time.sleep(0.1)
            return True
    
    comm_manager = MockCommunicationManager()
    transfer_manager = DataTransferManager(comm_manager)
    
    # 测试发送数据
    test_data = {
        'key1': 'value1',
        'key2': 'value2',
        'key3': 'value3' * 1000  # 生成较大的数据
    }
    
    transfer_id = transfer_manager.send_data('127.0.0.1:5001', 'test_data_1', test_data)
    print(f"开始传输，传输ID: {transfer_id}")
    
    # 监控传输状态
    while True:
        status = transfer_manager.get_transfer_status(transfer_id)
        if status:
            print(f"状态: {status['status']}, 进度: {status['transferred_size']}/{status['total_size']}")
            if status['status'] in [TransferStatus.COMPLETED.value, TransferStatus.FAILED.value]:
                break
        time.sleep(1)
    
    # 获取统计信息
    stats = transfer_manager.get_transfer_statistics()
    print(f"传输统计: {stats}")
