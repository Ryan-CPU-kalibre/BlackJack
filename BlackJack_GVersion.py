import pygame
import random
import itertools

# Game logic

#Card class
class Card:
    def __init__(self, value, suit):
        self.value = value
        self.suit = suit

    def __str__(self):
        return f"{self.value}_of_{self.suit}"

#Deck class
class Deck:
    def __init__(self):
        suits = ["hearts", "diamonds", "clubs", "spades"]
        values = ["A", "K", "Q", "J"] + [str(n) for n in range(10, 1, -1)]
        self.cards = [Card(v, s) for v, s in itertools.product(values, suits)] #Create all combinations
        random.shuffle(self.cards) #Shuffle deck

    def deal(self): #Deal one card
        return self.cards.pop()

#Hand class
class Hand:
    def __init__(self):
        self.cards = []

    def add_card(self, card): #Add card
        self.cards.append(card)

    def score(self): #Calculate score
        score, aces = 0, 0
        for card in self.cards:
            if card.value in ["K", "Q", "J"]:
                score += 10
            elif card.value == "A":
                score += 11
                aces += 1
            else:
                score += int(card.value)

        #Adjust Aces if needed
        while score > 21 and aces:
            score -= 10
            aces -= 1
        return score


#Blackjack game class
class BlackjackGame:
    def __init__(self):
        self.deck = Deck()
        self.player = Hand()
        self.dealer = Hand()
        self.over = False
        self.message = ""

        #Initial deal
        self.player.add_card(self.deck.deal())
        self.player.add_card(self.deck.deal())
        self.dealer.add_card(self.deck.deal())
        self.dealer.add_card(self.deck.deal())

    def player_hit(self): #Player takes a card
        if not self.over:
            self.player.add_card(self.deck.deal())
            if self.player.score() > 21:
                self.message = "Player busts, Dealer wins."
                self.over = True

    def player_stay(self): #Player stays
        if not self.over:
            while self.dealer.score() < 17:
                self.dealer.add_card(self.deck.deal())
            self.check_winner()

    def check_winner(self): #Check who wins
        if self.dealer.score() > 21:
            self.message = "Dealer busts, Player wins."
        elif self.dealer.score() > self.player.score():
            self.message = "Dealer wins."
        elif self.dealer.score() < self.player.score():
            self.message = "Player wins."
        else:
            self.message = "It's a tie!"
        self.over = True

# Pygame UI
pygame.init()

#Window
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("BlackJack")

#Font
font = pygame.font.SysFont("Arial", 20)

#Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 155, 0)
GRAY = (128, 128, 128)


#Button class
class Button:
    def __init__(self, text, x, y, visible=True, padding_x=20, padding_y=10, font_size=24):
        self.text = text
        self.x = x
        self.y = y
        self.visible = visible
        self.font = pygame.font.SysFont("Arial", font_size)

        self.bg_color = WHITE
        self.hover_color = GRAY
        self.text_color = BLACK

        #Size
        text_surface = self.font.render(self.text, True, self.text_color)
        self.width = text_surface.get_width() + padding_x * 2
        self.height = text_surface.get_height() + padding_y * 2
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self): #Draw button
        if self.visible:
            mouse_pos = pygame.mouse.get_pos()
            color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.bg_color
            pygame.draw.rect(screen, color, self.rect, border_radius=8)
            pygame.draw.rect(screen, BLACK, self.rect, 2, border_radius=8)

            text_surface = self.font.render(self.text, True, self.text_color)
            text_rect = text_surface.get_rect(center=self.rect.center)
            screen.blit(text_surface, text_rect)

    def is_clicked(self, event): #Detect click
        return (
            self.visible and event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)
        )


#Blackjack UI class
class BlackjackUI:
    def __init__(self):
        self.game = BlackjackGame()
        self.running = True

        #Buttons
        self.hit_button = Button("Hit", 100, 500, True)
        self.stay_button = Button("Stay", 220, 500, True)
        self.new_game_button = Button("New Game", 600, 25, False)

    def draw_card(self, card, x, y, hide=False): #Draw card
        filename = "back.png" if hide else f"{card}.png"
        img = pygame.image.load(f"assets/cards/{filename}")
        img = pygame.transform.scale(img, (100, 140))
        pygame.draw.rect(screen, WHITE, (x, y, 100, 140))
        screen.blit(img, (x, y))

    def render(self): #Render game screen
        screen.fill(GREEN)

        #Buttons
        self.hit_button.draw()
        self.stay_button.draw()
        if self.game.over:
            self.new_game_button.visible = True
            self.new_game_button.draw()
        else:
            self.new_game_button.visible = False

        #Player cards
        for i, card in enumerate(self.game.player.cards):
            x = WIDTH - (len(self.game.player.cards) - i) * 120
            self.draw_card(card, x, 400)

        #Dealer cards
        for i, card in enumerate(self.game.dealer.cards):
            hide = (i == 0 and not self.game.over) #Hide first card if game not over
            self.draw_card(card, 50 + i * 120, 100, hide=hide)

        #Scores
        player_text = font.render(f"Player: {self.game.player.score()}", True, BLACK)
        screen.blit(player_text, (50, 350))

        if self.game.over:
            dealer_text = font.render(f"Dealer: {self.game.dealer.score()}", True, BLACK)
            screen.blit(dealer_text, (50, 250))

            msg_text = font.render(self.game.message, True, BLACK)
            screen.blit(msg_text, (400, 300))

        pygame.display.flip()

    def handle_event(self, event): #Handle events
        if self.hit_button.is_clicked(event) and not self.game.over:
            self.game.player_hit()

        if self.stay_button.is_clicked(event) and not self.game.over:
            self.game.player_stay()

        if self.new_game_button.is_clicked(event) and self.game.over:
            self.game = BlackjackGame()



# Main loop
def main():
    ui = BlackjackUI()
    clock = pygame.time.Clock()

    while ui.running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                ui.running = False
            ui.handle_event(event)

        ui.render()
        clock.tick(30)

    pygame.quit()


if __name__ == "__main__":
    main()
