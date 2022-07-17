from github import Github, RateLimitExceededException
from credentials import ACCESS_TOKEN_0, ACCESS_TOKEN_1, DB_USER, DB_PASSWORD, URL
import time
from db_client import DBClient
from urllib.request import urlopen
from data_object import DataObject
import argparse
import nltk


client = DBClient(DB_USER, DB_PASSWORD, URL)

simplification_set = set()

with open("External.txt", 'r') as f:
    for line in f.readlines():
        simplification_set.add(line.strip())


def github_api_data_harvester(db_name, id):

    ACCESS_TOKEN = ACCESS_TOKEN_0 if id == 0 else ACCESS_TOKEN_1

    g = Github(ACCESS_TOKEN)
    repos = g.get_repos()  # this is all the available public repos sorted based on their created time

    count = 0
    while True:  # this is a long-running process, gather a few days of data and decide what to do next.
        try:
            print("count", count)
            last_md_url = None
            page = count * 4 + id
            repo_page = repos.get_page(page)

            i = 0
            while i < len(repo_page):

                try:
                    repo = repo_page[i]
                    commits = repo.get_commits()  # the commits in a repo are also sorted based on time.
                    print("page idx", i)
                    j = 0
                    while j < commits.totalCount:
                        try:
                            print("commit count", j)
                            if last_md_url is None:
                                for file in commits[j].files:
                                    if file.filename == "README.md":
                                        last_md_url = file.raw_url

                            else:
                                current_commit_message = commits[j].commit.message
                                if only_change_md_file(commits, j) and is_simplification_commit(current_commit_message):
                                    gather_md_file_pairs(db_name, repo, commits, j, last_md_url)
                                    last_md_url = commits[j].files[0].raw_url
                        except RateLimitExceededException as e:
                            print(e)
                            continue
                        j += 1
                    i += 1
                except RateLimitExceededException as e:
                    print("Exceed the rate limit")
                    time.sleep(300)
                    continue

                count += 1

        except RateLimitExceededException as e:  # Github API only have a rate limit of 5000 requests/ hour. 
            print("Exceed the rate limit")
            time.sleep(300)  # sleep for 5 minutes to avoid the time limits.
            continue
        except Exception as e:
            print(e)
            continue


def only_change_md_file(commits, idx):
    """
    see whether this commit only change the .md file
    """
    if len(commits[idx].files) == 1 and commits[idx].files[0].filename == 'README.md':
        return True
    else:
        return False


def is_simplification_commit(current_commit_message):
    """
    see if the current commit message is an indication of simplifying the texts.
    """
    tokenizer = nltk.SpaceTokenizer()
    tokens = tokenizer.tokenize(current_commit_message)
    # print(simplification_set)
    # print(tokens)
    for token in tokens:
        if token in simplification_set:
            return True

    return False


def gather_md_file_pairs(db_name, repo, commits, idx, last_md_url):
    """
    after verifying the current commit is a simplifying commit, we gather these two version of markdown files.
    we decide to store them as json files and dumps into a CouchDB.
    """
    current_commit = commits[idx]
    current_commit_url = current_commit.files[0].raw_url
    data_instance = None

    while not data_instance:
        try:
            data_instance = DataObject(last_md_url, current_commit_url, repo, str(idx))

            try:
                client.put_record(db_name, data_instance.to_json_format())

            except Exception as e:
                print(e)

        except:
            continue


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=str, help="Specify the intended db name")
    parser.add_argument("--id", type=int, help="Specify the currently working process id")
    args = parser.parse_args()
    db_name = args.db
    id = args.id
    github_api_data_harvester(db_name, id)

