# © 2026 MirageShield 团队 版权所有，侵权必究
# 本项目已申请发明专利，未经许可禁止商用
# 局域网安全通信模块
import ssl
import socket
import threading
import json
import logging
import os
from datetime import datetime, timedelta

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s:%(funcName)s:%(lineno)d - %(message)s'
)
logger = logging.getLogger('network.secure_communication')

class SecureCommunication:
    def __init__(self, cert_dir='certs', host='0.0.0.0', port=5001):
        """初始化安全通信模块"""
        self.cert_dir = cert_dir
        self.host = host
        self.port = port
        self.running = False
        self.server_thread = None
        self.connections = {}
        self.lock = threading.RLock()
        
        # 确保证书目录存在
        os.makedirs(self.cert_dir, exist_ok=True)
        
        # 生成或加载证书
        self.cert_file = os.path.join(self.cert_dir, 'server.crt')
        self.key_file = os.path.join(self.cert_dir, 'server.key')
        
        # 生成自签名证书（仅用于测试）
        if not os.path.exists(self.cert_file) or not os.path.exists(self.key_file):
            self._generate_certificate()
    
    def _generate_certificate(self):
        """生成自签名证书"""
        try:
            from cryptography import x509
            from cryptography.x509.oid import NameOID
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.asymmetric import rsa
            from cryptography.hazmat.backends import default_backend
            from cryptography.hazmat.primitives import serialization
            
            # 生成私钥
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )
            
            # 生成证书签名请求
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, "CN"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Beijing"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, "Beijing"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "MirageShield"),
                x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
            ])
            
            certificate = x509.CertificateBuilder().subject_name(
                subject
            ).issuer_name(
                issuer
            ).public_key(
                private_key.public_key()
            ).serial_number(
                x509.random_serial_number()
            ).not_valid_before(
                datetime.utcnow()
            ).not_valid_after(
                datetime.utcnow() + timedelta(days=365)
            ).add_extension(
                x509.SubjectAlternativeName([x509.DNSName("localhost")]),
                critical=False,
            ).sign(private_key, hashes.SHA256(), default_backend())
            
            # 保存证书和私钥
            with open(self.cert_file, "wb") as f:
                f.write(certificate.public_bytes(serialization.Encoding.PEM))
            
            with open(self.key_file, "wb") as f:
                f.write(private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            
            logger.info("自签名证书生成成功")
        except Exception as e:
            logger.error(f"生成证书时出错: {str(e)}")
            # 如果生成失败，使用不安全的通信
            self.use_secure = False
            logger.warning("将使用不安全的通信")
        else:
            self.use_secure = True
    
    def start_server(self):
        """启动安全服务器"""
        if self.running:
            logger.warning("服务器已经在运行")
            return
        
        self.running = True
        self.server_thread = threading.Thread(target=self._server_loop, daemon=True)
        self.server_thread.start()
        logger.info(f"安全通信服务器已启动，监听 {self.host}:{self.port}")
    
    def stop_server(self):
        """停止安全服务器"""
        self.running = False
        if self.server_thread:
            self.server_thread.join(timeout=5)
        
        # 关闭所有连接
        with self.lock:
            for conn in self.connections.values():
                try:
                    conn.close()
                except Exception:
                    pass
            self.connections.clear()
        
        logger.info("安全通信服务器已停止")
    
    def _server_loop(self):
        """服务器循环"""
        try:
            # 创建套接字
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((self.host, self.port))
            sock.listen(5)
            
            while self.running:
                try:
                    sock.settimeout(1)
                    conn, addr = sock.accept()
                    
                    if self.use_secure:
                        # 包装为SSL连接
                        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
                        context.load_cert_chain(certfile=self.cert_file, keyfile=self.key_file)
                        context.check_hostname = False  # 局域网内不检查主机名
                        context.verify_mode = ssl.CERT_NONE  # 不验证客户端证书
                        
                        try:
                            ssl_conn = context.wrap_socket(conn, server_side=True)
                            client_thread = threading.Thread(
                                target=self._handle_client, 
                                args=(ssl_conn, addr),
                                daemon=True
                            )
                            client_thread.start()
                        except ssl.SSLError as e:
                            logger.error(f"SSL连接错误: {str(e)}")
                            conn.close()
                    else:
                        # 使用不安全的连接
                        client_thread = threading.Thread(
                            target=self._handle_client, 
                            args=(conn, addr),
                            daemon=True
                        )
                        client_thread.start()
                except socket.timeout:
                    continue
                except Exception as e:
                    logger.error(f"服务器循环出错: {str(e)}")
                    break
        finally:
            if 'sock' in locals():
                try:
                    sock.close()
                except Exception:
                    pass
    
    def _handle_client(self, conn, addr):
        """处理客户端连接"""
        client_id = f"{addr[0]}:{addr[1]}"
        logger.info(f"新客户端连接: {client_id}")
        
        with self.lock:
            self.connections[client_id] = conn
        
        try:
            while self.running:
                try:
                    # 接收数据
                    data = conn.recv(4096)
                    if not data:
                        break
                    
                    # 处理数据
                    message = data.decode('utf-8')
                    self._process_message(message, client_id)
                except socket.timeout:
                    continue
                except Exception as e:
                    logger.error(f"处理客户端数据时出错: {str(e)}")
                    break
        finally:
            with self.lock:
                if client_id in self.connections:
                    del self.connections[client_id]
            try:
                conn.close()
            except Exception:
                pass
            logger.info(f"客户端连接关闭: {client_id}")
    
    def _process_message(self, message, client_id):
        """处理收到的消息"""
        try:
            data = json.loads(message)
            message_type = data.get('type')
            
            if message_type == 'ping':
                # 响应ping
                response = {
                    'type': 'pong',
                    'timestamp': datetime.now().isoformat()
                }
                self.send_message(client_id, response)
            elif message_type == 'data_transfer':
                # 处理数据传输
                data_content = data.get('data')
                data_id = data.get('data_id')
                logger.info(f"收到数据传输请求: {data_id}")
                # 这里可以添加数据处理逻辑
            elif message_type == 'data_request':
                # 处理数据请求
                data_id = data.get('data_id')
                logger.info(f"收到数据请求: {data_id}")
                # 这里可以添加数据请求处理逻辑
        except json.JSONDecodeError:
            logger.error("收到无效的JSON消息")
        except Exception as e:
            logger.error(f"处理消息时出错: {str(e)}")
    
    def send_message(self, client_id, message):
        """发送消息给客户端"""
        with self.lock:
            if client_id in self.connections:
                conn = self.connections[client_id]
                try:
                    message_str = json.dumps(message)
                    conn.sendall(message_str.encode('utf-8'))
                    return True
                except Exception as e:
                    logger.error(f"发送消息时出错: {str(e)}")
                    return False
            return False
    
    def send_data(self, client_id, data_id, data):
        """发送数据给客户端"""
        message = {
            'type': 'data_transfer',
            'data_id': data_id,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        return self.send_message(client_id, message)
    
    def request_data(self, client_id, data_id):
        """向客户端请求数据"""
        message = {
            'type': 'data_request',
            'data_id': data_id,
            'timestamp': datetime.now().isoformat()
        }
        return self.send_message(client_id, message)
    
    def get_connections(self):
        """获取当前连接列表"""
        with self.lock:
            return list(self.connections.keys())
    
    def connect_to_node(self, ip, port):
        """连接到其他节点"""
        try:
            # 创建套接字
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            if self.use_secure:
                # 包装为SSL连接
                context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
                context.check_hostname = False  # 局域网内不检查主机名
                context.verify_mode = ssl.CERT_NONE  # 不验证服务器证书
                
                try:
                    ssl_conn = context.wrap_socket(sock, server_hostname=ip)
                    ssl_conn.connect((ip, port))
                    client_id = f"{ip}:{port}"
                    
                    with self.lock:
                        self.connections[client_id] = ssl_conn
                    
                    # 启动线程处理连接
                    client_thread = threading.Thread(
                        target=self._handle_client, 
                        args=(ssl_conn, (ip, port)),
                        daemon=True
                    )
                    client_thread.start()
                    
                    logger.info(f"成功连接到节点: {client_id}")
                    return client_id
                except ssl.SSLError as e:
                    logger.error(f"SSL连接错误: {str(e)}")
                    sock.close()
                    return None
            else:
                # 使用不安全的连接
                sock.connect((ip, port))
                client_id = f"{ip}:{port}"
                
                with self.lock:
                    self.connections[client_id] = sock
                
                # 启动线程处理连接
                client_thread = threading.Thread(
                    target=self._handle_client, 
                    args=(sock, (ip, port)),
                    daemon=True
                )
                client_thread.start()
                
                logger.info(f"成功连接到节点: {client_id}")
                return client_id
        except Exception as e:
            logger.error(f"连接到节点时出错: {str(e)}")
            return None

if __name__ == "__main__":
    # 测试代码
    import time
    from datetime import timedelta
    
    # 修复导入
    from cryptography import x509
    from cryptography.x509.oid import NameOID
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import serialization
    
    comm = SecureCommunication()
    comm.start_server()
    
    try:
        while True:
            connections = comm.get_connections()
            print(f"当前连接: {connections}")
            time.sleep(5)
    except KeyboardInterrupt:
        comm.stop_server()
        print("测试结束")
