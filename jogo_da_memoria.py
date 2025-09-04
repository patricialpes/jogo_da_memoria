import pygame
import random
import os

# Configurações
WIDTH, HEIGHT = 800, 600
FPS = 60
TITLE = "Jogo da Memória - Pirata"
BG_COLOR = (25, 28, 35)
CARD_BACK_COLOR = (50, 60, 80)
GRID_ROWS, GRID_COLS = 3, 4  # 3x4 = 12 cartas = 6 pares
CARD_SIZE = (120, 120)
MARGIN = 20

FLIP_BACK_EVENT = pygame.USEREVENT + 1


# Inicialização
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", 28)


# Carregar imagens
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")

IMAGES = [
    pygame.image.load(os.path.join(ASSETS_DIR, "dragao.png")),
    pygame.image.load(os.path.join(ASSETS_DIR, "ilha_tesouro.png")),
    pygame.image.load(os.path.join(ASSETS_DIR, "navio.png")),
    pygame.image.load(os.path.join(ASSETS_DIR, "pirata.png")),
    pygame.image.load(os.path.join(ASSETS_DIR, "tesouro.png")),
    pygame.image.load(os.path.join(ASSETS_DIR, "tubarao.png")),
]

IMAGES = [pygame.transform.scale(img, CARD_SIZE) for img in IMAGES]

# Carregar sons
som_acerto = pygame.mixer.Sound(os.path.join(ASSETS_DIR, "som_de_acerto.wav"))
som_vitoria = pygame.mixer.Sound(os.path.join(ASSETS_DIR, "som_de_vitoria.wav"))
som_jogo = pygame.mixer.Sound(os.path.join(ASSETS_DIR, "som_do_jogo.wav"))
som_gameover = pygame.mixer.Sound(os.path.join(ASSETS_DIR, "som_game_over.wav"))

# Classe Card
class Card:
    def __init__(self, x, y, image, identifier):
        self.rect = pygame.Rect(x, y, *CARD_SIZE)
        self.image = image
        self.identifier = identifier
        self.revealed = False
        self.matched = False

    def draw(self, surf):
        if self.revealed or self.matched:
            surf.blit(self.image, self.rect)
        else:
            pygame.draw.rect(surf, CARD_BACK_COLOR, self.rect, border_radius=8)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# Criar baralho
def create_deck():
    images = IMAGES.copy()
    random.shuffle(images)
    needed = (GRID_ROWS * GRID_COLS) // 2
    selected = images[:needed]
    deck_images = selected * 2
    random.shuffle(deck_images)

    deck = []
    start_x = (WIDTH - (GRID_COLS * CARD_SIZE[0] + (GRID_COLS - 1) * MARGIN)) // 2
    start_y = (HEIGHT - (GRID_ROWS * CARD_SIZE[1] + (GRID_ROWS - 1) * MARGIN)) // 2

    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            x = start_x + col * (CARD_SIZE[0] + MARGIN)
            y = start_y + row * (CARD_SIZE[1] + MARGIN)
            img = deck_images.pop()
            deck.append(Card(x, y, img, img))
    return deck


# Tela de vitória
def mostrar_tela_vitoria(screen, tentativas, erros, acertos, frame):
    screen.fill((0, 0, 30))

    # Título piscando (dourado ↔ branco)
    if (frame // 20) % 2 == 0:
        cor_titulo = (255, 215, 0)   # dourado
    else:
        cor_titulo = (255, 255, 255) # branco brilhante

    fonte_titulo = pygame.font.SysFont("Arial", 50, bold=True)
    texto_vitoria = fonte_titulo.render("Você Venceu!", True, cor_titulo)
    rect = texto_vitoria.get_rect(center=(WIDTH//2, 80))
    screen.blit(texto_vitoria, rect)

    # Baú da vitória pulsando
    bau_img = pygame.image.load(os.path.join(ASSETS_DIR, "bau_vitoria.png"))
    pulse = 20 * abs((frame % 40) - 20) / 20
    size = 200 + int(pulse)
    bau_img = pygame.transform.scale(bau_img, (size, size))
    bau_rect = bau_img.get_rect(center=(WIDTH//2, HEIGHT//2))
    screen.blit(bau_img, bau_rect)

    
    pygame.display.flip()


# Loop principal
def main():
    deck = create_deck()
    first_card = None
    second_card = None
    matches = 0
    attempts = 0
    wrong_attempts = 0
    acertos = 0
    running = True
    vitoria = False
    frame = 0  # contador de quadros

    som_jogo.play(-1)

    while running:
        dt = clock.tick(FPS)
        frame += 1  # incrementa para animação

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            elif not vitoria and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for card in deck:
                    if card.is_clicked(event.pos) and not card.revealed and not card.matched:
                        card.revealed = True
                        if first_card is None:
                            first_card = card
                        elif second_card is None:
                            second_card = card
                            attempts += 1
                            if first_card.identifier == second_card.identifier:
                                first_card.matched = True
                                second_card.matched = True
                                first_card = None
                                second_card = None
                                matches += 1
                                acertos += 1
                                som_acerto.play()
                            else:
                                wrong_attempts += 1
                                pygame.time.set_timer(FLIP_BACK_EVENT, 1000, True)
                                if wrong_attempts >= 6:
                                    screen.fill(BG_COLOR)
                                    gameover_text = font.render("GAME OVER", True, (0, 0, 255))
                                    rect = gameover_text.get_rect(center=(WIDTH//2, HEIGHT//2))
                                    screen.blit(gameover_text, rect)
                                    pygame.display.flip()
                                    som_jogo.stop()
                                    som_gameover.play() 
                                    pygame.time.delay(2000) 
                                    deck = create_deck()
                                    first_card = None
                                    second_card = None
                                    matches = 0
                                    attempts = 0
                                    wrong_attempts = 0
                                    acertos = 0
                                    som_jogo.play(-1)

            elif event.type == FLIP_BACK_EVENT:
                if first_card and second_card:
                    first_card.revealed = False
                    second_card.revealed = False
                first_card = None
                second_card = None

        if not vitoria:
            screen.fill(BG_COLOR)
            for card in deck:
                card.draw(screen)

            # HUD
            tentativas_text = font.render(f"Tentativas: {attempts}", True, (0, 0, 255))
            erros_text = font.render(f"Erros: {wrong_attempts}/9", True, (0, 0, 255))
            acertos_text = font.render(f"Acertos: {acertos}", True, (0, 0, 255))

            tentativas_rect = tentativas_text.get_rect()
            erros_rect = erros_text.get_rect()
            acertos_rect = acertos_text.get_rect()

            total_width = tentativas_rect.width + 40 + erros_rect.width + 40 + acertos_rect.width
            start_x = (WIDTH - total_width) // 2
            y_pos = 20

            tentativas_rect.topleft = (start_x, y_pos)
            erros_rect.topleft = (tentativas_rect.topright[0] + 40, y_pos)
            acertos_rect.topleft = (erros_rect.topright[0] + 40, y_pos)

            screen.blit(tentativas_text, tentativas_rect)
            screen.blit(erros_text, erros_rect)
            screen.blit(acertos_text, acertos_rect)

            # Vitória
            if matches == (GRID_ROWS * GRID_COLS) // 2:
                vitoria = True
                som_jogo.stop()
                som_vitoria.play()
        else:
            mostrar_tela_vitoria(screen, attempts, wrong_attempts, acertos, frame)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()

# Aluno: Patricia Lopes Da Silva
# RU:4670440
