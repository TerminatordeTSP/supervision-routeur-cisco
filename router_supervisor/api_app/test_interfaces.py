#!/usr/bin/env python3
import os
import sys

# Ajoute le dossier parent au PYTHONPATH pour bien importer influx_utils
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from influx_utils import InfluxDBDashboard

def main():
    dash = InfluxDBDashboard()
    stats = dash.get_interfaces_mbps()
    for iface in sorted(stats.keys()):
        if iface.startswith("GigabitEthernet"):
            in_mbps = stats[iface].get("in", 0)
            out_mbps = stats[iface].get("out", 0)
            print(f"Interface {iface} :")
            print(f"   In:  {in_mbps:.2f} Mbit/s")
            print(f"   Out: {out_mbps:.2f} Mbit/s")
    dash.close()

if __name__ == '__main__':
    main()