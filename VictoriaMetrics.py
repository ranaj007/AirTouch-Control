import numpy as np
import urllib3
import json
import time

def upload_data(data: dict, url: str) -> int:
    """Uploads data to VictoriaMetrics and calculates the number of bytes.
    If inp.upload is set to False, the size is calculated but no data is uploaded."""

    http = urllib3.PoolManager()

    data['version'] = "v1.0.0"

    data = json.dumps(data, cls=NpEncoder)

    err_cntr = 0
    while err_cntr < 5:
        try:
            http.request('POST', url, body=data)
            return len(data)
        except Exception:
            err_cntr += 1
            print(f"Failed to upload data to {url}")
            print("Retrying in 5 seconds...")
            time.sleep(5)
    print(f"Failed all attempts to send data to {url}")
    return False


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)
    