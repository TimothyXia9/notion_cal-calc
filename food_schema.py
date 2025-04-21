class FoodItem:
    def __init__(self, name, calories, unit="克", protein=None, fat=None, carbs=None):
        self.name = name
        self.calories = calories  # 每单位热量(千卡)
        self.unit = unit
        self.protein = protein  # 蛋白质(克)
        self.fat = fat  # 脂肪(克)
        self.carbs = carbs  # 碳水(克)
        self.notion_id = None  # Notion页面ID