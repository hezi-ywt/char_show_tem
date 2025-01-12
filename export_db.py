import os
import json
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from bson import ObjectId

class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

async def export_database():
    # 连接MongoDB
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.dan
    
    # 创建导出目录
    export_dir = "db_export"
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)
    
    # 导出时间戳
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 导出collections
    collections = ['char_detailed_info', 'character_rating']
    
    for collection_name in collections:
        collection = db[collection_name]
        # 获取所有文档
        documents = await collection.find({}).to_list(length=None)
        
        # 导出文件路径
        export_path = os.path.join(export_dir, f"{collection_name}_{timestamp}.json")
        
        # 写入JSON文件
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(documents, f, ensure_ascii=False, indent=2, cls=JSONEncoder)
        
        print(f"已导出 {collection_name} 到 {export_path}")
        print(f"文档数量: {len(documents)}")

if __name__ == "__main__":
    asyncio.run(export_database()) 