from card import Card
from collections import Counter

class PokerHandEvaluator:
    def __init__(self):
        self.hand_rankings = {
            "straight_flush": 10,
            "five_of_a_kind": 9,
            "four_of_a_kind": 8,
            "full_house": 7,
            "flush": 6,
            "straight": 5,
            "three_of_a_kind": 4,
            "two_pair": 3,
            "one_pair": 2,
            "high_card": 1
        }

    def is_flush(self, hand):
        # hand is a list of five Card objects
        # hand = [Card("hearts", 2), Card("hearts", 3), Card("hearts", 4), ...]
        # returns True if hand is a flush, False otherwise
        return len(set([card.suit for card in hand])) == 1
    
    def is_straight(self, hand):
        # hand is a list of five Card objects
        # hand = [Card("hearts", 2), Card("hearts", 3), Card("hearts", 4), ...]
        # returns True if hand is a straight, False otherwise
        ranks = [card.rank for card in hand]
        ranks.sort()
        if ranks == [2, 3, 4, 5, 14]:
            return True
        for i in range(len(ranks) - 1):
            if ranks[i + 1] - ranks[i] != 1:
                return False
        return True
    
    def is_straight_flush(self, hand):
        # hand is a list of five Card objects
        # hand = [Card("hearts", 2), Card("hearts", 3), Card("hearts", 4), ...]
        # returns True if hand is a straight flush, False otherwise
        return self.is_straight(hand) and self.is_flush(hand)

    def evaluate_hand(self, hand):
        # hand is a list of five Card objects
        # hand = [Card("hearts", 2), Card("hearts", 3), Card("hearts", 4), ...]
        # returns a tuple (hand_ranking, hand_ranking_value)

        # Check for straight flush
        if self.is_straight_flush(hand):
            return ("straight_flush")
        # Check for four of a kind
        card_counts = Counter([card.rank for card in hand])
        if 5 in card_counts.values():
            return ("five_of_a_kind")
        if 4 in card_counts.values():
            return ("four_of_a_kind")
        # Check for full house
        if 3 in card_counts.values() and 2 in card_counts.values():
            return ("full_house")
        # Check for flush
        if self.is_flush(hand):
            return ("flush")
        # Check for straight
        if self.is_straight(hand):
            return ("straight")
        # Check for three of a kind
        if 3 in card_counts.values():
            return ("three_of_a_kind")
        # Check for two pair
        if list(card_counts.values()).count(2) == 2:
            return ("two_pair")
        # Check for one pair
        if 2 in card_counts.values():
            return ("one_pair")
        # High card
        return ("high_card")
    
    def break_ties(self, hands, high):
        my_hands = hands.copy()
        # hands is a list of lists of Card objects with the same hand_ranking
        # hands = [[Card("hearts", 2), Card("hearts", 3), Card("hearts", 4), ...], [Card("hearts", 2), Card("hearts", 3), Card("hearts", 4), ...], ...]
        # returns index of winning hand
        hand_ranking = self.evaluate_hand(my_hands[0])
        if hand_ranking == "straight_flush" or hand_ranking == "straight" or hand_ranking == "five_of_a_kind":
            # Straight flush or straight: highest card wins
            # if same highest card, tie

            high_cards = [max([card.rank for card in my_hands[i]]) for i in range(len(my_hands))]

            if high:
                best_high = max(high_cards)
            else:
                best_high = min(high_cards)
            return [i for i in range(len(high_cards)) if high_cards[i] == best_high]
        
        if hand_ranking == "flush" or hand_ranking == "high_card":
            # Flush or high card: highest card wins (if tie, second highest card wins, etc.)
            my_hands = {i: hand for i, hand in enumerate(my_hands)}
            while len(my_hands) > 1:
                if len(list(my_hands.values())[0]) == 0:
                    return list(my_hands.keys())
                # Get highest cards
                high_cards = {i: max([card.rank for card in hand]) for i, hand in my_hands.items()}
                # Get highest card
                if high:
                    best_high = max(high_cards.values())
                else:
                    best_high = min(high_cards.values())
                # Remove all non-winners
                # hands = [i: hand for hand in hands if max([card.rank for card in hand]) == best_high]
                
                for i in range(len(high_cards)):
                    if high_cards[i] != best_high:
                        my_hands.pop(i)
                    else:
                        for card in my_hands[i]:
                            if card.rank == best_high:
                                my_hands[i].remove(card)
                                break

            # Return the winner
            return list(my_hands.keys()) 
                    
                
        

        if hand_ranking in ["four_of_a_kind", "full_house", "three_of_a_kind", "two_pair", "one_pair"]:
            # Four of a kind: highest card wins

            # {5: 3, 3: 2}
            # {5: 3, 8: 2}
            # {4: 3, 10: 2}
            
            card_counts = {i: Counter([card.rank for card in hand]) for i, hand in enumerate(hands)}

            while len(card_counts) > 1:
                # If all hands are the same, return tie
                if len(list(card_counts.values())[0]) == 0:
                    return list(card_counts.keys())

                high_cards = {i: card_count.most_common(1)[0][0] for i, card_count in card_counts.items()}

                # [5, 5, 4]: remove the 4
                #     remove high_cards from hands
                # Remove all non-winners:
                if high:
                    best_high = max(high_cards.values())
                else:
                    best_high = min(high_cards.values())
                for i in range(len(high_cards)):
                    if high_cards[i] != best_high:
                        card_counts.pop(i)
                    else:
                        card_counts[i].pop(best_high)


            # Return the winner
            return list(card_counts.keys())
        
        
    def return_winners(self, hands, high):

        rankings = {i: self.hand_rankings[self.evaluate_hand(hand)] for i, hand in enumerate(hands)}
        if high:
            highest_ranking = max(rankings.values())
        else:
            highest_ranking = min(rankings.values())

        # If there is a tie, break the tie
        if list(rankings.values()).count(highest_ranking) > 1:
            # Break the tie
            winners = self.break_ties([hand for i, hand in enumerate(hands) if rankings[i] == highest_ranking], high)
            return [i for i in rankings.keys() if rankings[i] == highest_ranking and i in winners]
        else:
            return [i for i in rankings.keys() if rankings[i] == highest_ranking]

        