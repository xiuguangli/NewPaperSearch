# --- Build Stage ---
# 使用 Node.js 镜像来构建前端应用
FROM node:20-alpine as builder

# 设置工作目录
WORKDIR /app

# 复制 package.json 和 package-lock.json
COPY package*.json ./

# 安装依赖
RUN npm install

# 复制所有前端代码
COPY . .

# 执行构建命令
RUN npm run build

# --- Final Stage ---
# 使用官方 Nginx 镜像
FROM nginx:stable-alpine

# 复制构建好的静态文件到 Nginx 的 web 根目录
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制自定义的 Nginx 配置文件
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露 80 端口
EXPOSE 80

# 启动 Nginx
CMD ["nginx", "-g", "daemon off;"]
