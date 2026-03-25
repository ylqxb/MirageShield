# © 2026 MirageShield 团队 版权所有，侵权必究
# 本项目已申请发明专利，未经许可禁止商用
# 联防接口模块社区联防接口
import json
import logging
import os
import hashlib
import time
import asyncio
from datetime import datetime
import requests

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s:%(funcName)s:%(lineno)d - %(message)s'
)
logger = logging.getLogger('community联防接口')

class CommunityDefenseInterface:
    def __init__(self, config_file=None):
        """初始化社区联防接口"""
        try:
            # 获取项目根目录
            self.root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
            # 加载配置文件
            if config_file and os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            else:
                # 默认配置
                self.config = {
                    "community": {
                        "api_endpoint": "https://security-community.example.com/api",
                        "api_key": "your_api_key_here",
                        "share_anonymized_data": True,
                        "sync_interval": 3600  # 秒
                    },
                    "local": {
                        "blacklist_file": os.path.join(self.root_dir, "data", "community", "blacklist.json"),
                        "threat_intel_file": os.path.join(self.root_dir, "data", "community", "threat_intel.json"),
                        "last_sync": None
                    }
                }
            
            # 创建数据目录
            os.makedirs(os.path.dirname(self.config["local"]["blacklist_file"]), exist_ok=True)
            os.makedirs(os.path.dirname(self.config["local"]["threat_intel_file"]), exist_ok=True)
            
            # 初始化本地数据
            self.blacklist = self._load_blacklist()
            self.threat_intel = self._load_threat_intel()
            
            # 初始化状态
            self.last_sync = self.config["local"]["last_sync"]
            
            logger.info("社区联防接口初始化完成")
            
        except Exception as e:
            logger.error(f"初始化失败: {str(e)}")
            raise
    
    def _load_blacklist(self):
        """加载黑名单"""
        blacklist_file = self.config["local"]["blacklist_file"]
        if os.path.exists(blacklist_file):
            try:
                with open(blacklist_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"加载黑名单失败: {str(e)}")
                return {"ips": [], "fingerprints": [], "last_updated": datetime.now().isoformat()}
        return {"ips": [], "fingerprints": [], "last_updated": datetime.now().isoformat()}
    
    def _save_blacklist(self):
        """保存黑名单"""
        try:
            blacklist_file = self.config["local"]["blacklist_file"]
            with open(blacklist_file, 'w', encoding='utf-8') as f:
                json.dump(self.blacklist, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"保存黑名单失败: {str(e)}")
    
    def _load_threat_intel(self):
        """加载威胁情报"""
        threat_intel_file = self.config["local"]["threat_intel_file"]
        if os.path.exists(threat_intel_file):
            try:
                with open(threat_intel_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"加载威胁情报失败: {str(e)}")
                return {"threats": [], "last_updated": datetime.now().isoformat()}
        return {"threats": [], "last_updated": datetime.now().isoformat()}
    
    def _save_threat_intel(self):
        """保存威胁情报"""
        try:
            threat_intel_file = self.config["local"]["threat_intel_file"]
            with open(threat_intel_file, 'w', encoding='utf-8') as f:
                json.dump(self.threat_intel, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"保存威胁情报失败: {str(e)}")
    
    def anonymize_attacker_fingerprint(self, fingerprint):
        """脱敏攻击者指纹"""
        try:
            # 创建脱敏指纹
            anonymized = {
                "fingerprint_id": hashlib.md5(str(fingerprint).encode('utf-8')).hexdigest(),
                "attack_type": fingerprint.get("attack_type", "unknown"),
                "port_scan_pattern": fingerprint.get("port_scan_pattern", "unknown"),
                "connection_rate": fingerprint.get("connection_rate", 0),
                "timestamp": datetime.now().isoformat(),
                "anonymized": True
            }
            
            # 移除敏感信息
            if "source_ip" in fingerprint:
                # 只保留网段，移除具体IP
                ip_parts = fingerprint["source_ip"].split('.')
                if len(ip_parts) == 4:
                    anonymized["ip_prefix"] = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.0/24"
            
            return anonymized
        except Exception as e:
            logger.error(f"脱敏失败: {str(e)}")
            return None
    
    def upload_threat_intel(self, attacker_info):
        """上传威胁情报"""
        if not self.config["community"]["share_anonymized_data"]:
            logger.info("威胁情报共享已禁用")
            return False
        
        try:
            # 脱敏攻击者指纹
            fingerprint = attacker_info.get("fingerprint", {})
            anonymized_fingerprint = self.anonymize_attacker_fingerprint(fingerprint)
            
            if not anonymized_fingerprint:
                return False
            
            # 构建威胁情报
            threat_intel = {
                "attacker_id": attacker_info.get("attacker_id", "unknown"),
                "fingerprint": anonymized_fingerprint,
                "attack_type": attacker_info.get("attack_type", "unknown"),
                "threat_level": attacker_info.get("threat_level", "low"),
                "confidence": attacker_info.get("confidence", 0.0),
                "timestamp": datetime.now().isoformat(),
                "source": "ChimeraSystem"
            }
            
            # 模拟上传（实际应该调用API）
            logger.info(f"上传威胁情报: {threat_intel['attacker_id']}")
            
            # 这里应该是实际的API调用
            # response = requests.post(
            #     f"{self.config['community']['api_endpoint']}/threats",
            #     headers={"Authorization": f"Bearer {self.config['community']['api_key']}"},
            #     json=threat_intel
            # )
            # return response.status_code == 200
            
            # 模拟成功
            return True
        except Exception as e:
            logger.error(f"上传威胁情报失败: {str(e)}")
            return False
    
    def download_threat_intel(self):
        """下载威胁情报"""
        try:
            logger.info("下载威胁情报")
            
            # 模拟下载（实际应该调用API）
            # response = requests.get(
            #     f"{self.config['community']['api_endpoint']}/threats",
            #     headers={"Authorization": f"Bearer {self.config['community']['api_key']}"}
            # )
            # if response.status_code == 200:
            #     threats = response.json()
            # else:
            #     return False
            
            # 模拟威胁情报
            mock_threats = [
                {
                    "id": "threat_1",
                    "fingerprint": {
                        "fingerprint_id": "abc123",
                        "attack_type": "port_scan",
                        "port_scan_pattern": "strobe",
                        "connection_rate": 100,
                        "ip_prefix": "192.168.1.0/24"
                    },
                    "attack_type": "port_scan",
                    "threat_level": "high",
                    "confidence": 0.85,
                    "reported_by": "OtherSystem",
                    "timestamp": datetime.now().isoformat()
                },
                {
                    "id": "threat_2",
                    "fingerprint": {
                        "fingerprint_id": "def456",
                        "attack_type": "brute_force",
                        "port_scan_pattern": "random",
                        "connection_rate": 50,
                        "ip_prefix": "10.0.0.0/8"
                    },
                    "attack_type": "brute_force",
                    "threat_level": "medium",
                    "confidence": 0.7,
                    "reported_by": "AnotherSystem",
                    "timestamp": datetime.now().isoformat()
                }
            ]
            
            # 更新本地威胁情报
            self.threat_intel["threats"] = mock_threats
            self.threat_intel["last_updated"] = datetime.now().isoformat()
            self._save_threat_intel()
            
            # 更新黑名单
            self._update_blacklist_from_threats(mock_threats)
            
            logger.info(f"下载威胁情报完成，共 {len(mock_threats)} 条")
            return True
        except Exception as e:
            logger.error(f"下载威胁情报失败: {str(e)}")
            return False
    
    def _update_blacklist_from_threats(self, threats):
        """从威胁情报更新黑名单"""
        for threat in threats:
            # 提取IP前缀
            ip_prefix = threat.get("fingerprint", {}).get("ip_prefix")
            if ip_prefix and ip_prefix not in self.blacklist["ips"]:
                self.blacklist["ips"].append(ip_prefix)
            
            # 提取指纹ID
            fingerprint_id = threat.get("fingerprint", {}).get("fingerprint_id")
            if fingerprint_id and fingerprint_id not in self.blacklist["fingerprints"]:
                self.blacklist["fingerprints"].append(fingerprint_id)
        
        # 更新时间
        self.blacklist["last_updated"] = datetime.now().isoformat()
        self._save_blacklist()
    
    def check_blacklist(self, ip=None, fingerprint=None):
        """检查是否在黑名单中"""
        result = {
            "ip_in_blacklist": False,
            "fingerprint_in_blacklist": False
        }
        
        # 检查IP
        if ip:
            # 检查具体IP
            if ip in self.blacklist["ips"]:
                result["ip_in_blacklist"] = True
            else:
                # 检查IP前缀
                ip_parts = ip.split('.')
                if len(ip_parts) == 4:
                    ip_prefix = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.0/24"
                    if ip_prefix in self.blacklist["ips"]:
                        result["ip_in_blacklist"] = True
        
        # 检查指纹
        if fingerprint:
            fingerprint_id = hashlib.md5(str(fingerprint).encode('utf-8')).hexdigest()
            if fingerprint_id in self.blacklist["fingerprints"]:
                result["fingerprint_in_blacklist"] = True
        
        return result
    
    def sync_with_community(self):
        """与社区同步"""
        logger.info("与社区同步")
        
        try:
            # 下载威胁情报
            download_success = self.download_threat_intel()
            
            # 更新同步时间
            self.last_sync = datetime.now().isoformat()
            self.config["local"]["last_sync"] = self.last_sync
            
            logger.info(f"与社区同步完成，下载状态: {download_success}")
            return download_success
        except Exception as e:
            logger.error(f"与社区同步失败: {str(e)}")
            return False
    
    async def sync_with_community_async(self):
        """异步与社区同步"""
        logger.info("异步与社区同步")
        
        try:
            # 异步执行同步操作
            loop = asyncio.get_event_loop()
            download_success = await loop.run_in_executor(None, self.download_threat_intel)
            
            # 更新同步时间
            self.last_sync = datetime.now().isoformat()
            self.config["local"]["last_sync"] = self.last_sync
            
            logger.info(f"异步与社区同步完成，下载状态: {download_success}")
            return download_success
        except Exception as e:
            logger.error(f"异步与社区同步失败: {str(e)}")
            return False
    
    def get_blacklist(self):
        """获取黑名单"""
        return self.blacklist
    
    def get_threat_intel(self):
        """获取威胁情报"""
        return self.threat_intel
    
    def get_sync_status(self):
        """获取同步状态"""
        return {
            "last_sync": self.last_sync,
            "blacklist_size": {
                "ips": len(self.blacklist["ips"]),
                "fingerprints": len(self.blacklist["fingerprints"])
            },
            "threat_intel_size": len(self.threat_intel["threats"])
        }
    
    def run_sync_task(self):
        """运行同步任务"""
        logger.info("运行同步任务")
        
        # 检查是否需要同步
        if self.last_sync:
            last_sync_time = datetime.fromisoformat(self.last_sync)
            sync_interval = self.config["community"]["sync_interval"]
            if (datetime.now() - last_sync_time).total_seconds() < sync_interval:
                logger.info("同步间隔未到，跳过同步")
                return False
        
        # 执行同步
        return self.sync_with_community()

if __name__ == "__main__":
    # 测试代码
    cdi = CommunityDefenseInterface()
    
    # 测试上传威胁情报
    test_attacker = {
        "attacker_id": "attacker_123",
        "fingerprint": {
            "source_ip": "192.168.1.100",
            "attack_type": "port_scan",
            "port_scan_pattern": "strobe",
            "connection_rate": 100
        },
        "attack_type": "port_scan",
        "threat_level": "high",
        "confidence": 0.85
    }
    
    upload_result = cdi.upload_threat_intel(test_attacker)
    print(f"上传威胁情报结果: {upload_result}")
    
    # 测试下载威胁情报
    download_result = cdi.download_threat_intel()
    print(f"下载威胁情报结果: {download_result}")
    
    # 测试检查黑名单
    ip_check = cdi.check_blacklist(ip="192.168.1.100")
    print(f"IP检查结果: {ip_check}")
    
    # 测试获取同步状态
    sync_status = cdi.get_sync_status()
    print(f"同步状态: {sync_status}")
    
    # 测试运行同步任务
    sync_task_result = cdi.run_sync_task()
    print(f"运行同步任务结果: {sync_task_result}")
