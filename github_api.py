import time
from typing import Optional
import requests


class GithubAPIWrapper:
    def __init__(self, token_manager):
        self.token_manager = token_manager

    def get_github_headers(self):
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "GitHubDataFetcher/1.0"
        }
        token = self.token_manager.get_token()
        if token:
            headers['Authorization'] = f"token {token}"
        return headers

    def make_github_request(self, url: str, num_retry: int = 3) -> Optional[requests.Response]:
        for retry in range(num_retry):
            try:
                response = requests.get(url, headers=self.get_github_headers())
                if response.status_code == 403:
                    wait_time = 10
                    time.sleep(wait_time)
                    continue
                if response.status_code == 404:
                    return None
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                print(f"Request failed: {str(e)}")
        return None
