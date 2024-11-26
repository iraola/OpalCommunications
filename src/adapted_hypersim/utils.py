import os
import sys
import re
import sqlite3
from datetime import datetime
import time
import psutil
import matplotlib.pyplot as plt
from collections import deque


PACKET_HISTORY = deque(maxlen=30)
CPU_HISTORY = deque(maxlen=30)
AVG_PROCESSING_TIME_HISTORY = deque(maxlen=30)
TIME_HISTORY = deque(maxlen=30)

def update_plot():
    """Updates the plot with the most recent data."""
    plt.clf()
    plt.subplot(311)
    plt.plot(TIME_HISTORY, PACKET_HISTORY, label="Packets Received")
    plt.title("Packets Received Over Time")
    plt.xlabel("Time (seconds)")
    plt.ylabel("Packets Received")
    
    plt.subplot(312)  # Plot for Avg Processing Time
    plt.plot(TIME_HISTORY, AVG_PROCESSING_TIME_HISTORY, label="Average Processing Time", color='orange')
    plt.title("Average Processing Time Over Time")
    plt.xlabel("Time (seconds)")
    plt.ylabel("Avg Processing Time (s)")
    
    plt.subplot(313) 
    plt.plot(TIME_HISTORY, CPU_HISTORY, label="CPU Usage", color='green')
    plt.title("CPU Usage Over Time")
    plt.xlabel("Time (seconds)")
    plt.ylabel("CPU Usage (%)")
    
    plt.tight_layout()
    plt.pause(0.1)  

def main_monitor():
    initialize_database("main.db")
    plt.ion()
    while True:
        time.sleep(10)
        collected_data = read_all_databases_and_collect_data()
        
        current_time = time.time()
        TIME_HISTORY.append(current_time)
        PACKET_HISTORY.append(collected_data['packets_received'])
        CPU_HISTORY.append(collected_data['cpu_usage'])
        AVG_PROCESSING_TIME_HISTORY.append(collected_data['avg_processing_time'])
        
        update_plot()

        print_metrics("Main monitor", 
                    collected_data['packets_received'], 
                    collected_data['packets_processed'], 
                    collected_data['avg_processing_time'], 
                    collected_data['cpu_usage'])
        
        record_metrics_in_database("main.db", 
                    collected_data['packets_received'], 
                    collected_data['packets_processed'], 
                    collected_data['avg_processing_time'], 
                    collected_data['cpu_usage'])


def read_all_databases_and_collect_data():
    """Read all edge*.db files and collect the data from the udp_monitor table."""
    db_files = [f for f in os.listdir('.') if re.match(r'edge\d+\.db', f)]

    collected_data = {}

    for db_file in db_files:
        initialize_database(db_file)

        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        cursor.execute('''SELECT timestamp, packets_received, packets_processed, avg_processing_time, cpu_usage
                          FROM udp_monitor ORDER BY id DESC LIMIT 1''')

        result = cursor.fetchone()

        if result:
            timestamp, packets_received, packets_processed, avg_processing_time, cpu_usage = result

            collected_data['timestamp'] = timestamp

            if 'packets_received' in collected_data:
               collected_data['packets_received'] = collected_data['packets_received'] + packets_received
            else: 
                collected_data['packets_received'] = packets_received

            if 'packets_processed' in collected_data:
               collected_data['packets_processed'] = collected_data['packets_processed'] + packets_processed
            else: 
                collected_data['packets_processed'] = packets_processed
            
            if 'avg_processing_time' in collected_data:
                collected_data['avg_processing_time'] = collected_data['avg_processing_time'] + avg_processing_time
            else:
                collected_data['avg_processing_time'] = avg_processing_time

            collected_data['cpu_usage'] = cpu_usage

        conn.close()

    collected_data['avg_processing_time'] = collected_data['avg_processing_time'] / len(db_files)
    return collected_data


def initialize_database(db_path):
    """Create the database and table if they don't exist."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS udp_monitor (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            packets_received INTEGER NOT NULL,
            packets_processed INTEGER NOT NULL,
            avg_processing_time REAL NOT NULL,
            cpu_usage REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


def calculate_average_processing_time(total_processing_time, packets_processed):
    """Calculate the average processing time."""
    if packets_processed > 0:
        return total_processing_time / packets_processed
    return 0.0


def record_metrics_in_database(db_path, packets_received, packets_processed, avg_processing_time, cpu_usage):
    """Insert the metrics into the database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('''
        INSERT INTO udp_monitor (timestamp, packets_received, packets_processed, avg_processing_time, cpu_usage)
        VALUES (?, ?, ?, ?, ?)
    ''', (timestamp, packets_received, packets_processed, avg_processing_time, cpu_usage))
    conn.commit()
    conn.close()


def print_metrics(label, packets_received, packets_processed, avg_processing_time, cpu_usage):
    """Print the metrics to the console."""
    print(f"{label}:")
    print(f" - Packets Received: {packets_received}")
    print(f" - Packets Processed: {packets_processed}")
    print(f" - Average Processing Time: {avg_processing_time:.4f}s")
    print(f"System CPU usage: {cpu_usage}%")
    print("----------------------------------------")
    print()


def get_last_int(cadena):
    match = re.search(r'\d+$', cadena)
    if match:
        return match.group()
    else:
        return None


def hypersim_setup():
    hypersimDir = r"C:\\OPAL-RT\\HYPERSIM\\hypersim_2024.1.0.o39"
    if not os.path.isdir(hypersimDir):
        print("INVALID HYPERSIM DIRECTORY SPECIFIED IN THE SCRIPT")
        exit(1)
    sys.path.append(os.path.join(hypersimDir, 'Windows', 'HyApi', 'python'))
    import HyWorksApiGRPC as HyWorksApi
    HyWorksApi.startAndConnectHypersim()
    print(os.path.realpath(__file__))
    designPath = r"C:\Users\Hypersim\Documents\docs hypersim\HYPERSIM\HYPERSIM_IEEE9Bus_50Hz\HVAC_230kV_9bus_IEEE.ecf"
    print(designPath)
    HyWorksApi.openDesign(designPath) 
    try:
        HyWorksApi.startSim()
    except:
        print("Simulation is already running")


def get_type_values(driver, types, indexes):
    suffix = driver.split(".")[-1]
    for type in types.keys():
        if suffix in types[type]:
            if type == "Generator" and len(indexes) == 2:
                values = (['lfVolt', 'lfP'], indexes)
            elif type == "Load" and len(indexes) == 2:
                values = (['P', 'Q'], indexes)
            elif type == "Switch" and len(indexes) == 3:
                values = (['STATEa', 'STATEb', 'STATEc'], indexes)
            elif type == "Switch" and len(indexes) == 1:
                values = (['STATEa'], indexes)
            elif type == "Voltmeter" and len(indexes) == 3:
                values = (['Va', 'Vb', 'Vc'], indexes)
            elif type == "Voltmeter" and len(indexes) == 1:
                values = (['Va'], indexes)
            elif type == "Ammeter" and len(indexes) == 3:
                values = (['Ia', 'Ib', 'Ic'], indexes)
            elif type == "Ammeter" and len(indexes) == 1:
                values = (['Ia'], indexes)
            elif type == "Wattmeter" and len(indexes) == 3:
                values = (['Wa', 'Wb', 'Wc'], indexes)
            elif type == "Wattmeter" and len(indexes) == 1:
                values = (['Wa'], indexes)
            elif type == "Varmeter" and len(indexes) == 3:
                values = (['VAa', 'VAb', 'VAc'], indexes)
            elif type == "Varmeter" and len(indexes) == 1:
                values = (['VAa'], indexes)
            else:
                values = None
            return values
    return None