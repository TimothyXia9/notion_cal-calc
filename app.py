import requests
import json
import os
from dotenv import load_dotenv
import time

# 加载环境变量
load_dotenv()
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
LLM_API_KEY = os.getenv("LLM_API_KEY")

# Notion API请求头
notion_headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"  # 使用最新版本
}

# LLM API请求头
llm_headers = {
    "Authorization": f"Bearer {LLM_API_KEY}",
    "Content-Type": "application/json"
}

def get_pending_entries():
    """从Notion获取标记为'待处理'的条目"""
    url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"
    
    # 构建查询 - 筛选状态为"待处理"的条目
    payload = {
        "filter": {
            "property": "状态",
            "select": {
                "equals": "待处理"
            }
        }
    }
    
    response = requests.post(url, headers=notion_headers, json=payload)
    if response.status_code == 200:
        return response.json()["results"]
    else:
        print(f"获取Notion条目失败: {response.status_code}")
        return []

def calculate_calories(food_description):
    """使用LLM API计算食物热量"""
    llm_url = "https://api.anthropic.com/v1/messages"  # 假设使用Anthropic Claude
    
    prompt = f"""
    请根据以下食物描述计算大致热量(千卡)，只返回食物名称和热量数值的格式化结果：
    
    {food_description}
    
    返回格式：
    食物名: XX千卡
    食物名: XX千卡
    总计: XX千卡
    """
    
    payload = {
        "model": "claude-3-opus-20240229",  # 使用适当的模型
        "max_tokens": 1000,
        "messages": [{"role": "user", "content": prompt}]
    }
    
    response = requests.post(llm_url, headers=llm_headers, json=payload)
    if response.status_code == 200:
        return response.json()["content"][0]["text"]
    else:
        print(f"LLM API调用失败: {response.status_code}")
        return "热量计算失败，请重试"

def update_notion_entry(page_id, calories_result):
    """更新Notion条目的热量结果和状态"""
    url = f"https://api.notion.com/v1/pages/{page_id}"
    
    payload = {
        "properties": {
            "热量计算结果": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": calories_result
                        }
                    }
                ]
            },
            "状态": {
                "select": {
                    "name": "已计算"
                }
            }
        }
    }
    
    response = requests.patch(url, headers=notion_headers, json=payload)
    if response.status_code != 200:
        print(f"更新Notion条目失败: {response.status_code}")

def main():
    """主函数 - 定期检查并处理待计算的条目"""
    while True:
        print("检查待处理条目...")
        entries = get_pending_entries()
        
        for entry in entries:
            # 获取食物描述
            food_description = entry["properties"]["食物描述"]["rich_text"][0]["text"]["content"]
            page_id = entry["id"]
            
            print(f"处理条目: {food_description}")
            
            # 计算热量
            calories_result = calculate_calories(food_description)
            
            # 更新Notion条目
            update_notion_entry(page_id, calories_result)
            
            print(f"条目已更新: {calories_result}")
            
            # 避免API速率限制
            time.sleep(1)
        
        # 每隔一段时间检查一次
        time.sleep(60)  # 每分钟检查一次

if __name__ == "__main__":
    main()