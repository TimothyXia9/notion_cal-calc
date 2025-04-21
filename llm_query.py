import re
import requests
import json
import os
from dotenv import load_dotenv
from food_schema import FoodItem


class LLMService:
    def __init__(self):
        load_dotenv()
        self.LLM_API_KEY = os.getenv("LLM_API_KEY")

        self.headers = {
            "x-api-key": self.LLM_API_KEY,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }

    def query_llm(self, prompt):
        """使用LLM API查询"""
        llm_url = "https://api.anthropic.com/v1/messages"

        payload = {
            "model": "claude-3-opus-20240229",  # 使用适当的模型
            "max_tokens": 1000,
            "messages": [{"role": "user", "content": prompt}],
        }

        response = requests.post(llm_url, headers=self.headers, json=payload)
        print(f"LLM API响应: {response.text}")
        if response.status_code == 200:
            return response.json()["content"][0]["text"]
        else:
            print(f"LLM API调用失败: {response.status_code}")
            return None

    def get_food_nutrition(self, food_name, unit):
        prompt = f"""
        请分析以下食物的营养信息，并返回JSON格式的结果：
        
        食物名称：{food_name}
        
        请估算该食物每单位的以下营养成分，并严格按照以下JSON格式返回：
        
        {{
          "name": "食物名称",
          "calories": 每{unit}热量(千卡),
          "unit": "{unit}",
          "protein": 蛋白质含量(克),
          "fat": 脂肪含量(克),
          "carbs": 碳水化合物含量(克)
        }}
        
        确保返回的是一个有效的JSON对象，所有数值应该是数字而非字符串。
        如果某些营养成分无法确定，可以返回null。
        """

        result_text = self.query_llm(prompt)
        try:
            # 尝试解析JSON
            nutrition_data = json.loads(result_text)

            # 创建食物对象
            food_item = FoodItem(
                name=nutrition_data["name"],
                calories=nutrition_data["calories"],
                unit=nutrition_data["unit"],
                protein=nutrition_data["protein"],
                fat=nutrition_data["fat"],
                carbs=nutrition_data["carbs"],
            )
            return food_item
        except json.JSONDecodeError:
            print(f"解析JSON失败: {result_text}")
            return None


def parse_multiple_food(food_description):
    """解析多个食物描述，返回食物名称、数量和单位的列表"""
    food_items = []
    prompt = (
        f"""
    请根据以下食物描述提取食物名称、数量和单位，返回JSON格式的结果：
    {food_description}
    
    请严格按照以下JSON格式返回，不要添加其他文本或解释：
    """
        + """
    {{
    "items": [
        {{
        "name": "食物名1",
        "calories": 数值
        }},
        {{
        "name": "食物名2", 
        "calories": 数值
        }}
    ]
    }}

    确保返回的是一个有效的JSON对象，所有数值应该是数字而非字符串。
    """
    )


if __name__ == "__main__":
    llm_service = LLMService()
    food_name = "苹果"
    food_item = llm_service.get_food_nutrition(food_name, "克")
    if food_item:
        print(f"食物名称: {food_item.name}")
        print(f"热量: {food_item.calories}千卡")
        print(f"单位: {food_item.unit}")
        print(f"蛋白质: {food_item.protein}克")
        print(f"脂肪: {food_item.fat}克")
        print(f"碳水化合物: {food_item.carbs}克")
    else:
        print("未能获取食物信息")
