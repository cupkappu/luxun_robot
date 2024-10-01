from datetime import datetime
from fuzzywuzzy import process

def get_time() -> str:
    return f'<Time>{datetime.now().strftime("%Y-%m-%d %H:%M")}</Time>'

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
    
    # 去重
    unique_matching_items = {tuple(item[key] for key in keys if key in item): item for item in matching_items}

    return list(unique_matching_items.values())

# import networkx as nx

# class BusNetwork:
#     def __init__(self, bus_routes):
#         """
#         初始化巴士网络类，构建图，并保留巴士线路信息。
        
#         :param bus_routes: 字典，键为线路名，值为站点列表
#         """
#         self.bus_routes = bus_routes  # 保留巴士线路信息
#         self.graph = nx.Graph()
#         self.build_graph(bus_routes)

#     def build_graph(self, bus_routes):
#         """
#         根据巴士线路构建图。
        
#         :param bus_routes: 字典，键为线路名，值为站点列表
#         """
#         for route, stations in bus_routes.items():
#             for i in range(len(stations) - 1):
#                 self.graph.add_edge(stations[i], stations[i + 1], route=route)
#                 self.graph.add_edge(stations[i + 1], stations[i], route=route)  # 添加反向边

#     def find_path(self, start, end):
#         """
#         查找从起点到终点的最短路径，并附上线路信息。
        
#         :param start: 起点站
#         :param end: 终点站
#         :return: 包含路径和线路信息的字典或提示信息
#         """
#         try:
#             path = nx.shortest_path(self.graph, source=start, target=end)
#             routes = []
#             for i in range(len(path) - 1):
#                 edge_data = self.graph[path[i]][path[i + 1]]
#                 routes.append(edge_data['route'])
#             return {
#                 "path": path,
#                 "routes": routes
#             }
#         except nx.NetworkXNoPath:
#             return f"从 {start} 到 {end} 没有路径."

#     def get_routes(self):
#         """
#         获取所有巴士线路信息。
        
#         :return: 巴士线路字典
#         """
#         return self.bus_routes