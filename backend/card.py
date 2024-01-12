# Card representation
class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
        self.card_string = str(rank) + suit
        self.wild = (rank == 2 or (rank == 11 and (suit == "hearts" or suit == "spades")))