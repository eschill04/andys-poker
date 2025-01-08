import random 
from collections import Counter
from hand_evaluator import PokerHandEvaluator
from card import Card

# Constants
SUITS = ["hearts", "diamonds", "clubs", "spades"]
RANKS = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]


class Game:
    def __init__(self, game_id=0):
        self.gid = game_id
        self.players = []
        self.hands = {}
        self.bets = {}
        self.scores = {}
        self.started = False
        self.deck = Deck()
        self.deck.shuffle()
        self.rounds = 0
        self.rounds_left = 0
        self.hand_evaluator = PokerHandEvaluator()

    def add_player(self, username):
        self.players.append(username)
        self.hands[username] = []
        self.bets[username] = (0, "none")
        self.scores[username] = 0

    def remove_player(self, username):
        self.players.remove(username)
        self.hands.pop(username)
        self.bets.pop(username)
        self.scores.pop(username)
    
    def can_start(self):
        return len(self.players) >= 2
    
    def start(self):
        self.started = True
    
    def set_rounds(self, rounds):
        self.rounds = int(rounds)
        self.rounds_left = int(rounds)
    
    # For now, just deal 5 cards to each player. Later, maybe per player function? 
    def deal_cards(self, username):
        self.hands[username] = self.deck.deal(5)
        self.hands[username].sort(key=lambda card: card.rank)
        return [[card.card_string, card.wild] for card in self.hands[username]]
        
    
    def replace_wild(self, username, new, old):
        # search for first card in hand with card_string old and REPLACE with new (same order)
        new_rank, new_suit = new.split(" ")[0], new.split(" ")[2]
        if new_rank == "Jack":
            new_rank = 11
        elif new_rank == "Queen":
            new_rank = 12
        elif new_rank == "King":
            new_rank = 13
        elif new_rank == "Ace":
            new_rank = 14
        new = Card(new_suit, int(new_rank))
        new.wild = True
        
        found = False
        for i in range(len(self.hands[username])):
            if self.hands[username][i].card_string == old and not found and self.hands[username][i].wild:
                self.hands[username][i] = new
                found = True
        
        return [[card.card_string, card.wild] for card in self.hands[username]]

    def make_bet(self, username, bet, direction):
        self.bets[username] = (bet, direction)

    def all_bets_in(self):
        return all([bet[0] != 0 for bet in self.bets.values()])
    
    def update_scores(self):
        high_bets = [username for username, bet in self.bets.items() if bet[1] == "high"]
        low_bets = [username for username, bet in self.bets.items() if bet[1] == "low"]

        # TODO: THIS SECTION WILL BE REPLACED BY CODE TO ACTUALLY DETERMINE THE WINNERS
        winners = []
        if len(high_bets) > 0:
            winner_hands = [self.hands[username].copy() for username in high_bets]
            winner_indices = self.hand_evaluator.return_winners(winner_hands, True)
            winners += [high_bets[i] for i in winner_indices]
        if len(low_bets) > 0:
            winner_hands = [self.hands[username].copy() for username in low_bets]
            winner_indices = self.hand_evaluator.return_winners(winner_hands, False)
            winners += [low_bets[i] for i in winner_indices]

        score_change = {}
        hands = {username: [[card.card_string, card.wild] for card in self.hands[username]] for username in self.hands.keys()}
        for username in self.players:
            
            bet = int(self.bets[username][0])
            if username in winners:
                self.scores[username] += bet
                score_change[username] = bet
            else:
                self.scores[username] -= bet
                score_change[username] = -bet

            self.bets[username] = (0, "none")
            self.hands[username] = []
        self.rounds_left -= 1

        # sort high and low bets by user score
        high_bets.sort(key=lambda username: self.scores[username], reverse=True)
        low_bets.sort(key=lambda username: self.scores[username], reverse=True)
        bets = {"high": high_bets, "low": low_bets}

        # TODO: THIS SECTION WILL ALSO RETURN HOW MUCH EACH PLAYER GAINED/LOST THIS ROUND
        self.deck.reset()
        self.deck.shuffle()
        return {'scores': self.scores, 
                'hands': hands, 
                'bets': bets,
                'score_change': score_change}
        
    def get_state(self):
        return {'players': self.players, 'hands': list(self.hands.values()), 'bets': list(self.bets.values()), 'scores': list(self.scores.values())}
    
    def distribute_money(self):
        # Top n-1 players get money from the last n+1 player
        num_winners = (len(self.players)//2) + (len(self.players) % 2)

        # Sort players by score
        self.players.sort(key=lambda username: self.scores[username], reverse=True)
        winners = self.players[:num_winners]
        losers = self.players[num_winners:]

        # Distribute money: total winnings is top score minus lowest score
        total_winnings = self.scores[winners[0]] - self.scores[losers[-1]]

        # Calculate how much each winner is owed
        winners_owed = {}
        total = 0.0
        for winner in winners:
            diff = self.scores[winner] - self.scores[losers[-1]]
            total += diff
            winners_owed[winner] = diff
        winners_owed = {winner: "{:.2f}".format(round((owed/total)*total_winnings, 2)) for winner, owed in winners_owed.items()}

        # Calculate how much each loser owes
        lowers_owe = {}
        total = 0.0
        for loser in losers:
            diff = self.scores[winners[0]] - self.scores[loser]
            total += diff
            lowers_owe[loser] = diff

        lowers_owe = {loser: "{:.2f}".format(round((owe/total)*total_winnings, 2)) for loser, owe in lowers_owe.items()}

        # return dictionary of owes/owed concatenated
        return {"win": winners_owed, "lose": lowers_owe}
        
    
    def reset_game(self):
        self.deck.reset()
        self.deck.shuffle()
        self.started = False
        self.rounds = 0
        self.rounds_left = 0
        self.players = []
        self.hands = {}
        self.bets = {}
        self.scores = {}


# Deck representation
class Deck:
    def __init__(self):
        self.cards = [Card(suit, rank) for suit in SUITS for rank in RANKS]

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self, num_cards):
        return [self.cards.pop() for _ in range(num_cards)]
    
    def reset(self):
        self.cards = [Card(suit, rank) for suit in SUITS for rank in RANKS]