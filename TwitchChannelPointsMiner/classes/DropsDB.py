import sqlite3
import time
from contextlib import closing

# A game's "account not linked" warning is repeated at most once per this many seconds
NOTICE_INTERVAL = 24 * 60 * 60


class DropsDB(object):
    """Remembers which drops we already tried to claim, so each is attempted only once,
    and when we last warned about a game whose account is not connected."""

    def __init__(self, path):
        self.path = path
        with closing(self.__connect()) as db, db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS drops ("
                "drop_id TEXT PRIMARY KEY, name TEXT, game TEXT, "
                "claimed INTEGER NOT NULL, attempted_at REAL NOT NULL)"
            )
            # Older databases have no benefit column
            columns = [row[1] for row in db.execute("PRAGMA table_info(drops)")]
            if "benefit" not in columns:
                db.execute("ALTER TABLE drops ADD COLUMN benefit TEXT")
            db.execute(
                "CREATE TABLE IF NOT EXISTS game_notices ("
                "game TEXT PRIMARY KEY, notified_at REAL NOT NULL)"
            )

    def __connect(self):
        return sqlite3.connect(self.path, timeout=10)

    def was_attempted(self, drop_id):
        with closing(self.__connect()) as db:
            return (
                db.execute(
                    "SELECT 1 FROM drops WHERE drop_id = ?", (drop_id,)
                ).fetchone()
                is not None
            )

    def was_claimed(self, drop_id):
        with closing(self.__connect()) as db:
            row = db.execute(
                "SELECT claimed FROM drops WHERE drop_id = ?", (drop_id,)
            ).fetchone()
            return row is not None and row[0] == 1

    def record_attempt(self, drop_id, name, game, claimed, benefit=None):
        with closing(self.__connect()) as db, db:
            db.execute(
                "INSERT OR REPLACE INTO drops "
                "(drop_id, name, game, claimed, attempted_at, benefit) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (drop_id, name, game, int(claimed), time.time(), benefit),
            )

    def recent(self, limit=200):
        """Newest first: [{name, benefit, game, claimed, at}], `at` in milliseconds."""
        with closing(self.__connect()) as db:
            rows = db.execute(
                "SELECT name, benefit, game, claimed, attempted_at FROM drops "
                "ORDER BY attempted_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [
            {
                "name": name,
                "benefit": benefit,
                "game": game,
                "claimed": bool(claimed),
                "at": int(at * 1000),
            }
            for name, benefit, game, claimed, at in rows
        ]

    def should_notify_game(self, game):
        """True (and the notice is recorded) when this game was not warned about in the last day."""
        now = time.time()
        with closing(self.__connect()) as db, db:
            row = db.execute(
                "SELECT notified_at FROM game_notices WHERE game = ?", (game,)
            ).fetchone()
            if row is not None and now - row[0] < NOTICE_INTERVAL:
                return False
            db.execute(
                "INSERT OR REPLACE INTO game_notices VALUES (?, ?)", (game, now)
            )
            return True
