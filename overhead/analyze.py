import silk
import utils
import numpy as np
import json
import pprint


class Analyzer(object):
    # TODO: clean this mess!
    def __init__(self, file_name, ip):
        self.ip = silk.IPAddr(ip)
        self.silk_file = silk.silkfile_open(file_name, silk.READ)

    def print_factors(self):
        result = {}
        inbound_connections = {}
        tmp = {}
        # Preprocess
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
            expected_ports = [i*a + b for i in x]
            coef = np.corrcoef(expected_ports, ports)[0, 1]

            result[source] = {'connection_count': flow_count,
                              'CFR': cfr,
                              'average_data_exchange': average,
                              'linear_matching': np.nan_to_num(coef)}
        pp = pprint.PrettyPrinter(indent=4)
        open('overhead_out.json', 'w').write(json.dumps(result))
