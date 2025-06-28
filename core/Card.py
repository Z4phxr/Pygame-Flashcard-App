from datetime import datetime
from core.Enums import CardStatus
from functools import total_ordering

@total_ordering
class Card:
    """
    Represents a single flashcard used in spaced repetition learning (SM-2).
    Tracks learning stats, scheduling, and historical review data.
    """
    def __init__(self, f, b):
        self.front = f
        self.back = b
        self.create_date = datetime.today()

        self.status = CardStatus.NEW
        self.last_review = None
        self.interval = 0
        self.repetition = 0
        self.easiness = 2.5
        self.lapses = 0
        self.scheduled_date = None
        self.history = []

        self.learning_index = 0
        self.learning_steps = [1, 10]

    @property
    def graduated(self) -> bool:
        return self.status == CardStatus.REVIEW

    def __eq__(self, other):
        return self.scheduled_date == other.scheduled_date

    def __lt__(self, other):
        return self.scheduled_date < other.scheduled_date

    def __hash__(self):
        return hash((self.front, self.back))

    def __str__(self):
        return f"Front: {self.front}, Back: {self.back}"

    @staticmethod
    def from_dict(data: dict) -> 'Card':
        c = Card(data["front"], data["back"])
        c.create_date = datetime.fromisoformat(data.get("create_date")) if data.get("create_date") else datetime.today()
        c.last_review = datetime.fromisoformat(data.get("last_review")) if data.get("last_review") else None
        c.interval = data.get("interval", 0)
        c.repetition = data.get("repetition", 0)
        c.easiness = data.get("easiness", 2.5)
        c.lapses = data.get("lapses", 0)
        c.scheduled_date = datetime.fromisoformat(data.get("scheduled_date")) if data.get("scheduled_date") else datetime.max
        c.history = [
            (datetime.fromisoformat(dt), rating) for dt, rating in data.get("history", [])
        ]
        if data.get("status"):
            c.status = CardStatus(data.get("status"))
        return c

    def to_dict(self) -> dict:
        return {
            "front": self.front,
            "back": self.back,
            "create_date": self.create_date.isoformat(),
            "last_review": self.last_review.isoformat() if self.last_review else None,
            "interval": self.interval,
            "repetition": self.repetition,
            "easiness": self.easiness,
            "lapses": self.lapses,
            "scheduled_date": self.scheduled_date.isoformat() if self.scheduled_date else datetime.max,
            "history": [(dt.isoformat(), int(rating)) for dt, rating in self.history],
            "status": self.status.value,
        }
