# © 2026 MirageShield 团队 版权所有，侵权必究
# 本项目已申请发明专利，未经许可禁止商用
# 网络适配器网络适应和传输策略调整模块
import threading
import time
import logging
import socket
import statistics
from datetime import datetime
from enum import Enum

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s:%(funcName)s:%(lineno)d - %(message)s'
)
logger = logging.getLogger('network.network_adapter')

class NetworkQuality(Enum):
    """网络质量枚举"""
    EXCELLENT = "excellent"  # 优秀
    GOOD = "good"          # 良好
    FAIR = "fair"          # 一般
    POOR = "poor"          # 较差
    BAD = "bad"            # 糟糕

class NetworkAdapter:
    def __init__(self, data_transfer_manager=None):
        """初始化网络适应模块"""
        self.data_transfer_manager = data_transfer_manager
        self.network_quality = {}
        self.transfer_strategies = {}
        self.lock = threading.RLock()
        self.running = False
        self.monitoring_thread = None
        self.strategy_thread = None
        
        # 网络质量监测参数
        self.ping_interval = 5  # 秒
        self.ping_timeout = 2   # 秒
        self.ping_count = 5      # 每次监测的ping次数
        
        # 传输策略参数
        self.default_chunk_size = 1024 * 1024  # 默认分块大小
        self.min_chunk_size = 64 * 1024        # 最小分块大小
        self.max_chunk_size = 4 * 1024 * 1024   # 最大分块大小
        
        # 重试策略参数
        self.default_max_retries = 3           # 默认最大重试次数
        self.min_max_retries = 1               # 最小最大重试次数
        self.max_max_retries = 5               # 最大最大重试次数
    
    def start(self):
        """启动网络适应服务"""
        if self.running:
            logger.warning("网络适应服务已经在运行")
            return
        
        self.running = True
        
        # 启动网络质量监测线程
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        # 启动传输策略调整线程
        self.strategy_thread = threading.Thread(target=self._strategy_loop, daemon=True)
        self.strategy_thread.start()
        
        logger.info("网络适应服务已启动")
    
    def stop(self):
        """停止网络适应服务"""
        self.running = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        if self.strategy_thread:
            self.strategy_thread.join(timeout=5)
        logger.info("网络适应服务已停止")
    
    def _monitoring_loop(self):
        """网络质量监测循环"""
        while self.running:
            try:
                # 监测所有已知节点的网络质量
                nodes = self._get_known_nodes()
                for node in nodes:
                    node_id = f"{node['ip']}:{node['port']}"
                    quality = self._measure_network_quality(node['ip'])
                    with self.lock:
                        self.network_quality[node_id] = {
                            'quality': quality.value,
                            'timestamp': datetime.now().isoformat(),
                            'ip': node['ip'],
                            'port': node['port']
                        }
                time.sleep(self.ping_interval)
            except Exception as e:
                logger.error(f"网络质量监测出错: {str(e)}")
                time.sleep(self.ping_interval)
    
    def _strategy_loop(self):
        """传输策略调整循环"""
        while self.running:
            try:
                # 根据网络质量调整传输策略
                with self.lock:
                    for node_id, quality_info in self.network_quality.items():
                        strategy = self._calculate_strategy(quality_info['quality'])
                        self.transfer_strategies[node_id] = strategy
                time.sleep(10)  # 每10秒调整一次策略
            except Exception as e:
                logger.error(f"传输策略调整出错: {str(e)}")
                time.sleep(10)
    
    def _get_known_nodes(self):
        """获取已知节点列表"""
        # 这里可以从局域网发现模块获取节点列表
        # 暂时返回一个空列表
        return []
    
    def _measure_network_quality(self, ip):
        """测量网络质量"""
        try:
            ping_times = []
            for i in range(self.ping_count):
                start_time = time.time()
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(self.ping_timeout)
                try:
                    sock.connect((ip, 5001))
                    end_time = time.time()
                    ping_time = (end_time - start_time) * 1000  # 转换为毫秒
                    ping_times.append(ping_time)
                except socket.timeout:
                    ping_times.append(float('inf'))
                except Exception:
                    ping_times.append(float('inf'))
                finally:
                    try:
                        sock.close()
                    except Exception:
                        pass
                time.sleep(0.1)  # 等待100ms
            
            # 计算平均ping时间
            valid_ping_times = [t for t in ping_times if t != float('inf')]
            if not valid_ping_times:
                return NetworkQuality.BAD
            
            avg_ping = statistics.mean(valid_ping_times)
            
            # 根据ping时间判断网络质量
            if avg_ping < 50:
                return NetworkQuality.EXCELLENT
            elif avg_ping < 100:
                return NetworkQuality.GOOD
            elif avg_ping < 200:
                return NetworkQuality.FAIR
            elif avg_ping < 500:
                return NetworkQuality.POOR
            else:
                return NetworkQuality.BAD
        except Exception as e:
            logger.error(f"测量网络质量时出错: {str(e)}")
            return NetworkQuality.BAD
    
    def _calculate_strategy(self, quality):
        """根据网络质量计算传输策略"""
        if quality == NetworkQuality.EXCELLENT.value:
            return {
                'chunk_size': self.max_chunk_size,
                'max_retries': self.min_max_retries,
                'timeout': 30,
                'concurrency': 4
            }
        elif quality == NetworkQuality.GOOD.value:
            return {
                'chunk_size': self.default_chunk_size * 2,
                'max_retries': self.default_max_retries - 1,
                'timeout': 20,
                'concurrency': 3
            }
        elif quality == NetworkQuality.FAIR.value:
            return {
                'chunk_size': self.default_chunk_size,
                'max_retries': self.default_max_retries,
                'timeout': 15,
                'concurrency': 2
            }
        elif quality == NetworkQuality.POOR.value:
            return {
                'chunk_size': self.default_chunk_size // 2,
                'max_retries': self.default_max_retries + 1,
                'timeout': 10,
                'concurrency': 1
            }
        else:  # BAD
            return {
                'chunk_size': self.min_chunk_size,
                'max_retries': self.max_max_retries,
                'timeout': 5,
                'concurrency': 1
            }
    
    def get_network_quality(self, node_id):
        """获取指定节点的网络质量"""
        with self.lock:
            return self.network_quality.get(node_id)
    
    def get_transfer_strategy(self, node_id):
        """获取指定节点的传输策略"""
        with self.lock:
            return self.transfer_strategies.get(node_id, {
                'chunk_size': self.default_chunk_size,
                'max_retries': self.default_max_retries,
                'timeout': 15,
                'concurrency': 2
            })
    
    def get_all_network_quality(self):
        """获取所有节点的网络质量"""
        with self.lock:
            return list(self.network_quality.values())
    
    def get_all_transfer_strategies(self):
        """获取所有节点的传输策略"""
        with self.lock:
            return self.transfer_strategies.copy()
    
    def adjust_transfer(self, node_id, transfer_id):
        """根据网络质量调整正在进行的传输"""
        if not self.data_transfer_manager:
            logger.error("数据传输管理器未初始化")
            return False
        
        strategy = self.get_transfer_strategy(node_id)
        # 这里可以根据策略调整传输参数
        # 例如调整分块大小、重试次数等
        logger.info(f"为节点 {node_id} 的传输 {transfer_id} 应用策略: {strategy}")
        return True

if __name__ == "__main__":
    # 测试代码
    import time
    from enum import Enum
    
    # 修复导入
    class NetworkQuality(Enum):
        """网络质量枚举"""
        EXCELLENT = "excellent"  # 优秀
        GOOD = "good"          # 良好
        FAIR = "fair"          # 一般
        POOR = "poor"          # 较差
        BAD = "bad"            # 糟糕
    
    adapter = NetworkAdapter()
    adapter.start()
    
    try:
        while True:
            quality = adapter.get_all_network_quality()
            strategies = adapter.get_all_transfer_strategies()
            print(f"网络质量: {quality}")
            print(f"传输策略: {strategies}")
            time.sleep(5)
    except KeyboardInterrupt:
        adapter.stop()
        print("测试结束")
