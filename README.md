# 角色图片评分系统 🌟

一个用于收集用户对动漫角色图片偏好的Web应用，支持脸部和全身图片的分类评分。

## ✨ 特色功能

- 🎯 分类展示：分别展示角色的脸部图片和全身图片
- 🔄 智能排序：优先展示同时具有脸部和全身图片的角色，其他随机排序
- 📝 评分历史：可以查看和编辑之前的评分记录
- 🚀 跳过功能：遇到没有满意图片的角色可以跳过
- 💾 数据备份：支持MongoDB数据库导入导出功能

## 🚀 快速开始

1. 克隆仓库：
```bash
git clone https://github.com/hezi-ywt/char_show_tem.git
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 启动MongoDB：
```bash
mongod
```

4. 运行应用：
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8111
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
python import_db.py
```

## 📄 许可证

MIT License

## 🙏 致谢

感谢所有为这个项目做出贡献的朋友！




