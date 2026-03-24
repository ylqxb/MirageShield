# © 2026 MirageShield 团队 版权所有，侵权必究
# 本项目已申请发明专利，未经许可禁止商用
# AI-2 Baiter 智能体

import asyncio
import json
import random
import string
from loguru import logger
from typing import List, Dict, Any, Optional

class BaiterAgent:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.mcp_integrations = config.get('mcp_integrations', {})
        self.fake_data_templates = config.get('fake_data_templates', {})
        self.deployed_honeypots = {}
        self.deployment_options = config.get('deployment_options', {})
        self.logger = logger.bind(agent="AI-2")
        
        # 初始化MCP模块
        self.generative_ai_config = self.mcp_integrations.get('generative_ai', {})
        self.honeypot_manager_config = self.mcp_integrations.get('honeypot_manager', {})
        self.file_watermark_config = self.mcp_integrations.get('file_watermark', {})
        self.docker_config = self.mcp_integrations.get('docker', {})
        
        # 从蜜罐管理MCP获取模板
        self.honeypot_templates = self.honeypot_manager_config.get('templates', {})
        
        self.logger.info("AI-2 Baiter 智能体初始化完成")
    
    async def generate_ai_content(self, prompt: str) -> str:
        """使用生成式AI生成内容"""
        try:
            if not self.generative_ai_config.get('enabled', False):
                self.logger.warning("生成式AI功能未启用")
                return f"[模拟生成] {prompt}"
            
            api_url = self.generative_ai_config.get('api_url')
            api_key = self.generative_ai_config.get('api_key')
            model = self.generative_ai_config.get('model', 'gpt-3.5-turbo')
            
            if not api_url or not api_key:
                self.logger.warning("生成式AI配置不完整")
                return f"[模拟生成] {prompt}"
            
            # 模拟AI生成内容
            self.logger.info(f"使用生成式AI生成内容: {prompt[:50]}...")
            # 模拟不同类型的内容生成
            if "document" in prompt.lower():
                return "这是一份模拟的内部文档内容，包含了一些敏感信息和业务计划。请注意保密。"
            elif "email" in prompt.lower():
                return "这是一封模拟的内部邮件，讨论了项目进展和团队协作事宜。"
            else:
                return f"这是使用生成式AI生成的内容，基于提示: {prompt}"
        except Exception as e:
            self.logger.error(f"生成式AI内容生成失败: {str(e)}")
            return f"[生成失败] {prompt}"
    
    def add_watermark(self, content: str) -> str:
        """添加文件水印"""
        try:
            if not self.file_watermark_config.get('enabled', False):
                self.logger.warning("文件水印功能未启用")
                return content
            
            algorithm = self.file_watermark_config.get('algorithm', 'steganography')
            watermark_key = self.file_watermark_config.get('watermark_key', 'default_watermark')
            
            # 模拟添加水印
            self.logger.info("添加文件水印")
            watermark = f"[CHIMERA_WATERMARK:{watermark_key}]\n"
            return watermark + content
        except Exception as e:
            self.logger.error(f"添加水印失败: {str(e)}")
            return content
    
    async def deploy_with_docker(self, honeypot_type: str, name: str) -> Dict[str, Any]:
        """使用Docker部署蜜罐"""
        try:
            if not self.docker_config.get('enabled', False):
                self.logger.warning("Docker功能未启用")
                return {"status": "disabled"}
            
            socket_path = self.docker_config.get('socket_path', '/var/run/docker.sock')
            registry = self.docker_config.get('registry', 'docker.io')
            image_prefix = self.docker_config.get('image_prefix', 'chimera_honeypot')
            network_name = self.docker_config.get('network_name', 'chimera_network')
            
            # 模拟Docker部署
            self.logger.info(f"使用Docker部署蜜罐: {name}")
            container_id = f"docker_{random.randint(100000, 999999)}"
            
            return {
                "status": "success",
                "container_id": container_id,
                "image": f"{registry}/{image_prefix}:{honeypot_type}",
                "network": network_name,
                "deploy_time": "2026-03-07T12:00:00Z"
            }
        except Exception as e:
            self.logger.error(f"Docker部署失败: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def generate_fake_data(self, template_name: str, count: int = 1) -> List[Dict[str, Any]]:
        """生成假数据"""
        try:
            self.logger.info(f"生成假数据，模板: {template_name}, 数量: {count}")
            template = self.fake_data_templates.get(template_name)
            if not template:
                self.logger.warning(f"模板 {template_name} 不存在，使用默认模板")
                template = self._get_default_template()
            
            fake_data = []
            for i in range(count):
                data = self._generate_data_from_template(template)
                # 添加水印和信标
                data['watermark'] = self._generate_watermark()
                data['beacon'] = self._generate_beacon()
                
                # 如果是文档类型，使用AI生成内容
                if template_name == "internal_documents" and "content" in data:
                    ai_content = await self.generate_ai_content(f"生成一份{data.get('title', '内部文档')}的内容")
                    data['content'] = self.add_watermark(ai_content)
                
                fake_data.append(data)
            
            self.logger.info(f"生成了 {len(fake_data)} 条假数据")
            return fake_data
        except Exception as e:
            self.logger.error(f"假数据生成失败: {str(e)}")
            return []
    
    def _get_default_template(self) -> Dict[str, Any]:
        """获取默认模板"""
        return {
            "type": "user_data",
            "fields": {
                "username": "user_{id}",
                "email": "user_{id}@example.com",
                "password": "Password123!",
                "phone": "138{random}",
                "address": "{street}, {city}, {country}"
            },
            "values": {
                "street": ["Main St", "Oak Ave", "Maple Rd", "Pine Ln"],
                "city": ["Beijing", "Shanghai", "Guangzhou", "Shenzhen"],
                "country": ["China"]
            }
        }
    
    def _generate_data_from_template(self, template: Dict[str, Any]) -> Dict[str, Any]:
        """根据模板生成数据"""
        data = {}
        fields = template.get('fields', {})
        values = template.get('values', {})
        
        for field, pattern in fields.items():
            if '{id}' in pattern:
                data[field] = pattern.replace('{id}', str(random.randint(1000, 9999)))
            elif '{random}' in pattern:
                data[field] = pattern.replace('{random}', ''.join(random.choices(string.digits, k=8)))
            else:
                # 检查是否有预定义值
                if field in values:
                    data[field] = random.choice(values[field])
                else:
                    # 生成随机字符串
                    data[field] = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        
        return data
    
    def _generate_watermark(self) -> str:
        """生成水印"""
        return f"CHIMERA_{random.randint(100000, 999999)}"
    
    def _generate_beacon(self) -> Dict[str, Any]:
        """生成信标"""
        return {
            "id": f"beacon_{random.randint(100000, 999999)}",
            "trigger_url": f"http://example.com/beacon/{random.randint(100000, 999999)}",
            "timestamp": "2026-03-07T12:00:00Z"
        }
    
    async def deploy_honeypot(self, honeypot_type: str, name: str) -> Dict[str, Any]:
        """部署蜜罐"""
        try:
            self.logger.info(f"部署蜜罐，类型: {honeypot_type}, 名称: {name}")
            template = self.honeypot_templates.get(honeypot_type, self._get_default_honeypot_template())
            
            # 使用Docker部署蜜罐
            docker_result = await self.deploy_with_docker(honeypot_type, name)
            
            # 模拟部署过程
            await asyncio.sleep(random.uniform(1, 3))
            
            honeypot_id = f"honeypot_{random.randint(100000, 999999)}"
            honeypot = {
                "id": honeypot_id,
                "name": name,
                "type": honeypot_type,
                "status": "running",
                "services": template.get('services', []),
                "ip": f"192.168.1.{random.randint(100, 200)}",
                "deploy_time": "2026-03-07T12:00:00Z",
                "last_activity": "2026-03-07T12:00:00Z",
                "docker_info": docker_result
            }
            
            self.deployed_honeypots[honeypot_id] = honeypot
            self.logger.info(f"蜜罐部署成功: {honeypot_id}")
            return honeypot
        except Exception as e:
            self.logger.error(f"蜜罐部署失败: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": "2026-03-07T12:00:00Z"
            }
    
    def _get_default_honeypot_template(self) -> Dict[str, Any]:
        """获取默认蜜罐模板"""
        return {
            "services": [
                {"name": "ssh", "port": 22, "status": "open"},
                {"name": "http", "port": 80, "status": "open"},
                {"name": "ftp", "port": 21, "status": "open"},
                {"name": "mysql", "port": 3306, "status": "open"}
            ]
        }
    
    async def update_honeypot(self, honeypot_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """更新蜜罐配置"""
        try:
            if honeypot_id not in self.deployed_honeypots:
                self.logger.warning(f"蜜罐 {honeypot_id} 不存在")
                return {
                    "status": "error",
                    "error": f"蜜罐 {honeypot_id} 不存在",
                    "timestamp": "2026-03-07T12:00:00Z"
                }
            
            self.logger.info(f"更新蜜罐 {honeypot_id}")
            # 模拟更新过程
            await asyncio.sleep(random.uniform(0.5, 1.5))
            
            honeypot = self.deployed_honeypots[honeypot_id]
            honeypot.update(updates)
            honeypot['last_activity'] = "2026-03-07T12:00:00Z"
            
            self.logger.info(f"蜜罐更新成功: {honeypot_id}")
            return honeypot
        except Exception as e:
            self.logger.error(f"蜜罐更新失败: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": "2026-03-07T12:00:00Z"
            }
    
    async def stop_honeypot(self, honeypot_id: str) -> Dict[str, Any]:
        """停止蜜罐"""
        try:
            if honeypot_id not in self.deployed_honeypots:
                self.logger.warning(f"蜜罐 {honeypot_id} 不存在")
                return {
                    "status": "error",
                    "error": f"蜜罐 {honeypot_id} 不存在",
                    "timestamp": "2026-03-07T12:00:00Z"
                }
            
            self.logger.info(f"停止蜜罐 {honeypot_id}")
            # 模拟停止过程
            await asyncio.sleep(random.uniform(0.5, 1.5))
            
            honeypot = self.deployed_honeypots[honeypot_id]
            honeypot['status'] = "stopped"
            honeypot['last_activity'] = "2026-03-07T12:00:00Z"
            
            self.logger.info(f"蜜罐停止成功: {honeypot_id}")
            return honeypot
        except Exception as e:
            self.logger.error(f"蜜罐停止失败: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": "2026-03-07T12:00:00Z"
            }
    
    def get_deployed_honeypots(self) -> List[Dict[str, Any]]:
        """获取已部署的蜜罐列表"""
        return list(self.deployed_honeypots.values())
    
    def adjust_bait_strategy(self, threat_level: str, adjustment: Dict[str, Any]) -> Dict[str, Any]:
        """调整诱饵策略"""
        try:
            self.logger.info(f"调整诱饵策略，威胁等级: {threat_level}")
            # 模拟策略调整
            strategy = {
                "threat_level": threat_level,
                "bait_ratio": adjustment.get('bait_ratio', 0.5),
                "honeytoken_count": adjustment.get('honeytoken_count', 10),
                "deception_level": adjustment.get('deception_level', 'medium'),
                "updated_at": "2026-03-07T12:00:00Z"
            }
            
            self.logger.info(f"诱饵策略调整成功: {strategy}")
            return strategy
        except Exception as e:
            self.logger.error(f"诱饵策略调整失败: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": "2026-03-07T12:00:00Z"
            }
    
    async def run(self) -> Dict[str, Any]:
        """运行Baiter智能体"""
        try:
            self.logger.info("开始运行Baiter智能体")
            # 生成假数据（包括使用AI生成文档内容）
            user_data = await self.generate_fake_data("user_data", 5)
            internal_docs = await self.generate_fake_data("internal_documents", 3)
            # 部署蜜罐
            honeypot = await self.deploy_honeypot("web_server", "test_honeypot")
            # 调整诱饵策略
            strategy = self.adjust_bait_strategy("medium", {"bait_ratio": 0.7, "honeytoken_count": 15})
            
            return {
                "fake_data_generated": len(user_data) + len(internal_docs),
                "user_data_generated": len(user_data),
                "internal_docs_generated": len(internal_docs),
                "deployed_honeypots": self.get_deployed_honeypots(),
                "bait_strategy": strategy,
                "mcp_integrations": {
                    "generative_ai": self.generative_ai_config.get('enabled', False),
                    "honeypot_manager": self.honeypot_manager_config.get('enabled', False),
                    "file_watermark": self.file_watermark_config.get('enabled', False),
                    "docker": self.docker_config.get('enabled', False)
                },
                "status": "success",
                "timestamp": "2026-03-07T12:00:00Z"
            }
        except Exception as e:
            self.logger.error(f"Baiter智能体运行失败: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": "2026-03-07T12:00:00Z"
            }

if __name__ == "__main__":
    # 测试代码
    import json
    
    # 加载配置文件
    with open("../../config/baiter_config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
    
    agent = BaiterAgent(config)
    result = asyncio.run(agent.run())
    print(json.dumps(result, indent=2, ensure_ascii=False))