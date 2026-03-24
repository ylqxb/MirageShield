# © 2026 MirageShield 团队 版权所有，侵权必究
import json
import os
from datetime import datetime

class DeletionRecordManager:
    def __init__(self, records_file='deletion_records.json'):
        """初始化删除操作记录管理器"""
        self.records_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'data',
            records_file
        )
        # 确保目录存在
        os.makedirs(os.path.dirname(self.records_file), exist_ok=True)
        # 确保记录文件存在
        if not os.path.exists(self.records_file):
            with open(self.records_file, 'w', encoding='utf-8') as f:
                json.dump([], f)
    
    def add_record(self, file_path, deleted_lines, operator, approver=None, approval_status=False, reason=None):
        """添加删除操作记录"""
        record = {
            "id": self._generate_id(),
            "timestamp": datetime.now().isoformat(),
            "file_path": file_path,
            "deleted_lines": deleted_lines,
            "operator": operator,
            "approver": approver,
            "approval_status": approval_status,
            "reason": reason
        }
        
        # 读取现有记录
        records = self.get_all_records()
        # 添加新记录
        records.append(record)
        # 写回文件
        with open(self.records_file, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        
        return record
    
    def get_all_records(self):
        """获取所有删除操作记录"""
        try:
            with open(self.records_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []
    
    def get_record_by_id(self, record_id):
        """根据ID获取删除操作记录"""
        records = self.get_all_records()
        for record in records:
            if record.get('id') == record_id:
                return record
        return None
    
    def get_records_by_file(self, file_path):
        """根据文件路径获取删除操作记录"""
        records = self.get_all_records()
        return [record for record in records if record.get('file_path') == file_path]
    
    def get_records_by_operator(self, operator):
        """根据操作者获取删除操作记录"""
        records = self.get_all_records()
        return [record for record in records if record.get('operator') == operator]
    
    def get_records_by_date_range(self, start_date, end_date):
        """根据日期范围获取删除操作记录"""
        records = self.get_all_records()
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)
        
        return [record for record in records if 
                start_dt <= datetime.fromisoformat(record.get('timestamp')) <= end_dt]
    
    def update_record_approval(self, record_id, approver, approval_status, reason):
        """更新记录的批准状态"""
        records = self.get_all_records()
        for record in records:
            if record.get('id') == record_id:
                record['approver'] = approver
                record['approval_status'] = approval_status
                record['reason'] = reason
                # 写回文件
                with open(self.records_file, 'w', encoding='utf-8') as f:
                    json.dump(records, f, ensure_ascii=False, indent=2)
                return record
        return None
    
    def _generate_id(self):
        """生成唯一记录ID"""
        import uuid
        return str(uuid.uuid4())
