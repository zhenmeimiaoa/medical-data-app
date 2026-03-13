FROM kivy/buildozer:latest

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY . /app/

# 设置权限
RUN chmod +x /app

# 默认命令
CMD ["buildozer", "android", "debug"]
