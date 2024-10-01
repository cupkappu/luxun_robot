from fuzzywuzzy import process

def fuzzy_match(data, substring, keys, threshold=70):
    """
    在字典列表中进行模糊匹配。

    :param data: 字典列表
    :param substring: 要匹配的子字符串
    :param keys: 需要进行匹配的键列表
    :param threshold: 匹配的阈值（默认70）
    :return: 匹配的字典列表
    """
    matching_items = []

    for key in keys:
        # 获取所有对应键的值
        values = [item[key] for item in data if key in item]
        
        # 进行模糊匹配
        matches = process.extract(substring, values, limit=None)

        # 找到匹配的字典
        for match in matches:
            if match[1] > threshold:
                # 找到匹配项，添加到结果中
                matching_items.append(data[values.index(match[0])])

    return matching_items

# 示例数据
data = [
    {'name': 'Alice', 'age': 30},
    {'name': 'Bob', 'age': 25},
    {'name': 'Charlie', 'age': 35},
    {'name': 'David', 'age': 28},
]

# 要匹配的子字符串
substring = 'Alcee'
# 要匹配的键列表
keys = ['name', 'age']  # 可根据需要添加更多键

# 调用函数
result = fuzzy_match(data, substring, keys)

print(result)