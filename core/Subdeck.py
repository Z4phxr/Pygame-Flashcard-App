from typing import Optional, Union
import datetime
import heapq
from core.Enums import CardStatus, Rating
from core.Deck import Deck
from core.Scheduler import Scheduler
from core.Card import Card


class Subdeck(Deck):
    """
    A temporary subset of a deck (or decks) for learning purposes.
    Pulls a limited number of cards from a source deck or container,
    supports modifying card states and syncing changes back.
    """

    def __init__(self, source: Union[Deck, object], limit: int = 20) -> None:
        self.limit = limit
        self.original_deck = source
        self.scheduler = Scheduler()
        self.modified_cards = set()

        if isinstance(source, Deck):
            super().__init__(name=source.name, path=source.file_path)
        else:
            super().__init__(name="Subdeck", path="")

        self.cards = self._generate_cards(source)
        self.current_card: Optional[Card] = self.get_next_card()

    def _generate_cards(self, source: Union[Deck, object]) -> list[tuple[datetime.datetime, int, Card]]:
        """
        Extract a limited number of due and new cards from the source.
        """
        today = datetime.date.today()
        review_cards = []
        new_cards = []

        def process(card_heap: list[tuple[datetime.datetime, int, Card]]) -> None:
            for sd, _, card in sorted(card_heap):
                if card.status in {CardStatus.REVIEW, CardStatus.LEARNING}:
                    if card.scheduled_date and card.scheduled_date.date() <= today:
                        review_cards.append(card)
                elif card.status == CardStatus.NEW:
                    new_cards.append(card)
                if len(review_cards) + len(new_cards) >= self.limit:
                    break

        if isinstance(source, Deck):
            process(source.cards)
        elif hasattr(source, "decks"):
            for deck in source.decks:
                process(deck.cards)
        else:
            raise TypeError(f"Expected Deck or DeckContainer, got {type(source)}")

        selected = (review_cards + new_cards)[:self.limit]
        return [(card.scheduled_date, id(card), card) for card in selected]

    def has_cards(self) -> bool:
        return bool(self.cards)

    def get_next_card(self) -> Optional[Card]:
        if self.cards:
            _, _, card = self.cards[0]
            self.current_card = card
            return card
        return None

    def pop_current_card(self) -> Optional[Card]:
        if self.cards:
            _, _, card = heapq.heappop(self.cards)
            self.current_card = None
            return card
        return None

    def again_insert(self) -> None:
        if self.current_card:
            card = self.pop_current_card()
            heapq.heappush(self.cards, (card.scheduled_date, id(card), card))

    def modify_card(self, rating: Rating) -> None:
        """
        Update the current card using the spaced repetition scheduler,
        and update its position or remove it depending on rating.
        """
        if not self.current_card:
            return

        card = self.current_card
        self.scheduler.update_card(card, rating)
        self.modified_cards.add(card)

        if rating == Rating.AGAIN:
            self.again_insert()
        elif rating == Rating.EASY:
            self.pop_current_card()
        elif card.status == CardStatus.LEARNING:
            self.pop_current_card()
            heapq.heappush(self.cards, (card.scheduled_date, id(card), card))
        elif card.status == CardStatus.REVIEW:
            self.pop_current_card()

        self._update_original_card(card)
        self.current_card = self.get_next_card()

    def _update_original_card(self, updated_card: Card) -> None:
        """
        Update the card's data in the original deck or decks.
        """
        decks = []
        if isinstance(self.original_deck, Deck):
            decks = [self.original_deck]
        elif hasattr(self.original_deck, "decks"):
            decks = self.original_deck.decks

        for deck in decks:
            for i, (_, _, c) in enumerate(deck.cards):
                if c is updated_card:
                    deck.cards[i] = (updated_card.scheduled_date, id(updated_card), updated_card)
                    heapq.heapify(deck.cards)
                    break

    def save_deck(self) -> None:
        """
        Save only the decks that were modified.
        """
        if isinstance(self.original_deck, Deck):
            self.original_deck.save_deck()
        elif hasattr(self.original_deck, "decks"):
            affected = set()
            for card in self.modified_cards:
                for deck in self.original_deck.decks:
                    if any(c is card for _, _, c in deck.cards):
                        affected.add(deck)
            for deck in affected:
                deck.save_deck()

        self.modified_cards.clear()

    def get_stats(self) -> dict[CardStatus, int]:
        """
        Return counts of card statuses in the subdeck.
        """
        counts = {status: 0 for status in CardStatus}
        for _, _, card in self.cards:
            counts[card.status] += 1
        return counts
