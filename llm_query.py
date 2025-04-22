import re
import requests
import json
import os
from dotenv import load_dotenv
from FoodItem import FoodItem


class LLMService:
    def __init__(self):
        load_dotenv()
        self.LLM_API_KEY = os.getenv("LLM_API_KEY")
        self.LLM_model = os.getenv("LLM_MODEL", "claude-3-5-haiku-20241022")
        self.headers = {
            "x-api-key": self.LLM_API_KEY,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }

    def query_llm(self, prompt, temperature=0.1):
        """使用LLM API查询"""
        llm_url = "https://api.anthropic.com/v1/messages"

        payload = {
            "model": self.LLM_model,  # 使用适当的模型
            "max_tokens": 1000,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}],
        }

        response = requests.post(llm_url, headers=self.headers, json=payload)
        # print(f"LLM API响应: {response.text}")
        if response.status_code == 200:
            return response.json()["content"][0]["text"]
        else:
            print(f"LLM API调用失败: {response.status_code}")
            return None

    def get_food_nutrition(self, food_items):
        """return: [FoodItem, ...]"""
        prompt = f"""
        请根据以下食物名称和单位，返回每种食物的营养信息。
        {food_items}
        如果单位为"克"，则给出每克的热量。
        如果食物名称格式类似 "咖啡:300卡", 则返回300卡的热量。
        请严格按照以下JSON格式返回，不要添加其他文本或解释：

        {{
        "items": [
            {{
            "name": "食物1",
            "calories": 按照每给出的单位计算的热量(千卡),
            "unit": "单位",
            "protein": 蛋白质含量(克),
            "fat": 脂肪含量(克),
            "carbs": 碳水化合物含量(克),
            "grams": 按照给出的单位换算为等量重量(克)
            }},
            {{
            "name": "食物2",
            "calories": 按照每给出的单位计算的热量(千卡),
            "unit": "单位",
            "protein": 蛋白质含量(克),
            "fat": 脂肪含量(克),
            "carbs": 碳水化合物含量(克),
            "grams": 按照给出的单位换算为等量重量(克)
            }}
        ]
        }}

        确保返回的是一个有效的JSON对象，所有数值应该是数字而非字符串。
        """
        result_text = LLMService().query_llm(prompt)
        try:
            food_nutrition = json.loads(result_text)
            food_nutrition_items = food_nutrition.get("items", [])
            food_nutrition_list = []
            for item in food_nutrition_items:
                food_item = FoodItem(
                    name=item.get("name"),
                    calories=item.get("calories"),
                    unit=item.get("unit"),
                    protein=item.get("protein"),
                    fat=item.get("fat"),
                    carbs=item.get("carbs"),
                    grams=item.get("grams") if item.get("unit") != "克" else 1,
                )
                food_nutrition_list.append(food_item)
            return food_nutrition_list

        except json.JSONDecodeError:
            print(f"解析JSON失败: {result_text}")
            return None

    def get_name_quantity_unit(self, food_description):
        """return: [(食物名称, 数量, 单位), ...]"""
        food_items = []
        prompt = f"""
            请根据以下食物描述提取食物名称、数量和单位，返回JSON格式的结果：
            {food_description}

            请按照以下规则提取：
            1. 数量词（如"一个"、"两碗"、"10个"）应分解为数字和单位
            2. 食物名称不应包含数量词，但应保留其他描述性形容词
            3. 例如："一个去皮的鸡腿" → 数量=1, 单位=个, 名称="去皮的鸡腿"
            4. 例如："三碗卤肉饭" → 数量=3, 单位=碗, 名称="卤肉饭"
            5. 例如："两个巨无霸" → 数量=2, 单位=个, 名称="巨无霸"

            请严格按照以下JSON格式返回，不要添加其他文本或解释：

            {{
            "items": [
                {{"name": "食物名称(不含数量词)", "quantity": 数量, "unit": "单位"}},
                {{"name": "食物名称(不含数量词)", "quantity": 数量, "unit": "单位"}}
            ]
            }}

            若无法确定quantity，请返回1
            若无法确定unit，请返回"个"
            """

        result_text = LLMService().query_llm(prompt)
        try:
            food_data = json.loads(result_text)
            items = food_data.get("items", [])
            for item in items:
                name = item.get("name")
                quantity = item.get("quantity", 1)
                unit = item.get("unit", "个")
                food_items.append((name, quantity, unit))
            return food_items
        except json.JSONDecodeError:
            print(f"解析JSON失败: {result_text}")
            return None

        # def parse_multiple_food(self, food_description, get_nutrition=True):
        """解析多个食物描述，返回食物名称、数量和单位的列表

        return: [(食物名称, 数量, 单位), ...], [FoodItem, ...]"""
        food_items = self.get_name_quantity_unit(food_description)
        if not get_nutrition:
            return food_items, None
        if food_items:
            prompt = f"""
            请根据以下食物名称、数量和单位，返回每种食物的营养信息。
            {food_items}
            请严格按照以下JSON格式返回，不要添加其他文本或解释：

            {{
            "items": [
                {{
                "name": "食物1",
                "calories": 按照每给出的单位计算的热量(千卡),
                "unit": "单位",
                "protein": 蛋白质含量(克),
                "fat": 脂肪含量(克),
                "carbs": 碳水化合物含量(克)
                }},
                {{
                "name": "食物2",
                "calories": 按照每给出的单位计算的热量(千卡),
                "unit": "单位",
                "protein": 蛋白质含量(克),
                "fat": 脂肪含量(克),
                "carbs": 碳水化合物含量(克)
                }}
            ]
            }}

            确保返回的是一个有效的JSON对象，所有数值应该是数字而非字符串。
            """
            result_text = LLMService().query_llm(prompt)

            try:
                food_nutrition = json.loads(result_text)
                food_nutrition_items = food_nutrition.get("items", [])
                food_nutrition_list = []
                for item in food_nutrition_items:
                    food_item = FoodItem(
                        name=item.get("name"),
                        calories=item.get("calories"),
                        unit=item.get("unit"),
                        protein=item.get("protein"),
                        fat=item.get("fat"),
                        carbs=item.get("carbs"),
                    )
                    food_nutrition_list.append(food_item)
                return food_items, food_nutrition_list

            except json.JSONDecodeError:
                print(f"解析JSON失败: {result_text}")
                return None


if __name__ == "__main__":
    llm_service = LLMService()
    # food_name = "苹果"
    # food_item = llm_service.get_food_nutrition(food_name, "克")
    # if food_item:
    #     print(f"食物名称: {food_item.name}")
    #     print(f"热量: {food_item.calories}千卡")
    #     print(f"单位: {food_item.unit}")
    #     print(f"蛋白质: {food_item.protein}克")
    #     print(f"脂肪: {food_item.fat}克")
    #     print(f"碳水化合物: {food_item.carbs}克")
    # else:
    #     print("未能获取食物信息")
    # food_description = "10个鸡块，两个巨无霸，三碗卤肉饭,一个去皮的鸡腿"
    food_description = "两个巨无霸"
    food_items, nut_l = llm_service.parse_multiple_food(food_description)
    print(f"解析结果: {food_items, nut_l}")
