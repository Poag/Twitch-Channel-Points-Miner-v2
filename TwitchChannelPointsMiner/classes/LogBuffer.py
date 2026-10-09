import logging
from collections import deque
from threading import Lock

import emoji

# How many lines the analytics Log panel can show
MAX_LINES = 2000


class LogBuffer(logging.Handler):
    """Keeps the most recent log lines in memory for the analytics Log panel.

    Lines get an increasing sequence number so the page can ask for "everything after N".
    Being in memory it needs no log file, and it only holds the current session.
    """

    def __init__(self, max_lines=MAX_LINES):
        super().__init__()
        self.lock_buffer = Lock()
        self.lines = deque(maxlen=max_lines)
        self.seq = 0

    def emit(self, record):
        try:
            text = self.format(record)
            if getattr(record, "emoji", None) and getattr(self, "use_emoji", True):
                text = text.replace(
                    record.getMessage(),
                    emoji.emojize(f"{record.emoji}  ", language="alias")
                    + record.getMessage(),
                    1,
                )
        except Exception:
            self.handleError(record)
            return
        with self.lock_buffer:
            self.seq += 1
            self.lines.append((self.seq, text))

    def since(self, seq, tail=300):
        """Returns (new_seq, [lines]). seq < 0 means "the last `tail` lines".
        Also returns reset=True when the client's seq is ahead of ours (the miner restarted)."""
        with self.lock_buffer:
            current = self.seq
            reset = seq > current
            if seq < 0 or reset:
                wanted = list(self.lines)[-tail:]
            else:
                wanted = [item for item in self.lines if item[0] > seq]
        return current, [text for _, text in wanted], reset


# One buffer per process, shared by the logger setup and the analytics server
LOG_BUFFER = LogBuffer()
