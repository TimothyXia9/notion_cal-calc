import os
import json


import requests
from dotenv import load_dotenv
from FoodItem import FoodItem


load_dotenv()
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_MAIN_DATABASE_ID = os.getenv("NOTION_MAIN_DATABASE_ID")
NOTION_FOOD_DATABASE_ID = os.getenv("NOTION_FOOD_DATABASE_ID")


notion_headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",  # 使用最新版本
}


class Notion:
    def __init__(self):
        self.main_database_id = NOTION_MAIN_DATABASE_ID
        self.food_database_id = NOTION_FOOD_DATABASE_ID

    def get_pending_entries(self):
        """从Notion获取所有非'已完成'状态的条目"""
        url = f"https://api.notion.com/v1/databases/{self.main_database_id}/query"
        payload = {
            "filter": {
                "or": [
                    {"property": "状态", "select": {"does_not_equal": "已完成"}},
                    {
                        "property": "食物",
                        "relation": {"is_empty": True},
                    },
                ],
            }
        }
        response = requests.post(url, headers=notion_headers, json=payload)
        if response.status_code == 200:
            return response.json()["results"]
        else:
            print(f"获取Notion条目失败: {response.status_code}")
            print(response.json())

    def update_main_database(self, entry_id, food_items=[], quantities=[]):
        url = f"https://api.notion.com/v1/pages/{entry_id}"
        total_calories = 0
        for i, food_item in enumerate(food_items):
            total_calories += food_item.calories * quantities[i]
        payload = {
            "properties": {
                "总热量": {
                    "number": total_calories,
                },
                "状态": {"select": {"name": "已完成"}},
                "数量": {"rich_text": [{"text": {"content": json.dumps(quantities)}}]},
            }
        }
        response = requests.patch(url, headers=notion_headers, json=payload)
        if response.status_code == 200:

            return True
        if response.status_code != 200:
            print(f"更新Notion条目失败: {response.status_code}")
            print(response.json())

            try:
                payload = {"properties": {"状态": {"select": {"name": "出错"}}}}
                response = requests.patch(url, headers=notion_headers, json=payload)
                if response.status_code != 200:
                    print(f"更新Notion条目状态失败: {response.status_code}")
            except Exception as e:

                print(f"更新Notion条目状态失败: {e}")
                return False

    def update_time(self, entry_id, update_time):
        url = f"https://api.notion.com/v1/pages/{entry_id}"
        payload = {
            "properties": {
                "更新用时": {
                    "number": update_time,
                },
            }
        }
        response = requests.patch(url, headers=notion_headers, json=payload)
        if response.status_code == 200:
            return True
        else:
            return False

    def create_food_item(self, food_item: FoodItem):
        """在Notion数据库中创建食物条目"""

        if not self.query_food_item(food_item.name, food_item.unit, food_item.calories):
            url = f"https://api.notion.com/v1/pages"
            payload = {
                "parent": {"database_id": self.food_database_id},
                "properties": {
                    "名称": {
                        "title": [{"text": {"content": food_item.name}}],
                    },
                    "热量": {
                        "number": food_item.calories,
                    },
                    "单位": {
                        "select": {"name": food_item.unit},
                    },
                    "蛋白质": {
                        "number": food_item.protein,
                    },
                    "脂肪": {
                        "number": food_item.fat,
                    },
                    "碳水": {
                        "number": food_item.carbs,
                    },
                    "大致克数": {
                        "number": food_item.grams,
                    },
                    "状态": {
                        "select": {"name": "正常"},
                    },
                },
            }
            response = requests.post(url, headers=notion_headers, json=payload)

            if response.status_code == 200:
                print(f"创建食物条目成功: {food_item.name,response.json()["id"]}")
                return response.json()["id"]
            else:
                print(f"创建食物条目失败: {response.status_code}")
                print(response.json())

        else:
            print(f"食物条目已存在: {food_item.name}")
            return self.query_food_item(
                food_item.name, food_item.unit, food_item.calories
            )["id"]

    def query_food_item(self, food_name, unit, calories=None):
        url = f"https://api.notion.com/v1/databases/{self.food_database_id}/query"
        payload = {
            "filter": {
                "and": [
                    {"property": "名称", "title": {"equals": food_name}},
                    {"property": "单位", "select": {"equals": unit}},
                    {"property": "热量", "number": {"equals": calories}},
                ]
            }
        }
        response = requests.post(url, headers=notion_headers, json=payload)
        if response.status_code == 200:
            results = response.json()["results"]
            if results:
                return results[0]
            else:
                print(f"未找到食物: {food_name}")
                return None

    def get_all_food_items(self):
        """
        return"""
        output = []
        url = f"https://api.notion.com/v1/databases/{self.food_database_id}/query"
        payload = {
            "filter": {
                "property": "名称",
                "rich_text": {
                    "is_not_empty": True,
                },
            }
        }
        response = requests.post(url, headers=notion_headers, json=payload)
        if response.status_code == 200:
            results = response.json()["results"]
            for result in results:
                food_item = FoodItem(
                    name=result["properties"]["名称"]["title"][0]["text"]["content"],
                    calories=result["properties"]["热量"]["number"],
                    unit=result["properties"]["单位"]["select"]["name"],
                    protein=result["properties"]["蛋白质"]["number"],
                    fat=result["properties"]["脂肪"]["number"],
                    carbs=result["properties"]["碳水"]["number"],
                    grams=result["properties"]["大致克数"]["number"],
                )
                food_item.notion_id = result["id"]
                output.append(food_item)
            return output
        else:
            print(f"获取食物条目失败: {response.status_code}")
            print(response.json())

    def create_associations(self, entry_id, food_items):
        """在Notion数据库中创建食物条目与主条目的关联"""
        relations = []
        for food_item in food_items:
            food_item_id = food_item.notion_id
            if not food_item_id:
                food_item_id = self.create_food_item(food_item)
            relations.append({"id": food_item_id})
        print(f"创建关联: {relations}")
        url = f"https://api.notion.com/v1/pages/{entry_id}"
        payload = {
            "properties": {
                "食物": {
                    "relation": relations,
                },
            }
        }
        response = requests.patch(url, headers=notion_headers, json=payload)
        if response.status_code == 200:
            return True
        else:
            print(f"创建关联失败: {response.status_code}")
            print(response.json())
            return False

    def get_update_food(self):
        """更新食物条目"""
        url = f"https://api.notion.com/v1/databases/{self.food_database_id}/query"
        payload = {"filter": {"property": "状态", "select": {"equals": "异常"}}}

        response = requests.post(url, headers=notion_headers, json=payload)

        if response.status_code == 200:
            results = response.json()["results"]
            food_items = []
            for result in results:
                food_item = FoodItem(
                    name=result["properties"]["名称"]["title"][0]["text"]["content"],
                    calories=result["properties"]["热量"]["number"],
                    unit=result["properties"]["单位"]["select"]["name"],
                    protein=result["properties"]["蛋白质"]["number"],
                    fat=result["properties"]["脂肪"]["number"],
                    carbs=result["properties"]["碳水"]["number"],
                    grams=result["properties"]["大致克数"]["number"],
                )
                food_item.notion_id = result["id"]
                food_items.append(food_item)
            return food_items
        else:
            print(f"获取食物条目失败: {response.status_code}")
            print(response.json())
            return []

    def get_updated_associations(self, food_item: FoodItem):
        """获取食物条目与主条目的关联"""
        url = f"https://api.notion.com/v1/pages/{food_item.notion_id}"
        response = requests.get(url, headers=notion_headers)
        if response.status_code == 200:
            results = response.json()
            if "properties" in results and "关联" in results["properties"]:
                return results["properties"]["关联"]["relation"]
            else:
                print(f"未找到关联: {food_item.name}")
                return None
        else:
            print(f"获取关联失败: {response.status_code}")
            print(response.json())
            return None

    def get_food_items(self, entry_id):
        url = f"https://api.notion.com/v1/pages/{entry_id}"
        response = requests.get(url, headers=notion_headers)
        if response.status_code == 200:
            result = response.json()
            food_item = FoodItem(
                name=result["properties"]["名称"]["title"][0]["text"]["content"],
                calories=result["properties"]["热量"]["number"],
                unit=result["properties"]["单位"]["select"]["name"],
                protein=result["properties"]["蛋白质"]["number"],
                fat=result["properties"]["脂肪"]["number"],
                carbs=result["properties"]["碳水"]["number"],
                grams=result["properties"]["大致克数"]["number"],
            )
            food_item.notion_id = result["id"]
            return food_item
        else:
            print(f"获取食物条目失败: {response.status_code}")
            print(response.json())
            return None

    def get_food_item_and_quantities(self, entry_id):
        """获取条目中的数量"""
        url = f"https://api.notion.com/v1/pages/{entry_id}"
        response = requests.get(url, headers=notion_headers)
        if response.status_code == 200:
            results = response.json()
            if "properties" in results:
                if "数量" in results["properties"]:
                    quantities = json.loads(
                        results["properties"]["数量"]["rich_text"][0]["text"]["content"]
                    )
                else:
                    print(f"未找到数量: {entry_id}")
                if "食物" in results["properties"]:
                    food_items_ids = results["properties"]["食物"]["relation"]
                    food_items = []
                    for food_item_id in food_items_ids:
                        food_item = self.get_food_items(food_item_id["id"])
                        food_items.append(food_item)
                    return food_items, quantities

        else:
            print(f"获取数量失败: {response.status_code}")
            print(response.json())
            return None

    def fix_updated_status(self, food_item: FoodItem):
        """修复食物条目的状态"""
        url = f"https://api.notion.com/v1/pages/{food_item.notion_id}"
        payload = {
            "properties": {
                "状态": {
                    "select": {"name": "正常"},
                },
            }
        }
        response = requests.patch(url, headers=notion_headers, json=payload)
        if response.status_code == 200:
            return True
        else:
            print(f"修复食物条目状态失败: {response.status_code}")
            print(response.json())
            return False

    def delete_no_association_food(self):
        url = f"https://api.notion.com/v1/databases/{self.food_database_id}/query"
        payload = {
            "filter": {
                "property": "关联",
                "relation": {"is_empty": True},
            }
        }
        response = requests.post(url, headers=notion_headers, json=payload)
        if response.status_code == 200:
            results = response.json()["results"]
            for result in results:
                food_item_id = result["id"]

                url = f"https://api.notion.com/v1/pages/{food_item_id}"
                response = requests.delete(url, headers=notion_headers)
                if response.status_code == 200:
                    print(f"删除食物条目成功: {food_item_id}")
                else:
                    print(f"删除食物条目失败: {response.status_code}")
                    print(response.json())
        else:
            print(f"获取食物条目失败: {response.status_code}")
            print(response.json())


if __name__ == "__main__":
    notion = Notion()
    food_item = FoodItem(
        name="苹果",
        calories=52,
        unit="克",
        protein=0.3,
        fat=0.2,
        carbs=14,
        grams=100,
    )
    # notion.create_food_item(food_item)
    # print(notion.get_all_food_item())
    # entries = notion.get_pending_entries()
    # print(entries)
    # entry_id = entries[0]["id"]
    # food_item_id = notion.query_food_item("苹果")["id"]
    # notion.create_association(food_item_id, entry_id)

    print(notion.get_food_item_and_quantities("1dc505a6-7b0e-8033-accf-f6b0663d8e08"))
