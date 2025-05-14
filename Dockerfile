FROM ubuntu:20.04

# 防止交互式前端阻塞
ENV DEBIAN_FRONTEND=noninteractive

# 设置时区
ENV TZ=Asia/Shanghai

# 安装必要的软件包
RUN apt-get update && \
    apt-get install -y wget gnupg curl unzip python3 python3-pip tzdata && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 安装Google Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 创建工作目录
WORKDIR /app

# 复制应用文件
COPY . /app/

# 创建静态目录
RUN mkdir -p /app/static

# 安装Python依赖
RUN pip3 install --no-cache-dir -r requirements.txt

# 暴露端口
EXPOSE 5000

# 启动服务
CMD ["python3", "app.py"] 