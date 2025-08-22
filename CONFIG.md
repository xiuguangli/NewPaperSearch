# 环境配置说明

本项目使用 `.env` 文件来统一管理所有配置参数，包括数据库连接、API密钥、服务端口等。

## 快速开始

1. **复制配置模板**：
   ```bash
   cp .env.example .env
   ```

2. **编辑配置文件**：
   ```bash
   nano .env  # 或使用其他编辑器
   ```

3. **查看当前配置**：
   ```bash
   python config.py
   ```

## 配置项说明

### 后端 Flask 应用配置
- `FLASK_HOST`: Flask服务器监听地址 (默认: 0.0.0.0)
- `FLASK_PORT`: Flask服务器端口 (默认: 5000)
- `FLASK_DEBUG`: 是否启用调试模式 (默认: false)
- `FLASK_ENV`: Flask环境 (默认: production)

### 前端 Vite 开发服务器配置
- `VITE_DEV_PORT`: Vite开发服务器端口 (默认: 5173)
- `VITE_API_PROXY_TARGET`: API代理目标地址 (默认: http://localhost:5000)

### MongoDB 数据库配置
- `MONGO_HOST`: MongoDB主机地址 (默认: localhost)
- `MONGO_PORT`: MongoDB端口 (默认: 27017)
- `MONGO_USER`: MongoDB用户名
- `MONGO_PASSWORD`: MongoDB密码
- `MONGO_DATABASE`: MongoDB数据库名 (默认: papersearch)
- `MONGO_URI`: 完整的MongoDB连接字符串 (可选，优先级高于单独参数)

### 日志配置
- `LOG_DIR`: 日志文件目录 (默认: logs)
- `LOG_RETENTION_DAYS`: 日志保留天数 (默认: 30)
- `LOG_MAX_SIZE`: 日志文件大小限制 (默认: 100MB)
- `LOG_LEVEL`: 日志级别 (默认: INFO，可选: DEBUG, INFO, WARNING, ERROR)

### API 服务配置
- `API_BASE_URL`: API基础URL (默认: http://localhost:5000)
- `API_VERSION`: API版本 (默认: v1)
- `CORS_ORIGINS`: CORS允许的来源，用逗号分隔 (默认: http://localhost:5173,http://127.0.0.1:5173)

### 外部 API 配置
- `GEMINI_API_KEYS`: Gemini API密钥，用逗号分隔多个密钥
- `GEMINI_PROMPT_DEFAULT`: 默认的Gemini提示语
- `GEMINI_PROMPT_DETAILED`: 详细的Gemini提示语

### 开发配置开关
- `DEV_MODE`: 是否启用开发模式 (默认: true)
- `SHOW_ERROR_DETAILS`: 是否显示详细错误信息 (默认: true)
- `ENABLE_API_LOGGING`: 是否启用API日志 (默认: true)

## 使用方法

### 在Python代码中使用配置

```python
from config import Config

# 获取MongoDB配置
host = Config.MONGO_HOST
port = Config.MONGO_PORT

# 获取API密钥
api_keys = Config.GEMINI_API_KEYS

# 获取MongoDB连接字符串
connection_string = Config.get_mongo_connection_string()
```

### 在后端代码中

后端代码已经集成了环境变量配置，会自动从 `.env` 文件读取配置。

### 在前端代码中

前端通过Vite的环境变量系统读取配置，变量名需要以 `VITE_` 开头。

## 配置优先级

1. 环境变量 (最高优先级)
2. `.env` 文件
3. 代码中的默认值 (最低优先级)

## 安全注意事项

- ⚠️ **不要提交 `.env` 文件到版本控制系统**
- ⚠️ **保护好API密钥和数据库密码**
- ⚠️ **在生产环境中设置合适的 `FLASK_DEBUG=false`**
- ⚠️ **定期更新API密钥**

## 常见问题

### 1. 配置文件不生效
- 确保 `.env` 文件在项目根目录
- 检查环境变量名是否正确
- 重启服务后再测试

### 2. MongoDB连接失败
- 检查 `MONGO_HOST` 和 `MONGO_PORT` 是否正确
- 验证用户名和密码
- 确保MongoDB服务正在运行

### 3. API调用失败
- 检查 `VITE_API_PROXY_TARGET` 是否指向正确的后端地址
- 确认后端服务已启动
- 查看CORS配置是否正确

## 示例配置

### 开发环境示例
```env
FLASK_DEBUG=true
MONGO_HOST=localhost
MONGO_PORT=27017
VITE_DEV_PORT=5173
LOG_LEVEL=DEBUG
DEV_MODE=true
```

### 生产环境示例
```env
FLASK_DEBUG=false
FLASK_HOST=0.0.0.0
FLASK_PORT=80
MONGO_HOST=prod-mongo-server
MONGO_PORT=27017
LOG_LEVEL=WARNING
DEV_MODE=false
```
