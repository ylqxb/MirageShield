# © 2026 MirageShield 团队 版权所有，侵权必究
# 本项目已申请发明专利，未经许可禁止商用
# 局域网发现局域网节点发现模块
import socket
import threading
import time
import json
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s:%(funcName)s:%(lineno)d - %(message)s'
)
logger = logging.getLogger('network.lan_discovery')

class LANDiscovery:
    def __init__(self, service_name='miragesheild', service_type='_miragesheild._tcp.local.', port=5000):
        """初始化局域网发现模块"""
        self.service_name = service_name
        self.service_type = service_type
        self.port = port
        self.nodes = {}
        self.lock = threading.RLock()
        self.running = False
        self.discovery_thread = None
        self.announcement_thread = None
    
    def start(self):
        """启动发现服务"""
        if self.running:
            logger.warning("发现服务已经在运行")
            return
        
        self.running = True
        
        # 启动发现线程
        self.discovery_thread = threading.Thread(target=self._discovery_loop, daemon=True)
        self.discovery_thread.start()
        
        # 启动公告线程
        self.announcement_thread = threading.Thread(target=self._announcement_loop, daemon=True)
        self.announcement_thread.start()
        
        logger.info("局域网发现服务已启动")
    
    def stop(self):
        """停止发现服务"""
        self.running = False
        if self.discovery_thread:
            self.discovery_thread.join(timeout=5)
        if self.announcement_thread:
            self.announcement_thread.join(timeout=5)
        logger.info("局域网发现服务已停止")
    
    def _discovery_loop(self):
        """发现循环"""
        while self.running:
            try:
                # 创建UDP套接字用于接收mDNS查询
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind(('0.0.0.0', 5353))
                sock.settimeout(1)
                
                try:
                    data, addr = sock.recvfrom(1024)
                    self._process_mdns_query(data, addr)
                except socket.timeout:
                    pass
                except Exception as e:
                    logger.error(f"处理mDNS查询时出错: {str(e)}")
                finally:
                    sock.close()
            except Exception as e:
                logger.error(f"发现循环出错: {str(e)}")
            
            time.sleep(0.1)
    
    def _announcement_loop(self):
        """公告循环"""
        while self.running:
            try:
                self._send_announcement()
                time.sleep(30)  # 每30秒发送一次公告
            except Exception as e:
                logger.error(f"公告循环出错: {str(e)}")
                time.sleep(5)
    
    def _send_announcement(self):
        """发送服务公告"""
        try:
            # 创建UDP套接字
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            
            # 构建公告消息
            announcement = {
                'type': 'announcement',
                'service_name': self.service_name,
                'service_type': self.service_type,
                'port': self.port,
                'timestamp': datetime.now().isoformat(),
                'ip': self._get_local_ip()
            }
            
            # 发送到广播地址
            sock.sendto(json.dumps(announcement).encode('utf-8'), ('255.255.255.255', 5353))
            sock.close()
        except Exception as e:
            logger.error(f"发送公告时出错: {str(e)}")
    
    def _process_mdns_query(self, data, addr):
        """处理mDNS查询"""
        try:
            message = data.decode('utf-8')
            if 'announcement' in message:
                try:
                    announcement = json.loads(message)
                    if announcement.get('type') == 'announcement':
                        node_id = f"{announcement.get('ip')}:{announcement.get('port')}"
                        with self.lock:
                            self.nodes[node_id] = {
                                'ip': announcement.get('ip'),
                                'port': announcement.get('port'),
                                'service_name': announcement.get('service_name'),
                                'service_type': announcement.get('service_type'),
                                'last_seen': datetime.now().isoformat()
                            }
                        logger.debug(f"发现新节点: {node_id}")
                except json.JSONDecodeError:
                    pass
        except Exception as e:
            logger.error(f"处理mDNS查询时出错: {str(e)}")
    
    def _get_local_ip(self):
        """获取本地IP地址"""
        try:
            # 创建一个UDP套接字，连接到一个外部地址，然后获取本地地址
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.connect(('8.8.8.8', 80))
            local_ip = sock.getsockname()[0]
            sock.close()
            return local_ip
        except Exception as e:
            logger.error(f"获取本地IP时出错: {str(e)}")
            return '127.0.0.1'
    
    def get_nodes(self):
        """获取发现的节点列表"""
        with self.lock:
            # 过滤掉超过5分钟没有更新的节点
            current_time = datetime.now()
            valid_nodes = {}
            for node_id, node_info in self.nodes.items():
                last_seen = datetime.fromisoformat(node_info['last_seen'])
                if (current_time - last_seen).total_seconds() < 300:  # 5分钟
                    valid_nodes[node_id] = node_info
            
            # 更新节点列表
            self.nodes = valid_nodes
            return list(valid_nodes.values())
    
    def get_node_by_ip(self, ip):
        """根据IP获取节点信息"""
        with self.lock:
            for node_info in self.nodes.values():
                if node_info['ip'] == ip:
                    return node_info
            return None
    
    def clear_nodes(self):
        """清空节点列表"""
        with self.lock:
            self.nodes.clear()
        logger.info("节点列表已清空")

if __name__ == "__main__":
    # 测试代码
    discovery = LANDiscovery()
    discovery.start()
    
    try:
        while True:
            nodes = discovery.get_nodes()
            print(f"发现的节点: {nodes}")
            time.sleep(5)
    except KeyboardInterrupt:
        discovery.stop()
        print("测试结束")
