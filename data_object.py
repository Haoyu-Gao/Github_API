from urllib.request import urlopen


class DataObject:

    def __init__(self, prev_url, current_url, repo):
        last_md, current_md = urlopen(prev_url), urlopen(current_url)
        self.src_text, self.dest_text = last_md.read(), current_md.read()
        self._id = str(hash(prev_url + current_url))  # a unique pair to form its hash function
        # some interesting features, not necessarily related to our project, but extract them anyway.
        self.language = repo.language
        self.forks_count = repo.forks_count

    def to_json_format(self):
        json_file = dict()
        json_file.update({"src": str(self.src_text)})
        json_file.update({"dest": str(self.dest_text)})
        json_file.update({"_id": self._id})
        json_file.update({"lang": self.language})
        json_file.update({"forks_count": self.forks_count})

        return json_file

