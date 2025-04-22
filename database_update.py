from food_database import LocalFoodDatabase
from llm_query import LLMService
from parse_input import parse_multiple_food
from notion import Notion


class FoodAgent:
    def __init__(self):
        self.local_db = LocalFoodDatabase()
        self.notion_db = Notion()
        self.llm_service = LLMService()

    def add_to_db(self, food_item):
        try:
            notion_id = self.notion_db.create_food_item(food_item)
        except Exception as e:
            print(f"添加到Notion失败: {e}")
        if notion_id:
            print(f"成功添加到Notion: {food_item.name}")
            food_item.notion_id = notion_id
        # 添加到本地
        self.local_db.add_food_item(food_item)

    def process_food_description(self, food_description):
        """处理食物描述，返回匹配或新创建的食物项目

        returns: List[(quantity, FoodItem),...]
        """
        try:
            food_items = parse_multiple_food(food_description)
        except:
            try:
                food_items = self.llm_service.get_name_quantity_unit(food_description)
            except:
                return None
            if not food_items:
                print("解析食物描述失败")
                return None
        print(f"解析食物描述: {food_items}")
        food_results = []
        quantities = []
        not_in_local = []
        for i, (food_name, quantity, unit) in enumerate(food_items):
            # 2. 在本地数据库中查找

            quantities.append(quantity)
            food_item = self.local_db.get_food_item(food_name, unit)

            if food_item:
                print(f"在本地数据库中找到食物: {food_name}")
                food_results.append((i, food_item))
                continue
            else:
                print(f"在本地数据库中未找到食物: {food_name}")
                not_in_local.append((i, {"food_name": food_name, "unit": unit}))

            # 3. 查找相似食物
        print(f"在本地数据库中未找到食物: {not_in_local}")
        if not_in_local:
            llm_food_result = self.llm_service.get_food_nutrition(
                [food[1] for food in not_in_local]
            )
            for food_item in llm_food_result:
                print(f"写入本地数据库: {food_item.name, food_item.unit}")
                self.add_to_db(food_item)
            food_results.extend(
                list(zip([food[0] for food in not_in_local], llm_food_result))
            )
        food_results.sort(key=lambda x: x[0])
        food_results = [food[1] for food in food_results]
        return quantities, food_results


if __name__ == "__main__":
    import time

    start_time_total = time.time()

    food_agent = FoodAgent()
    existing_all = food_agent.local_db.get_all_food_items()
    for food in existing_all:
        food_agent.local_db.delete_food_item(food.name)
    food_description = "10个鸡块，一个巨无霸，三碗卤肉饭,1个去皮的鸡腿，两个巨无霸"
    print(parse_multiple_food(food_description))
    # food_items = food_agent.process_food_description(food_description)
    # for item in food_items:
    #     print(item)
