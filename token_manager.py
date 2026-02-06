import datetime
import json
import time
from threading import RLock
import requests


def _gen_headers(token):
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}"
    }
    return headers


class TokenManager:
    def __init__(self, tokens: list[str]):
        self.tokens_pool = tokens
        self.lock = RLock()
        self.rate_limit = [0 for i in range(len(self.tokens_pool))]
        self._update_rate_limit(verbose=True)

    def get_token(self):
        return self._get_token_block()

    def _update_rate_limit(self, verbose=False):
        # should work with lock
        with self.lock:
            for idx in range(len(self.tokens_pool)):
                token = self.tokens_pool[idx]
                try:
                    with requests.get("https://api.github.com/rate_limit", headers=_gen_headers(token)) as r:
                        content = r.text
                        doc = json.loads(content)
                        if "rate" in doc:
                            # print(doc)
                            self.rate_limit[idx] = doc["rate"]["remaining"]
                except Exception as e:
                    print(f"[{datetime.datetime.now()}] Error: TokenManger _update_rate_limit {e}")
            if verbose:
                print("Token health check:")
                for i in range(len(self.rate_limit)):
                    print(f"{self.rate_limit[i]}  ", end='')
                print()

    def _get_token_block(self):
        # block until a valid token is obtained
        wait_cnt = 0
        with self.lock:
            ret_token = self._get_token_nowait()
            if ret_token is None:
                self._update_rate_limit()
            else:
                return ret_token
            ret_token = self._get_token_nowait()
            while ret_token is None:
                print(f"\r[{datetime.datetime.now()}] Wait for tokens: {wait_cnt}                      ", end="")
                self._update_rate_limit()
                ret_token = self._get_token_nowait()
                wait_cnt += 1
                time.sleep(5)
            print()
        return ret_token

    def _get_token_nowait(self):
        # should work with lock
        with self.lock:
            for i in range(len(self.tokens_pool)):
                if self.rate_limit[i] > 0:
                    self.rate_limit[i] -= 1
                    ret_token = self.tokens_pool[i]
                    return ret_token
        return None
