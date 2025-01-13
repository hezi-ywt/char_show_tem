# 角色图片评分系统 🌟

一个用于收集用户对动漫角色图片偏好的Web应用，支持脸部和全身图片的分类评分。

## ✨ 特色功能

- 🎯 分类展示：分别展示角色的脸部图片和全身图片
- 🔄 智能排序：优先展示同时具有脸部和全身图片的角色，其他随机排序
- 📝 评分历史：可以查看和编辑之前的评分记录
- 🚀 跳过功能：遇到没有满意图片的角色可以跳过
- 💾 数据备份：支持MongoDB数据库导入导出功能

## 🚀 快速开始

1. 安装MongoDB：
```bash
# Windows
# 1. 从官网下载 MongoDB Community Server:
# https://www.mongodb.com/try/download/community

# 2. 运行下载的.msi文件
# - 选择"Complete"安装
# - 取消勾选"Install MongoDB Compass"
# - 点击"Install"

# 3. 创建数据目录
mkdir C:\data\db

# 4. 添加MongoDB到系统环境变量
# - 打开系统属性 -> 环境变量
# - 在Path中添加: C:\Program Files\MongoDB\Server\6.0\bin
# - 确认并重启终端

# 5. 启动MongoDB服务
mongod --dbpath C:\data\db

# 如果看到错误，也可以使用完整路径：
# "C:\Program Files\MongoDB\Server\6.0\bin\mongod.exe" --dbpath C:\data\db

# Linux (Ubuntu/Debian)
# 1. 导入MongoDB公钥
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -

# 2. 添加MongoDB源
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list

# 3. 更新包列表并安装MongoDB
sudo apt-get update
sudo apt-get install -y mongodb-org

# 4. 启动MongoDB服务
sudo systemctl start mongod

# 5. 设置开机自启
sudo systemctl enable mongod

# 检查MongoDB状态
sudo systemctl status mongod

# Linux (在Docker容器中)
# 1. 安装MongoDB
curl -fsSL https://pgp.mongodb.com/server-7.0.asc | \
   gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg \
   --dearmor
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-7.0.list
apt-get update
apt-get install -y mongodb-org

# 2. 创建数据目录和日志目录
mkdir -p db
mkdir -p log

# 3. 直接启动MongoDB
mongod --fork --logpath log/mongodb.log --dbpath db

# 4. 检查MongoDB是否运行
ps aux | grep mongod

# 如果上述方法不行，也可以使用完整路径：
# /usr/bin/mongod --fork --logpath log/mongodb.log --dbpath db

# 5. 检查MongoDB是否正常工作
mongosh --eval "db.version()"
```

2. 克隆仓库：
```bash
git clone https://github.com/hezi-ywt/char_show_tem.git
```

3. 安装Python依赖：
```bash
pip install -r requirements.txt
```

4. 导入示例数据：
```bash
# 查看可用的数据备份
python import_db.py

# 选择要导入的备份
# 如果是首次使用，直接按Enter使用最新备份
```

5. 运行应用（根据环境选择）：

```bash
# 本地运行
uvicorn backend.main:app --host 0.0.0.0 --port 8111

# AutoDL环境运行
# 1. 在启动器中设置HTTP端口（例如：6006）
# 2. 运行以下命令
uvicorn backend.main:app --host 127.0.0.1 --port 6006 --reload --proxy-headers --forwarded-allow-ips='*'

# 或者使用环境变量
export PORT=6006
uvicorn backend.main:app --host 127.0.0.1 --port $PORT --reload
```

## 📁 项目结构

```
char_show_tem/
├── backend/
│   ├── main.py         # FastAPI应用主文件
│   ├── database.py     # 数据库操作
│   └── models.py       # 数据模型
├── frontend/
│   ├── index.html      # 主页面
│   ├── script.js       # 前端逻辑
│   └── style.css       # 样式表
├── static/
│   ├── character_images/       # 全身图片
│   └── character_images_face/  # 脸部图片
├── db_export/          # 数据库备份
├── export_db.py        # 数据导出工具
└── import_db.py        # 数据导入工具
```

## 📝 使用说明

1. 首次访问需要输入用户ID
2. 系统会展示角色信息和相关图片
3. 可以选择喜欢的脸部和全身图片
4. 点击"提交选择"保存评分，或"没有满意的图片"跳过
5. 可以通过"历史记录"查看和编辑之前的评分

## 🔄 数据管理

导出数据库：
```bash
python export_db.py
```

导入数据库：
```bash
# 1. 确保MongoDB正在运行（默认端口27017）
ps aux | grep mongod

# 2. 检查MongoDB连接
mongosh --port 27017

# 3. 创建dan数据库（如果是首次使用）
mongosh --port 27017 --eval "use dan"

# 4. 导入数据
python import_db.py
# - 查看可用的备份列表
# - 首次使用直接按Enter使用最新备份
# - 等待导入完成

# 5. 验证数据导入
mongosh --port 27017 --eval "use dan; db.char_detailed_info.count()"
```

## 📄 许可证

MIT License

## 💡 特殊环境说明

### AutoDL环境

1. 端口配置：
   - 在启动器中设置HTTP端口（例如：6006）
   - 使用127.0.0.1作为host
   - 确保端口与启动器中设置的一致

2. MongoDB配置：
   - 使用相对路径存储数据：`db`目录
   - 使用相对路径存储日志：`log`目录

3. 访问应用：
   - 使用AutoDL提供的访问链接
   - 端口号与启动器中设置的一致






