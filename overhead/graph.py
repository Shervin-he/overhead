import operator
import silk
from matplotlib import pylab
import networkx as nx
import matplotlib.pyplot as plt
from networkx.linalg.spectrum import adjacency_spectrum
import numpy as np


class GraphBuilder(object):
    graph = None
    eccentricity = None

    def __init__(self, file_name, sip):
        self.sip = silk.IPAddr(sip)

        self.silk_file = silk.silkfile_open(file_name, silk.READ)

    def _create_graph(self):
        self.graph = nx.Graph()
        for rec in self.silk_file:
            if rec.sip == self.sip:
                self.graph.add_node(rec.dip.padded(), bipartite=0)
                self.graph.add_node(rec.dport, bipartite=1)
                self.graph.add_edge(rec.dip.padded(), rec.dport)

    def show_graph(self):
        if self.graph is None:
            self._create_graph()
        ips = set(n for n, d in self.graph.nodes(data=True) if d['bipartite'] == 0)
        ports = set(n for n, d in self.graph.nodes(data=True) if d['bipartite'] == 1)
        pos = dict()

        for i in ips:
            pos[i] = [p for p in ports if self.graph.has_edge(i, p)]
        pos.update((n, (1, i)) for i, n in enumerate(ips))
        pos.update((n, (2, i)) for i, n in enumerate(ports))
        nx.draw(self.graph, pos, with_labels=True)
        plt.show()

    def get_spectrum(self):
        if self.graph is None:
            self._create_graph()
        return adjacency_spectrum(self.graph)

    def get_node_count(self):
        if self.graph is None:
            self._create_graph()

        return len(self.graph.nodes())

    def get_edge_count(self):
        if self.graph is None:
            self._create_graph()

        return len(self.graph.edges())

    def get_density(self):
        if self.graph is None:
            self._create_graph()

        return nx.density(self.graph)

    def get_diameter(self):
        if self.graph is None:
            self._create_graph()

        return nx.diameter(self.graph, self._get_eccentricity())

    def get_radius(self):
        if self.graph is None:
            self._create_graph()

        return nx.radius(self.graph, self._get_eccentricity())

    def get_center_node(self):
        if self.graph is None:
            self._create_graph()

        return nx.center(self.graph, self._get_eccentricity())

    def get_connected_component_count(self):
        if self.graph is None:
            self._create_graph()

        return nx.number_connected_components(self.graph)

    def _get_eccentricity(self):
        if self.graph is None:
            self._create_graph()
        if self.eccentricity is None:
            self.eccentricity = nx.eccentricity(self.graph)
        return self.eccentricity

    def get_closeness_centrality(self):
        if self.graph is None:
            self._create_graph()

        return nx.closeness_centrality(self.graph)

    def get_eigenvector_centrality(self):
        if self.graph is None:
            self._create_graph()

        return nx.eigenvector_centrality_numpy(self.graph)

    def get_edge_betweenness_centrality(self):
        if self.graph is None:
            self._create_graph()

        return nx.edge_betweenness_centrality(self.graph)

    def get_betweenness_centrality(self):
        if self.graph is None:
            self._create_graph()

        return nx.betweenness_centrality(self.graph)

    def get_page_rank(self):
        if self.graph is None:
            self._create_graph()

        return nx.pagerank(self.graph)

    def get_average_clustring_coefficient(self):
        if self.graph is None:
            self._create_graph()

        return nx.average_clustering(self.graph)

    def get_edge_overlap(self, node1=None, node2=None):
        if self.graph is None:
            self._create_graph()
        node1 = self.graph.nodes()[0]
        node2 = self.graph.nodes()[1]
        neighbors1 = self.graph.degree(node1)
        neighbors2 = self.graph.degree(node2)
        common_neighbors = len(set(nx.common_neighbors(self.graph, node1, node2)))
        return common_neighbors / ((neighbors1 - 1) + (neighbors2 - 1) - common_neighbors)

    def draw_degree_plot(self):
        if self.graph is None:
            self._create_graph()
        degree_sequence = nx.degree(self.graph).items()
        degree_dict = {}
        for n in degree_sequence:
            degree_dict[n[0]] = degree_dict.get(n[0], 0) + 1

        sorted_list = [(k, degree_dict[k]) for k in sorted(degree_dict, key=degree_dict.get, reverse=True)]

        xs = []
        ys = []
        for i, n in enumerate(sorted_list):
            xs.append(i)
            ys.append(n[1])

        pylab.ylim(ymin=0, ymax=ys[0]+1)
        plt.plot(xs, ys)
        plt.title("Degree rank plot")
        plt.ylabel("degree")
        plt.xlabel("rank")
        plt.savefig("degree_histogram.png")
        plt.show()