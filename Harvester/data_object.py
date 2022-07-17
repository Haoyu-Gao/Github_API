from urllib.request import urlopen


class DataObject:

    def __init__(self, prev_url, current_url, repo, idx):
        last_md, current_md = urlopen(prev_url), urlopen(current_url)
        self.src_text, self.dest_text = last_md.read(), current_md.read()
        self.id = repo.full_name + idx
        # some interesting features, not necessarily related to our project, but extract them anyway.
        self.language = repo.language
        self.forks_count = repo.forks_count


    def to_json_format(self):
        json_file = dict()
        json_file.update({"src": str(self.src_text)})
        json_file.update({"dest": str(self.dest_text)})
        json_file.update({"_id": self.id})
        json_file.update({"lang": self.language})
        json_file.update({"forks_count": self.forks_count})

        return json_file

