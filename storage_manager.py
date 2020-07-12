import sqlite3

from data.data_classes import *


# TODO: Comply with GDPR
# TODO: add db initialization, init tables etc.

def update_user(user: User):
    with sqlite3.connect('storage.db') as con:
        c = con.cursor()
        sql: str = "INSERT INTO USERS VALUES (?, ?, ?, ?, ?, 0);"
        user: Optional[User] = get_user_by_id(user.user_id)
        if user is not None:
            sql: str = "REPLACE INTO USERS VALUES (?, ?, ?, ?, ?, ?);"
        c.execute(sql, (user.user_id, user.username, user.discriminator, user.avatar, user.code, user.admin))
        con.commit()


def get_user_by_id(user_id: int) -> Optional[User]:
    with sqlite3.connect('storage.db') as con:
        c = con.cursor()
        if user_id is not None:
            sql: str = "SELECT * from USERS where id = ?;"
            c.execute(sql, (user_id,))

            row: iter = c.fetchone()
            if row is not None:
                return User(row[0], row[1], row[2], row[3], row[4], row[5])
            else:
                return None


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
        return get_event(rows[len(rows)-1][1])


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
            l.append(get_badge(x[1]))
        return l


def get_badge(badge_id: int) -> Optional[Badge]:
    with sqlite3.connect('storage.db') as con:
        c = con.cursor()
        sql: str = "SELECT * FROM BADGES WHERE id = ?;"
        c.execute(sql, (badge_id,))
        d: iter = c.fetchone()
        if d is None:
            return None
        return Badge(d[0], d[1], d[2])


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
        sql: str = "SELECT id FROM USER_ENTRIES WHERE user = ?;"
        c.execute(sql, (user.user_id,))
        r: iter = c.fetchall()

        l: List[Entry] = []
        for x in r:
            l.append(get_entry(x[0]))
        return l


def get_settings() -> Settings:
    with sqlite3.connect('storage.db') as con:
        c = con.cursor()
        sql: str = "SELECT * FROM SETTINGS;"
        c.execute(sql)
        r: iter = c.fetchone()

        connect: bool = True
        submissions: bool = True
        edit_entries: bool = True

        print(r)

        return Settings(connect, submissions, edit_entries)
