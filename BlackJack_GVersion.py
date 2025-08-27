import pygame
import random
import itertools

#Initialize pygame
pygame.init()

#Window
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("BlackJack")

#Fond
font = pygame.font.SysFont("Arial", 20)

#Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 155, 0)
GRAY = (128, 128, 128)

#Create deck with suits and values
suits = ["hearts", "diamonds", "clubs", "spades"]
values = ["A", "K", "Q", "J"] + [str(n) for n in range(10, 1, -1)]
deck = [f"{v}_of_{s}" for v, s in itertools.product(values, suits)]#Returns all possible combinations to match with names of images
random.shuffle(deck)

#Class for buttons
class Button:
    def __init__(self, text, x, y, visible=True, padding_x=20, padding_y=10, font_size=24):
        self.text = text
        self.x = x
        self.y = y
        self.visible = visible
        self.font = pygame.font.SysFont("Arial", font_size)

        #Colors and hover color
        self.bg_color = WHITE
        self.hover_color = GRAY
        self.text_color = BLACK

        #Adjust size
        text_surface = self.font.render(self.text, True, self.text_color)
        self.width = text_surface.get_width() + padding_x * 2
        self.height = text_surface.get_height() + padding_y * 2
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self):
        if self.visible:
            mouse_pos = pygame.mouse.get_pos()
            if self.rect.collidepoint(mouse_pos):
                color = self.hover_color
            else:
                color = self.bg_color

            #Draw rect
            pygame.draw.rect(screen, color, self.rect, border_radius=8)
            pygame.draw.rect(screen, BLACK, self.rect, 2, border_radius=8)

            #Center text
            text_surface = self.font.render(self.text, True, self.text_color)
            text_rect = text_surface.get_rect(center=self.rect.center)
            screen.blit(text_surface, text_rect)

    def is_clicked(self, event):
        if self.visible and event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False



#Function to get values of cards
def calculate_score(hand):
    score = 0
    aces = 0
    for card in hand:
        value = card.split("_")[0]  # Ex: "A", "10", "K"
        if value in ["K", "Q", "J"]:
            score += 10
        elif value == "A":
            score += 11
            aces += 1
        else:
            score += int(value)

    # Adjust A to 1 or 11 depending on value
    while score > 21 and aces:
        score -= 10
        aces -= 1

    return score

# Deal a card
def deal_card(deck):
    return deck.pop()

# Draw a card on Window
def draw_card(card_name, x, y, hide=False):
    if hide:
        filename = "back.png"  #hidden card for player
    else:
        filename = f"{card_name}.png"  #Example: 9_of_spades.png

    img = pygame.image.load(f"assets/cards/{filename}")
    img = pygame.transform.scale(img, (100, 140))
    pygame.draw.rect(screen, WHITE, (x, y, 100, 140))#Draw a rectangle behind card
    screen.blit(img, (x, y))# Combine in the screen image with rectangle

# Main game
def game():
    global deck
    running = True
    player_turn = True
    game_over = False
    message = ""

    # Starting hands
    player_hand = [deal_card(deck), deal_card(deck)]
    dealer_hand = [deal_card(deck), deal_card(deck)]

    #Create instance of Button class
    hit_button = Button("Hit", 100, 500, True)
    stay_button = Button("Stay", 200, 500, True)
    new_game_button = Button("NewGame", 600, 25, False)

    #Loop for game
    while running:
        screen.fill(GREEN)

        #Draw buttons
        hit_button.draw()
        stay_button.draw()
        if game_over:
            new_game_button.visible = True
            new_game_button.draw()
        else:
            new_game_button.visible = False

        CARD_WIDTH, CARD_HEIGHT, SPACING = 100, 130, 20

        # Draw player's cards
        for i, card in enumerate(player_hand):
            x = WIDTH - (len(player_hand) - i) * (CARD_WIDTH + SPACING)
            draw_card(card, x, 400)

        # Draw dealer's cards
        for i, card in enumerate(dealer_hand):
            hide = (i == 0 and player_turn)  # First hided cart while player plays
            draw_card(card, 50 + i * 120, 100, hide=hide)

        # Show scores
        player_score = calculate_score(player_hand)
        dealer_score = calculate_score(dealer_hand)

        player_text = font.render(f"Player: {player_score}", True, BLACK)
        screen.blit(player_text, (50, 350))

        if not player_turn:
            dealer_text = font.render(f"Dealer: {dealer_score}", True, BLACK)
            screen.blit(dealer_text, (50, 250))

        # Show final message
        if game_over:
            msg_text = font.render(message, True, BLACK)
            screen.blit(msg_text, (400, 300))

        pygame.display.flip()

        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            #Hit Button event
            if hit_button.is_clicked(event) and not game_over and player_turn:
                player_hand.append(deal_card(deck))
                player_score = calculate_score(player_hand)
                if player_score > 21:
                    message = "Player busts, Dealer wins."
                    game_over = True
                    player_turn = False


            #Stay button event
            if stay_button.is_clicked(event) and not game_over and player_turn:
                player_turn = False

                #Dealer's turn
                while calculate_score(dealer_hand) < 17:
                    dealer_hand.append(deal_card(deck))

                #calculate scores
                dealer_score = calculate_score(dealer_hand)
                player_score = calculate_score(player_hand)

                if dealer_score > 21:
                    message = "Dealer busts, Player wins."
                elif dealer_score > player_score:
                    message = "Dealer wins."
                elif dealer_score < player_score:
                    message = "Player wins."
                else:
                    message = "It's a tie!"
                game_over = True

            if new_game_button.is_clicked(event) and game_over:
                game()


            if event.type == pygame.KEYDOWN and not game_over:
                #Hit (space)
                if player_turn and event.key == pygame.K_SPACE:
                    player_hand.append(deal_card(deck))
                    player_score = calculate_score(player_hand)
                    if player_score > 21:
                        message = "Player busts, Dealer wins."
                        game_over = True
                        player_turn = False

                #Stand (Enter)
                elif player_turn and event.key == pygame.K_RETURN:
                    player_turn = False

                    # Dealer Plays
                    while calculate_score(dealer_hand) < 17:
                        dealer_hand.append(deal_card(deck))

                    dealer_score = calculate_score(dealer_hand)
                    player_score = calculate_score(player_hand)

                    if dealer_score > 21:
                        message = "Dealer busts, Player wins."
                    elif dealer_score > player_score:
                        message = "Dealer wins."
                    elif dealer_score < player_score:
                        message = "Player wins."
                    else:
                        message = "It's a tie!"
                    game_over = True

    pygame.quit()

#Start game
game()

