import networkx as nx

class BusNetwork:
    def __init__(self, bus_routes):
        """
        初始化巴士网络类，构建图。
        
        :param bus_routes: 字典，键为线路名，值为站点列表
        """
        self.graph = nx.Graph()
        self.build_graph(bus_routes)

    def build_graph(self, bus_routes):
        """
        根据巴士线路构建图。
        
        :param bus_routes: 字典，键为线路名，值为站点列表
        """
        for stations in bus_routes.values():
            for i in range(len(stations) - 1):
                self.graph.add_edge(stations[i], stations[i + 1])
                self.graph.add_edge(stations[i + 1], stations[i])  # 添加反向边

    def find_path(self, start, end):
        """
        查找从起点到终点的最短路径。
        
        :param start: 起点站
        :param end: 终点站
        :return: 最短路径列表或提示信息
        """
        try:
            path = nx.shortest_path(self.graph, source=start, target=end)
            return path
        except nx.NetworkXNoPath:
            return f"从 {start} 到 {end} 没有路径."

# 示例使用
if __name__ == "__main__":
    bus_routes = {
        'Route1': ['A', 'B', 'C', 'D'],
        'Route2': ['C', 'E', 'F'],
        'Route3': ['D', 'G', 'H', 'A'],
    }

    bus_network = BusNetwork(bus_routes)
    start = 'A'
    end = 'F'
    path = bus_network.find_path(start, end)
    print(f"从 {start} 到 {end} 的路径: {path}")