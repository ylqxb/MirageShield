# © 2026 MirageShield 团队 版权所有，侵权必究
# 本项目已申请发明专利，未经许可禁止商用
# AI-3 Watcher 智能体
import os
import sys
import json
import logging
import time
import random
import asyncio
import hashlib
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s:%(funcName)s:%(lineno)d - %(message)s'
)
logger = logging.getLogger('agents.ai3.watcher')

# 导入消息队列管理器
def get_message_queue_manager():
    """获取消息队列管理器实例"""
    try:
        from utils.config import get_config
        use_mock = get_config('use_mock_message_queue', True)
        if use_mock:
            from utils.mock_message_queue import MockMessageQueueManager
            return MockMessageQueueManager()
        else:
            from utils.message_queue import message_queue_manager
            return message_queue_manager
    except ImportError:
        logger.warning("消息队列模块导入失败，使用简化实现")
        import asyncio
        
        class SimpleMockMessageQueueManager:
            """简化模拟消息队列管理器"""
            async def send_message(self, agent_name, message):
                """发送消息"""
                logger.debug(f"发送消息到 {agent_name}: {message}")
            
            def register_agent(self, agent_name, handler=None):
                """注册智能体"""
                pass
            
            async def receive_message(self, agent_name):
                """接收消息"""
                return None
            
            async def start_processing(self):
                """开始处理消息"""
                pass
            
            async def stop_processing(self):
                """停止处理消息"""
                pass
            
            def get_queue_size(self, agent_name):
                """获取队列大小"""
                return 0
        
        return SimpleMockMessageQueueManager()

# 获取消息队列管理器实例
message_queue_manager = get_message_queue_manager()

class InvisibilityModule:
    """隐身机制子模块"""
    def __init__(self, watcher_agent):
        """初始化隐身机制"""
        self.watcher_agent = watcher_agent
        # 先初始化基本属性
        self.identity_change_interval = 300  # 身份变换间隔（秒）
        self.min_behavior_similarity = 0.7  # 行为相似度阈值
        self.learning_rate = 0.1  # 学习率
        
        # 初始化环境感知
        environmental_awareness = {
            'network_load': 'normal',
            'attack_activity': 'low',
            'system_resources': 'sufficient'
        }
        
        # 生成行为模式（使用初始环境感知）
        behavior_patterns = self._generate_behavior_patterns(environmental_awareness)
        
        # 初始化隐身状态
        self.stealth_status = {
            'enabled': True,
            'current_identity': self._generate_random_identity(),
            'last_identity_change': datetime.now().isoformat(),
            'behavior_patterns': behavior_patterns,
            'detection_risk': 0.0,
            'evasion_tactics': [],
            'learning_history': [],
            'adaptive_parameters': {
                'camouflage_intensity': 0.3,
                'noise_intensity': 0.1,
                'identity_change_frequency': 300,
                'evasion_threshold': 0.6
            },
            'environmental_awareness': environmental_awareness
        }
        
        logger.info("隐身机制子模块初始化完成")
    
    def _generate_random_identity(self):
        """生成随机身份"""
        return {
            'agent_id': f"watcher_{random.randint(10000, 99999)}",
            'network_signature': hashlib.sha256(str(random.random()).encode('utf-8')).hexdigest()[:16],
            'communication_pattern': random.choice(['periodic', 'bursty', 'random']),
            'response_delay': random.uniform(0.1, 1.5),
            'probe_frequency': random.uniform(0.1, 0.5),
            'operating_system': random.choice(['Windows', 'Linux', 'macOS']),
            'network_role': random.choice(['client', 'server', 'router'])
        }
    
    def _generate_behavior_patterns(self, environmental_awareness=None):
        """生成行为模式"""
        # 基于环境感知生成行为模式
        if environmental_awareness is None:
            environmental_awareness = self.stealth_status['environmental_awareness']
        
        network_load = environmental_awareness['network_load']
        
        if network_load == 'high':
            # 网络负载高时，生成更保守的行为模式
            base_packet_rate = random.uniform(5, 30)
            base_byte_rate = random.uniform(500, 3000)
            base_connection_count = random.randint(1, 10)
        elif network_load == 'low':
            # 网络负载低时，生成更活跃的行为模式
            base_packet_rate = random.uniform(20, 70)
            base_byte_rate = random.uniform(2000, 7000)
            base_connection_count = random.randint(5, 30)
        else:
            # 正常网络负载
            base_packet_rate = random.uniform(10, 50)
            base_byte_rate = random.uniform(1000, 5000)
            base_connection_count = random.randint(3, 20)
        
        return {
            'normal_traffic': {
                'packet_rate': base_packet_rate,
                'byte_rate': base_byte_rate,
                'connection_count': base_connection_count,
                'port_activity': {port: random.uniform(0.05, 0.5) for port in getattr(self.watcher_agent, 'monitored_ports', [])},
                'protocol_distribution': {
                    'TCP': random.uniform(0.6, 0.8),
                    'UDP': random.uniform(0.1, 0.3),
                    'ICMP': random.uniform(0.05, 0.1)
                }
            },
            'background_noise': {
                'frequency': random.uniform(0.1, 0.3),
                'intensity': random.uniform(0.01, 0.1),
                'patterns': ['random', 'periodic', 'bursty']
            },
            'time_based_patterns': {
                'day': {
                    'packet_rate': base_packet_rate * 1.2,
                    'connection_count': base_connection_count * 1.2
                },
                'night': {
                    'packet_rate': base_packet_rate * 0.8,
                    'connection_count': base_connection_count * 0.8
                }
            }
        }
    
    def camouflage_behavior(self, network_data):
        """伪装行为"""
        if not self.stealth_status['enabled']:
            return network_data
        
        # 应用时间基于模式
        current_hour = datetime.now().hour
        time_pattern = 'day' if 6 <= current_hour <= 18 else 'night'
        time_adjustments = self.stealth_status['behavior_patterns']['time_based_patterns'][time_pattern]
        
        # 应用正常流量模式
        normal_pattern = self.stealth_status['behavior_patterns']['normal_traffic']
        camouflage_intensity = self.stealth_status['adaptive_parameters']['camouflage_intensity']
        
        # 调整数据包率（考虑时间因素）
        if normal_pattern.get('packet_rate', 0) > 0 and camouflage_intensity > 0 and camouflage_intensity <= 1.0:
            network_data['packet_rate'] = (
                network_data['packet_rate'] * (1 - camouflage_intensity) + 
                normal_pattern['packet_rate'] * camouflage_intensity * time_adjustments['packet_rate']
            )
        
        # 调整字节率（考虑时间因素）
        if normal_pattern.get('byte_rate', 0) > 0 and camouflage_intensity > 0 and camouflage_intensity <= 1.0:
            network_data['byte_rate'] = (
                network_data['byte_rate'] * (1 - camouflage_intensity) + 
                normal_pattern['byte_rate'] * camouflage_intensity * time_adjustments['byte_rate']
            )
        
        # 调整连接数（考虑时间因素）
        if normal_pattern.get('connection_count', 0) > 0 and camouflage_intensity > 0 and camouflage_intensity <= 1.0:
            network_data['connection_count'] = int(
                network_data['connection_count'] * (1 - camouflage_intensity) + 
                normal_pattern['connection_count'] * camouflage_intensity * time_adjustments['connection_count']
            )
        
        # 调整端口活动
        if 'port_activity' in network_data and camouflage_intensity > 0 and camouflage_intensity <= 1.0:
            for port in self.watcher_agent.monitored_ports:
                network_data['port_activity'][port] = (
                    network_data['port_activity'][port] * (1 - camouflage_intensity) + 
                    normal_pattern['port_activity'].get(port, 0.1) * camouflage_intensity
                )
        elif 'port_activity' not in network_data and camouflage_intensity > 0 and camouflage_intensity <= 1.0:
            # 如果port_activity不存在，创建一个新的
            network_data['port_activity'] = {}
            for port in self.watcher_agent.monitored_ports:
                network_data['port_activity'][port] = normal_pattern['port_activity'].get(port, 0.1) * camouflage_intensity
        
        # 添加背景噪声
        noise_pattern = self.stealth_status['behavior_patterns']['background_noise']
        noise_intensity = self.stealth_status['adaptive_parameters']['noise_intensity']
        if random.random() < noise_pattern['frequency']:
            # 根据噪声模式选择不同的噪声类型
            noise_type = random.choice(noise_pattern['patterns'])
            if noise_type == 'random':
                network_data['packet_rate'] *= (1 + random.uniform(-noise_intensity, noise_intensity))
                network_data['byte_rate'] *= (1 + random.uniform(-noise_intensity, noise_intensity))
            elif noise_type == 'periodic':
                # 周期性噪声
                if datetime.now().second % 10 < 2:
                    network_data['packet_rate'] *= (1 + noise_intensity)
            elif noise_type == 'bursty':
                # 突发噪声
                if random.random() < 0.1:
                    network_data['packet_rate'] *= (1 + noise_intensity * 2)
        
        return network_data
    
    def transform_identity(self):
        """变换身份"""
        if not self.stealth_status['enabled']:
            return
        
        current_time = datetime.now().timestamp()
        try:
            last_change = datetime.fromisoformat(self.stealth_status['last_identity_change']).timestamp()
        except ValueError:
            # 时间戳格式错误，使用当前时间
            logger.warning("时间戳格式错误，使用当前时间作为默认值")
            last_change = current_time
        
        # 基于环境和风险调整变换间隔
        attack_activity = self.stealth_status['environmental_awareness']['attack_activity']
        if attack_activity == 'high':
            # 攻击活动高时，缩短身份变换间隔
            current_interval = max(60, self.stealth_status['adaptive_parameters']['identity_change_frequency'] / 2)
        elif attack_activity == 'low':
            # 攻击活动低时，延长身份变换间隔
            current_interval = min(600, self.stealth_status['adaptive_parameters']['identity_change_frequency'] * 1.5)
        else:
            current_interval = self.stealth_status['adaptive_parameters']['identity_change_frequency']
        
        if current_time - last_change >= current_interval:
            old_identity = self.stealth_status['current_identity']
            self.stealth_status['current_identity'] = self._generate_random_identity()
            self.stealth_status['last_identity_change'] = datetime.now().isoformat()
            self.stealth_status['behavior_patterns'] = self._generate_behavior_patterns()
            logger.info(f"守望者身份已变换: {old_identity['agent_id']} → {self.stealth_status['current_identity']['agent_id']}")
    
    def detect_detection(self, network_data):
        """检测是否被攻击者检测"""
        # 分析网络数据，检测是否有针对守望者的探测
        detection_signs = 0
        
        # 1. 检测针对特定端口的集中探测
        port_activity = network_data.get('port_activity', {})
        high_activity_ports = [port for port, activity in port_activity.items() if activity > 1.0]
        if len(high_activity_ports) > len(self.watcher_agent.monitored_ports) * 0.8:
            detection_signs += 1
        
        # 2. 检测异常的连接模式
        connection_count = network_data.get('connection_count', 0)
        if connection_count > 50:
            detection_signs += 1
        
        # 3. 检测突发流量
        packet_rate = network_data.get('packet_rate', 0)
        if packet_rate > 200:
            detection_signs += 1
        
        # 4. 检测扫描模式
        if len(high_activity_ports) > len(self.watcher_agent.monitored_ports) * 0.6:
            # 检查是否是顺序扫描
            sorted_ports = sorted(high_activity_ports)
            is_sequential = True
            for i in range(1, len(sorted_ports)):
                if sorted_ports[i] - sorted_ports[i-1] > 5:
                    is_sequential = False
                    break
            if is_sequential:
                detection_signs += 1
        
        # 5. 检测针对特定协议的探测
        if 'protocol_distribution' in network_data:
            protocol_dist = network_data['protocol_distribution']
            if protocol_dist.get('TCP', 0) > 0.9:
                detection_signs += 1
        
        # 计算检测风险
        self.stealth_status['detection_risk'] = min(detection_signs / 5.0, 1.0)
        
        # 更新环境感知
        if self.stealth_status['detection_risk'] > 0.7:
            self.stealth_status['environmental_awareness']['attack_activity'] = 'high'
        elif self.stealth_status['detection_risk'] > 0.3:
            self.stealth_status['environmental_awareness']['attack_activity'] = 'medium'
        else:
            self.stealth_status['environmental_awareness']['attack_activity'] = 'low'
        
        return self.stealth_status['detection_risk'] > self.stealth_status['adaptive_parameters']['evasion_threshold']
    
    def execute_evasion(self):
        """执行规避策略"""
        if not self.stealth_status['enabled']:
            return
        
        # 基于检测风险选择规避策略
        risk_level = self.stealth_status['detection_risk']
        
        if risk_level > 0.8:
            # 高风险：使用更积极的规避策略
            evasion_tactics = [
                self._evade_by_network_hop,
                self._evade_by_deep_camouflage,
                self._evade_by_disguise
            ]
        elif risk_level > 0.6:
            # 中等风险：使用标准规避策略
            evasion_tactics = [
                self._evade_by_slowdown,
                self._evade_by_diversion,
                self._evade_by_mimicry
            ]
        else:
            # 低风险：使用轻微规避策略
            evasion_tactics = [
                self._evade_by_noise_injection,
                self._evade_by_pattern_shift
            ]
        
        # 随机选择一个规避策略
        tactic = random.choice(evasion_tactics)
        tactic()
        
        # 记录使用的规避策略
        tactic_name = tactic.__name__[1:]  # 移除下划线前缀
        self.stealth_status['evasion_tactics'].append({
            'tactic': tactic_name,
            'timestamp': datetime.now().isoformat(),
            'detection_risk': self.stealth_status['detection_risk'],
            'risk_level': 'high' if risk_level > 0.8 else 'medium' if risk_level > 0.6 else 'low'
        })
        
        # 限制规避策略记录数量
        if len(self.stealth_status['evasion_tactics']) > 20:
            self.stealth_status['evasion_tactics'] = self.stealth_status['evasion_tactics'][-20:]
        
        # 学习和适应
        self._learn_from_evasion(tactic_name, risk_level)
    
    def _evade_by_slowdown(self):
        """通过降低活动频率进行规避"""
        logger.info("执行规避策略: 降低活动频率")
        # 临时增加监控间隔
        self.watcher_agent.monitor_interval = min(self.watcher_agent.monitor_interval * 2, 30)
        # 降低行为模式强度
        for key in self.stealth_status['behavior_patterns']['normal_traffic']:
            if isinstance(self.stealth_status['behavior_patterns']['normal_traffic'][key], (int, float)):
                self.stealth_status['behavior_patterns']['normal_traffic'][key] *= 0.5
    
    def _evade_by_diversion(self):
        """通过分散注意力进行规避"""
        logger.info("执行规避策略: 分散注意力")
        # 生成虚假的网络活动
        # 这里可以通知Baiter智能体部署更多蜜罐
        asyncio.create_task(
            self._safe_notify_agent('baiter', {'action': 'deploy_deception', 'level': 'high'})
        )
    
    def _evade_by_mimicry(self):
        """通过模仿正常流量进行规避"""
        logger.info("执行规避策略: 模仿正常流量")
        # 重新生成行为模式，更接近正常流量
        self.stealth_status['behavior_patterns'] = self._generate_behavior_patterns()
        # 立即变换身份
        self.stealth_status['current_identity'] = self._generate_random_identity()
        self.stealth_status['last_identity_change'] = datetime.now().isoformat()
    
    def _evade_by_network_hop(self):
        """通过网络跳变进行规避"""
        logger.info("执行规避策略: 网络跳变")
        # 模拟网络跳变，更换网络路径
        # 这里可以通知网络管理智能体进行网络路径调整
        asyncio.create_task(
            self._safe_notify_agent('network_manager', {'action': 'change_network_path', 'priority': 'high'})
        )
        # 立即变换身份
        self.stealth_status['current_identity'] = self._generate_random_identity()
        self.stealth_status['last_identity_change'] = datetime.now().isoformat()
    
    def _evade_by_deep_camouflage(self):
        """通过深度伪装进行规避"""
        logger.info("执行规避策略: 深度伪装")
        # 增加伪装强度
        self.stealth_status['adaptive_parameters']['camouflage_intensity'] = min(0.8, self.stealth_status['adaptive_parameters']['camouflage_intensity'] + 0.2)
        # 增加噪声强度
        self.stealth_status['adaptive_parameters']['noise_intensity'] = min(0.2, self.stealth_status['adaptive_parameters']['noise_intensity'] + 0.05)
        # 重新生成行为模式
        self.stealth_status['behavior_patterns'] = self._generate_behavior_patterns()
    
    def _evade_by_disguise(self):
        """通过伪装成其他设备进行规避"""
        logger.info("执行规避策略: 设备伪装")
        # 生成完全不同类型的身份
        new_identity = self._generate_random_identity()
        # 确保新身份与旧身份有显著差异
        while new_identity['operating_system'] == self.stealth_status['current_identity']['operating_system'] and \
              new_identity['network_role'] == self.stealth_status['current_identity']['network_role']:
            new_identity = self._generate_random_identity()
        self.stealth_status['current_identity'] = new_identity
        self.stealth_status['last_identity_change'] = datetime.now().isoformat()
        # 重新生成行为模式以匹配新身份
        self.stealth_status['behavior_patterns'] = self._generate_behavior_patterns()
    
    def _evade_by_noise_injection(self):
        """通过注入噪声进行规避"""
        logger.info("执行规避策略: 注入噪声")
        # 临时增加噪声强度
        original_noise = self.stealth_status['adaptive_parameters']['noise_intensity']
        self.stealth_status['adaptive_parameters']['noise_intensity'] = min(0.3, original_noise + 0.1)
        # 30秒后恢复
        asyncio.create_task(self._restore_noise_intensity(original_noise))
    
    def _evade_by_pattern_shift(self):
        """通过模式转移进行规避"""
        logger.info("执行规避策略: 模式转移")
        # 随机改变通信模式
        current_pattern = self.stealth_status['current_identity']['communication_pattern']
        new_patterns = [p for p in ['periodic', 'bursty', 'random'] if p != current_pattern]
        if new_patterns:
            self.stealth_status['current_identity']['communication_pattern'] = random.choice(new_patterns)
            logger.info(f"通信模式已更改为: {self.stealth_status['current_identity']['communication_pattern']}")
    
    async def _safe_notify_agent(self, agent_name, message):
        """安全地通知其他智能体"""
        try:
            # 直接使用message_queue_manager发送消息，避免依赖WatcherAgent的方法
            # 这样可以消除潜在的循环依赖风险，简化代码结构
            await message_queue_manager.send_message(agent_name, message)
        except Exception as e:
            logger.error(f"通知 {agent_name} 智能体失败: {str(e)}")
    
    async def _restore_noise_intensity(self, original_value):
        """恢复噪声强度"""
        try:
            await asyncio.sleep(30)
            self.stealth_status['adaptive_parameters']['noise_intensity'] = original_value
            logger.info("噪声强度已恢复")
        except Exception as e:
            logger.error(f"恢复噪声强度失败: {str(e)}")
    
    def _learn_from_evasion(self, tactic_name, risk_level):
        """从规避行为中学习"""
        # 记录学习历史
        self.stealth_status['learning_history'].append({
            'tactic': tactic_name,
            'risk_level': risk_level,
            'timestamp': datetime.now().isoformat(),
            'outcome': 'success'  # 简化处理，实际应该根据后续检测结果评估
        })
        
        # 限制学习历史数量
        if len(self.stealth_status['learning_history']) > 50:
            self.stealth_status['learning_history'] = self.stealth_status['learning_history'][-50:]
        
        # 分析学习历史，调整参数
        if len(self.stealth_status['learning_history']) >= 10:
            # 计算不同策略的成功率
            tactic_success = {}
            for entry in self.stealth_status['learning_history']:
                if entry['tactic'] not in tactic_success:
                    tactic_success[entry['tactic']] = {'count': 0, 'success': 0}
                tactic_success[entry['tactic']]['count'] += 1
                if entry['outcome'] == 'success':
                    tactic_success[entry['tactic']]['success'] += 1
            
            # 调整参数基于学习结果
            for tactic, stats in tactic_success.items():
                success_rate = stats['success'] / stats['count']
                if success_rate < 0.5:
                    # 成功率低，减少使用该策略
                    logger.info(f"策略 {tactic} 成功率低 ({success_rate:.2f})，将减少使用")
                elif success_rate > 0.8:
                    # 成功率高，增加使用该策略
                    logger.info(f"策略 {tactic} 成功率高 ({success_rate:.2f})，将增加使用")
    
    def update_environmental_awareness(self, network_data):
        """更新环境感知"""
        # 基于网络数据更新环境感知
        packet_rate = network_data.get('packet_rate', 0)
        connection_count = network_data.get('connection_count', 0)
        
        # 更新网络负载
        if packet_rate > 100 or connection_count > 50:
            self.stealth_status['environmental_awareness']['network_load'] = 'high'
        elif packet_rate < 20 and connection_count < 10:
            self.stealth_status['environmental_awareness']['network_load'] = 'low'
        else:
            self.stealth_status['environmental_awareness']['network_load'] = 'normal'
        
        # 这里可以添加更多环境感知的更新逻辑
        # 例如系统资源使用情况、其他智能体的状态等
    
    def get_stealth_status(self):
        """获取隐身状态"""
        return self.stealth_status

class WatcherAgent:
    def __init__(self, config_file='config/watcher_config.json'):
        """初始化Watcher智能体"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            
            self.agent_name = self.config['agent']['name']
            self.agent_version = self.config['agent']['version']
            self.network_interfaces = self.config['network']['interfaces']
            self.monitored_ports = self.config['network']['monitored_ports']
            self.monitor_interval = self.config['mcp_integrations']['network_monitor']['config']['monitor_interval']
            
            # 初始化状态
            self.network_baseline = {}
            self.attacker_fingerprints = {}
            self.threat_assessments = {}
            self.active_responses = {}
            
            # 初始化缓存
            self.fingerprint_cache = {}
            self.cache_timeout = 300  # 缓存超时时间（秒）
            
            # 初始化MCP集成
            self.mcp_integrations = {
                'network_monitor': self.config['mcp_integrations']['network_monitor']['enabled'],
                'attacker_analyzer': self.config['mcp_integrations']['attacker_analyzer']['enabled'],
                'psychological_warfare': self.config['mcp_integrations']['psychological_warfare']['enabled'],
                'threat_assessment': self.config['mcp_integrations']['threat_assessment']['enabled']
            }
            
            # 初始化网络基线
            self._initialize_network_baseline()
            
            # 初始化隐身机制
            self.invisibility_module = InvisibilityModule(self)
            
            logger.info(f"{self.agent_name} 智能体初始化完成")
            
        except Exception as e:
            logger.error(f"初始化失败: {str(e)}")
            raise
    
    def _initialize_network_baseline(self):
        """初始化网络行为基线"""
        for interface in self.network_interfaces:
            self.network_baseline[interface] = {
                'packet_rate': random.uniform(10, 100),
                'byte_rate': random.uniform(1000, 10000),
                'connection_count': random.randint(5, 50),
                'port_activity': {port: random.uniform(0.1, 1.0) for port in self.monitored_ports},
                'last_updated': datetime.now().isoformat()
            }
    
    async def monitor_network(self):
        """监控网络行为"""
        logger.info("开始监控网络行为")
        
        while True:
            try:
                # 执行身份变换
                self.invisibility_module.transform_identity()
                
                # 每5次循环输出一次隐身状态
                if random.randint(1, 5) == 1:
                    stealth_status = self.invisibility_module.get_stealth_status()
                    logger.info(f"隐身状态: 身份={stealth_status['current_identity']['agent_id']}, 检测风险={stealth_status['detection_risk']:.2f}, 网络负载={stealth_status['environmental_awareness']['network_load']}, 攻击活动={stealth_status['environmental_awareness']['attack_activity']}")
                
                for interface in self.network_interfaces:
                    # 模拟网络数据采集
                    current_data = {
                        'packet_rate': random.uniform(5, 150),
                        'byte_rate': random.uniform(500, 15000),
                        'connection_count': random.randint(1, 100),
                        'port_activity': {port: random.uniform(0, 1.5) for port in self.monitored_ports},
                        'timestamp': datetime.now().isoformat(),
                        'protocol_distribution': {
                            'TCP': random.uniform(0.5, 0.9),
                            'UDP': random.uniform(0.05, 0.3),
                            'ICMP': random.uniform(0.01, 0.15)
                        }
                    }
                    
                    # 更新环境感知
                    self.invisibility_module.update_environmental_awareness(current_data)
                    
                    # 应用行为伪装
                    camouflaged_data = self.invisibility_module.camouflage_behavior(current_data)
                    
                    # 检测是否被攻击者检测
                    if self.invisibility_module.detect_detection(camouflaged_data):
                        logger.warning("检测到被攻击者探测，执行规避策略")
                        self.invisibility_module.execute_evasion()
                    
                    # 检测异常
                    anomaly = self._detect_anomaly(interface, camouflaged_data)
                    if anomaly:
                        logger.warning(f"检测到网络异常: {anomaly}")
                        # 分析攻击者
                        attacker_info = await self.analyze_attacker(camouflaged_data)
                        if attacker_info:
                            # 评估威胁
                            threat_level = self.assess_threat(attacker_info)
                            # 执行响应
                            await self.execute_response(threat_level, attacker_info)
                    
                    # 更新基线
                    self._update_baseline(interface, camouflaged_data)
                
                await asyncio.sleep(self.monitor_interval)
                
            except Exception as e:
                logger.error(f"网络监控出错: {str(e)}")
                await asyncio.sleep(self.monitor_interval)
    
    def _detect_anomaly(self, interface, current_data):
        """检测网络异常"""
        baseline = self.network_baseline[interface]
        
        # 基于模式检测的异常检测算法
        # 1. 计算基本指标差异
        packet_rate_diff = abs(current_data['packet_rate'] - baseline['packet_rate']) / max(baseline['packet_rate'], 1)
        byte_rate_diff = abs(current_data['byte_rate'] - baseline['byte_rate']) / max(baseline['byte_rate'], 1)
        connection_diff = abs(current_data['connection_count'] - baseline['connection_count']) / max(baseline['connection_count'], 1)
        
        # 2. 端口活动异常检测
        port_anomalies = []
        port_anomaly_count = 0
        for port in self.monitored_ports:
            port_diff = abs(current_data['port_activity'][port] - baseline['port_activity'][port]) / max(baseline['port_activity'][port], 0.1)
            if port_diff > 2.0:
                port_anomalies.append(f"端口 {port} 活动异常")
                port_anomaly_count += 1
        
        # 3. 快速检测模式
        # 检测突发模式
        burst_detection = current_data['packet_rate'] > baseline['packet_rate'] * 5
        
        # 检测扫描模式
        scan_detection = port_anomaly_count > len(self.monitored_ports) * 0.6
        
        # 检测DDoS模式
        ddos_detection = packet_rate_diff > 5.0 and byte_rate_diff > 3.0
        
        # 检测异常连接模式
        connection_pattern_anomaly = connection_diff > 4.0
        
        # 4. 综合判断
        if burst_detection or scan_detection or ddos_detection or connection_pattern_anomaly:
            anomaly = {
                'interface': interface,
                'timestamp': current_data['timestamp'],
                'packet_rate_anomaly': packet_rate_diff > 3.0,
                'byte_rate_anomaly': byte_rate_diff > 3.0,
                'connection_anomaly': connection_diff > 3.0,
                'port_anomalies': port_anomalies,
                'burst_detection': burst_detection,
                'scan_detection': scan_detection,
                'ddos_detection': ddos_detection,
                'connection_pattern_anomaly': connection_pattern_anomaly
            }
            return anomaly
        
        return None
    
    def _update_baseline(self, interface, current_data):
        """更新网络行为基线"""
        # 平滑更新基线
        alpha = 0.1  # 学习率
        baseline = self.network_baseline[interface]
        
        baseline['packet_rate'] = baseline['packet_rate'] * (1 - alpha) + current_data['packet_rate'] * alpha
        baseline['byte_rate'] = baseline['byte_rate'] * (1 - alpha) + current_data['byte_rate'] * alpha
        baseline['connection_count'] = int(baseline['connection_count'] * (1 - alpha) + current_data['connection_count'] * alpha)
        
        for port in self.monitored_ports:
            baseline['port_activity'][port] = baseline['port_activity'][port] * (1 - alpha) + current_data['port_activity'][port] * alpha
        
        baseline['last_updated'] = current_data['timestamp']
    
    async def analyze_attacker(self, network_data):
        """分析攻击者"""
        if not self.mcp_integrations['attacker_analyzer']:
            return None
        
        # 生成缓存键，使用json.dumps确保字典顺序一致
        cache_key = hashlib.sha256(json.dumps(network_data, sort_keys=True).encode('utf-8')).hexdigest()
        
        # 检查缓存
        current_time = datetime.now().timestamp()
        if cache_key in self.fingerprint_cache:
            cached_data = self.fingerprint_cache[cache_key]
            if current_time - cached_data['timestamp'] < self.cache_timeout:
                logger.info("使用缓存的攻击者分析结果")
                return cached_data['result']
        
        logger.info("分析攻击者行为")
        
        # 生成攻击者ID
        attacker_id = f"attacker_{random.randint(1000, 9999)}"
        
        # 基于网络数据提取真实的指纹
        # 1. 分析端口活动模式
        port_activities = network_data.get('port_activity', {})
        active_ports = [port for port, activity in port_activities.items() if activity > 0.5]
        
        # 2. 确定扫描模式
        scan_pattern = 'random'
        if len(active_ports) > 0:
            # 检查是否是顺序扫描
            sorted_ports = sorted(active_ports)
            is_sequential = True
            for i in range(1, len(sorted_ports)):
                if sorted_ports[i] - sorted_ports[i-1] > 5:
                    is_sequential = False
                    break
            
            if is_sequential:
                scan_pattern = 'sequential'
            elif len(active_ports) >= len(self.monitored_ports) * 0.8:
                scan_pattern = 'strobe'
        
        # 3. 分析连接率
        connection_rate = network_data.get('connection_count', 0) / 10.0
        
        # 4. 分析数据包大小分布
        packet_sizes = []
        if connection_rate > 5:
            # 模拟不同攻击类型的数据包大小
            if scan_pattern == 'strobe':
                # DDoS攻击通常使用小数据包
                packet_sizes = [40 for _ in range(10)]
            else:
                # 其他攻击类型
                packet_sizes = [random.randint(40, 1500) for _ in range(10)]
        else:
            # 正常流量
            packet_sizes = [random.randint(60, 1000) for _ in range(10)]
        
        # 5. 提取指纹
        fingerprint = {
            'source_ip': f"192.168.1.{random.randint(100, 200)}",
            'port_scan_pattern': scan_pattern,
            'connection_rate': connection_rate,
            'packet_size_distribution': packet_sizes,
            'timestamp': datetime.now().isoformat(),
            'ddos_detection': network_data.get('ddos_detection', False),
            'connection_pattern_anomaly': network_data.get('connection_pattern_anomaly', False)
        }
        
        # 6. 确定攻击类型
        attack_type = 'port_scan'
        if connection_rate > 10:
            attack_type = 'ddos'
        elif len(active_ports) == 1 and active_ports[0] in [22, 3389]:
            attack_type = 'brute_force'
        elif connection_rate > 5:
            attack_type = 'exploit'
        elif network_data.get('connection_pattern_anomaly', False):
            attack_type = 'apt'
        elif any('443' in str(port) for port in active_ports):
            attack_type = 'ssl_flood'
        
        # 7. 计算置信度
        confidence = 0.5
        if attack_type == 'ddos' and connection_rate > 15:
            confidence = 0.9
        elif attack_type == 'brute_force' and len(active_ports) == 1:
            confidence = 0.85
        elif attack_type == 'exploit' and connection_rate > 7:
            confidence = 0.8
        elif attack_type == 'port_scan' and len(active_ports) > len(self.monitored_ports) * 0.6:
            confidence = 0.75
        elif attack_type == 'apt' and network_data.get('connection_pattern_anomaly', False):
            confidence = 0.95
        elif attack_type == 'ssl_flood' and 443 in active_ports:
            confidence = 0.8
        
        # 8. 构建威胁画像
        threat_profile = {
            'attacker_id': attacker_id,
            'fingerprint': fingerprint,
            'attack_type': attack_type,
            'confidence': confidence,
            'targets': active_ports or self.monitored_ports,
            'timestamp': datetime.now().isoformat(),
            'severity': self._calculate_severity(attack_type, confidence)
        }
        
        # 9. 存储攻击者信息
        self.attacker_fingerprints[attacker_id] = threat_profile
        
        # 10. 缓存结果
        self.fingerprint_cache[cache_key] = {
            'result': threat_profile,
            'timestamp': current_time
        }
        
        # 清理过期缓存
        self._cleanup_cache()
        
        logger.info(f"攻击者分析完成: {attacker_id}, 攻击类型: {attack_type}, 置信度: {confidence:.2f}, 严重程度: {threat_profile['severity']}")
        return threat_profile
    
    def _cleanup_cache(self):
        """清理过期缓存"""
        current_time = datetime.now().timestamp()
        expired_keys = []
        
        for key, data in self.fingerprint_cache.items():
            if current_time - data['timestamp'] >= self.cache_timeout:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.fingerprint_cache[key]
        
        if expired_keys:
            logger.info(f"清理了 {len(expired_keys)} 个过期缓存")
    
    def _calculate_severity(self, attack_type, confidence):
        """计算攻击严重程度"""
        severity_scores = {
            'port_scan': 2,
            'brute_force': 4,
            'exploit': 6,
            'ddos': 8,
            'apt': 10,
            'ssl_flood': 7
        }
        
        base_score = severity_scores.get(attack_type, 3)
        # 根据置信度调整分数
        adjusted_score = base_score * confidence
        
        if adjusted_score < 3:
            return 'low'
        elif adjusted_score < 6:
            return 'medium'
        elif adjusted_score < 8:
            return 'high'
        else:
            return 'critical'
    
    def assess_threat(self, attacker_info):
        """评估威胁等级"""
        if not self.mcp_integrations['threat_assessment']:
            return 'low'
        
        logger.info("评估威胁等级")
        
        # 计算威胁置信度
        confidence = attacker_info['confidence']
        
        # 根据置信度确定威胁等级
        thresholds = self.config['mcp_integrations']['threat_assessment']['config']['confidence_thresholds']
        
        if confidence < thresholds['low']:
            threat_level = 'low'
        elif confidence < thresholds['medium']:
            threat_level = 'medium'
        elif confidence < thresholds['high']:
            threat_level = 'high'
        elif confidence < thresholds['critical']:
            threat_level = 'critical'
        else:
            threat_level = 'extreme'
        
        # 存储威胁评估结果
        self.threat_assessments[attacker_info['attacker_id']] = {
            'threat_level': threat_level,
            'confidence': confidence,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"威胁评估完成: {threat_level} (置信度: {confidence:.2f})")
        return threat_level
    
    async def execute_response(self, threat_level, attacker_info):
        """执行响应措施"""
        if not self.mcp_integrations['psychological_warfare']:
            return
        
        logger.info(f"执行响应措施，威胁等级: {threat_level}")
        
        response_actions = {
            'low': self._respond_low,
            'medium': self._respond_medium,
            'high': self._respond_high,
            'critical': self._respond_critical,
            'extreme': self._respond_extreme
        }
        
        if threat_level in response_actions:
            await response_actions[threat_level](attacker_info)
        
        # 记录响应
        self.active_responses[attacker_info['attacker_id']] = {
            'threat_level': threat_level,
            'response_time': datetime.now().isoformat(),
            'status': 'completed'
        }
    
    async def _respond_low(self, attacker_info):
        """低威胁响应"""
        logger.info("执行低威胁响应: 记录事件")
        # 仅记录，无其他动作
        await asyncio.sleep(1)
    
    async def _respond_medium(self, attacker_info):
        """中威胁响应"""
        logger.info("执行中威胁响应: 启动诱饵强化")
        # 通知Baiter智能体增加假数据比例
        await self._notify_agent('baiter', {'action': 'increase_bait_ratio', 'ratio': 0.7})
        # 启动轻度网络监控
        await self._notify_agent('prober', {'action': 'start_monitoring', 'level': 'low'})
        await asyncio.sleep(2)
    
    async def _respond_high(self, attacker_info):
        """高威胁响应"""
        logger.info("执行高威胁响应: 启动心理战")
        # 执行一级/二级心理战
        await self._execute_psychological_warfare(2, attacker_info)
        # 通知Baiter智能体部署特定类型的蜜罐
        await self._notify_agent('baiter', {'action': 'deploy_honeypot', 'type': 'web_server'})
        # 启动中度网络监控
        await self._notify_agent('prober', {'action': 'start_monitoring', 'level': 'medium'})
        await asyncio.sleep(3)
    
    async def _respond_critical(self, attacker_info):
        """严重威胁响应"""
        logger.info("执行严重威胁响应: 网络整建迁移 + 三级心理战")
        # 执行网络整建迁移
        await self._execute_network_reconstruction()
        # 执行三级心理战
        await self._execute_psychological_warfare(3, attacker_info)
        # 通知Baiter智能体部署高级蜜罐
        await self._notify_agent('baiter', {'action': 'deploy_honeypot', 'type': 'database'})
        # 启动高级网络监控
        await self._notify_agent('prober', {'action': 'start_monitoring', 'level': 'high'})
        # 临时封锁可疑IP
        await self._block_ip(attacker_info['fingerprint']['source_ip'])
        await asyncio.sleep(5)
    
    async def _respond_extreme(self, attacker_info):
        """极严重威胁响应"""
        logger.info("执行极严重威胁响应: 社区联防 + 四级心理战 + 永久标记")
        # 执行社区联防
        await self._execute_community_defense(attacker_info)
        # 执行四级心理战
        await self._execute_psychological_warfare(4, attacker_info)
        # 永久标记攻击者
        await self._mark_attacker(attacker_info)
        # 启动全面网络隔离
        await self._execute_network_isolation()
        # 部署虚拟补丁
        await self._deploy_virtual_patch(attacker_info)
        # 永久封锁IP
        await self._block_ip(attacker_info['fingerprint']['source_ip'], permanent=True)
        await asyncio.sleep(10)
    
    async def _block_ip(self, ip, permanent=False):
        """封锁IP"""
        logger.info(f"{'永久' if permanent else '临时'}封锁IP: {ip}")
        # 模拟IP封锁
        await asyncio.sleep(1)
    
    async def _execute_network_isolation(self):
        """执行网络隔离"""
        logger.info("执行网络隔离")
        # 模拟网络隔离
        await asyncio.sleep(2)
    
    async def _deploy_virtual_patch(self, attacker_info):
        """部署虚拟补丁"""
        logger.info("部署虚拟补丁")
        # 模拟虚拟补丁部署
        await asyncio.sleep(1)
    
    async def _notify_agent(self, agent_name, message):
        """通知其他智能体"""
        logger.info(f"通知 {agent_name} 智能体: {message}")
        # 使用消息队列发送消息
        await message_queue_manager.send_message(agent_name, message)
        # 不再需要同步等待，消息会异步处理
    
    async def _execute_psychological_warfare(self, level, attacker_info):
        """执行心理战"""
        logger.info(f"执行 {level} 级心理战")
        # 模拟心理战执行
        await asyncio.sleep(2)
    
    async def _execute_network_reconstruction(self):
        """执行网络整建迁移"""
        logger.info("执行网络整建迁移")
        # 模拟网络整建迁移
        await asyncio.sleep(3)
    
    async def _execute_community_defense(self, attacker_info):
        """执行社区联防"""
        if not self.config['community']['enabled']:
            return
        
        logger.info("执行社区联防")
        # 模拟社区联防
        await asyncio.sleep(2)
    
    async def _mark_attacker(self, attacker_info):
        """永久标记攻击者"""
        logger.info("永久标记攻击者")
        # 模拟永久标记
        await asyncio.sleep(1)
    
    def get_network_status(self):
        """获取网络状态"""
        return {
            'baseline': self.network_baseline,
            'monitored_interfaces': self.network_interfaces,
            'monitored_ports': self.monitored_ports,
            'last_updated': datetime.now().isoformat()
        }
    
    def get_attacker_info(self, attacker_id=None):
        """获取攻击者信息"""
        if attacker_id:
            return self.attacker_fingerprints.get(attacker_id)
        return self.attacker_fingerprints
    
    def get_threat_assessments(self):
        """获取威胁评估结果"""
        return self.threat_assessments
    
    def get_active_responses(self):
        """获取活动响应"""
        return self.active_responses
    
    def get_stealth_status(self):
        """获取隐身状态"""
        return self.invisibility_module.get_stealth_status()
    
    async def run(self):
        """运行Watcher智能体"""
        logger.info("开始运行Watcher智能体")
        
        try:
            # 启动网络监控
            await self.monitor_network()
        except KeyboardInterrupt:
            logger.info("Watcher智能体停止运行")
        except Exception as e:
            logger.error(f"Watcher智能体运行出错: {str(e)}")
            raise

if __name__ == "__main__":
    # 测试代码
    watcher = WatcherAgent()
    asyncio.run(watcher.run())
