# © 2026 MirageShield 团队 版权所有，侵权必究
# 本项目已申请发明专利，未经许可禁止商用
# 策略引擎
import json
import logging
import time
import random
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s:%(funcName)s:%(lineno)d - %(message)s'
)
logger = logging.getLogger('control_plane.strategy_engine')

class StrategyEngine:
    def __init__(self, config_file=None):
        """初始化策略引擎"""
        try:
            # 加载配置文件
            if config_file:
                with open(config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            else:
                # 默认配置
                self.config = {
                    "strategy": {
                        "default_bait_ratio": 0.5,
                        "default_path_complexity": 3,
                        "default_psychological_warfare_level": 1,
                        "learning_rate": 0.1
                    },
                    "thresholds": {
                        "low": 0.3,
                        "medium": 0.6,
                        "high": 0.8,
                        "critical": 0.95
                    },
                    "ai_strategy": {
                        "bait_ratio": 1.0,
                        "path_complexity": 8,
                        "psychological_warfare_level": 5,
                        "dynamic_adjustment": True
                    }
                }
            
            # 初始化策略状态
            self.current_strategy = {
                "bait_ratio": self.config["strategy"]["default_bait_ratio"],
                "path_complexity": self.config["strategy"]["default_path_complexity"],
                "psychological_warfare_level": self.config["strategy"]["default_psychological_warfare_level"],
                "last_updated": datetime.now().isoformat()
            }
            
            # 初始化历史策略
            self.strategy_history = []
            
            # 初始化智能体状态
            self.agent_states = {
                "prober": {"status": "idle", "last_updated": datetime.now().isoformat()},
                "baiter": {"status": "idle", "last_updated": datetime.now().isoformat()},
                "watcher": {"status": "idle", "last_updated": datetime.now().isoformat()}
            }
            
            logger.info("策略引擎初始化完成")
            
        except Exception as e:
            logger.error(f"初始化失败: {str(e)}")
            raise
    
    def update_strategy(self, threat_assessment):
        """根据威胁评估更新策略"""
        logger.info(f"根据威胁评估更新策略: {threat_assessment}")
        
        # 提取威胁等级和置信度
        threat_level = threat_assessment.get("threat_level", "low")
        confidence = threat_assessment.get("confidence", 0.0)
        attack_type = threat_assessment.get("attack_type", "other")
        is_ai_attack = threat_assessment.get("is_ai_attack", False)
        source_ip = threat_assessment.get("source_ip", "")
        
        # 检查是否为AI攻击
        if is_ai_attack:
            self._adjust_for_ai_threat()
        else:
            # 根据威胁等级调整策略
            if threat_level == "low":
                self._adjust_for_low_threat()
            elif threat_level == "medium":
                self._adjust_for_medium_threat()
            elif threat_level == "high":
                self._adjust_for_high_threat()
            elif threat_level == "critical":
                self._adjust_for_critical_threat()
            elif threat_level == "extreme":
                self._adjust_for_extreme_threat()
        
        # 增强智能体协同机制
        self._enhance_agent_coordination(threat_level, is_ai_attack, attack_type)
        
        # 记录策略变更
        self._record_strategy_change(threat_assessment)
        
        return self.current_strategy
    
    def _adjust_for_low_threat(self):
        """调整低威胁策略"""
        logger.info("调整低威胁策略")
        self.current_strategy.update({
            "bait_ratio": min(0.6, self.current_strategy["bait_ratio"] + 0.1),
            "path_complexity": max(2, self.current_strategy["path_complexity"] - 1),
            "psychological_warfare_level": 1,
            "last_updated": datetime.now().isoformat()
        })
    
    def _adjust_for_medium_threat(self):
        """调整中威胁策略"""
        logger.info("调整中威胁策略")
        self.current_strategy.update({
            "bait_ratio": min(0.8, self.current_strategy["bait_ratio"] + 0.2),
            "path_complexity": min(4, self.current_strategy["path_complexity"] + 1),
            "psychological_warfare_level": 2,
            "last_updated": datetime.now().isoformat()
        })
    
    def _adjust_for_high_threat(self):
        """调整高威胁策略"""
        logger.info("调整高威胁策略")
        self.current_strategy.update({
            "bait_ratio": 0.9,
            "path_complexity": min(5, self.current_strategy["path_complexity"] + 2),
            "psychological_warfare_level": 3,
            "last_updated": datetime.now().isoformat()
        })
    
    def _adjust_for_critical_threat(self):
        """调整严重威胁策略"""
        logger.info("调整严重威胁策略")
        self.current_strategy.update({
            "bait_ratio": 0.95,
            "path_complexity": 6,
            "psychological_warfare_level": 3,
            "last_updated": datetime.now().isoformat()
        })
    
    def _adjust_for_extreme_threat(self):
        """调整极严重威胁策略"""
        logger.info("调整极严重威胁策略")
        self.current_strategy.update({
            "bait_ratio": 1.0,
            "path_complexity": 7,
            "psychological_warfare_level": 4,
            "last_updated": datetime.now().isoformat()
        })
    
    def _adjust_for_ai_threat(self):
        """调整AI攻击威胁策略"""
        logger.info("调整AI攻击威胁策略")
        # 针对AI攻击的特殊防护策略
        # 1. 极高的诱饵比例，增加AI的学习难度
        # 2. 最高的路径复杂度，增加AI的探索成本
        # 3. 最高的心理战等级，干扰AI的决策
        # 4. 添加动态变化，使AI难以适应
        ai_strategy = self.config.get("ai_strategy", {})
        self.current_strategy.update({
            "bait_ratio": ai_strategy.get("bait_ratio", 1.0),  # 全部使用诱饵
            "path_complexity": ai_strategy.get("path_complexity", 8),  # 比极严重威胁更高的复杂度
            "psychological_warfare_level": ai_strategy.get("psychological_warfare_level", 5),  # 最高心理战等级
            "dynamic_adjustment": ai_strategy.get("dynamic_adjustment", True),  # 启用动态调整
            "is_ai_attack": True,  # 明确标识为AI攻击
            "last_updated": datetime.now().isoformat()
        })
    
    def _enhance_agent_coordination(self, threat_level, is_ai_attack, attack_type):
        """增强智能体协同机制"""
        logger.info(f"增强智能体协同机制，威胁等级: {threat_level}, AI攻击: {is_ai_attack}, 攻击类型: {attack_type}")
        
        # 根据威胁等级和攻击类型调整智能体协同策略
        if is_ai_attack:
            # AI攻击场景下的协同策略
            self.current_strategy.update({
                "agent_coordination": "high",
                "prober_priority": "network_analysis",
                "baiter_priority": "adaptive_deception",
                "watcher_priority": "ai_detection",
                "real_time_coordination": True,
                "cross_agent_communication": True
            })
        elif threat_level in ["critical", "extreme"]:
            # 高威胁场景下的协同策略
            self.current_strategy.update({
                "agent_coordination": "medium",
                "prober_priority": "data_collection",
                "baiter_priority": "honeytoken_deployment",
                "watcher_priority": "anomaly_detection",
                "real_time_coordination": True,
                "cross_agent_communication": True
            })
        elif threat_level == "high":
            # 中等威胁场景下的协同策略
            self.current_strategy.update({
                "agent_coordination": "medium",
                "prober_priority": "network_monitoring",
                "baiter_priority": "deception_strategy",
                "watcher_priority": "alert_monitoring",
                "real_time_coordination": False,
                "cross_agent_communication": True
            })
        else:
            # 低威胁场景下的协同策略
            self.current_strategy.update({
                "agent_coordination": "low",
                "prober_priority": "regular_scanning",
                "baiter_priority": "maintenance",
                "watcher_priority": "routine_monitoring",
                "real_time_coordination": False,
                "cross_agent_communication": False
            })
        
        # 根据攻击类型调整特定智能体策略
        if attack_type == "ddos":
            self.current_strategy.update({
                "prober_priority": "traffic_analysis",
                "watcher_priority": "rate_limiting"
            })
        elif attack_type == "brute_force":
            self.current_strategy.update({
                "prober_priority": "authentication_monitoring",
                "baiter_priority": "honeypot_activation"
            })
        elif attack_type == "port_scan":
            self.current_strategy.update({
                "prober_priority": "network_mapping",
                "watcher_priority": "scan_detection"
            })
        elif attack_type == "exploit":
            self.current_strategy.update({
                "prober_priority": "vulnerability_scanning",
                "watcher_priority": "exploit_detection"
            })
    
    def _record_strategy_change(self, threat_assessment):
        """记录策略变更"""
        change_record = {
            "timestamp": datetime.now().isoformat(),
            "threat_assessment": threat_assessment,
            "strategy_before": self.current_strategy.copy(),
            "strategy_after": self.current_strategy.copy()
        }
        self.strategy_history.append(change_record)
        
        # 限制历史记录长度
        if len(self.strategy_history) > 100:
            self.strategy_history = self.strategy_history[-100:]
    
    def get_strategy_for_agent(self, agent_name):
        """获取指定智能体的策略"""
        logger.info(f"获取 {agent_name} 智能体的策略")
        
        # 检查是否为AI攻击
        is_ai_attack = self.current_strategy.get("is_ai_attack", False) or self.current_strategy.get("dynamic_adjustment", False)
        
        if agent_name == "prober":
            return {
                "path_complexity": self.current_strategy["path_complexity"],
                "encryption_strength": "highest" if is_ai_attack else ("high" if self.current_strategy["path_complexity"] > 4 else "medium"),
                "data_collection_rate": "reduced" if is_ai_attack else ("normal" if self.current_strategy["bait_ratio"] < 0.8 else "reduced"),
                "dynamic_path_changes": is_ai_attack
            }
        elif agent_name == "baiter":
            return {
                "bait_ratio": self.current_strategy["bait_ratio"],
                "honeytoken_count": int(20 * self.current_strategy["bait_ratio"]) if is_ai_attack else int(10 * self.current_strategy["bait_ratio"]),
                "deception_level": "extreme" if is_ai_attack else ("high" if self.current_strategy["bait_ratio"] > 0.8 else "medium"),
                "adaptive_deception": is_ai_attack
            }
        elif agent_name == "watcher":
            return {
                "monitoring_interval": 1 if is_ai_attack else (2 if self.current_strategy["psychological_warfare_level"] > 2 else 5),
                "alert_threshold": "very_low" if is_ai_attack else ("low" if self.current_strategy["psychological_warfare_level"] > 2 else "medium"),
                "ai_attack_detection": True,
                "pattern_analysis": is_ai_attack
            }
        else:
            logger.error(f"未知智能体: {agent_name}")
            return {}
    
    def update_agent_state(self, agent_name, state):
        """更新智能体状态"""
        if agent_name in self.agent_states:
            self.agent_states[agent_name].update({
                "status": state,
                "last_updated": datetime.now().isoformat()
            })
            logger.info(f"更新 {agent_name} 智能体状态为: {state}")
        else:
            logger.error(f"未知智能体: {agent_name}")
    
    def get_agent_states(self):
        """获取所有智能体状态"""
        return self.agent_states
    
    def get_current_strategy(self):
        """获取当前策略"""
        return self.current_strategy
    
    def get_strategy_history(self, limit=10):
        """获取策略历史"""
        return self.strategy_history[-limit:]
    
    def set_strategy(self, strategy):
        """直接设置策略"""
        logger.info(f"直接设置策略: {strategy}")
        
        # 更新当前策略
        self.current_strategy.update({
            "bait_ratio": strategy.get("bait_ratio", self.current_strategy["bait_ratio"]),
            "path_complexity": strategy.get("path_complexity", self.current_strategy["path_complexity"]),
            "psychological_warfare_level": strategy.get("psychological_warfare_level", self.current_strategy["psychological_warfare_level"]),
            "last_updated": datetime.now().isoformat()
        })
        
        # 记录策略变更
        change_record = {
            "timestamp": datetime.now().isoformat(),
            "threat_assessment": {"threat_level": "manual", "confidence": 1.0},
            "strategy_before": self.current_strategy.copy(),
            "strategy_after": self.current_strategy.copy()
        }
        self.strategy_history.append(change_record)
        
        # 限制历史记录长度
        if len(self.strategy_history) > 100:
            self.strategy_history = self.strategy_history[-100:]
        
        return self.current_strategy
    
    def optimize_strategy(self):
        """优化策略"""
        logger.info("优化策略")
        
        # 简单的策略优化逻辑
        # 基于历史策略和威胁评估结果进行优化
        if len(self.strategy_history) > 5:
            # 分析历史数据
            recent_changes = self.strategy_history[-5:]
            
            # 计算平均威胁等级
            threat_levels = [change["threat_assessment"].get("threat_level", "low") for change in recent_changes]
            threat_counts = {}
            for level in threat_levels:
                threat_counts[level] = threat_counts.get(level, 0) + 1
            
            # 根据威胁分布调整默认策略
            if threat_counts.get("high", 0) > 2:
                logger.info("检测到高频高威胁，调整默认策略")
                self.config["strategy"]["default_bait_ratio"] = min(0.7, self.config["strategy"]["default_bait_ratio"] + 0.1)
                self.config["strategy"]["default_path_complexity"] = min(4, self.config["strategy"]["default_path_complexity"] + 1)
        
        return self.current_strategy

if __name__ == "__main__":
    # 测试代码
    engine = StrategyEngine()
    
    # 模拟威胁评估
    threat_assessments = [
        {"threat_level": "low", "confidence": 0.2},
        {"threat_level": "medium", "confidence": 0.5},
        {"threat_level": "high", "confidence": 0.7},
        {"threat_level": "critical", "confidence": 0.9},
        {"threat_level": "extreme", "confidence": 0.98}
    ]
    
    for assessment in threat_assessments:
        strategy = engine.update_strategy(assessment)
        print(f"威胁评估: {assessment}")
        print(f"更新后的策略: {strategy}")
        print(f"Prober 策略: {engine.get_strategy_for_agent('prober')}")
        print(f"Baiter 策略: {engine.get_strategy_for_agent('baiter')}")
        print(f"Watcher 策略: {engine.get_strategy_for_agent('watcher')}")
        print()
    
    # 测试优化策略
    engine.optimize_strategy()
    print("优化后的策略:")
    print(engine.get_current_strategy())
