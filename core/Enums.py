from enum import Enum, IntEnum


class CardStatus(Enum):
    """
    Status of a flashcard within spaced repetition:
    - NEW:         card never reviewed
    - LEARNING:    in initial learning phase
    - REVIEW:      in ongoing review phase
    """
    NEW = "new"
    LEARNING = "learning"
    REVIEW = "review"

class Rating(IntEnum):
    """
    User performance rating for scheduling reviews.
    Numeric values correspond to SM-2 grades: 0 (AGAIN), 2 (HARD), 4 (GOOD), 5 (EASY).
    """
    AGAIN = 0
    HARD = 2
    GOOD = 4
    EASY = 5