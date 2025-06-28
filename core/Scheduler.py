from datetime import datetime, timedelta
import random
from core.Enums import Rating, CardStatus

class Scheduler:
    """
    A spaced repetition scheduler inspired by Anki's algorithm.

    Supports transitioning cards between NEW, LEARNING, and REVIEW phases,
    based on user ratings (AGAIN, HARD, GOOD, EASY). It updates each card's
    interval, ease factor, repetition count, and next review date accordingly.
    """

    def __init__(self):
        # Learning step durations in minutes (e.g., 1 min, then 10 min)
        self.learning_steps = [1, 10]

        # Initial intervals in days
        self.graduating_interval = 1
        self.easy_interval = 4

        # Multipliers and constraints
        self.easy_bonus = 1.3
        self.hard_multiplier = 1.2
        self.minimum_ease_factor = 1.3

    def update_card(self, card, rating: Rating) -> None:
        """
        Update the card's scheduling data based on the given rating.

        Args:
            card: The flashcard object to update.
            rating (Rating): The user's feedback rating.
        """
        now = datetime.now()
        card.last_review = now
        card.history.append((now, rating))

        # -----------------------------
        # NEW → LEARNING or REVIEW
        # -----------------------------
        if card.status == CardStatus.NEW:
            if rating == Rating.EASY:
                card.status = CardStatus.REVIEW
                card.repetition = 1
                card.interval = self.easy_interval
                card.easiness = 2.65
                card.scheduled_date = self._anki_schedule_day(self._fuzz(card.interval))
            else:
                card.status = CardStatus.LEARNING
                card.learning_index = 0
                card.scheduled_date = self._minutes_from_now(self.learning_steps[0])
            return

        # -----------------------------
        # LEARNING
        # -----------------------------
        if card.status == CardStatus.LEARNING:
            if rating == Rating.AGAIN:
                card.learning_index = 0
                card.scheduled_date = self._minutes_from_now(self.learning_steps[0])
            elif rating == Rating.GOOD:
                card.learning_index += 1
                if card.learning_index >= len(self.learning_steps):
                    card.status = CardStatus.REVIEW
                    card.repetition = 1
                    card.interval = self.graduating_interval
                    card.easiness = 2.5
                    card.scheduled_date = self._anki_schedule_day(self._fuzz(card.interval))
                else:
                    card.scheduled_date = self._minutes_from_now(self.learning_steps[card.learning_index])
            elif rating == Rating.EASY:
                card.status = CardStatus.REVIEW
                card.repetition = 1
                card.interval = self.easy_interval
                card.easiness = 2.65
                card.scheduled_date = self._anki_schedule_day(self._fuzz(card.interval))
            return

        # -----------------------------
        # REVIEW
        # -----------------------------
        if card.status == CardStatus.REVIEW:
            if rating == Rating.AGAIN:
                card.status = CardStatus.LEARNING
                card.learning_index = 0
                card.repetition = 0
                card.interval = 0
                card.lapses += 1
                card.scheduled_date = self._minutes_from_now(self.learning_steps[0])
                return

            # Update ease factor (EF)
            q = rating.value  # 1–4
            ef = card.easiness
            ef = ef - 0.8 + 0.28 * q - 0.02 * q * q
            card.easiness = max(self.minimum_ease_factor, ef)

            card.repetition += 1

            # Calculate new interval
            if card.repetition == 1:
                card.interval = self.easy_interval if rating == Rating.EASY else self.graduating_interval
            else:
                if rating == Rating.HARD:
                    card.interval = max(1, int(card.interval * self.hard_multiplier))
                elif rating == Rating.GOOD:
                    card.interval = max(1, int(card.interval * card.easiness))
                elif rating == Rating.EASY:
                    card.interval = max(1, int(card.interval * card.easiness * self.easy_bonus))
                    card.easiness += 0.15

            fuzzed = self._fuzz(card.interval)
            card.scheduled_date = self._anki_schedule_day(fuzzed)


    def _minutes_from_now(self, minutes: int) -> datetime:
        """Returns a datetime object that is `minutes` from now."""
        return datetime.now() + timedelta(minutes=minutes)

    def _anki_schedule_day(self, interval_days: int) -> datetime:
        """Returns the scheduled day at 8:00 AM after `interval_days`."""
        today = datetime.now().date()
        due_day = today + timedelta(days=interval_days)
        return datetime.combine(due_day, datetime.min.time()).replace(hour=8)

    def _fuzz(self, interval: int) -> int:
        """
        Apply Anki-style fuzzing to the interval to avoid predictable patterns.
        """
        if interval <= 2:
            return interval
        fuzz_range = int(interval * 0.15)
        return interval + random.randint(-fuzz_range, fuzz_range)
