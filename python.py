import pygame
import random
import os
import colorsys
import math


# Initialize Pygame
pygame.init()
cwd = os.getcwd()

# Set up the display
screen_width = 800
screen_height = 800
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("2D-Game")

# Set up the fonts
FONT = pygame.font.SysFont("Arial", 30)

# Load background image
file_path = os.path.join("background.png")
file_path1 = os.path.join("blaha.png")
file_path2 = os.path.join("pixil-frame-0.png")
file_path3 = os.path.join("collectible.png")
file_path4 = os.path.join("bullet.png")
BACKGROUND_IMAGE = pygame.image.load(file_path).convert()
PLAYER_RIGHT = pygame.image.load(file_path2).convert_alpha()
PLAYER_LEFT = pygame.image.load(file_path1).convert_alpha()
NOT_RACIST_COLLECTABLE = pygame.image.load(file_path3).convert_alpha()
BULLET = pygame.image.load(file_path4).convert_alpha()

PLAYER_RIGHT = pygame.transform.scale(PLAYER_RIGHT, (100, 100))
PLAYER_LEFT = pygame.transform.scale(PLAYER_LEFT, (100, 100))
NOT_RACIST_COLLECTABLE = pygame.transform.scale(PLAYER_RIGHT, (100, 100))
BULLET = pygame.transform.scale(PLAYER_LEFT, (10, 10))


class Collectible:
    def __init__(self, x, y, width=30, height=30, image_path="collectible.png"):
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (width, height))

    def spawn(self):
        self.rect.x = random.randint(0, screen_width - self.rect.width)
        self.rect.y = random.randint(0, screen_height - self.rect.height)


class Score:
    def __init__(self, x, y):
        self.value = 0
        self.x = x
        self.y = y
        self.font = pygame.font.SysFont("Arial", 30)

    def increase(self, amount=1):
        self.value += amount

    def draw(self, surface):
        text_surf = self.font.render("Score: " + str(self.value), True, (255, 255, 255))
        surface.blit(text_surf, (self.x, self.y))



class Button:
    def __init__(self, text, x, y, width=200, height=50, color=(255, 255, 255), text_color=(0, 0, 0)):
        self.rect = pygame.Rect(x, y, width, height)
        self.surface = pygame.Surface((width, height))
        self.surface.fill(color)
        text_surf = FONT.render(text, True, text_color)
        text_rect = text_surf.get_rect(center=(width // 2, height // 2))
        self.surface.blit(text_surf, text_rect)

    def draw(self, surface):
        surface.blit(self.surface, self.rect)


class Player:
    def __init__(self, x, y, width=40, height=40, speed=4, lives=3):
        self.rect = pygame.Rect(x, y, width, height)
        self.image = PLAYER_LEFT
        self.speed = speed
        self.lives = lives


    def move(self, keys, screen_width, screen_height):
        if keys[pygame.K_w] and self.rect.top > 0:
            self.rect.top -= self.speed
        if keys[pygame.K_s] and self.rect.bottom < screen_height:
            self.rect.bottom += self.speed
        if keys[pygame.K_a] and self.rect.left > 0:
            self.rect.left -= self.speed
            self.image = PLAYER_LEFT
        if keys[pygame.K_d] and self.rect.right < screen_width:
            self.rect.right += self.speed
            self.image = PLAYER_RIGHT
        pygame.display.flip()


class Enemy:
    def __init__(self, x, y, width=50, height=50, speed=1, xvel=0, yvel=0):
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height))
        self.image.fill((0, 0, 255))
        self.speed = speed
        self.xvel = xvel
        self.yvel = yvel

    def move(self, screen_width, screen_height):
        self.rect.top += self.speed * self.yvel
        if self.rect.top > screen_height:
            self.rect.top = 0
            self.rect.left = random.randint(0, screen_width - self.rect.width)
        self.rect.left += self.speed * self.xvel
        if self.rect.left > screen_width:
            self.rect.left = 0
            self.rect.top = random.randint(0, screen_height - self.rect.height)

    def check_collision(self, bullets):
        for bullet in bullets:
            if self.rect.colliderect(bullet.rect):
                bullets.remove(bullet)
                return True
        return False

class Bullet:
    def __init__(self, x, y, target_x, target_y):
        self.rect = pygame.Rect(x, y, 10, 10)
        self.x = x + 20
        self.y = y + 20
        self.target_x = target_x
        self.target_y = target_y
        self.image = BULLET 
        self.k = (target_y - y)/(target_x - x)
        self.direction = None
        self.fired = False

class Game:
    def __init__(self):
        self.clock = pygame.time.Clock()
        self.player = Player(screen_width // 2 - 25, screen_height - 60)
        self.enemies = [Enemy(random.randint(0, screen_width - 30), random.randint(0, screen_height // 2), xvel=1)
                        for _ in range(2)] + [Enemy(random.randint(0, screen_width - 30), random.randint(0, screen_height // 2), yvel=1)
                                              for _ in range(2)] + [Enemy(random.randint(0, screen_width - 30), random.randint(0, screen_height // 2), yvel=1, xvel=1)
                                                                    for _ in range(2)]
        self.score = Score(10, 10)
        self.start_button = Button(
            "Start", screen_width // 2 - 100, screen_height // 2)
        self.end_button = Button(
            "Restart", screen_width // 2 - 100, screen_height // 2)
        self.game_state = "start_menu"
        self.running = True
        self.show_end_screen = False
        self.frame = 0
        self.collectibles = [Collectible(random.randint(0, screen_width - 30), random.randint(0, screen_height - 30))
                             for _ in range(5)]
        self.bullets = []

    

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if self.game_state == "start_menu" and self.start_button.rect.collidepoint(mouse_pos):
                    self.game_state = "playing"
                elif self.game_state == "end_screen" and self.end_button.rect.collidepoint(mouse_pos):
                    self.reset_game()
                elif self.game_state == "playing":
                    print(mouse_pos)
                    self.bullets.append(Bullet(self.player.rect.x, self.player.rect.y, mouse_pos[0], mouse_pos[1]))

        if self.game_state == "playing":
            keys = pygame.key.get_pressed()
            self.player.move(keys, screen_width, screen_height)
        

    def update(self):
        if self.game_state == "playing":
            for enemy in self.enemies:
                color = colorsys.hls_to_rgb((self.frame % 100) / 100, 0.5, 1)
                enemy.image.fill((color[0] * 255, color[1] * 255, color[2] * 255))
                enemy.move(screen_width, screen_height)
                if enemy.rect.colliderect(self.player.rect):
                    self.player.lives -= 1
                    if self.player.lives == 0:
                        self.show_end_screen = True
                if enemy.check_collision(self.bullets):
                    self.enemies.remove(enemy)  # Remove enemy when hit by a bullet

            if not self.enemies:
                self.show_end_screen = True
            
            for collectible in self.collectibles:
                if self.player.rect.colliderect(collectible):
                    collectible.spawn()
                    self.score.increase(10)

            for bullet in self.bullets:
                if not bullet.fired:
                    bullet_pos = (bullet.rect.x, bullet.rect.y)
                    cursor_pos = pygame.mouse.get_pos()
                    dx = cursor_pos[0] - bullet_pos[0]
                    dy = cursor_pos[1] - bullet_pos[1]
                    angle = math.atan2(dy, dx) * 180 / math.pi
                    rad_angle = math.radians(angle)
                    bullet.direction = [math.cos(rad_angle), math.sin(rad_angle)]
                    bullet.fired = True
                speed = 10
                bullet.rect.x += bullet.direction[0] * speed
                bullet.rect.y += bullet.direction[1] * speed



        self.frame += 1

    def draw(self):
        screen.fill((0, 0, 0))
        if self.game_state == "start_menu":
            self.start_button.draw(screen)
        elif self.game_state == "playing":
            screen.blit(BACKGROUND_IMAGE, (0, 0))
            screen.blit(self.player.image, self.player.rect)
            self.score.draw(screen)
            for enemy in self.enemies:
                screen.blit(enemy.image, enemy.rect)

            for collectible in self.collectibles:
                screen.blit(collectible.image, collectible.rect)

            for bullet in self.bullets:
                screen.blit(bullet.image, bullet.rect)

        elif self.game_state == "end_screen":
            end_text = FONT.render("Game Over", True, (255, 0, 0))
            end_text_rect = end_text.get_rect(
                center=(screen_width // 2, screen_height // 2 - 50))
            screen.blit(end_text, end_text_rect)
            self.end_button.draw(screen)

    def reset_game(self):
        self.player = Player(screen_width // 2 - 25, screen_height - 60)
        self.enemies = [Enemy(random.randint(0, screen_width - 30), random.randint(0, screen_height // 2), xvel=1)
                        for _ in range(3)] + [Enemy(random.randint(0, screen_width - 30), random.randint(0, screen_height // 2), yvel=1)
                                              for _ in range(3)] + [Enemy(random.randint(0, screen_width - 30), random.randint(0, screen_height // 2), yvel=1, xvel=1)
                                                                    for _ in range(3)]
        self.show_end_screen = False
        self.game_state = "playing"
        self.score = Score(10, 10)

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            pygame.display.update()
            self.clock.tick(60)


            if self.show_end_screen:
                self.game_state = "end_screen"


if __name__ == "__main__":
    pygame.init()
    game = Game()
    game.run()
    pygame.quit()