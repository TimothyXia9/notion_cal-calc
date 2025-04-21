from urllib import response
import requests
import json
import os
from dotenv import load_dotenv
import time

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
            "filter": {"property": "状态", "select": {"does_not_equal": "已完成"}}
        }
        response = requests.post(url, headers=notion_headers, json=payload)
        if response.status_code == 200:
            return response.json()["results"]
        else:
            print(f"获取Notion条目失败: {response.status_code}")
            print(response.json())

    def update_main_database(self, entry_id, total_calories="0", food_items=[]):
        url = f"https://api.notion.com/v1/pages/{entry_id}"

        payload = {
            "properties": {
                "总热量": {
                    "rich_text": [
                        {"type": "text", "text": {"content": str(total_calories)}}
                    ]
                },
                "状态": {"select": {"name": "已完成"}},
            }
        }
        response = requests.patch(url, headers=notion_headers, json=payload)
        print(response.text)  # 打印响应以便调试
        if response.status_code != 200:
            print(f"更新Notion条目失败: {response.status_code}")
            try:
                payload = {"properties": {"状态": {"select": {"name": "出错"}}}}
                response = requests.patch(url, headers=notion_headers, json=payload)
                if response.status_code != 200:
                    print(f"更新Notion条目状态失败: {response.status_code}")
            except Exception as e:
                print(f"更新Notion条目状态失败: {e}")

    def create_food_item(self, food_item):
        """在Notion数据库中创建食物条目"""

        if not self.query_food_item(food_item["name"]):
            url = f"https://api.notion.com/v1/pages"
            payload = {
                "parent": {"database_id": self.food_database_id},
                "properties": {
                    "名称": {
                        "title": [{"text": {"content": food_item["name"]}}],
                    },
                    "热量": {
                        "number": food_item["calories"],
                    },
                    "单位": {
                        "select": {"name": food_item["unit"]},
                    },
                    "蛋白质": {
                        "number": food_item["protein"],
                    },
                    "脂肪": {
                        "number": food_item["fat"],
                    },
                    "碳水": {
                        "number": food_item["carbs"],
                    },
                },
            }
            response = requests.post(url, headers=notion_headers, json=payload)
            if response.status_code == 200:
                return response.json()["id"]
            else:
                print(f"创建食物条目失败: {response.status_code}")
                print(response.json())

    def query_food_item(self, food_name):
        url = f"https://api.notion.com/v1/databases/{self.food_database_id}/query"
        payload = {
            "filter": {
                "property": "名称",
                "title": {
                    "equals": food_name,
                },
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

    def get_all_food_item(self):
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
            return response.json()["results"]
        else:
            print(f"获取食物条目失败: {response.status_code}")
            print(response.json())

    def create_association(self, food_item_id, entry_id):
        """在Notion数据库中创建食物条目与主条目的关联"""

        url = f"https://api.notion.com/v1/pages/{entry_id}"
        payload = {
            "properties": {
                "食物": {
                    "relation": [{"id": food_item_id}],
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


if __name__ == "__main__":
    notion = Notion()
    food_item = {
        "name": "苹果",
        "calories": 52,
        "unit": "克",
        "protein": 0.3,
        "fat": 0.2,
        "carbs": 14,
    }
    # notion.create_food_item(food_item)
    # print(notion.get_all_food_item())
    entries = notion.get_pending_entries()
    print(entries)
    entry_id = entries[0]["id"]
    food_item_id = notion.query_food_item("苹果")["id"]
    notion.create_association(food_item_id, entry_id)
