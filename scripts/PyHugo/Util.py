
import requests


class ArchiveOrg:
    def __init__(self, base_dir):
        self.base_dir = base_dir

    def get_snapshot(url, timestamp):
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
    
    def latest(url):
        return ArchiveOrg.get_snapshot(url, "21001231")
    
    def earliest(url):
        return ArchiveOrg.get_snapshot(url, "19000101")

class Wikidata:
    def getLabel(id_or_url, lang="en"):
        if not id_or_url:
            return None
        qid = id_or_url
        if "http" in qid:
            qid = qid.rstrip("/").split("/")[-1]

        api_url = "https://www.wikidata.org/w/api.php"
        params = {
            "action": "wbgetentities",
            "ids": qid,
            "props": "labels",
            "languages": lang,
            "format": "json"
        }
        try:
            response = requests.get(api_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            entity = data.get("entities", {}).get(qid, {})
            if "labels" in entity and lang in entity["labels"]:
                return entity["labels"][lang]["value"].strip()
        except requests.exceptions.RequestException:
            pass
        return None