
import requests


class ArchiveOrg:
    def __init__(self, base_dir):
        self.base_dir = base_dir

    def get_snapshot(sel, url, timestamp):
      api_url = "http://archive.org/wayback/available"
      params = {"url": url, "timestamp": timestamp}
      try:
          response = requests.get(api_url, params=params, timeout=10)
          response.raise_for_status()
          data = response.json()
          snapshot = data.get("archived_snapshots", {}).get("closest")
          if snapshot and snapshot.get("available"):
              return {"url": snapshot['url'], "timestamp": snapshot['timestamp']}
      except requests.exceptions.RequestException:
          pass
      return None
    
    def latest(self, url):
        return self.get_snapshot(url, "21001231")
    
    def earliest(self, url):
        return self.get_snapshot(url, "19000101")