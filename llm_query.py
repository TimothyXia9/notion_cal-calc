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
            "Authorization": f"Bearer {self.LLM_API_KEY}",
            "Content-Type": "application/json"
        }
    
    def get_food_nutrition(self, food_name):
        """使用LLM获取食物的营养信息"""
        llm_url = "https://api.anthropic.com/v1/messages"
        
        prompt = f"""
        请分析以下食物的营养信息，并返回JSON格式的结果：
        
        食物名称：{food_name}
        
        请估算该食物每100克或每份标准量的以下营养成分，并严格按照以下JSON格式返回：
        
        {{
          "name": "食物名称",
          "calories": 每100克热量(千卡),
          "unit": "克",
          "protein": 蛋白质含量(克),
          "fat": 脂肪含量(克),
          "carbs": 碳水化合物含量(克)
        }}
        
        确保返回的是一个有效的JSON对象，所有数值应该是数字而非字符串。
        如果某些营养成分无法确定，可以返回null。
        """
        
        payload = {
            "model": "claude-3-haiku-20240307",
            "max_tokens": 1000,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        response = requests.post(llm_url, headers=self.headers, json=payload)
        if response.status_code == 200:
            # 提取LLM响应中的JSON部分
            result_text = response.json()["content"][0]["text"]
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
                    carbs=nutrition_data["carbs"]
                )
                return food_item
            except json.JSONDecodeError:
                print("无法解析LLM返回的JSON数据")
                return None
        else:
            print(f"LLM API调用失败: {response.status_code}")
            return None