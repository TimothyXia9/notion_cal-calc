from food_database import LocalFoodDatabase
from llm_query import LLMService
from notion_database import NotionFoodDatabase
from food_schema import FoodItem


class FoodAgent:
    def __init__(self):
        self.local_db = LocalFoodDatabase()
        self.notion_db = NotionFoodDatabase()
        self.llm_service = LLMService()

    def process_food_description(self, food_description):
        """处理食物描述，返回匹配或新创建的食物项目"""
        # 1. 解析描述，提取食物名称
        food_items = self._parse_food_names(food_description)

        results = []
        for food_name in food_items:
            # 2. 在本地数据库中查找
            food_item = self.local_db.get_food_item(food_name)

            if food_item:
                print(f"在本地数据库中找到食物: {food_name}")
                results.append(food_item)
                continue

            # 3. 查找相似食物
            similar_foods = self.local_db.search_similar_foods(food_name)
            if similar_foods:
                print(f"找到相似食物: {similar_foods}")
                # 使用第一个相似食物(实际应用中可能需要用户确认)
                food_item = self.local_db.get_food_item(similar_foods[0])
                results.append(food_item)
                continue

            # 4. 在Notion中查找
            notion_food = self.notion_db.find_food_by_name(food_name)
            if notion_food:
                print(f"在Notion中找到食物: {food_name}")
                # 创建食物对象并添加到本地
                food_item = FoodItem(
                    name=notion_food["name"],
                    calories=notion_food["calories"],
                    unit=notion_food.get("unit", "克"),
                    protein=notion_food.get("protein"),
                    fat=notion_food.get("fat"),
                    carbs=notion_food.get("carbs"),
                )
                food_item.notion_id = notion_food["id"]

                # 添加到本地数据库
                self.local_db.add_food_item(food_item)
                results.append(food_item)
                continue

            # 5. 使用LLM获取食物信息
            print(f"使用LLM分析食物: {food_name}")
            food_item = self.llm_service.get_food_nutrition(food_name)

            if food_item:
                # 6. 添加到本地和Notion数据库
                print(f"成功获取食物信息: {food_name}")

                # 添加到Notion
                notion_id = self.notion_db.create_food_item(food_item)
                if notion_id:
                    food_item.notion_id = notion_id

                # 添加到本地
                self.local_db.add_food_item(food_item)
                results.append(food_item)
            else:
                print(f"无法获取食物信息: {food_name}")

        return results

    def _parse_food_names(self, food_description):
        """解析食物描述，提取食物名称列表(简单实现)"""
        # 实际应用中，可能需要更复杂的NLP处理
        # 这里简单实现，以逗号分隔
        food_items = [item.strip() for item in food_description.split(",")]
        return [item for item in food_items if item]

    def calculate_total_calories(self, food_items):
        """计算总热量"""
        total = 0
        for item in food_items:
            total += item.calories
        return total
