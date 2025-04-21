import sqlite3
import json
import os
from food_schema import FoodItem


class LocalFoodDatabase:
    def __init__(self, db_path="food_database.db"):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        """创建食物数据表"""
        self.cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS food_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            calories REAL,
            unit TEXT,
            protein REAL,
            fat REAL, 
            carbs REAL,
            notion_id TEXT
        )
        """
        )
        self.conn.commit()

    def add_food_item(self, food_item):
        """添加新食物到数据库"""
        try:
            self.cursor.execute(
                """INSERT INTO food_items 
                   (name, calories, unit, protein, fat, carbs, notion_id) 
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    food_item.name,
                    food_item.calories,
                    food_item.unit,
                    food_item.protein,
                    food_item.fat,
                    food_item.carbs,
                    food_item.notion_id,
                ),
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            # 食物名已存在
            return False

    def update_food_item(self, food_item):
        """更新食物信息"""
        self.cursor.execute(
            """UPDATE food_items SET 
               calories=?, unit=?, protein=?, fat=?, carbs=?, notion_id=?
               WHERE name=?""",
            (
                food_item.calories,
                food_item.unit,
                food_item.protein,
                food_item.fat,
                food_item.carbs,
                food_item.notion_id,
                food_item.name,
            ),
        )
        self.conn.commit()
        return self.cursor.rowcount > 0

    def get_food_item(self, name, unit=None):
        """根据名称和可选单位获取食物信息"""
        if unit:
            # 如果提供了单位，同时匹配名称和单位
            self.cursor.execute(
                "SELECT name, calories, unit, protein, fat, carbs, notion_id FROM food_items WHERE name=? AND unit=?",
                (name, unit),
            )
        else:
            # 如果没有提供单位，只匹配名称
            self.cursor.execute(
                "SELECT name, calories, unit, protein, fat, carbs, notion_id FROM food_items WHERE name=?",
                (name,),
            )

        result = self.cursor.fetchone()
        if result:
            food = FoodItem(
                name=result[0],
                calories=result[1],
                unit=result[2],
                protein=result[3],
                fat=result[4],
                carbs=result[5],
            )
            food.notion_id = result[6]
            return food
        return None

    def search_similar_foods(self, name, threshold=0.7):
        """搜索相似食物名称(简单实现)"""
        self.cursor.execute("SELECT name FROM food_items")
        all_foods = self.cursor.fetchall()
        similar_foods = []

        for food_name in all_foods:
            # 简单的相似度计算，实际应用中可以使用更复杂的算法
            similarity = self._calculate_similarity(name, food_name[0])
            if similarity >= threshold:
                similar_foods.append(food_name[0])

        return similar_foods

    def _calculate_similarity(self, str1, str2):
        """简单的字符串相似度计算"""
        # 这里使用简单的方法，实际应用可以使用更复杂的算法如编辑距离
        # 或者中文分词后的余弦相似度等
        str1 = str1.lower()
        str2 = str2.lower()

        # 检查一个字符串是否包含另一个
        if str1 in str2 or str2 in str1:
            return 0.8

        # 计算重叠字符比例
        common_chars = set(str1) & set(str2)
        return len(common_chars) / max(len(set(str1)), len(set(str2)))

    def close(self):
        """关闭数据库连接"""
        self.conn.close()
