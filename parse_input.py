import re


# 数字中文转换词典
chinese_digit_map = {
    "一": 1,
    "二": 2,
    "两": 2,
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
    item_text = item_text.strip()

    # 匹配阿拉伯数字或中文数字
    quantity_match = re.match(r"^([0-9一二两三四五六七八九十半]+)(.*)", item_text)

    if quantity_match:
        # 提取数量
        quantity_str = quantity_match.group(1)
        remainder = quantity_match.group(2).strip()

        # 转换数量
        if quantity_str.isdigit():
            quantity = int(quantity_str)
        else:
            quantity = convert_chinese_num(quantity_str)
            if quantity is None:
                raise ValueError(f"无法解析数量: {quantity_str}")
    else:
        # 如果没有指定数量，默认为1
        quantity = 1
        remainder = item_text

    # 匹配单位
    unit_match = re.match(r"^([个杯碗份块片克g千克kg包]+)(.*)", remainder)

    if unit_match:
        unit = unit_match.group(1)
        food_name = unit_match.group(2).strip()
    else:
        unit = "个"  # 默认单位
        food_name = remainder
        raise ValueError(f"无法解析单位: {item_text}，请指定单位。")

    # 确保食品名称不为空
    if not food_name:
        raise ValueError(f"无法解析食品名称: {item_text}")

    return quantity, unit, food_name


def parse_multiple_food(input_text):
    """
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
    # test_input = "10坨鸡块，2杯米饭，半份沙拉"
    # result = parse_multiple_food(test_input)
    # print(result)  # 输出解析结果
    print(parse_food_item("一根白面包"))  # 测试单个食品项解析
