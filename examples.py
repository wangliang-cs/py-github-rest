import json
import os

from PyGithubRest import PyGithubRest


def example_readme(tokens: list[str], repo_full_name_list: list[str], output_folder: str):
    os.makedirs(output_folder, exist_ok=True)
    github = PyGithubRest(tokens)
    readme_dict_list = github.get_readme(repo_full_name_list)
    for idx, readme in enumerate(readme_dict_list):
        readme_path = os.path.join(output_folder, repo_full_name_list[idx].replace('/', '_') + ".json")
        with open(readme_path, "w", encoding="utf-8") as fd:
            if readme:
                readme["repo_name"] = repo_full_name_list[idx]
                fd.write(json.dumps(readme, indent=4))
            else:
                readme_not_found = {}
                readme_not_found["repo_name"] = repo_full_name_list[idx]
                fd.write(json.dumps(readme_not_found, indent=4))


if __name__ == "__main__":
    tokens = ["token1", "token2"]
    repo_full_name_list = ["tensorflow/tensorflow", "pytorch/pytorch", "no_exists/no_exists"]
    example_readme(tokens, repo_full_name_list, output_folder="../examples/readme/")
