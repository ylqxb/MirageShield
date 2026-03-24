# 环境变量设置指南

## 重要环境变量

### 1. ADMIN_PASSWORD
**功能**：设置管理员初始密码

**设置方法**：
- **Windows**：
  ```powershell
  # 临时设置（当前会话）
  $env:ADMIN_PASSWORD="your_secure_password"
  
  # 永久设置
  [Environment]::SetEnvironmentVariable("ADMIN_PASSWORD", "your_secure_password", "User")
  ```

- **Linux/macOS**：
  ```bash
  # 临时设置（当前会话）
  export ADMIN_PASSWORD="your_secure_password"
  
  # 永久设置（添加到 ~/.bashrc 或 ~/.zshrc）
  echo 'export ADMIN_PASSWORD="your_secure_password"' >> ~/.bashrc
  source ~/.bashrc
  ```

**注意**：
- 密码强度要求：至少8个字符，包含大小写字母、数字和特殊字符
- 如果不设置此环境变量，系统会自动生成随机初始密码并在日志中显示

### 2. 其他重要环境变量

| 环境变量 | 功能 | 必要性 |
|---------|------|--------|
| TOR_CONTROL_PASSWORD | Tor 控制密码 | 可选 |
| ENCRYPTION_KEY | 加密密钥 | 推荐 |
| IP_REPUTATION_API_KEY | IP 声誉 API 密钥 | 可选 |
| OPENAI_API_KEY | OpenAI API 密钥 | 可选 |
| WATERMARK_KEY | 水印密钥 | 推荐 |

## 自动备份机制

### 功能说明
- 系统会在每次修改用户数据时自动创建备份
- 备份文件存储在 `backups/` 目录
- 自动清理旧备份，保留最近5个

### 手动备份
```python
from utils.backup import backup_users_data
backup_users_data()
```

### 恢复备份
```python
from utils.backup import restore_users_data
restore_users_data()  # 恢复最新备份
# 或指定备份文件
# restore_users_data("backups/users_20260323_123456.json")
```

### 查看备份列表
```python
from utils.backup import get_backup_list
backups = get_backup_list()
for backup in backups:
    print(f"{backup['file_name']} - {backup['modified_time']}")
```

## 预防措施

1. **定期备份**：系统会自动备份，但建议定期手动备份重要数据
2. **环境变量管理**：使用环境变量管理敏感信息，避免硬编码
3. **密码管理**：使用强密码，并定期更换
4. **权限控制**：限制对用户数据文件的访问权限
5. **监控**：定期检查系统日志，确保备份正常执行

## 故障恢复

如果遇到管理员密码丢失的情况：

1. **使用备份恢复**：
   ```python
   from utils.backup import restore_users_data
   restore_users_data()
   ```

2. **重置管理员密码**：
   - 删除 `data/users.json` 文件
   - 设置 `ADMIN_PASSWORD` 环境变量
   - 重启系统，系统会自动创建新的管理员用户

3. **检查日志**：如果未设置 `ADMIN_PASSWORD`，系统会在日志中生成随机初始密码

## 最佳实践

- **生产环境**：设置 `ADMIN_PASSWORD` 环境变量，使用强密码
- **开发环境**：可以使用随机生成的密码，方便测试
- **定期检查**：定期检查备份文件是否正常生成
- **版本控制**：不要将包含敏感信息的文件提交到版本控制系统
