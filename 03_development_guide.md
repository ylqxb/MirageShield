# 开发指南

## 模块构建规范

### 1. 代码结构

MirageShield 采用模块化设计，代码结构如下：

```
MirageShield/
├── agents/           # AI 智能体
│   ├── ai1/          # Prober 智能体
│   ├── ai2/          # Baiter 智能体
│   └── ai3/          # Watcher 智能体
├── api/              # API 服务
├── community/        # 社区联防
├── config/           # 配置文件
├── control_plane/    # 控制平面
├── data_plane/       # 数据平面
├── network/          # 网络模块
├── ui/               # 前端界面
└── utils/            # 工具函数
```

### 2. 开发流程

#### 2.1 环境搭建

1. **克隆代码库**
```bash
git clone https://github.com/ylqxb/MirageShield.git
cd MirageShield
```

2. **创建开发环境**
```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 安装开发依赖
pip install pytest flake8 black
```

#### 2.2 模块开发

**创建新模块**：
1. 在对应目录下创建新文件
2. 遵循现有的代码风格和命名规范
3. 实现核心功能
4. 添加适当的注释和文档

**修改现有模块**：
1. 理解现有代码的功能和结构
2. 进行必要的修改
3. 确保修改不会破坏现有功能
4. 运行测试验证修改

### 3. 智能体开发

#### 3.1 智能体架构

每个智能体由以下部分组成：
- **核心逻辑**：实现智能体的主要功能
- **配置管理**：处理智能体的配置
- **通信机制**：与其他智能体和系统的通信
- **错误处理**：处理异常情况

#### 3.2 智能体开发规范

1. **命名规范**：
   - 智能体类名：`ProberAgent`、`BaiterAgent`、`WatcherAgent`
   - 方法名：使用小写字母和下划线，如 `scan_network()`
   - 变量名：使用小写字母和下划线，如 `network_scan_results`

2. **代码风格**：
   - 遵循 PEP 8 代码风格
   - 使用 4 空格缩进
   - 每行代码不超过 80 字符

3. **文档规范**：
   - 每个智能体类和方法都要有文档字符串
   - 文档字符串应包含功能描述、参数说明和返回值

### 4. API 开发

#### 4.1 API 架构

MirageShield 使用 Flask 框架实现 RESTful API，API 架构如下：
- **蓝图**：按功能模块组织 API 路由
- **中间件**：处理认证、日志等横切关注点
- **控制器**：处理 API 请求和响应
- **服务**：实现业务逻辑

#### 4.2 API 开发规范

1. **路由命名**：
   - 使用 RESTful 风格，如 `/api/system/status`
   - 路由参数使用 `<param>` 格式

2. **请求处理**：
   - 使用 `request.get_json()` 获取请求数据
   - 验证请求参数的有效性
   - 处理异常情况并返回适当的错误码

3. **响应格式**：
   - 统一响应格式：
     ```json
     {
       "code": 200,
       "data": {...},
       "msg": "success"
     }
     ```
   - 错误响应：
     ```json
     {
       "code": 400,
       "data": null,
       "msg": "参数错误"
     }
     ```

### 5. 前端开发

#### 5.1 前端架构

MirageShield 使用纯 HTML、CSS 和 JavaScript 实现前端界面，前端架构如下：
- **页面**：按功能模块组织页面
- **脚本**：处理页面交互和 API 调用
- **样式**：定义页面样式
- **国际化**：支持多语言

#### 5.2 前端开发规范

1. **命名规范**：
   - CSS 类名：使用 kebab-case，如 `system-status`
   - JavaScript 变量名：使用 camelCase，如 `systemStatus`
   - 函数名：使用 camelCase，如 `updateSystemStatus()`

2. **代码风格**：
   - 遵循 JavaScript 标准风格
   - 使用 2 空格缩进
   - 每行代码不超过 80 字符

3. **API 调用**：
   - 使用 `fetch()` 或 `axios` 进行 API 调用
   - 处理 API 响应和错误
   - 实现适当的加载状态和错误提示

## 测试与调试

### 1. 单元测试

**编写单元测试**：
1. 在 `tests/` 目录下创建测试文件
2. 使用 `pytest` 框架编写测试用例
3. 测试覆盖核心功能和边界情况

**运行单元测试**：
```bash
# 运行所有测试
python -m pytest

# 运行特定测试文件
python -m pytest tests/test_auth.py

# 查看测试覆盖率
python -m pytest --cov=.
```

### 2. 集成测试

**编写集成测试**：
1. 创建测试脚本模拟完整的系统流程
2. 测试不同模块之间的交互
3. 验证系统的整体功能

**运行集成测试**：
```bash
# 启动系统
python start_server.py

# 运行集成测试
python tests/integration_test.py
```

### 3. 调试技巧

**日志调试**：
- 使用 `logger` 记录调试信息
- 配置不同的日志级别：DEBUG、INFO、WARNING、ERROR

**断点调试**：
- 使用 IDE 的断点功能
- 使用 `pdb` 进行命令行调试：
  ```python
  import pdb; pdb.set_trace()
  ```

**性能调试**：
- 使用 `cProfile` 分析性能瓶颈
- 使用 `memory_profiler` 分析内存使用

## 代码质量

### 1. 代码检查

**使用 flake8 检查代码风格**：
```bash
flake8 .
```

**使用 black 格式化代码**：
```bash
black .
```

### 2. 代码审查

**代码审查流程**：
1. 提交代码前进行自我审查
2. 提交 Pull Request
3. 团队成员进行代码审查
4. 解决审查意见
5. 合并代码

**代码审查要点**：
- 代码正确性和完整性
- 代码风格和规范
- 性能和安全性
- 文档和注释

## 开发工具

### 1. 推荐 IDE
- **Visual Studio Code**：轻量级 IDE，支持 Python、JavaScript 等语言
- **PyCharm**：专业的 Python IDE，功能丰富

### 2. 推荐插件
- **Python**：Python 语言支持
- **Flask**：Flask 框架支持
- **ESLint**：JavaScript 代码检查
- **Prettier**：代码格式化

### 3. 版本控制

**Git 工作流**：
1. **主分支**：`master`，稳定版本
2. **开发分支**：`develop`，开发中的版本
3. **特性分支**：`feature/*`，新功能开发
4. **修复分支**：`fix/*`，Bug 修复

**提交规范**：
- 提交信息应清晰描述修改内容
- 使用语义化提交信息：
  - `feat`：新功能
  - `fix`：Bug 修复
  - `docs`：文档更新
  - `style`：代码风格修改
  - `refactor`：代码重构
  - `test`：测试更新
  - `chore`：构建或依赖更新

## 部署与发布

### 1. 开发环境部署

**本地开发**：
- 使用虚拟环境
- 启用调试模式
- 热重载代码

### 2. 测试环境部署

**测试环境**：
- 模拟生产环境配置
- 运行完整的测试套件
- 进行性能测试

### 3. 生产环境部署

**生产环境**：
- 禁用调试模式
- 配置生产级别的日志
- 启用 HTTPS
- 配置监控和告警

### 4. 版本发布

**发布流程**：
1. 更新版本号
2. 更新 CHANGELOG.md
3. 运行测试套件
4. 构建发布包
5. 部署到生产环境
6. 验证发布结果

## 开发资源

### 1. 文档资源
- **项目文档**：DOCS_README.md
- **API 文档**：README.md 中的 API 部分
- **技术文档**：08_安全白皮书.md

### 2. 代码资源
- **核心模块**：agents/、control_plane/、data_plane/
- **API 模块**：api/
- **前端模块**：ui/

### 3. 社区资源
- **GitHub Issues**：提交问题和功能请求
- **Discord/Slack**：社区交流
- **邮件列表**：开发讨论

---

**最后更新时间**：2026-03-26
**适配版本**：MirageShield v0.2.1