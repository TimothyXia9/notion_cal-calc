class FoodItem:
    def __init__(self, name, calories, unit="克", protein=None, fat=None, carbs=None):
        self.name = name
        self.calories = calories  # 每单位热量(千卡)
        self.unit = unit
        self.protein = protein  # 蛋白质(克)
        self.fat = fat  # 脂肪(克)
        self.carbs = carbs  # 碳水(克)
        self.notion_id = None  # Notion页面ID

    def __str__(self):
        """字典格式输出食物信息"""
        return "FoodItem" + self.to_dict().__str__()

    def __repr__(self):
        """字典格式输出食物信息"""
        return "FoodItem" + self.to_dict().__repr__()

    def to_dict(self):
        """将食物对象转换为字典"""
        food_dict = {
            "name": self.name,
            "calories": self.calories,
            "unit": self.unit,
        }

        # 只添加非空属性
        if self.protein is not None:
            food_dict["protein"] = self.protein

        if self.fat is not None:
            food_dict["fat"] = self.fat

        if self.carbs is not None:
            food_dict["carbs"] = self.carbs

        if self.notion_id is not None:
            food_dict["notion_id"] = self.notion_id

        return food_dict
