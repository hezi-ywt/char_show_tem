import os
import json
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from bson import ObjectId
import glob

async def import_database(import_dir="db_export", timestamp=None):
    """
    导入数据库备份
    :param import_dir: 备份文件目录
    :param timestamp: 指定要导入的时间戳，如果为None则使用最新的备份
    """
    # 连接MongoDB
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.dan
    
    # 获取要导入的文件
    if timestamp:
        char_file = os.path.join(import_dir, f"char_detailed_info_{timestamp}.json")
        rating_file = os.path.join(import_dir, f"character_rating_{timestamp}.json")
    else:
        # 获取最新的备份文件
        char_files = glob.glob(os.path.join(import_dir, "char_detailed_info_*.json"))
        rating_files = glob.glob(os.path.join(import_dir, "character_rating_*.json"))
        
        if not char_files or not rating_files:
            print("未找到备份文件")
            return
            
        char_file = max(char_files, key=os.path.getctime)
        rating_file = max(rating_files, key=os.path.getctime)
    
    # 检查文件是否存在
    if not os.path.exists(char_file) or not os.path.exists(rating_file):
        print("备份文件不存在")
        return
    
    try:
        # 清空现有集合
        await db.char_detailed_info.delete_many({})
        await db.character_rating.delete_many({})
        
        # 导入角色信息
        with open(char_file, 'r', encoding='utf-8') as f:
            char_data = json.load(f)
            if char_data:
                # 转换_id字符串回ObjectId
                for doc in char_data:
                    if '_id' in doc:
                        doc['_id'] = ObjectId(doc['_id'])
                await db.char_detailed_info.insert_many(char_data)
                print(f"已导入 {len(char_data)} 条角色信息")
        
        # 导入评分记录
        with open(rating_file, 'r', encoding='utf-8') as f:
            rating_data = json.load(f)
            if rating_data:
                # 转换_id字符串回ObjectId和时间戳
                for doc in rating_data:
                    if '_id' in doc:
                        doc['_id'] = ObjectId(doc['_id'])
                    if 'timestamp' in doc:
                        doc['timestamp'] = datetime.fromisoformat(doc['timestamp'])
                await db.character_rating.insert_many(rating_data)
                print(f"已导入 {len(rating_data)} 条评分记录")
        
        print("数据库导入完成")
        
    except Exception as e:
        print(f"导入失败: {e}")
        raise

def list_backups(import_dir="db_export"):
    """列出所有可用的备份"""
    backups = {}
    for file in glob.glob(os.path.join(import_dir, "*.json")):
        timestamp = file.split('_')[-1].replace('.json', '')
        collection = file.split('_')[-2]
        if timestamp not in backups:
            backups[timestamp] = set()
        backups[timestamp].add(collection)
    
    print("\n可用的备份:")
    for timestamp, collections in backups.items():
        print(f"时间戳: {timestamp}")
        print(f"包含的集合: {', '.join(collections)}\n")

if __name__ == "__main__":
    # 列出所有可用的备份
    list_backups()
    
    # 询问用户是否要导入
    response = input("是否要导入数据？(y/n): ")
    if response.lower() == 'y':
        timestamp = input("请输入要导入的时间戳（直接回车使用最新备份）: ").strip()
        if not timestamp:
            timestamp = None
        asyncio.run(import_database(timestamp=timestamp)) 