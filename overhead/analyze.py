import operator
import silk
import utils
import numpy as np
import json
import pprint
import matplotlib.pyplot as plt
from datetime import timedelta
import networkx as nx
from scipy.stats import entropy
from matplotlib import pylab


class Analyzer(object):
    def __init__(self, file_name, ip):
        self.ip = silk.IPAddr(ip)
        self.silk_file = silk.silkfile_open(file_name, silk.READ)
        self.time_dict = {}
        self.size_list = None
        self.time_list = None
        self.time_delta = None
        self.min_time = None

    def _fill_time_dict(self, time_delta=timedelta(seconds=30)):
        self.time_dict = self._create_time_dict(time_delta, self.ip)
        self.time_delta = time_delta

    def time_dict_statistical_features(self):
        time_series = []
        if self.time_dict == {}:
            self._fill_time_dict()
        if self.size_list is None or self.time_list is None:
            self.calculate_flow_sizes()
        for key in self.time_list:
            data = self.time_dict[key]
            mean = np.mean([d.bytes for d in data])
            std = np.std([d.bytes for d in data])
            median = np.median([d.bytes for d in data])
            time_series.append((mean, median, std))

        x = []
        min_time = self.min_time
        for i in self.time_list:
            min_time = min_time + self.time_delta
            x.append(min_time)

        plt.plot(x, [k[0] for k in time_series], label="mean")
        plt.plot(x, [k[1] for k in time_series], label="median")
        plt.plot(x, [k[2] for k in time_series], label="std")
        plt.xlabel("time")
        plt.legend(loc="upper left", shadow=True, fancybox=True)

        plt.show()

    def _create_time_dict(self, time_delta, src_ip, dest_ip=None):
        time_dict = {}
        initial_time = None
        self.silk_file = silk.silkfile_open(self.silk_file.name, silk.READ)
        for rec in self.silk_file:
            if self.min_time is None or rec.stime < self.min_time:
                self.min_time = rec.stime
            if initial_time is None:
                initial_time = rec.stime
            if rec.sip == src_ip:
                if dest_ip is None or rec.sip == dest_ip:
                    if rec.stime > initial_time:
                        index = (rec.stime - initial_time).seconds / time_delta.seconds
                    else:
                        index = - ((initial_time - rec.stime).seconds / time_delta.seconds)
                _list = time_dict.get(index, [])
                _list.append(rec)
                time_dict[index] = _list
        return time_dict

    def calculate_duration_features(self):
        self.silk_file = silk.silkfile_open(self.silk_file.name, silk.READ)
        min_duration = None
        max_duration = None
        min_time = None
        max_time = None
        average_duration = timedelta(0)
        counter = 0
        for rec in self.silk_file:
            if min_time is None or rec.stime < min_time:
                min_time = rec.stime
            if max_time is None or rec.etime > max_time:
                max_time = rec.etime

            if min_duration is None or min_duration > rec.duration:
                min_duration = rec.duration

            if max_duration is None or max_duration < rec.duration:
                max_duration = rec.duration

            average_duration = (average_duration * counter + rec.duration) / (counter + 1)
            counter += 1
        return {'min': min_duration, 'max': max_duration, 'average': average_duration,
                'flow_per_sec': counter / (max_time - min_time).seconds}

    def basic_statistical_features_flow_sizes(self): # Done
        self.silk_file = silk.silkfile_open(self.silk_file.name, silk.READ)
        byte_list = []
        packet_list = []
        for rec in self.silk_file:
            byte_list.append(rec.bytes)
            packet_list.append(rec.packets)
        result = {
            'mean_bytes': np.mean(byte_list),
            'average_bytes': np.average(byte_list),
            'min_bytes': np.min(byte_list),
            'max_bytes': np.max(byte_list),
            'sd_bytes': np.std(byte_list),
            'mean_packets': np.mean(packet_list),
            'average_packets': np.average(packet_list),
            'min_packets': np.min(packet_list),
            'max_packets': np.max(packet_list),
            'sd_packets': np.std(packet_list)
        }
        return result

    def get_inter_arrival_times(self, target_ip):
        ip_dest = silk.IPAddr(target_ip)

        self.silk_file = silk.silkfile_open(self.silk_file.name, silk.READ)
        flow_time_list = []
        for rec in self.silk_file:
            if rec.sip == self.ip and rec.dip == ip_dest:
                flow_time_list.append(rec)
        inter_arrival_times = []
        flow_count = len(flow_time_list)
        flow_time_list.sort(key=lambda x: x.stime)

        if flow_count > 1:
            for i in range(1, flow_count):
                inter_arrival_times.append(flow_time_list[i].stime - flow_time_list[i-1].etime)

        return inter_arrival_times

    def calculate_statistical_features_inter_arrival_times(self, dest_ip):
        inter_arrival_times = [item.seconds for item in self.get_inter_arrival_times(dest_ip)]
        auto_corr = self._autocorrelation(inter_arrival_times)
        result = {
            'min': np.min(inter_arrival_times),
            'max': np.max(inter_arrival_times),
            'mean': np.mean(inter_arrival_times),
            'median': np.median(inter_arrival_times),
            'sd': np.std(inter_arrival_times),
            'autocorrelation': auto_corr
        }
        return result

    def calculate_flow_sizes(self, time_delta=timedelta(seconds=30), dest_ip=None):
        size_list = []
        if self.time_dict == {}:
            self._fill_time_dict()
        time_dict = self.time_dict if dest_ip is None else self._create_time_dict(time_delta, self.ip, dest_ip)
        time_list = [k for k in sorted(time_dict.keys(), reverse=False)]
        for index in time_list:
            size = 0
            for rec in self.time_dict[index]:
                size += rec.bytes
            size_list.append(size)
        self.time_list = time_list
        self.size_list = size_list

    def draw_flow_size_graph(self):
        if self.time_list is None or self.size_list is None:
            self.calculate_flow_sizes()
        plt.plot(self.time_list, self.size_list)
        plt.show()

    def flow_size_autocorrelation(self):
        if self.time_list is None or self.size_list is None:
            self.calculate_flow_sizes()
        self._autocorrelation(self.size_list)

    def _autocorrelation(self, data, shift=5):
        n = len(data)
        variance = np.var(self.size_list)
        x = np.array([size - np.mean(data) for size in data])
        r = np.correlate(x, x, mode='full')[-n:]
        result = r/(variance*(np.arange(n, 0, -1)))
        plt.plot(self.time_list, result)
        plt.show()

    def average_flow_sizes(self, time_delta=timedelta(seconds=30)):
        if self.time_dict == {}:
            self._fill_time_dict()
        size_list = []
        time_list = [k for k in sorted(self.time_dict.keys(), reverse=False)]
        count = 0
        for index in time_list:
            average = 0
            for rec in self.time_dict[index]:
                average = average * count
                average += rec.bytes
                count += 1
                average = average / count
            size_list.append(average)
        plt.plot(time_list, size_list)
        plt.show()

    def unique_flow_sizes(self):
        size_dict = {}
        self.silk_file = silk.silkfile_open(self.silk_file.name, silk.READ)
        for rec in self.silk_file:
            size_dict[rec.bytes] = size_dict.get(rec.bytes, 0) + 1
        time_list = [k for k in sorted(size_dict.keys(), reverse=False)]
        size_list = [size_dict[k] for k in time_list]
        pylab.ylim(ymin=0, ymax=size_list[-1]+1)
        # plt.plot(time_list, size_list)
        ind = np.arange(len(time_list))
        plt.bar(time_list, size_list, width=.35)
        self.time_list = time_list
        self.size_list = size_list
        plt.show()

    def aggregate_flow_sizes(self, time_delta=timedelta(seconds=30)):
        if self.time_dict == {}:
            self._fill_time_dict(time_delta)

        size_list = []
        time_list = [k for k in sorted(self.time_dict.keys(), reverse=False)]
        size = 0
        for index in time_list:
            for rec in self.time_dict[index]:
                size += rec.bytes
            size_list.append(size)

        plt.plot(time_list, size_list)
        plt.show()

    def unmatched_flows(self):
        self.silk_file = silk.silkfile_open(self.silk_file.name, silk.READ)
        unmatched_flows = set()
        for rec in self.silk_file:
            flow = (rec.sip, rec.dip, rec.sport, rec.dport)
            if flow in unmatched_flows:
                unmatched_flows -= {flow}
            else:
                unmatched_flows |= {flow}
        return len(unmatched_flows)

    def port_distribution_entropy(self, time_delta):
        self.silk_file = silk.silkfile_open(self.silk_file.name, silk.READ)
        time_dict = {}
        initial_time = None
        for rec in self.silk_file:
            if initial_time is None:
                initial_time = rec.stime
            if rec.stime > initial_time:
                index = ((rec.stime - initial_time).seconds / time_delta.seconds)
            else:
                index = - ((initial_time - rec.stime).seconds / time_delta.seconds)
            port_dist = time_dict.get(index, {})
            port_dist[rec.dport] = port_dist.get(rec.dport, 0) + 1
            time_dict[index] = port_dist
        sorted_keys = sorted(time_dict.keys())
        result = {}
        # prev_data = None
        for key in sorted_keys:
            _data = time_dict[key]
            # sorted_data = sorted(_data.items(), key=operator.itemgetter(0))
            result[key] = entropy(sorted([v for k, v in _data.items()]))
            # if prev_data is not None:
            #
            #     result['kl - %s' % key] = entropy([v for k, v in sorted_data],
            #                                       [v for k, v in sorted_prev_data])
            # prev_data = _data
        return result

    def port_distribution(self):
        port_dict = {}
        self.silk_file = silk.silkfile_open(self.silk_file.name, silk.READ)
        for rec in self.silk_file:
            port_dict[rec.dport] = port_dict.get(rec.dport, 0) + 1

        time_list = [k for k in sorted(port_dict.keys(), reverse=False)]
        size_list = [port_dict[k] for k in time_list]
        plt.bar(time_list, size_list)
        self.time_list = time_list
        self.size_list = size_list
        plt.show()

    def number_of_ports(self):
        self.silk_file = silk.silkfile_open(self.silk_file.name, silk.READ)
        ports = set()
        for rec in self.silk_file:
            if rec.dport not in ports:
                ports.add(rec.dport)
        print len(ports)

    def specific_port(self, port, time_delta):
        self.silk_file = silk.silkfile_open(self.silk_file.name, silk.READ)
        time_dict = {}
        initial_time = None
        min_time = None
        for rec in self.silk_file:
            if initial_time is None or rec.stime < min_time:
                min_time = rec.stime

            if initial_time is None:
                initial_time = rec.stime
            if rec.stime > initial_time:
                index = ((rec.stime - initial_time).seconds / time_delta.seconds)
            else:
                index = - ((initial_time - rec.stime).seconds / time_delta.seconds)
            time_dict[index] = time_dict.get(index, 0)
            if rec.dport == port:
                time_dict[index] += 1
        time_list = sorted([k for k, v in time_dict.items()])
        data_list = [time_dict[key] for key in time_list]
        plt.ylabel("count")
        plt.xlabel("time")
        x = []
        for i in time_list:
            min_time = min_time + time_delta
            x.append(min_time)
        plt.plot(x, data_list)
        plt.show()

    def packet_ratio(self):
        self.silk_file = silk.silkfile_open(self.silk_file.name, silk.READ)
        inbound_packets = 0
        inbound_flows = 0
        outbound_packets = 0
        outbound_flows = 0
        for rec in self.silk_file:
            if rec.sip == self.ip:
                outbound_flows += 1
                outbound_packets += rec.packets
            if rec.dip == self.ip:
                inbound_flows += 1
                inbound_packets += rec.bytes
        return {
            'packet_ratio': float(inbound_packets) / outbound_packets,
            'CFR': (float(outbound_flows) - inbound_flows) / outbound_flows
        }

    def print_factors(self):
        result = {}
        inbound_connections = {}
        tmp = {}
        # Preprocess
        self.silk_file = silk.silkfile_open(self.silk_file.name, silk.READ)
        for rec in self.silk_file:
            if rec.sip == self.ip:
                s = inbound_connections.get(rec.dip.padded(), set())
                s.add(rec.sip.padded())
                inbound_connections[rec.dip.padded()] = s
            if rec.dip == self.ip:
                factors = tmp.get(rec.sip.padded(), {})
                factors[rec.dport] = factors.get(rec.dport, 0) + 1
                tmp[rec.sip.padded()] = factors

        for source in tmp:
            values = tmp[source].values()
            lower_bound, upper_bound = utils.get_upper_and_lower_bounds(values)
            average = np.mean([v for v in values if lower_bound <= v <= upper_bound])
            ports = tmp[source].keys()
            flow_count = len(ports)
            in_c = inbound_connections.get(source)
            inbound_count = 0
            if in_c:
                inbound_count = len(in_c)
            cfr = (flow_count - inbound_count) / flow_count
            lower_bound, upper_bound = utils.get_upper_and_lower_bounds(ports)
            ports = [port for port in ports if lower_bound <= port <= upper_bound]
            x = range(0, len(ports))
            a, b = np.polyfit(x, ports, 1)
            expected_ports = [i * a + b for i in x]
            coef = np.corrcoef(expected_ports, ports)[0, 1]

            result[source] = {'connection_count': flow_count,
                              'CFR': cfr,
                              'average_data_exchange': average,
                              'linear_matching': np.nan_to_num(coef)}
        return result
