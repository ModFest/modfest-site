import sqlite3
import json
from typing import Optional

from data.data_classes import *


# TODO: Comply with GDPR

def validate_storage():
    print("Validating storage.")
    with sqlite3.connect('storage.db') as con:
        c = con.cursor()
        sql: str = "CREATE TABLE IF NOT EXISTS BADGES (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, " \
                   "icon TEXT NOT NULL, role INTEGER NOT NULL);"
        c.execute(sql)
        sql = "CREATE TABLE IF NOT EXISTS ENTRIES (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, " \
              "description TEXT NOT NULL, screenshot TEXT, link TEXT, dependencies TEXT, source TEXT, " \
              "issues TEXT, event TEXT);"
        c.execute(sql)
        sql = "CREATE TABLE IF NOT EXISTS EVENTS (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, " \
              "start TEXT NOT NULL, end TEXT NOT NULL, state INTEGER NOT NULL DEFAULT 0);"
        c.execute(sql)
        sql = "CREATE TABLE IF NOT EXISTS THEMES (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, " \
              "event TEXT NOT NULL);"
        c.execute(sql)
        sql = "CREATE TABLE IF NOT EXISTS USER_BADGES (id INTEGER PRIMARY KEY AUTOINCREMENT, " \
              "user INTEGER NOT NULL, badge INTEGER NOT NULL);"
        c.execute(sql)
        sql = "CREATE TABLE IF NOT EXISTS USER_ENTRIES (id INTEGER PRIMARY KEY AUTOINCREMENT, " \
              "user INTEGER NOT NULL, entry INTEGER NOT NULL);"
        c.execute(sql)
        sql = "CREATE TABLE IF NOT EXISTS USERS (id INTEGER PRIMARY KEY, username TEXT NOT NULL, " \
              "discriminator TEXT NOT NULL, avatar TEXT NOT NULL, code TEXT, admin INTEGER NOT NULL DEFAULT 0);"
        c.execute(sql)
        con.commit()


def update_user(user: User):
    with sqlite3.connect('storage.db') as con:
        c = con.cursor()
        sql: str = "INSERT INTO USERS VALUES (?, ?, ?, ?, ?, 0, ?);"
        u: Optional[User] = get_user_by_id(user.user_id)
        p: str = ""
        if u is not None:
            sql: str = "REPLACE INTO USERS VALUES (?, ?, ?, ?, ?, 0, ?);"
            p = u.pronouns
        c.execute(sql, (user.user_id, user.username, user.discriminator, user.avatar, user.code, p))
        con.commit()


def get_user_by_id(user_id: int) -> Optional[User]:
    with sqlite3.connect('storage.db') as con:
        c = con.cursor()
        if user_id is not None:
            sql: str = "SELECT * from USERS where id = ?;"
            c.execute(sql, (user_id,))

            row: iter = c.fetchone()
            if row is not None:
                return User(row[0], row[1], row[2], row[3], row[4], row[5], row[6])
            else:
                return None


def get_user_by_id_or_default(user_id: int) -> User:
    u: Optional[User] = get_user_by_id(user_id)
    if u is None:
        return User(user_id, "Unknown", "0000", "https://cdn.discordapp.com/embed/avatars/0.png")
    return u


def get_user_by_code(code: str) -> Optional[User]:
    with sqlite3.connect('storage.db') as con:
        c = con.cursor()
        if code != "":
            sql: str = "SELECT * from USERS where code = ?;"
            c.execute(sql, (code,))
            row: iter = c.fetchone()
            if row is not None:
                return User(row[0], row[1], row[2], row[3], row[4], row[5])
            else:
                return None


def get_latest_event() -> Event:
    with sqlite3.connect('storage.db') as con:
        c = con.cursor()
        sql: str = "SELECT * from EVENTS;"
        c.execute(sql)
        rows: List[iter] = c.fetchall()
        return get_event(rows[len(rows) - 1][1])


def get_event(name: str) -> Optional[Event]:
    with sqlite3.connect('storage.db') as con:
        c = con.cursor()
        if name != "":
            sql: str = "SELECT * from EVENTS where name = ?;"
            c.execute(sql, (name,))
            row: iter = c.fetchone()
            if row is not None:
                return Event(row[1], row[2], row[3], state=row[4])
            else:
                return None


def get_user_badges(user: User) -> List[Badge]:
    with sqlite3.connect('storage.db') as con:
        c = con.cursor()
        sql: str = "SELECT * FROM USER_BADGES WHERE user = ?;"
        c.execute(sql, (user.user_id,))
        l: List[Badge] = []
        for x in c.fetchall():
            l.append(get_badge(x[2]))
        return l


#  TODO: make this not suck
def update_user_badges(user: User, badges: List[Badge]) -> List[Badge]:
    with sqlite3.connect('storage.db') as con:
        c = con.cursor()
        sql: str = "DELETE FROM USER_BADGES WHERE user=?;"
        c.execute(sql, (user.user_id,))

        for b in badges:
            sql: str = "INSERT INTO USER_BADGES (user, badge) VALUES (?,?);"
            c.execute(sql, (user.user_id, b.badge_id))

        con.commit()

        return get_user_badges(user)


def add_badge(user: User, badge: Badge) -> List[Badge]:
    badges: List[Badge] = get_user_badges(user)
    if badge in badges:
        return badges
    else:
        badges.append(badge)
        return update_user_badges(user, badges)


def remove_badge(user: User, badge: Badge) -> List[Badge]:
    badges: List[Badge] = get_user_badges(user)
    if badge not in badges:
        return badges
    else:
        badges.remove(badge)
        return update_user_badges(user, badges)


def create_badge(badge: Badge):
    with sqlite3.connect('storage.db') as con:
        c = con.cursor()
        sql: str = "INSERT INTO BADGES (name, icon, role) VALUES(?,?,?);"
        c.execute(sql, (badge.name, badge.file, badge.role))
        con.commit()


def get_badge(badge_id: int) -> Optional[Badge]:
    with sqlite3.connect('storage.db') as con:
        c = con.cursor()
        sql: str = "SELECT * FROM BADGES WHERE id = ?;"
        c.execute(sql, (badge_id,))
        d: iter = c.fetchone()
        if d is None:
            return None
        return Badge(d[0], d[1], d[2], d[3])


def get_badge_by_name(badge_name: str) -> Optional[Badge]:
    with sqlite3.connect('storage.db') as con:
        c = con.cursor()
        sql: str = "SELECT * FROM BADGES WHERE name = ?;"
        c.execute(sql, (badge_name,))
        d: iter = c.fetchone()
        if d is None:
            return None
        return Badge(d[0], d[1], d[2], d[3])


def get_users_for_entry(entry: int) -> List[User]:
    with sqlite3.connect('storage.db') as con:
        c = con.cursor()
        sql: str = "SELECT * FROM USER_ENTRIES WHERE entry = ?;"
        c.execute(sql, (entry,))
        d: iter = c.fetchall()
        if d is None:
            return []
        l: List[User] = []
        for x in d:
            l.append(get_user_by_id(x[1]))
        return l


def get_entry_id_from_name(entry: str) -> Optional[int]:
    with sqlite3.connect('storage.db') as con:
        c = con.cursor()
        sql: str = "SELECT * FROM ENTRIES WHERE name = ?;"
        c.execute(sql, (entry,))
        x: iter = c.fetchone()
        if x is None:
            return None
        return x[0]


def get_entry(entry: int) -> Optional[Entry]:
    with sqlite3.connect('storage.db') as con:
        c = con.cursor()
        sql: str = "SELECT * FROM ENTRIES WHERE id = ?;"
        c.execute(sql, (entry,))
        x: iter = c.fetchone()

        if x is None:
            return None
        return Entry(
            get_users_for_entry(x[0]),
            x[1],
            x[2],
            x[3],
            x[4],
            x[5],
            x[6],
            x[7],
        )


def get_entries(event: str) -> List[Entry]:
    with sqlite3.connect('storage.db') as con:
        c = con.cursor()
        sql: str = "SELECT * FROM ENTRIES WHERE event = ?;"
        c.execute(sql, (event,))
        r: iter = c.fetchall()
        if r is None:
            return []
        entries: List[Entry] = []
        for x in r:
            entries.append(
                Entry(
                    get_users_for_entry(x[0]),
                    x[1],
                    x[2],
                    x[3],
                    x[4],
                    x[5],
                    x[6],
                    x[7],
                )
            )
        return entries


def get_entries_for_user(user: User) -> List[Entry]:
    with sqlite3.connect('storage.db') as con:
        c = con.cursor()
        sql: str = "SELECT entry FROM USER_ENTRIES WHERE user = ?;"
        c.execute(sql, (user.user_id,))
        r: iter = c.fetchall()

        l: List[Entry] = []
        for x in r:
            l.append(get_entry(x[0]))
        return l


def get_settings() -> Settings:
    with open("globals.json") as json_file:
        data = json.load(json_file)
        return Settings(data["connect"], data["submissions"], data["vote"], data["edit_entry"])


def save_settings(settings: Settings):
    with open("globals.json", "w") as json_file:
        json.dump(settings, json_file)


def create_event(name, start, end) -> Event:
    with sqlite3.connect('storage.db') as con:
        c = con.cursor()
        sql: str = "INSERT INTO EVENTS (name, start, end, state) VALUES(?,?,?,0);"
        c.execute(sql, (name, start, end,))
        return get_event(name)


def update_badge(badge_id: int, name=None, icon=None, role=None) -> Badge:
    with sqlite3.connect('storage.db') as con:
        c = con.cursor()
        if name:
            sql: str = f"UPDATE BADGES SET name=? where id=?;"
            c.execute(sql, (name, badge_id,))

        if icon:
            sql: str = f"UPDATE BADGES SET icon=? where id = ?;"
            c.execute(sql, (icon, badge_id,))

        if role:
            sql: str = f"UPDATE BADGES SET role=? where id = ?;"
            c.execute(sql, (role, badge_id,))

        con.commit()

        return get_badge(badge_id)


def update_event(old_name, name=None, start=None, end=None, state=None) -> Event:
    with sqlite3.connect('storage.db') as con:
        c = con.cursor()
        if name:
            sql: str = f"UPDATE EVENTS SET name=? where name = ?;"
            c.execute(sql, (name, old_name,))

        if start:
            sql: str = f"UPDATE EVENTS SET start=? where name = ?;"
            c.execute(sql, (start, old_name,))

        if end:
            sql: str = f"UPDATE EVENTS SET end=? where name = ?;"
            c.execute(sql, (end, old_name,))

        if state:
            sql: str = f"UPDATE EVENTS SET state=? where name = ?;"
            c.execute(sql, (int(state), old_name,))

        con.commit()

        if name:
            return get_event(name)
        else:
            return get_event(old_name)


def get_badge_list() -> List[Badge]:
    with sqlite3.connect('storage.db') as con:
        c = con.cursor()
        sql: str = "SELECT * FROM BADGES;"
        c.execute(sql,)
        r: iter = c.fetchall()
        if r is None:
            return []
        badges: List[Badge] = []
        for x in r:
            badges.append(
                Badge(x[0], x[1], x[2], x[3])
            )
        return badges


def create_entry(entry: Entry) -> Entry:
    with sqlite3.connect('storage.db') as con:
        c = con.cursor()
        sql: str = "INSERT INTO ENTRIES (name, description, screenshot, link, dependencies, " \
                   "source, issues, event) VALUES (?,?,?,?,?,?,?,?);"
        c.execute(sql, (entry.name, entry.description, entry.screenshot, entry.link, entry.dependencies, entry.source,
                        entry.issues, get_latest_event().name))
        con.commit()

        e: int = get_entry_id_from_name(entry.name)
        sql: str = "INSERT INTO USER_ENTRIES (user, entry) VALUES (?,?);"
        for u in entry.users:
            c.execute(sql, (u.user_id, e))

        con.commit()
    return get_entry(e)


def delete_entry(entry: int):
    with sqlite3.connect('storage.db') as con:
        c = con.cursor()
        sql: str = "DELETE FROM ENTRIES where id=?;"
        c.execute(sql, (entry,))

        sql: str = "DELETE FROM USER_ENTRIES WHERE entry=?;"
        c.execute(sql, (entry,))
        con.commit()
