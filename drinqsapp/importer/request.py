import requests


class Request:
    @staticmethod
    def get_json(url, path, params, port = 443):
        request_url = url + path
        resp = requests.get(url=request_url, params=params)
        data = resp.json()
        return data
