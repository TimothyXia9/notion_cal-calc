import re


# 数字中文转换词典
chinese_digit_map = {
    "一": 1,
    "二": 2,
    "三": 3,
    "四": 4,
    "五": 5,
    "六": 6,
    "七": 7,
    "八": 8,
    "九": 9,
    "十": 10,
    "半": 0.5,
}


def convert_chinese_num(chinese_str):
    """将中文数字转换为阿拉伯数字"""
    if chinese_str in chinese_digit_map:
        return chinese_digit_map[chinese_str]
    return None


def parse_food_item(item_text):
    """解析单个食品项"""
    # 匹配模式：数字+单位+食品名 或 中文数字+单位+食品名
    # 例如：10个鸡块、一个汉堡、半份沙拉

    # 尝试匹配阿拉伯数字
    arab_match = re.match(
        r"(\d+)([个|杯|碗|份|块|片|克|g|千克|kg]*)\s*(.+)", item_text.strip()
    )
    if arab_match:
        quantity = int(arab_match.group(1))
        unit = arab_match.group(2) if arab_match.group(2) else "个"  # 默认单位
        food_name = arab_match.group(3).strip()
        return quantity, unit, food_name

    # 尝试匹配中文数字
    chinese_match = re.match(
        r"([一二三四五六七八九十半]+)([个|杯|碗|份|块|片|克|g|千克|kg]*)\s*(.+)",
        item_text.strip(),
    )
    if chinese_match:
        chinese_num = chinese_match.group(1)
        quantity = convert_chinese_num(chinese_num)
        if quantity is None:
            return None, None, None
        unit = chinese_match.group(2) if chinese_match.group(2) else "个"  # 默认单位
        food_name = chinese_match.group(3).strip()
        return quantity, unit, food_name

    # 如果没有指定数量，默认为1
    # 尝试仅匹配食品名
    food_only_match = re.match(
        r"([个|杯|碗|份|块|片|克|g|千克|kg]*)\s*(.+)", item_text.strip()
    )
    if food_only_match:
        quantity = 1
        unit = (
            food_only_match.group(1) if food_only_match.group(1) else "个"
        )  # 默认单位
        food_name = food_only_match.group(2).strip()
        return quantity, unit, food_name

    return None, None, None


def parse_multiple_food(input_text):
    """计算多种食品的热量
    output: [(food_name, quantity, unit), ...]"""
    # 使用常见分隔符分割输入
    output = []
    food_items = re.split(r"[,，、和及与\s]+", input_text)

    # 过滤空项
    food_items = [item for item in food_items if item.strip()]
    print(f"解析的食物项: {food_items}")  # 调试输出

    if not food_items:
        return None

    for item in food_items:
        quantity, unit, food_name = parse_food_item(item)

        if food_name is None:
            raise ValueError(f"无法解析食品项: {item}")
        else:
            output.append((food_name, quantity, unit))
    return output


if __name__ == "__main__":
    # 测试代码
    test_input = "10坨鸡块，2杯米饭，半份沙拉"
    result = parse_multiple_food(test_input)
    print(result)  # 输出解析结果
