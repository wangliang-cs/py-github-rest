import base64
from github_api import GithubAPIWrapper
from token_manager import TokenManager
from util import clean_text
from concurrent.futures import ThreadPoolExecutor, as_completed


class PyGithubRest:
    def __init__(self, tokens: list[str]):
        """
        :param tokens: a list of GitHub tokens
        """
        # initialize token manager
        self._token_manager = TokenManager(tokens)
        self._github_api = GithubAPIWrapper(self._token_manager)

    def _batch(self, url_list: list[str], num_workers) -> list:
        ret_list = [None] * len(url_list)

        def fetch(index, url):
            return index, self._github_api.make_github_request(url)

        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            future_to_index = {executor.submit(fetch, i, url): i for i, url in enumerate(url_list)}
            for future in as_completed(future_to_index):
                idx, res = future.result()
                ret_list[idx] = res

        return ret_list

    def get_readme(self, repo_full_name_list: list[str], num_workers: int = 100):
        def _preprocess(repo_full_name_list_: list[str]):
            url_list_ = []
            for repo_full_name in repo_full_name_list_:
                api_url = f"https://api.github.com/repos/{repo_full_name}/readme"
                url_list_.append(api_url)
            return url_list_

        def _postprocess(response_list_):
            ret_list = []
            for response in response_list_:
                if response:
                    data = response.json()
                    if "content" in data:
                        # README 内容是 Base64 编码的，需要解码
                        decoded_content = base64.b64decode(data["content"]).decode("utf-8")
                        data["decoded_readme"] = decoded_content
                        data["clean_readme"] = clean_text(decoded_content)
                        ret_list.append(data)
                    else:
                        ret_list.append(None)
                else:
                    ret_list.append(None)
            return ret_list

        url_list = _preprocess(repo_full_name_list)
        response_list = self._batch(url_list, num_workers)
        return _postprocess(response_list)
