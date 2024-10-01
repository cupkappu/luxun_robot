import networkx as nx
class BusNetwork:
    def __init__(self, bus_routes):
        """
        初始化巴士网络类，构建图，并保留巴士线路信息。
        
        :param bus_routes: 字典，键为线路名，值为站点列表
        """
        self.bus_routes = bus_routes  # 保留巴士线路信息
        self.graph = nx.Graph()
        self.build_graph(bus_routes)

    def build_graph(self, bus_routes):
        """
        根据巴士线路构建图。
        
        :param bus_routes: 字典，键为线路名，值为站点列表
        """
        for route, stations in bus_routes.items():
            for i in range(len(stations) - 1):
                self.graph.add_edge(stations[i], stations[i + 1], route=route)
                self.graph.add_edge(stations[i + 1], stations[i], route=route)  # 添加反向边

    def find_path(self, start, end):
        """
        查找从起点到终点的最短路径，并附上线路信息。
        
        :param start: 起点站
        :param end: 终点站
        :return: 包含路径和线路信息的字典或提示信息
        """
        try:
            path = nx.shortest_path(self.graph, source=start, target=end)
            routes = []
            for i in range(len(path) - 1):
                edge_data = self.graph[path[i]][path[i + 1]]
                routes.append(edge_data['route'])
            return {
                "path": path,
                "routes": routes
            }
        except nx.NetworkXNoPath:
            return f"从 {start} 到 {end} 没有路径."

    def get_routes(self):
        """
        获取所有巴士线路信息。
        
        :return: 巴士线路字典
        """
        return self.bus_routes

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