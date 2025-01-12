from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import asyncio
import time
import os
from datetime import datetime

class Database:
    def __init__(self):
        # 连接MongoDB数据库
        self.client = AsyncIOMotorClient("mongodb://localhost:27017")
        self.db = self.client.dan  # 连接到dan数据库
        self.characters = self.db.char_detailed_info  # 角色信息集合
        self.ratings = self.db.character_rating  # 修改这里，直接在dan数据库中创建ratings集合
        self.images_base_path = "static/character_images"  # 全身图文件夹
        self.face_images_base_path = "static/character_images_face"  # 脸部图文件夹

    def _convert_object_id(self, doc):
        """转换文档中的ObjectId为字符串"""
        if doc is None:
            return None
        doc_copy = dict(doc)
        if '_id' in doc_copy:
            doc_copy['_id'] = str(doc_copy['_id'])
        return doc_copy

    def _get_character_images(self, character_folder, base_path):
        """获取指定路径下的角色图片"""
        folder_path = os.path.join(base_path, character_folder)
        if not os.path.exists(folder_path):
            return []
        
        # 获取所有图片文件
        valid_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
        images = [f for f in os.listdir(folder_path) 
                 if os.path.splitext(f)[1].lower() in valid_extensions]
        return sorted(images)  # 排序以保持顺序一致

    async def get_unrated_character(self, user_id: str):
        """获取用户未评分的角色，优先返回同时具有脸部和全身图片的角色"""
        try:
            # 获取已评分的角色列表
            rated_characters = await self.ratings.distinct(
                "character_id", 
                {"user_id": user_id}
            )
            
            # 获取所有未评分的角色
            unrated_characters = []
            async for character in self.characters.find({
                "character": {"$nin": rated_characters}
            }):
                character = self._convert_object_id(character)
                character["id"] = character["character"]
                # 获取两种图片
                character["full_body_images"] = self._get_character_images(
                    character["character"], 
                    self.images_base_path
                )
                character["face_images"] = self._get_character_images(
                    character["character"], 
                    self.face_images_base_path
                )
                unrated_characters.append(character)
            
            if not unrated_characters:
                return None
            
            # 对角色进行排序，优先返回同时具有脸部和全身图片的角色
            unrated_characters.sort(key=lambda x: (
                bool(x["face_images"] and x["full_body_images"]),  # 首要条件：是否同时具有两种图片
                len(x["face_images"] or []) + len(x["full_body_images"] or [])  # 次要条件：图片总数
            ), reverse=True)
            
            return unrated_characters[0]  # 返回排序后的第一个角色
            
        except Exception as e:
            print(f"获取未评分角色失败: {e}")
            raise

    async def save_rating(self, rating_data: dict):
        try:
            # 保存用户的图片选择记录
            rating_doc = {
                "character_id": rating_data["character_id"],
                "selected_images": rating_data["selected_images"],
                "user_id": rating_data["user_id"],
                "timestamp": datetime.utcnow()
            }
            print(f"Saving rating: {rating_doc}")  # 调试用
            result = await self.ratings.insert_one(rating_doc)
            return {"inserted_id": str(result.inserted_id)}
        except Exception as e:
            print(f"Database error: {e}")  # 调试用
            raise e

    async def get_character_details(self, character_id: str):
        # 先尝试通过character属性查找
        character = await self.characters.find_one({"character": character_id})
        if not character:
            # 如果找不到，尝试通过_id查找
            try:
                character = await self.characters.find_one({"_id": ObjectId(character_id)})
            except:
                pass
        
        if character:
            character = self._convert_object_id(character)
            character["id"] = character["character"]
            return character
        return None

    async def get_user_ratings(self, user_id: str):
        """获取用户的所有评分历史"""
        try:
            # 获取用户的所有评分记录
            ratings = await self.ratings.find({"user_id": user_id}).to_list(length=None)
            
            # 获取每个评分对应的角色信息
            result = []
            for rating in ratings:
                character = await self.characters.find_one({"character": rating["character_id"]})
                if character:
                    character = self._convert_object_id(character)
                    # 添加评分信息
                    character["rating_id"] = str(rating["_id"])
                    character["selected_images"] = rating["selected_images"]
                    character["rating_time"] = rating["timestamp"]
                    result.append(character)
            
            return result
        except Exception as e:
            print(f"获取用户评分历史失败: {e}")
            raise

    async def update_rating(self, rating_id: str, new_data: dict):
        """更新评分记录"""
        try:
            # 确保新数据中包含selected_images
            if "selected_images" not in new_data:
                raise ValueError("Missing selected_images in update data")
            
            # 使用$set操作符完全替换selected_images字段
            result = await self.ratings.update_one(
                {"_id": ObjectId(rating_id)},
                {"$set": {
                    "selected_images": new_data["selected_images"],
                    "timestamp": datetime.utcnow()
                }}
            )
            
            if result.modified_count == 0:
                raise ValueError(f"No rating found with id {rating_id}")
            
            # 获取更新后的评分记录
            updated_rating = await self.ratings.find_one({"_id": ObjectId(rating_id)})
            if not updated_rating:
                raise ValueError("Failed to retrieve updated rating")
            
            return {
                "modified_count": result.modified_count,
                "rating_id": str(rating_id),
                "selected_images": updated_rating["selected_images"]
            }
        except Exception as e:
            print(f"更新评分失败: {e}")
            raise

    async def get_character_for_edit(self, user_id: str, character_id: str):
        """获取用户已评分的特定角色信息"""
        try:
            # 获取用户对该角色的评分记录
            rating = await self.ratings.find_one({
                "user_id": user_id,
                "character_id": character_id
            })
            
            if not rating:
                return None
            
            # 获取角色信息
            character = await self.characters.find_one({"character": character_id})
            if character:
                character = self._convert_object_id(character)
                character["id"] = character["character"]
                # 获取两种图片
                character["full_body_images"] = self._get_character_images(
                    character["character"], 
                    self.images_base_path
                )
                character["face_images"] = self._get_character_images(
                    character["character"], 
                    self.face_images_base_path
                )
                # 添加评分信息
                character["rating_id"] = str(rating["_id"])
                character["selected_images"] = rating["selected_images"]
                return character
            
            return None
        except Exception as e:
            print(f"获取编辑角色失败: {e}")
            raise

    async def get_rating(self, rating_id: str):
        """获取单个评分记录及其角色信息"""
        try:
            rating = await self.ratings.find_one({"_id": ObjectId(rating_id)})
            if not rating:
                return None
            
            character = await self.characters.find_one({"character": rating["character_id"]})
            if character:
                character = self._convert_object_id(character)
                character["id"] = character["character"]
                # 获取两种图片
                character["full_body_images"] = self._get_character_images(
                    character["character"], 
                    self.images_base_path
                )
                character["face_images"] = self._get_character_images(
                    character["character"], 
                    self.face_images_base_path
                )
                # 添加评分信息
                character["rating_id"] = str(rating["_id"])
                character["selected_images"] = rating["selected_images"]
                return character
            
            return None
        except Exception as e:
            print(f"获取评分记录失败: {e}")
            raise

async def test():
    db = Database()
    
    # 1. 检查角色总数
    total_chars = await db.characters.count_documents({})
    print(f"数据库中的角色总数: {total_chars}")
    
    # 2. 检查一个新用户是否能获取角色
    test_user = "test_user"
    character = await db.get_unrated_character(test_user)
    print(f"新用户获取的角色: {character['character'] if character else None}")
    
    # 3. 检查评分记录
    total_ratings = await db.ratings.count_documents({})
    print(f"评分记录总数: {total_ratings}")
    
    # 测试获取角色图片
    character = await db.get_unrated_character("test_user")
    if character:
        print(f"角色: {character['character']}")
        print(f"图片列表: {character['images']}")

if __name__ == "__main__":
    asyncio.run(test())
