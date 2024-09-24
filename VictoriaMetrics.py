import numpy as np
import urllib3
import json


def upload_data(data: dict, url: str) -> int:
    """Uploads data to VictoriaMetrics and calculates the number of bytes.
    If inp.upload is set to False, the size is calculated but no data is uploaded."""

    http = urllib3.PoolManager()

    data = json.dumps(data, cls=NpEncoder)

    http.request('POST', url, body=data)
    return len(data)


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)