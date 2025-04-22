from database_update import FoodAgent
from time import time, sleep


def main():

    food_agent = FoodAgent()

    food_agent.update_food_item()
    entries = food_agent.notion.get_pending_entries()
    if not entries:
        return
    for entry in entries:
        start_time = time()
        food_description = entry["properties"]["食物描述"]["rich_text"][0]["text"][
            "content"
        ]
        print(f"处理条目: {food_description}")
        entry_id = entry["id"]
        quantities, food_items = food_agent.process_food_description(food_description)
        print(f"解析结果: {quantities}, {food_items}")
        food_agent.notion.create_associations(entry_id, food_items)
        update_status = food_agent.notion.update_main_database(
            entry_id, food_items, quantities
        )
        if update_status:
            total_time = time() - start_time
            food_agent.notion.update_time(entry_id, total_time)


if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            print(f"发生错误: {e}")
        finally:
            sleep(10)
