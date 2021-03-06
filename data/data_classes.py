import string
import random
from typing import List


class User:
    def __init__(self, user_id: int, username: str, discriminator: str, avatar: str, code: str = "", admin: int = 0,
                 pronouns: str = ""):
        self.user_id = user_id
        self.username = username
        self.discriminator = discriminator
        self.avatar = avatar
        self.code = code
        self.admin = admin
        self.pronouns = pronouns

    def update_code(self, clear: bool = False):
        code: str = ""
        if not clear:
            code = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(6)])
        self.code = code

    def format_name(self) -> str:
        return self.username + "#" + str(self.discriminator)


class Event:
    def __init__(self, name: str, start: str, end: str, state: int = 0, entry_count: int = 0, modder_count: int = 0):
        self.name = name
        self.start = start
        self.end = end
        self.state = state
        self.entry_count = entry_count
        self.modder_count = modder_count

    def format_dates(self):

        if self.state == 0:
            prefix: str = "will run"
        elif self.state == 1:
            prefix: str = "is running"
        else:
            prefix: str = "was ran"

        return f"{prefix} from {self.start} thru {self.end}"


class Badge:
    def __init__(self, badge_id: int, name: str, file: str, role: int):
        self.badge_id = badge_id
        self.name = name
        self.file = file
        self.role = role


class LinkResponse:
    def __init__(self, success: bool = False, message: str = "", user: User = None):
        self.success = success
        self.message = message
        self.user = user


class Entry:
    def __init__(self,
                 users: List[User],
                 name: str,
                 description: str,
                 screenshot: str,
                 link: str,
                 dependencies: str = "",
                 source: str = "",
                 issues: str = ""
                 ):
        self.users = users
        self.name = name
        self.description = description
        self.link = link
        self.screenshot = screenshot
        self.dependencies = dependencies
        self.source = source
        self.issues = issues


class Settings:
    def __init__(self, connect: bool = True, submissions: bool = True, vote: bool = True, edit_entry: bool = True):
        self.connect = connect
        self.submissions = submissions
        self.vote = vote
        self.edit_entry = edit_entry
