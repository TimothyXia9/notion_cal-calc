from database_update import FoodAgent
from notion import Notion
from food_database import LocalFoodDatabase


def clear_local_database():
    """清空本地数据库"""
    local_db = LocalFoodDatabase()
    local_db.clear_database()


def main():

    food_agent = FoodAgent()
    notion = Notion()
    entries = notion.get_pending_entries()
    local_db = LocalFoodDatabase()
    local_db.sync_database()
    for entry in entries:

        food_description = entry["properties"]["食物描述"]["rich_text"][0]["text"][
            "content"
        ]
        print(f"处理条目: {food_description}")
        entry_id = entry["id"]
        quantities, food_items = food_agent.process_food_description(food_description)
        print(f"解析结果: {quantities}, {food_items}")
        notion.create_associations(entry_id, food_items)
        notion.update_main_database(entry_id, food_items, quantities)
        print(f"条目已更新: {food_items}")
    # for item in food_items:
    #     print(item)


if __name__ == "__main__":
    clear_local_database()
    main()
