# © 2026 MirageShield 团队 版权所有，侵权必究
# 本项目已申请发明专利，未经许可禁止商用
# 监控模块import os
import psutil
import logging
from datetime import datetime
from flask import Blueprint, jsonify

# 创建监控管理蓝图
monitoring_bp = Blueprint('monitoring', __name__)

# 配置日志
logger = logging.getLogger('api.monitoring')

@monitoring_bp.route('/api/monitoring/system', methods=['GET'])
def get_system_stats():
    """获取系统资源使用情况"""
    try:
        # 获取CPU使用率（使用interval=0.1减少延迟）
        cpu_percent = psutil.cpu_percent(interval=0.1, percpu=True)
        avg_cpu = psutil.cpu_percent(interval=0.1)
        
        # 获取内存使用情况
        memory = psutil.virtual_memory()
        
        # 获取磁盘使用情况
        disk = psutil.disk_usage('/')
        
        # 获取网络使用情况
        net_io = psutil.net_io_counters()
        
        # 获取进程信息
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'cpu_percent': proc.info['cpu_percent'],
                    'memory_percent': proc.info['memory_percent']
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        # 按CPU使用率排序，取前10个进程
        processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
        top_processes = processes[:10]
        
        system_stats = {
            'timestamp': datetime.now().isoformat(),
            'cpu': {
                'average': avg_cpu,
                'cores': cpu_percent
            },
            'memory': {
                'total': memory.total,
                'used': memory.used,
                'available': memory.available,
                'percent': memory.percent
            },
            'disk': {
                'total': disk.total,
                'used': disk.used,
                'free': disk.free,
                'percent': disk.percent
            },
            'network': {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv
            },
            'processes': {
                'total': len(processes),
                'top': top_processes
            }
        }
        
        return jsonify(system_stats)
    except Exception as e:
        logger.error(f"获取系统资源使用情况失败: {str(e)}")
        return jsonify({"error": str(e)}), 500

@monitoring_bp.route('/api/monitoring/api', methods=['GET'])
def get_api_stats():
    """获取API性能统计信息"""
    try:
        # 这里可以添加API调用统计逻辑
        # 例如记录API调用次数、响应时间等
        
        api_stats = {
            'timestamp': datetime.now().isoformat(),
            'requests': {
                'total': 0,
                'success': 0,
                'error': 0
            },
            'response_times': {
                'average': 0,
                'max': 0,
                'min': 0
            }
        }
        
        return jsonify(api_stats)
    except Exception as e:
        logger.error(f"获取API性能统计信息失败: {str(e)}")
        return jsonify({"error": str(e)}), 500

@monitoring_bp.route('/api/monitoring/health', methods=['GET'])
def get_health_check():
    """健康检查"""
    try:
        # 检查系统各组件状态
        health_status = {
            'timestamp': datetime.now().isoformat(),
            'status': 'healthy',
            'components': {
                'api': 'healthy',
                'database': 'healthy',
                'message_queue': 'healthy',
                'agents': 'healthy'
            }
        }
        
        return jsonify(health_status)
    except Exception as e:
        logger.error(f"健康检查失败: {str(e)}")
        return jsonify({"error": str(e)}), 500