# © 2026 MirageShield 团队 版权所有，侵权必究
# 本项目已申请发明专利，未经许可禁止商用
# 安全评估模块
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
logger = logging.getLogger('control_plane.security_assessment')

class SecurityAssessmentModule:
    def __init__(self, config_file=None):
        """初始化安全评估模块"""
        try:
            # 加载配置文件
            if config_file:
                with open(config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            else:
                # 默认配置


                
                self.config = {
                    "thresholds": {
                        "low": 0.1,
                        "medium": 0.3,
                        "high": 0.5,
                        "critical": 0.7
                    },
                    "weights": {
                        "attack_type": 0.5,
                        "connection_rate": 0.2,
                        "target_count": 0.15,
                        "packet_size": 0.1,
                        "scan_pattern": 0.05
                    },
                    "attack_type_weights": {
                        "port_scan": 0.7,
                        "brute_force": 0.9,
                        "ddos": 1.0,
                        "exploit": 1.0,
                        "ai_attack": 1.0,
                        "other": 0.5
                    },
                    "scan_pattern_weights": {
                        "sequential": 0.6,
                        "random": 0.8,
                        "strobe": 1.0,
                        "other": 0.5
                    },
                    "ai_detection": {
                        "initial_threshold": 6.0,  # 降低阈值以提高检测灵敏度
                        "learning_rate": 0.1,
                        "min_threshold": 5.0,
                        "max_threshold": 15.0,
                        "scoring_weights": {
                            "time_based": 0.3,
                            "pattern": 0.3,
                            "machine_learning": 0.4
                        },
                        "time_series": {
                            "time_window": 3600,  # 1小时
                            "frequency_thresholds": {
                                "high": 10,
                                "medium": 5,
                                "low": 2
                            },
                            "rate_change_threshold": 100
                        },
                        "behavior_pattern": {
                            "target_count_thresholds": {
                                "high": 8,
                                "medium": 4
                            },
                            "packet_size_variation_thresholds": {
                                "high": 800,
                                "medium": 400
                            }
                        }
                    }
                }
            
            # 初始化评估历史
            self.assessment_history = []
            
            # 初始化威胁情报
            self.threat_intel = {
                "known_attackers": set(),
                "suspicious_ips": set(),
                "recent_attacks": []
            }
            
            # 初始化AI攻击检测相关数据
            self.ai_attack_history = []  # 存储AI攻击历史
            self.adaptive_threshold = self.config.get("ai_detection", {}).get("initial_threshold", 6.0)  # 初始阈值，降低阈值以提高检测灵敏度
            self.learning_rate = self.config.get("ai_detection", {}).get("learning_rate", 0.1)  # 学习率
            
            logger.info("安全评估模块初始化完成")
            
        except Exception as e:
            logger.error(f"初始化失败: {str(e)}")
            raise
    
    def assess_threat(self, attacker_info):
        """评估威胁"""
        logger.info(f"评估威胁: {attacker_info}")
        
        try:
            # 提取攻击者信息
            attack_type = attacker_info.get("attack_type", "other")
            fingerprint = attacker_info.get("fingerprint", {})
            source_ip = fingerprint.get("source_ip", "")
            connection_rate = fingerprint.get("connection_rate", 0)
            targets = attacker_info.get("targets", [])
            
            # 检测AI攻击特征
            is_ai_attack = self._detect_ai_attack(attacker_info)
            
            # 直接根据攻击类型和参数设置威胁等级
            if is_ai_attack:
                threat_level = "critical"
                confidence = 0.95
            elif attack_type == "ddos" and connection_rate > 500:
                threat_level = "critical"
                confidence = 0.9
            elif attack_type == "exploit":
                threat_level = "high"
                confidence = 0.8
            elif attack_type == "brute_force":
                threat_level = "medium"
                confidence = 0.6
            elif attack_type == "port_scan" and len(targets) > 5:
                threat_level = "medium"
                confidence = 0.5
            else:
                threat_level = "low"
                confidence = 0.2
            
            # 检查是否为已知攻击者
            is_known_attacker = source_ip in self.threat_intel["known_attackers"]
            if is_known_attacker:
                # 已知攻击者，提高威胁等级
                if threat_level == "medium":
                    threat_level = "high"
                    confidence = 0.8
                elif threat_level == "high":
                    threat_level = "critical"
                    confidence = 0.9
                elif threat_level == "critical":
                    threat_level = "extreme"
                    confidence = 1.0
            
            # 构建评估结果
            assessment_result = {
                "threat_level": threat_level,
                "confidence": confidence,
                "attack_type": attack_type,
                "is_ai_attack": is_ai_attack,
                "source_ip": source_ip,
                "timestamp": datetime.now().isoformat(),
                "is_known_attacker": is_known_attacker
            }
            
            # 记录评估结果
            self._record_assessment(assessment_result)
            
            # 更新威胁情报
            self._update_threat_intel(assessment_result, attacker_info)
            
            logger.info(f"威胁评估完成: {threat_level} (置信度: {confidence:.2f})")
            return assessment_result
            
        except Exception as e:
            logger.error(f"威胁评估失败: {str(e)}")
            return {
                "threat_level": "low",
                "confidence": 0.0,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _calculate_confidence(self, attack_type, connection_rate, packet_size_distribution, scan_pattern, targets):
        """计算威胁置信度"""
        # 基础分数
        base_score = 0.0
        
        # 攻击类型权重
        attack_type_weight = self.config["attack_type_weights"].get(attack_type, 0.5)
        base_score += attack_type_weight * self.config["weights"]["attack_type"]
        
        # 连接率权重（归一化）
        normalized_connection_rate = min(1.0, connection_rate / 1000)
        base_score += normalized_connection_rate * self.config["weights"]["connection_rate"]
        
        # 目标数量权重
        target_count = len(targets)
        normalized_target_count = min(1.0, target_count / 10)
        base_score += normalized_target_count * self.config["weights"]["target_count"]
        
        # 数据包大小分布权重（检测异常大小）
        if packet_size_distribution:
            avg_packet_size = sum(packet_size_distribution) / len(packet_size_distribution)
            # 异常大小检测（太小或太大）
            if avg_packet_size < 60 or avg_packet_size > 1400:
                packet_size_score = 0.9
            else:
                packet_size_score = 0.4
            base_score += packet_size_score * self.config["weights"]["packet_size"]
        
        # 扫描模式权重
        scan_pattern_weight = self.config["scan_pattern_weights"].get(scan_pattern, 0.5)
        base_score += scan_pattern_weight * self.config["weights"]["scan_pattern"]
        
        # 确保分数在0-1之间
        confidence = max(0.0, min(1.0, base_score))
        return confidence
    
    def _determine_threat_level(self, confidence):
        """确定威胁等级"""
        thresholds = self.config["thresholds"]
        
        if confidence < thresholds["low"]:
            return "low"
        elif confidence < thresholds["medium"]:
            return "medium"
        elif confidence < thresholds["high"]:
            return "high"
        elif confidence < thresholds["critical"]:
            return "critical"
        else:
            return "extreme"
    
    def _record_assessment(self, assessment_result):
        """记录评估结果"""
        self.assessment_history.append(assessment_result)
        
        # 限制历史记录长度
        if len(self.assessment_history) > 1000:
            self.assessment_history = self.assessment_history[-1000:]
    
    def _update_threat_intel(self, assessment_result, attacker_info):
        """更新威胁情报"""
        source_ip = assessment_result.get("source_ip", "")
        threat_level = assessment_result.get("threat_level", "low")
        
        # 如果威胁等级为高或以上，添加到已知攻击者
        if threat_level in ["high", "critical", "extreme"] and source_ip:
            self.threat_intel["known_attackers"].add(source_ip)
            self.threat_intel["suspicious_ips"].add(source_ip)
        
        # 记录最近攻击
        attack_record = {
            "source_ip": source_ip,
            "threat_level": threat_level,
            "attack_type": attacker_info.get("attack_type", "other"),
            "timestamp": datetime.now().isoformat()
        }
        self.threat_intel["recent_attacks"].append(attack_record)
        
        # 限制最近攻击记录长度
        if len(self.threat_intel["recent_attacks"]) > 100:
            self.threat_intel["recent_attacks"] = self.threat_intel["recent_attacks"][-100:]
    
    def get_assessment_history(self, limit=20):
        """获取评估历史"""
        return self.assessment_history[-limit:]
    
    def get_threat_intel(self):
        """获取威胁情报"""
        return self.threat_intel
    
    def update_thresholds(self, thresholds):
        """更新阈值"""
        logger.info(f"更新阈值: {thresholds}")
        self.config["thresholds"].update(thresholds)
    
    def update_weights(self, weights):
        """更新权重"""
        logger.info(f"更新权重: {weights}")
        if "weights" in weights:
            self.config["weights"].update(weights["weights"])
        if "attack_type_weights" in weights:
            self.config["attack_type_weights"].update(weights["attack_type_weights"])
        if "scan_pattern_weights" in weights:
            self.config["scan_pattern_weights"].update(weights["scan_pattern_weights"])
    
    def _extract_features(self, attacker_info):
        """提取攻击者特征"""
        fingerprint = attacker_info.get("fingerprint", {})
        connection_rate = fingerprint.get("connection_rate", 0)
        packet_size_distribution = fingerprint.get("packet_size_distribution", [])
        scan_pattern = fingerprint.get("scan_pattern", "other")
        targets = attacker_info.get("targets", [])
        attack_type = attacker_info.get("attack_type", "other")
        timestamp = datetime.now().timestamp()
        
        features = {
            "connection_rate": connection_rate,
            "target_count": len(targets),
            "scan_pattern": scan_pattern,
            "attack_type": attack_type,
            "packet_size_variation": 0,
            "packet_size_avg": 0,
            "timestamp": timestamp
        }
        
        # 计算数据包大小特征
        if packet_size_distribution and len(packet_size_distribution) > 0:
            features["packet_size_avg"] = sum(packet_size_distribution) / len(packet_size_distribution)
            if len(packet_size_distribution) > 1:
                features["packet_size_variation"] = max(packet_size_distribution) - min(packet_size_distribution)
        
        return features
    
    def _calculate_total_score(self, features):
        """计算综合评分"""
        # 1. 时间序列分析
        time_based_score = self._time_series_analysis(features)
        
        # 2. 行为模式分析
        pattern_score = self._behavior_pattern_analysis(features)
        
        # 3. 机器学习模型评分（简化版）
        ml_score = self._machine_learning_scoring(features)
        
        # 4. 综合评分
        scoring_weights = self.config.get("ai_detection", {}).get("scoring_weights", {})
        time_based_weight = scoring_weights.get("time_based", 0.3)
        pattern_weight = scoring_weights.get("pattern", 0.3)
        ml_weight = scoring_weights.get("machine_learning", 0.4)
        
        # 如果历史数据为空，增加其他特征的权重
        if len(self.ai_attack_history) == 0:
            time_based_weight = 0.1
            pattern_weight = 0.45
            ml_weight = 0.45
        
        total_score = time_based_score * time_based_weight + pattern_score * pattern_weight + ml_score * ml_weight
        return total_score
    
    def _detect_ai_attack(self, attacker_info):
        """检测AI攻击特征"""
        # 1. 特征提取
        features = self._extract_features(attacker_info)
        
        # 2. 计算综合评分
        total_score = self._calculate_total_score(features)
        
        # 3. 自适应阈值调整
        self._adjust_threshold(total_score)
        
        # 4. 记录攻击信息用于后续分析
        self._record_ai_attack_attempt(features, total_score)
        
        # 5. 判断是否为AI攻击
        is_ai_attack = total_score >= self.adaptive_threshold
        
        # 记录检测结果
        logger.info(f"AI攻击检测 - 得分: {total_score:.2f}, 阈值: {self.adaptive_threshold:.2f}, 结果: {is_ai_attack}")
        
        return is_ai_attack
    
    def _time_series_analysis(self, features):
        """时间序列分析"""
        # 简化的时间序列分析
        # 检查最近的攻击模式
        time_series_config = self.config.get("ai_detection", {}).get("time_series", {})
        time_window = time_series_config.get("time_window", 3600)  # 1小时
        frequency_thresholds = time_series_config.get("frequency_thresholds", {"high": 10, "medium": 5, "low": 2})
        rate_change_threshold = time_series_config.get("rate_change_threshold", 100)
        
        recent_attacks = [a for a in self.ai_attack_history if features["timestamp"] - a["timestamp"] < time_window]
        
        score = 0.0
        
        if len(recent_attacks) > 0:
            # 计算攻击频率
            attack_frequency = len(recent_attacks) / (time_window / 60)  # 每分钟攻击次数
            if attack_frequency > frequency_thresholds.get("high", 10):
                score += 3.0
            elif attack_frequency > frequency_thresholds.get("medium", 5):
                score += 2.0
            elif attack_frequency > frequency_thresholds.get("low", 2):
                score += 1.0
            
            # 检查攻击模式变化
            if len(recent_attacks) > 2:
                # 检查连接率变化
                rate_changes = []
                for i in range(1, len(recent_attacks)):
                    change = abs(recent_attacks[i]["connection_rate"] - recent_attacks[i-1]["connection_rate"])
                    rate_changes.append(change)
                
                if rate_changes:
                    avg_change = sum(rate_changes) / len(rate_changes)
                    if avg_change > rate_change_threshold:
                        score += 2.0
        
        return score
    
    def _behavior_pattern_analysis(self, features):
        """行为模式分析"""
        score = 0.0
        
        behavior_config = self.config.get("ai_detection", {}).get("behavior_pattern", {})
        target_count_thresholds = behavior_config.get("target_count_thresholds", {"high": 8, "medium": 4})
        packet_size_thresholds = behavior_config.get("packet_size_variation_thresholds", {"high": 800, "medium": 400})
        
        # 分析攻击目标分布
        if features["target_count"] > target_count_thresholds.get("high", 8):
            score += 2.0
        elif features["target_count"] > target_count_thresholds.get("medium", 4):
            score += 1.0
        
        # 分析扫描模式
        if features["scan_pattern"] == "random":
            score += 2.5
        elif features["scan_pattern"] == "strobe":
            score += 1.5
        
        # 分析数据包大小分布
        if features["packet_size_variation"] > packet_size_thresholds.get("high", 800):
            score += 2.0
        elif features["packet_size_variation"] > packet_size_thresholds.get("medium", 400):
            score += 1.0
        
        # 分析攻击类型
        if features["attack_type"] in ["exploit", "ddos"]:
            score += 1.5
        elif features["attack_type"] == "other":
            score += 1.0
        
        return score
    
    def _machine_learning_scoring(self, features):
        """简化的机器学习评分"""
        # 这里使用简化的评分模型，实际项目中可以使用真实的机器学习模型
        score = 0.0
        
        # 基于特征的加权评分
        weights = {
            "connection_rate": 0.3,
            "target_count": 0.2,
            "packet_size_variation": 0.2,
            "scan_pattern": 0.15,
            "attack_type": 0.15
        }
        
        # 标准化特征
        normalized_features = {
            "connection_rate": min(features["connection_rate"] / 1000, 1.0),
            "target_count": min(features["target_count"] / 20, 1.0),
            "packet_size_variation": min(features["packet_size_variation"] / 1500, 1.0),
            "scan_pattern": 0.8 if features["scan_pattern"] == "random" else 0.5 if features["scan_pattern"] == "strobe" else 0.2,
            "attack_type": 0.9 if features["attack_type"] in ["exploit", "ddos"] else 0.6 if features["attack_type"] == "other" else 0.3
        }
        
        # 计算加权评分
        for feature, weight in weights.items():
            score += normalized_features[feature] * weight * 10
        
        return score
    
    def _adjust_threshold(self, score):
        """自适应阈值调整"""
        # 基于最近的检测结果调整阈值
        # 如果最近的检测得分普遍较高，提高阈值
        # 如果最近的检测得分普遍较低，降低阈值
        
        recent_scores = [a["score"] for a in self.ai_attack_history if datetime.now().timestamp() - a["timestamp"] < 3600]
        
        if len(recent_scores) == 0:
            return
            
        if len(recent_scores) > 5:
            avg_score = sum(recent_scores) / len(recent_scores)
            # 调整阈值
            if avg_score > self.adaptive_threshold + 2:
                self.adaptive_threshold += self.learning_rate
            elif avg_score < self.adaptive_threshold - 2:
                self.adaptive_threshold -= self.learning_rate
            
            # 确保阈值在合理范围内
            ai_detection_config = self.config.get("ai_detection", {})
            min_threshold = ai_detection_config.get("min_threshold", 5.0)
            max_threshold = ai_detection_config.get("max_threshold", 15.0)
            self.adaptive_threshold = max(min_threshold, min(max_threshold, self.adaptive_threshold))
    
    def _record_ai_attack_attempt(self, features, score):
        """记录AI攻击尝试"""
        attack_record = {
            **features,
            "score": score,
            "timestamp": datetime.now().timestamp()
        }
        
        self.ai_attack_history.append(attack_record)
        
        # 限制历史记录长度
        if len(self.ai_attack_history) > 100:
            self.ai_attack_history = self.ai_attack_history[-100:]
    
    def get_statistics(self):
        """获取统计信息"""
        if not self.assessment_history:
            return {
                "total_assessments": 0,
                "threat_distribution": {},
                "average_confidence": 0.0
            }
        
        # 计算威胁分布
        threat_distribution = {}
        total_confidence = 0.0
        
        for assessment in self.assessment_history:
            threat_level = assessment.get("threat_level", "low")
            threat_distribution[threat_level] = threat_distribution.get(threat_level, 0) + 1
            total_confidence += assessment.get("confidence", 0.0)
        
        return {
            "total_assessments": len(self.assessment_history),
            "threat_distribution": threat_distribution,
            "average_confidence": total_confidence / len(self.assessment_history)
        }

if __name__ == "__main__":
    # 测试代码
    assessment_module = SecurityAssessmentModule()
    
    # 模拟攻击者信息
    test_attackers = [
        {
            "attack_type": "port_scan",
            "fingerprint": {
                "source_ip": "192.168.1.100",
                "connection_rate": 50,
                "packet_size_distribution": [40, 40, 40, 40, 40],
                "scan_pattern": "sequential"
            },
            "targets": [22, 80, 443]
        },
        {
            "attack_type": "brute_force",
            "fingerprint": {
                "source_ip": "192.168.1.101",
                "connection_rate": 80,
                "packet_size_distribution": [60, 60, 60, 60, 60],
                "scan_pattern": "random"
            },
            "targets": [22, 3389]
        },
        {
            "attack_type": "ddos",
            "fingerprint": {
                "source_ip": "192.168.1.102",
                "connection_rate": 150,
                "packet_size_distribution": [1500, 1500, 1500, 1500, 1500],
                "scan_pattern": "strobe"
            },
            "targets": [80, 443, 8080, 8443]
        },
        {
            "attack_type": "exploit",
            "fingerprint": {
                "source_ip": "192.168.1.103",
                "connection_rate": 30,
                "packet_size_distribution": [80, 120, 150, 200, 250],
                "scan_pattern": "other"
            },
            "targets": [443]
        }
    ]
    
    for i, attacker in enumerate(test_attackers):
        print(f"测试攻击者 {i+1}:")
        result = assessment_module.assess_threat(attacker)
        print(f"评估结果: {result}")
        print()
    
    # 测试已知攻击者
    print("测试已知攻击者:")
    known_attacker = {
        "attack_type": "port_scan",
        "fingerprint": {
            "source_ip": "192.168.1.100",  # 之前的攻击者
            "connection_rate": 40,
            "packet_size_distribution": [40, 40, 40, 40, 40],
            "scan_pattern": "sequential"
        },
        "targets": [22, 80]
    }
    result = assessment_module.assess_threat(known_attacker)
    print(f"评估结果: {result}")
    print()
    
    # 获取统计信息
    print("统计信息:")
    stats = assessment_module.get_statistics()
    print(stats)
