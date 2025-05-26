import sqlite3
from FoodItem import FoodItem


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
            name TEXT,
            calories REAL,
            unit TEXT,
            protein REAL,
            fat REAL, 
            carbs REAL,
            grams REAL,
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
                   (name, calories, unit, protein, fat, carbs, grams, notion_id) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    food_item.name,
                    food_item.calories,
                    food_item.unit,
                    food_item.protein,
                    food_item.fat,
                    food_item.carbs,
                    food_item.grams,
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
               calories=?, unit=?, protein=?, fat=?, carbs=?, grams=?, notion_id=?
               WHERE name=?""",
            (
                food_item.calories,
                food_item.unit,
                food_item.protein,
                food_item.fat,
                food_item.carbs,
                food_item.notion_id,
                food_item.grams,
                food_item.name,
            ),
        )
        self.conn.commit()
        return self.cursor.rowcount > 0

    def delete_food_item(self, name, notion_id=None):
        if notion_id:
            self.cursor.execute(
                "DELETE FROM food_items WHERE name=? AND notion_id=?", (name, notion_id)
            )
            self.conn.commit()
            return True
        if self.get_food_item(name):
            self.cursor.execute("DELETE FROM food_items WHERE name=?", (name,))
            self.conn.commit()
            return True
        else:
            return False

    def get_all_food_items(self):
        """return:  [FoodItem...]"""
        self.cursor.execute(
            "SELECT name, calories, unit, protein, fat, carbs, grams, notion_id FROM food_items"
        )
        results = self.cursor.fetchall()
        food_items = []
        for result in results:
            food = FoodItem(
                name=result[0],
                calories=result[1],
                unit=result[2],
                protein=result[3],
                fat=result[4],
                carbs=result[5],
                grams=result[6],
            )
            food.notion_id = result[7]
            food_items.append(food)
        return food_items

    def get_food_item(self, name, unit=None):
        """根据名称和可选单位获取食物信息
        return : FoodItem or None"""
        if unit:
            # 如果提供了单位，同时匹配名称和单位
            self.cursor.execute(
                "SELECT name, calories, unit, protein, fat, carbs, grams, notion_id FROM food_items WHERE name=? AND unit=?",
                (name, unit),
            )
        else:
            # 如果没有提供单位，只匹配名称
            self.cursor.execute(
                "SELECT name, calories, unit, protein, fat, carbs, grams, notion_id FROM food_items WHERE name=?",
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
                grams=result[6],
            )
            food.notion_id = result[7]
            return food
        return None

    def get_food_item_by_id(self, food_item: FoodItem):
        """根据ID获取食物信息"""
        self.cursor.execute(
            "SELECT name, calories, unit, protein, fat, carbs, grams, notion_id FROM food_items WHERE notion_id=?",
            (food_item.notion_id,),
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
                grams=result[6],
            )
            food.notion_id = result[7]
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

    def clear_database(self):
        """清空数据库"""
        self.cursor.execute("DELETE FROM food_items")
        self.conn.commit()
        self.close()

    def remove_duplicate_food_items(self):
        """删除重复的食物项"""
        self.cursor.execute(
            """
            DELETE FROM food_items
            WHERE id NOT IN (
                SELECT MIN(id)
                FROM food_items
                GROUP BY notion_id
            )
            """
        )
        self.conn.commit()

    def sync_database(self):
        """向notion同步数据库"""
        from notion import Notion

        notion = Notion()
        notion_food_items = notion.get_all_food_items()
        local_food_items = self.get_all_food_items()
        for food_item in local_food_items:
            if food_item.notion_id not in [
                item.notion_id for item in notion_food_items
            ]:
                # 如果本地数据库中有食物，但Notion中没有，则从本地删除
                self.delete_food_item(food_item.name, food_item.notion_id)
        for food_item in notion_food_items:
            if food_item.notion_id not in [item.notion_id for item in local_food_items]:
                # 如果Notion中有食物，但本地数据库中没有，则添加到本地数据库
                self.add_food_item(food_item)


if __name__ == "__main__":
    db = LocalFoodDatabase()
    # db.delete_food_item("鸡肉")
    # food1 = FoodItem(
    #     name="鸡肉",
    #     calories=239,
    #     unit="克",
    #     protein=27,
    #     fat=14,
    #     carbs=0,
    #     grams=100,
    # )
    # food1.notion_id = "111"
    # db.add_food_item(food1)
    # print(db.get_all_food_items())

    # print("-----------------")
    # food2 = FoodItem(
    #     name="鸡肉",
    #     calories=11111,
    #     unit="克",
    #     protein=27,
    #     fat=14,
    #     carbs=0,
    #     grams=100,
    # )
    # food2.notion_id = "222"
    # print(db.add_food_item(food2))
    print(db.get_all_food_items())
