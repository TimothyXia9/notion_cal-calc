from 

def main():
    agent = FoodAgent()

    print("=== 食物热量计算代理 ===")
    print("输入食物描述，多个食物用逗号分隔")
    print("输入'exit'退出")

    while True:
        food_description = input("\n请输入食物描述: ")
        if food_description.lower() == "exit":
            break

        if not food_description.strip():
            continue

        print("\n正在分析食物...")
        food_items = agent.process_food_description(food_description)

        if food_items:
            print("\n分析结果:")
            total_calories = 0
            for item in food_items:
                print(f"- {item.name}: {item.calories}千卡/100{item.unit}")
                if item.protein:
                    print(f"  蛋白质: {item.protein}克")
                if item.fat:
                    print(f"  脂肪: {item.fat}克")
                if item.carbs:
                    print(f"  碳水: {item.carbs}克")
                total_calories += item.calories

            print(f"\n总热量: {total_calories}千卡")
        else:
            print("未能识别任何食物，请重试")


if __name__ == "__main__":
    main()
