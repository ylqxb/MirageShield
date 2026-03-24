# © 2026 MirageShield 团队 版权所有，侵权必究
# 本项目已申请发明专利，未经许可禁止商用
# 诱饵数据池
import json
import logging
import os
import hashlib
import threading
from collections import OrderedDict
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s:%(funcName)s:%(lineno)d - %(message)s'
)
logger = logging.getLogger('data_plane.decoy_data_pool')

class DecoyDataPool:
    def __init__(self, data_dir='data/decoy'):
        """初始化诱饵数据池"""
        try:
            # 创建数据目录
            self.data_dir = data_dir
            os.makedirs(self.data_dir, exist_ok=True)
            
            # 创建冷热数据目录
            self.hot_data_dir = os.path.join(self.data_dir, 'hot')
            self.cold_data_dir = os.path.join(self.data_dir, 'cold')
            os.makedirs(self.hot_data_dir, exist_ok=True)
            os.makedirs(self.cold_data_dir, exist_ok=True)
            
            # 数据索引
            self.index_file = os.path.join(self.data_dir, 'index.json')
            # 线程安全同步锁
            self.lock = threading.RLock()
            self.index = self._load_index()
            
            # 内存缓存，使用有序字典管理访问顺序
            self.memory_cache = OrderedDict()
            self.cache_size = 100  # 缓存大小限制
            
            # 热数据阈值（访问次数）
            self.hot_data_threshold = 5
            # 冷数据阈值（最后访问时间，天数）
            self.cold_data_threshold = 7
            
            # 访问控制
            self.allowed_agents = {'baiter', 'prober'}
            
            # 初始化时进行数据冷热分离
            self._initialize_data_classification()
            
            logger.info("诱饵数据池初始化完成")
            
        except Exception as e:
            logger.error(f"初始化失败: {str(e)}")
            raise
    
    def _load_index(self):
        """加载数据索引"""
        with self.lock:
            if os.path.exists(self.index_file):
                try:
                    with open(self.index_file, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except Exception as e:
                    logger.error(f"加载索引失败: {str(e)}")
                    return {}
            return {}
    
    def _save_index(self):
        """保存数据索引"""
        with self.lock:
            try:
                with open(self.index_file, 'w', encoding='utf-8') as f:
                    json.dump(self.index, f, indent=2, ensure_ascii=False)
            except Exception as e:
                logger.error(f"保存索引失败: {str(e)}")
    
    def store_data(self, data, data_type, agent_name, watermark=None):
        """存储诱饵数据"""
        if agent_name not in self.allowed_agents:
            logger.error(f"Agent {agent_name} 无权限访问诱饵数据池")
            return None
        
        try:
            with self.lock:
                # 生成数据ID
                data_id = hashlib.md5(f"{datetime.now().isoformat()}{str(data)}".encode('utf-8')).hexdigest()
                
                # 添加水印
                if watermark:
                    data['watermark'] = watermark
                
                # 确定存储目录（新数据默认为普通数据）
                storage_dir = self.data_dir
                data_category = 'normal'
                
                # 存储数据
                data_file = os.path.join(storage_dir, f"{data_id}.json")
                with open(data_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                # 更新索引
                self.index[data_id] = {
                    "data_type": data_type,
                    "agent_name": agent_name,
                    "watermark": watermark,
                    "stored_at": datetime.now().isoformat(),
                    "size": os.path.getsize(data_file),
                    "access_count": 0,
                    "honeytoken_count": self._count_honeytokens(data),
                    "data_category": data_category
                }
                self._save_index()
                
                # 放入内存缓存
                if len(self.memory_cache) >= self.cache_size:
                    # 清理最早的缓存项（LRU策略，移除最久未使用的项）
                    oldest_key, _ = self.memory_cache.popitem(last=False)
                    logger.debug(f"清理缓存项: {oldest_key}")
                
                # 将新数据放入缓存，自动移到字典末尾（LRU策略）
                self.memory_cache[data_id] = data
                logger.debug(f"新数据放入缓存: {data_id}")
            
            logger.info(f"诱饵数据存储成功: {data_id}")
            return data_id
        except Exception as e:
            logger.error(f"存储数据失败: {str(e)}")
            return None
    
    def _count_honeytokens(self, data):
        """计算数据中的蜜罐令牌数量"""
        # 简单的蜜罐令牌检测
        honeytoken_count = 0
        
        # 递归检查数据
        def check_data(d):
            nonlocal honeytoken_count
            if isinstance(d, dict):
                for key, value in d.items():
                    if 'honeytoken' in key.lower() or 'bait' in key.lower():
                        honeytoken_count += 1
                    check_data(value)
            elif isinstance(d, list):
                for item in d:
                    check_data(item)
            elif isinstance(d, str):
                if 'honeytoken' in d.lower() or 'bait' in d.lower():
                    honeytoken_count += 1
        
        check_data(data)
        return honeytoken_count
    
    def _initialize_data_classification(self):
        """初始化数据冷热分类"""
        logger.info("开始初始化数据冷热分类")
        with self.lock:
            for data_id, info in self.index.items():
                # 根据访问次数和最后访问时间判断数据类型
                access_count = info.get('access_count', 0)
                last_accessed = info.get('last_accessed')
                
                # 确定数据存储目录
                if access_count >= self.hot_data_threshold:
                    # 热数据
                    info['data_category'] = 'hot'
                elif last_accessed:
                    # 检查最后访问时间
                    last_access_time = datetime.fromisoformat(last_accessed)
                    days_since_access = (datetime.now() - last_access_time).days
                    if days_since_access >= self.cold_data_threshold:
                        # 冷数据
                        info['data_category'] = 'cold'
                    else:
                        # 普通数据
                        info['data_category'] = 'normal'
                else:
                    # 新数据默认为普通数据
                    info['data_category'] = 'normal'
            
            # 保存更新后的索引
            self._save_index()
            logger.info("数据冷热分类初始化完成")
    
    def _move_data_to_category(self, data_id, new_category):
        """将数据移动到指定分类
        
        Args:
            data_id: 数据ID
            new_category: 新的分类 ('hot', 'cold', 'normal')
        """
        try:
            # 获取当前分类
            current_category = self.index[data_id].get('data_category', 'normal')
            
            if current_category == new_category:
                # 已经是目标分类，不需要移动
                return
            
            # 确定源文件和目标文件路径
            if current_category == 'hot':
                source_file = os.path.join(self.hot_data_dir, f"{data_id}.json")
            elif current_category == 'cold':
                source_file = os.path.join(self.cold_data_dir, f"{data_id}.json")
            else:
                source_file = os.path.join(self.data_dir, f"{data_id}.json")
            
            if new_category == 'hot':
                target_file = os.path.join(self.hot_data_dir, f"{data_id}.json")
            elif new_category == 'cold':
                target_file = os.path.join(self.cold_data_dir, f"{data_id}.json")
            else:
                target_file = os.path.join(self.data_dir, f"{data_id}.json")
            
            # 移动文件
            if os.path.exists(source_file):
                import shutil
                shutil.move(source_file, target_file)
                # 更新索引
                self.index[data_id]['data_category'] = new_category
                logger.info(f"数据 {data_id} 从 {current_category} 移动到 {new_category}")
            else:
                logger.error(f"源文件不存在: {source_file}")
        except Exception as e:
            logger.error(f"移动数据失败: {str(e)}")
    
    def retrieve_data(self, data_id, agent_name):
        """检索数据"""
        if agent_name not in self.allowed_agents:
            logger.error(f"Agent {agent_name} 无权限访问诱饵数据池")
            return None
        
        try:
            data = None
            with self.lock:
                # 检查数据是否存在
                if data_id not in self.index:
                    logger.error(f"数据不存在: {data_id}")
                    return None
                
                # 检查内存缓存
                if data_id in self.memory_cache:
                    logger.debug(f"从缓存中获取数据: {data_id}")
                    # 将访问的项移到字典末尾，实现LRU策略
                    data = self.memory_cache.pop(data_id)
                    self.memory_cache[data_id] = data
                else:
                    # 确定数据文件路径
                    data_category = self.index[data_id].get('data_category', 'normal')
                    if data_category == 'hot':
                        data_file = os.path.join(self.hot_data_dir, f"{data_id}.json")
                    elif data_category == 'cold':
                        data_file = os.path.join(self.cold_data_dir, f"{data_id}.json")
                    else:
                        data_file = os.path.join(self.data_dir, f"{data_id}.json")
                    
                    if not os.path.exists(data_file):
                        logger.error(f"数据文件不存在: {data_file}")
                        return None
                    
                    with open(data_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # 放入内存缓存
                    if len(self.memory_cache) >= self.cache_size:
                        # 清理最早的缓存项（LRU策略，移除最久未使用的项）
                        oldest_key, _ = self.memory_cache.popitem(last=False)
                        logger.debug(f"清理缓存项: {oldest_key}")
                    
                    self.memory_cache[data_id] = data
                    logger.debug(f"数据放入缓存: {data_id}")
                
                # 统一更新访问计数
                self.index[data_id]["access_count"] += 1
                self.index[data_id]["last_accessed"] = datetime.now().isoformat()
                
                # 检查是否需要升级为热数据
                access_count = self.index[data_id]["access_count"]
                current_category = self.index[data_id].get('data_category', 'normal')
                
                if access_count >= self.hot_data_threshold and current_category != 'hot':
                    # 升级为热数据
                    self._move_data_to_category(data_id, 'hot')
                
                self._save_index()
            
            logger.info(f"诱饵数据检索成功: {data_id}")
            return data
        except Exception as e:
            logger.error(f"检索数据失败: {str(e)}")
            return None
    
    def retrieve_by_type(self, data_type, limit=10, agent_name=None):
        """按类型检索数据"""
        if agent_name and agent_name not in self.allowed_agents:
            logger.error(f"Agent {agent_name} 无权限访问诱饵数据池")
            return []
        
        try:
            # 找出指定类型的数据
            data_ids = []
            with self.lock:
                for data_id, info in self.index.items():
                    if info["data_type"] == data_type:
                        data_ids.append((data_id, info["stored_at"]))
            
            # 按存储时间排序
            data_ids.sort(key=lambda x: x[1], reverse=True)
            
            # 限制数量
            data_ids = data_ids[:limit]
            
            # 检索数据
            data_list = []
            for data_id, _ in data_ids:
                data = self.retrieve_data(data_id, agent_name or 'baiter')
                if data:
                    with self.lock:
                        metadata = self.index.get(data_id, {})
                    data_list.append({
                        "data_id": data_id,
                        "data": data,
                        "metadata": metadata
                    })
            
            logger.info(f"按类型检索数据成功: {data_type}, 共 {len(data_list)} 条")
            return data_list
        except Exception as e:
            logger.error(f"按类型检索数据失败: {str(e)}")
            return []
    
    def delete_data(self, data_id, agent_name):
        """删除数据"""
        if agent_name not in self.allowed_agents:
            logger.error(f"Agent {agent_name} 无权限访问诱饵数据池")
            return False
        
        try:
            with self.lock:
                # 检查数据是否存在
                if data_id not in self.index:
                    logger.error(f"数据不存在: {data_id}")
                    return False
                
                # 删除数据文件
                data_file = os.path.join(self.data_dir, f"{data_id}.json")
                if os.path.exists(data_file):
                    os.remove(data_file)
                
                # 从内存缓存中删除
                if data_id in self.memory_cache:
                    del self.memory_cache[data_id]
                    logger.debug(f"从缓存中删除数据: {data_id}")
                
                # 从索引中删除
                del self.index[data_id]
                self._save_index()
            
            logger.info(f"诱饵数据删除成功: {data_id}")
            return True
        except Exception as e:
            logger.error(f"删除数据失败: {str(e)}")
            return False
    
    def list_data(self, data_type=None, agent_name=None):
        """列出数据"""
        if agent_name and agent_name not in self.allowed_agents:
            logger.error(f"Agent {agent_name} 无权限访问诱饵数据池")
            return []
        
        try:
            data_list = []
            with self.lock:
                for data_id, info in self.index.items():
                    if data_type and info["data_type"] != data_type:
                        continue
                    data_list.append({
                        "data_id": data_id,
                        "data_type": info["data_type"],
                        "watermark": info.get("watermark"),
                        "stored_at": info["stored_at"],
                        "access_count": info.get("access_count", 0),
                        "last_accessed": info.get("last_accessed", "N/A"),
                        "honeytoken_count": info.get("honeytoken_count", 0)
                    })
            
            # 按存储时间排序
            data_list.sort(key=lambda x: x["stored_at"], reverse=True)
            
            return data_list
        except Exception as e:
            logger.error(f"列出数据失败: {str(e)}")
            return []
    
    def get_data_info(self, data_id, agent_name=None):
        """获取数据信息"""
        if agent_name and agent_name not in self.allowed_agents:
            logger.error(f"Agent {agent_name} 无权限访问诱饵数据池")
            return None
        
        with self.lock:
            return self.index.get(data_id)
    
    def clear_expired_data(self, days=3, agent_name=None):
        """清理过期数据"""
        if agent_name and agent_name not in self.allowed_agents:
            logger.error(f"Agent {agent_name} 无权限访问诱饵数据池")
            return 0
        
        try:
            expired_count = 0
            current_time = datetime.now()
            
            # 找出过期数据
            expired_ids = []
            with self.lock:
                for data_id, info in self.index.items():
                    stored_time = datetime.fromisoformat(info["stored_at"])
                    if (current_time - stored_time).days > days:
                        expired_ids.append(data_id)
            
            # 删除过期数据
            for data_id in expired_ids:
                if self.delete_data(data_id, agent_name or 'baiter'):
                    expired_count += 1
            
            logger.info(f"清理过期数据完成，共删除 {expired_count} 条数据")
            return expired_count
        except Exception as e:
            logger.error(f"清理过期数据失败: {str(e)}")
            return 0
    
    def get_statistics(self):
        """获取统计信息"""
        try:
            # 计算数据类型分布
            type_distribution = {}
            total_honeytokens = 0
            total_accesses = 0
            total_data = 0
            
            with self.lock:
                total_data = len(self.index)
                for data_id, info in self.index.items():
                    data_type = info["data_type"]
                    type_distribution[data_type] = type_distribution.get(data_type, 0) + 1
                    total_honeytokens += info.get("honeytoken_count", 0)
                    total_accesses += info.get("access_count", 0)
            
            return {
                "total_data": total_data,
                "type_distribution": type_distribution,
                "total_honeytokens": total_honeytokens,
                "total_accesses": total_accesses,
                "average_accesses_per_data": total_accesses / total_data if total_data else 0
            }
        except Exception as e:
            logger.error(f"获取统计信息失败: {str(e)}")
            return {}

if __name__ == "__main__":
    # 测试代码
    data_pool = DecoyDataPool()
    
    # 测试存储数据
    test_data = {
        "user_id": "fake_user_123",
        "name": "John Doe",
        "email": "john.doe@example.com",
        "password": "honeytoken_fake_password_123",
        "credit_card": "4111111111111111",
        "timestamp": datetime.now().isoformat()
    }
    
    data_id = data_pool.store_data(test_data, "user_data", "baiter", "CHIMERA_WATERMARK_123")
    print(f"存储数据ID: {data_id}")
    
    # 测试检索数据
    retrieved_data = data_pool.retrieve_data(data_id, "baiter")
    print(f"检索数据: {retrieved_data}")
    
    # 测试按类型检索
    user_data_list = data_pool.retrieve_by_type("user_data", 5, "baiter")
    print(f"按类型检索数据数: {len(user_data_list)}")
    
    # 测试列出数据
    data_list = data_pool.list_data()
    print(f"数据列表: {data_list}")
    
    # 测试获取统计信息
    stats = data_pool.get_statistics()
    print(f"统计信息: {stats}")
    
    # 测试清理过期数据
    expired_count = data_pool.clear_expired_data(0)  # 清理所有数据
    print(f"清理过期数据数: {expired_count}")
