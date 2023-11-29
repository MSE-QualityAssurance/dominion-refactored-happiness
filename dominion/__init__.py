import random


class Card:
    def __init__(self, name, cost, card_type):
        self.name = name
        self.cost = cost
        self.card_type = card_type  # e.g., 'Treasure', 'Victory', 'Action'

    def play(self, player, game):
        """
        Define the effect when the card is played.
        To be overridden in subclasses for specific cards.
        """
        pass

    def __str__(self):
        return f"{self.name} (Cost: {self.cost}, Type: {self.card_type})"


# Example subclass for a specific type of card
class TreasureCard(Card):
    def __init__(self, name, cost, value):
        super().__init__(name, cost, "Treasure")
        self.value = value  # The value in coins

    def play(self, player, game):
        player.money += self.value


class Player:
    def __init__(self, name):
        self.name = name
        self.deck = []  # Player's deck
        self.hand = []  # Player's hand
        self.discard_pile = []  # Discard pile
        self.actions = 1  # Actions available per turn
        self.buys = 1  # Buys available per turn
        self.money = 0  # Money available to spend

    def draw_card(self, num=1):
        for _ in range(num):
            if not self.deck:
                self.shuffle_discard_into_deck()
            if self.deck:  # Check again in case deck and discard were both empty
                self.hand.append(self.deck.pop())

    def shuffle_discard_into_deck(self):
        self.deck = random.sample(self.discard_pile, len(self.discard_pile))
        self.discard_pile.clear()

    def play_card(self, card):
        if card in self.hand:
            card.play(self)  # Assuming card.play() modifies player state
            self.hand.remove(card)
            self.discard_pile.append(card)

    def buy_card(self, card, supply):
        if self.buys > 0 and self.money >= card.cost and supply.is_card_available(card):
            self.money -= card.cost
            self.buys -= 1
            self.discard_pile.append(supply.remove_card(card))

    def end_turn(self):
        self.discard_pile.extend(self.hand)
        self.hand.clear()
        self.draw_card(5)  # Draw new hand for next turn
        self.actions = 1  # Reset actions and buys for next turn
        self.buys = 1
        self.money = 0

    def __str__(self):
        return f"Player: {self.name}"


class Game:
    def __init__(self, players, supply_piles):
        self.players = players  # List of Player objects
        self.supply_piles = supply_piles  # Dictionary of Card: count
        self.current_player_index = 0  # Index of the current player

    def setup_game(self):
        # Initialize game: shuffle decks, draw initial hands, etc.

        # Shuffle decks
        random.shuffle(self.supply_piles)

        for player in self.players:
            player.draw_card(5)

    def next_player(self):
        # Move to the next player
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        return self.players[self.current_player_index]

    def is_game_over(self):
        # Check game end conditions (e.g., Province cards depleted)
        province_depleted = self.supply_piles.get("Province", 0) == 0
        empty_piles = sum(1 for count in self.supply_piles.values() if count == 0)
        return province_depleted or empty_piles >= 3

    def play_game(self):
        # Main game loop
        self.setup_game()
        while not self.is_game_over():
            current_player = self.players[self.current_player_index]
            self.play_turn(current_player)
            if self.is_game_over():
                break
            self.next_player()
        self.declare_winner()

    def play_turn(self, player):
        print(f"{player.name}'s turn:")

        # Action Phase
        self.action_phase(player)

        # Buy Phase
        self.buy_phase(player)

        # Cleanup Phase
        self.cleanup_phase(player)

    def action_phase(self, player):
        # Player can play action cards (if available)
        while player.actions > 0:
            action_card = (
                player.choose_action_card()
            )  # Player chooses an action card to play
            if action_card:
                player.play_card(action_card)
                player.actions -= 1
            else:
                break  # Player chooses to end action phase

    def buy_phase(self, player):
        # Player can play treasure cards and buy cards
        player.play_all_treasure()  # Player plays all treasure cards from hand
        while player.buys > 0:
            card_to_buy = player.choose_buy()  # Player chooses a card to buy
            if card_to_buy and self.supply_piles[card_to_buy.name] > 0:
                player.buy_card(card_to_buy, self)
                self.supply_piles[card_to_buy.name] -= 1
            else:
                break  # No more buys or player chooses to end buy phase

    def cleanup_phase(self, player):
        # Cleanup and prepare for next turn
        player.end_turn()

    def declare_winner(self):
        # Determine and announce the winner
        highest_score = max(player.calculate_score() for player in self.players)
        winners = [p for p in self.players if p.calculate_score() == highest_score]
        if len(winners) > 1:
            print("It's a tie!")
        else:
            print(f"The winner is {winners[0].name}!")


def main():
    # Initialize players
    player_names = ["Alice", "Bob"]  # Extend this list based on the number of players
    players = [Player(name) for name in player_names]

    # Initialize supply piles (simplified example)
    supply_piles = {
        "Copper": 60,  # Adjust numbers based on the actual game rules
        "Silver": 40,
        "Gold": 30,
        "Estate": 24,
        "Duchy": 12,
        "Province": 12,
        # Add Kingdom cards and other cards as needed
    }

    # Create the game instance
    game = Game(players, supply_piles)

    # Start the game
    game.play_game()


if __name__ == "__main__":
    main()
