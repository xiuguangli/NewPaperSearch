# 使用官方 Python 镜像作为基础
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 复制后端应用代码
COPY . .

# 暴露 Gunicorn 服务的端口
EXPOSE 5000

# 启动 Gunicorn 服务
CMD ["gunicorn", "--workers", "3", "--bind", "0.0.0.0:5000", "app:app"]
