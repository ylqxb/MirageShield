# © 2026 MirageShield 团队 版权所有，侵权必究
# 本项目已申请发明专利，未经许可禁止商用
import os
import re
import json
import logging
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify

# 创建日志管理蓝图
logs_bp = Blueprint('logs', __name__)

# 配置日志
logger = logging.getLogger('api.logs')

# 日志文件路径
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# 日志文件路径
LOG_FILE = os.path.join(LOG_DIR, 'mirageshield.log')

# 日志级别映射
LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

# 日志格式正则表达式
LOG_PATTERN = re.compile(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) \| (DEBUG|INFO|WARNING|ERROR|CRITICAL) \| ([^:]+):([^:]+):(\d+) - (.+)$')

def parse_log_line(line):
    """解析日志行"""
    match = LOG_PATTERN.match(line)
    if match:
        timestamp_str, level, module, function, line_num, message = match.groups()
        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')
        return {
            'timestamp': timestamp.isoformat(),
            'level': level,
            'module': module,
            'function': function,
            'line': int(line_num),
            'message': message
        }
    return None

def read_logs(start_time=None, end_time=None, level=None, module=None, limit=100):
    """读取日志"""
    logs = []
    try:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    log_entry = parse_log_line(line)
                    if not log_entry:
                        continue
                    
                    # 时间过滤
                    log_time = datetime.fromisoformat(log_entry['timestamp'])
                    if start_time and log_time < start_time:
                        continue
                    if end_time and log_time > end_time:
                        continue
                    
                    # 级别过滤
                    if level and log_entry['level'] != level:
                        continue
                    
                    # 模块过滤
                    if module and module not in log_entry['module']:
                        continue
                    
                    logs.append(log_entry)
                    
                    # 限制数量
                    if len(logs) >= limit:
                        break
    except Exception as e:
        logger.error(f"读取日志失败: {str(e)}")
    
    return logs

@logs_bp.route('/api/logs', methods=['GET'])
def get_logs():
    """获取日志"""
    try:
        # 解析参数
        start_time_str = request.args.get('start_time')
        end_time_str = request.args.get('end_time')
        level = request.args.get('level')
        module = request.args.get('module')
        limit = int(request.args.get('limit', 100))
        
        # 处理时间参数
        start_time = None
        end_time = None
        
        if start_time_str:
            start_time = datetime.fromisoformat(start_time_str)
        if end_time_str:
            end_time = datetime.fromisoformat(end_time_str)
        
        # 读取日志
        logs = read_logs(start_time, end_time, level, module, limit)
        
        return jsonify({
            'logs': logs,
            'total': len(logs)
        })
    except Exception as e:
        logger.error(f"获取日志失败: {str(e)}")
        return jsonify({"error": str(e)}), 500

@logs_bp.route('/api/logs/stats', methods=['GET'])
def get_log_stats():
    """获取日志统计信息"""
    try:
        # 读取最近24小时的日志
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=24)
        
        logs = read_logs(start_time, end_time)
        
        # 统计信息
        stats = {
            'total': len(logs),
            'by_level': {},
            'by_module': {},
            'time_range': {
                'start': start_time.isoformat(),
                'end': end_time.isoformat()
            }
        }
        
        # 按级别统计
        for log in logs:
            level = log['level']
            if level not in stats['by_level']:
                stats['by_level'][level] = 0
            stats['by_level'][level] += 1
        
        # 按模块统计
        for log in logs:
            module = log['module']
            if module not in stats['by_module']:
                stats['by_module'][module] = 0
            stats['by_module'][module] += 1
        
        return jsonify(stats)
    except Exception as e:
        logger.error(f"获取日志统计失败: {str(e)}")
        return jsonify({"error": str(e)}), 500

@logs_bp.route('/api/logs/clear', methods=['POST'])
def clear_logs():
    """清除日志"""
    try:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'w', encoding='utf-8') as f:
                f.write('')
            logger.info("日志已清除")
        return jsonify({"success": True, "message": "日志已清除"})
    except Exception as e:
        logger.error(f"清除日志失败: {str(e)}")
        return jsonify({"error": str(e)}), 500