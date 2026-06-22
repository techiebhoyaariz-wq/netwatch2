import csv
import time
import logger

class Logger:
    """
    Handles printing and saving network metrics to CSV.
    Each measurement includes timestamp, bandwidth, packet loss and jitter.
    """
    def __init__(self, csv_file="results.csv"):
        self.csv_file = open(csv_file, 'w', newline='')
        self.writer = csv.writer(self.csv_file)
        self.writer.writerow(['timestamp', 'bandwidth_mbps', 'loss_percent', 'jitter_ms'])
        print(f"Logging results to {csv_file}")

    def log(self, bandwidth=None, loss=None, jitter=None):
        timestamp = time.strftime('%H:%M:%S')
        row = [timestamp, bandwidth, loss, jitter]
        self.writer.writerow(row)
        self.csv_file.flush()
        parts = [f"[{timestamp}]"]
        if bandwidth is not None:
            parts.append(f"Bandwidth: {bandwidth:.2f} Mbps")
        if loss is not None:
            parts.append(f"Loss: {loss:.2f}%")
        if jitter is not None:
            parts.append(f"Jitter: {jitter:.2f}ms")
        print(" | ".join(parts))

    def close(self):
        self.csv_file.close()
        print("Logger closed. Results saved.")