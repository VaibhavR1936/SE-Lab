import math
import pygame
from .player import Player
from .obstacle import Obstacle


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BROWN = (120, 80, 40)
DARK_GREEN = (30, 100, 30)
RED = (180, 40, 40)
YELLOW = (240, 210, 60)


class GameEngine:
    """
    Main game controller.

    Features:
    - Player jumping and gravity
    - Obstacles and scoring
    - Fair collision detection using swept obstacle rectangles
    - Capped speed ramp
    - Game-over screen
    - Replay with Easy/Medium/Hard difficulty
    - Jump, score and game-over sound effects
    """

    DIFFICULTIES = {
        "Easy": {
            "speed": 5.0,
            "spawn_interval": 90,
            "speed_increase": 0.0015,
            "max_speed": 10.0,
        },
        "Medium": {
            "speed": 6.0,
            "spawn_interval": 70,
            "speed_increase": 0.0025,
            "max_speed": 14.0,
        },
        "Hard": {
            "speed": 7.5,
            "spawn_interval": 60,
            "speed_increase": 0.0030,
            "max_speed": 18.0,
        },
    }

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.ground_y = height - 40

        self.font = pygame.font.SysFont("Arial", 30, bold=True)
        self.big_font = pygame.font.SysFont("Arial", 52, bold=True)
        self.medium_font = pygame.font.SysFont("Arial", 36, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 24)

        self._setup_audio()
        self.state = "MENU"
        self.selected_difficulty = "Medium"

        self.player = None
        self.obstacles = []
        self.speed = 0.0
        self.speed_increase_per_frame = 0.0
        self.max_speed = 0.0
        self.spawn_interval = 0
        self._spawn_timer = 0
        self.score = 0
        self.distance = 0.0

    def _setup_audio(self):
        """Create short sound effects without requiring external audio files."""
        self.audio_available = False

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()

            sample_rate = 44100

            def make_tone(frequency, duration, volume=0.18):
                sample_count = int(sample_rate * duration)
                samples = bytearray()

                for i in range(sample_count):
                    t = i / sample_rate
                    envelope = min(1.0, i / 300)
                    remaining = sample_count - i
                    release = min(1.0, remaining / 1500)
                    amplitude = int(32767 * volume * envelope * release)
                    value = int(amplitude * math.sin(2 * math.pi * frequency * t))
                    samples += int(value).to_bytes(2, byteorder="little", signed=True)
                    samples += int(value).to_bytes(2, byteorder="little", signed=True)

                return pygame.mixer.Sound(buffer=bytes(samples))

            self.jump_sound = make_tone(520, 0.10, 0.15)
            self.score_sound = make_tone(780, 0.10, 0.15)
            self.game_over_sound = make_tone(180, 0.25, 0.18)
            self.audio_available = True
        except pygame.error:
            # The game remains fully playable if audio cannot be initialized.
            self.jump_sound = None
            self.score_sound = None
            self.game_over_sound = None

    def _play_sound(self, sound):
        if self.audio_available and sound is not None:
            try:
                sound.play()
            except pygame.error:
                pass

    def start_game(self, difficulty):
        """Start/restart a game with the selected difficulty."""
        settings = self.DIFFICULTIES[difficulty]

        self.selected_difficulty = difficulty
        self.player = Player(80, self.ground_y)
        self.obstacles = []

        self.speed = settings["speed"]
        self.speed_increase_per_frame = settings["speed_increase"]
        self.max_speed = settings["max_speed"]
        self.spawn_interval = settings["spawn_interval"]

        self._spawn_timer = 0
        self.score = 0
        self.distance = 0.0
        self.state = "PLAYING"

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if self.state == "MENU":
                if event.key in (pygame.K_1, pygame.K_KP1):
                    self.start_game("Easy")
                elif event.key in (pygame.K_2, pygame.K_KP2):
                    self.start_game("Medium")
                elif event.key in (pygame.K_3, pygame.K_KP3):
                    self.start_game("Hard")
                elif event.key in (pygame.K_ESCAPE, pygame.K_q):
                    self.state = "QUIT"

            elif self.state == "PLAYING":
                if event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                    if self.player.jump():
                        self._play_sound(self.jump_sound)

                elif event.key == pygame.K_ESCAPE:
                    self.state = "MENU"

            elif self.state == "GAME_OVER":
                if event.key in (pygame.K_1, pygame.K_KP1):
                    self.start_game("Easy")
                elif event.key in (pygame.K_2, pygame.K_KP2):
                    self.start_game("Medium")
                elif event.key in (pygame.K_3, pygame.K_KP3):
                    self.start_game("Hard")
                elif event.key in (pygame.K_r, pygame.K_RETURN, pygame.K_SPACE):
                    self.start_game(self.selected_difficulty)
                elif event.key in (pygame.K_ESCAPE, pygame.K_q):
                    self.state = "MENU"

    def handle_input(self):
        # Kept for compatibility with the original project structure.
        pass

    def update(self):
        if self.state != "PLAYING":
            return

        # Cap the speed so collision detection and gameplay remain fair.
        self.speed = min(
            self.speed + self.speed_increase_per_frame,
            self.max_speed
        )

        self.player.update()

        self._spawn_timer += 1
        if self._spawn_timer >= self.spawn_interval:
            self._spawn_timer = 0
            self.obstacles.append(
                Obstacle(self.width, self.ground_y, self.speed)
            )

        # Move obstacles and keep their previous position for swept collision.
        for obstacle in self.obstacles:
            obstacle.previous_x = obstacle.x
            obstacle.move()

            # Keep newly spawned/current obstacles synchronized with game speed.
            obstacle.speed = self.speed

        # Swept collision detection:
        # union(previous_rect, current_rect) represents the entire horizontal
        # path travelled by an obstacle during this frame.
        player_rect = self.player.rect()

        for obstacle in self.obstacles:
            previous_rect = obstacle.rect_at_x(obstacle.previous_x)
            current_rect = obstacle.rect()

            swept_rect = previous_rect.union(current_rect)

            if swept_rect.colliderect(player_rect):
                self._set_game_over()
                return

        # Score each obstacle exactly once after it passes the player.
        for obstacle in self.obstacles:
            if not obstacle.scored and obstacle.x + obstacle.width < self.player.x:
                obstacle.scored = True
                self.score += 1
                self._play_sound(self.score_sound)

        self.obstacles = [
            obstacle for obstacle in self.obstacles
            if not obstacle.off_screen()
        ]

        self.distance += self.speed

    def _set_game_over(self):
        if self.state != "GAME_OVER":
            self.state = "GAME_OVER"
            self._play_sound(self.game_over_sound)

    def render(self, screen):
        screen.fill((200, 220, 240))

        # Ground
        pygame.draw.line(
            screen,
            BROWN,
            (0, self.ground_y),
            (self.width, self.ground_y),
            4
        )

        if self.state in ("PLAYING", "GAME_OVER"):
            pygame.draw.rect(screen, WHITE, self.player.rect())

            for obstacle in self.obstacles:
                pygame.draw.rect(screen, DARK_GREEN, obstacle.rect())

            score_text = self.font.render(
                f"Score: {self.score}",
                True,
                BLACK
            )
            screen.blit(score_text, (10, 10))

            difficulty_text = self.small_font.render(
                f"Difficulty: {self.selected_difficulty}",
                True,
                BLACK
            )
            screen.blit(difficulty_text, (10, 45))

            speed_text = self.small_font.render(
                f"Speed: {self.speed:.1f}",
                True,
                BLACK
            )
            screen.blit(speed_text, (10, 75))

        if self.state == "MENU":
            self._render_menu(screen)
        elif self.state == "GAME_OVER":
            self._render_game_over(screen)
        elif self.state == "QUIT":
            return

    def _render_menu(self, screen):
        title = self.big_font.render("ENDLESS RUNNER", True, BLACK)
        title_rect = title.get_rect(center=(self.width // 2, 75))
        screen.blit(title, title_rect)

        subtitle = self.medium_font.render(
            "Choose Difficulty",
            True,
            BLACK
        )
        subtitle_rect = subtitle.get_rect(center=(self.width // 2, 135))
        screen.blit(subtitle, subtitle_rect)

        options = [
            ("1 - Easy", "Slower speed, longer spawn interval"),
            ("2 - Medium", "Balanced difficulty"),
            ("3 - Hard", "Faster speed, shorter spawn interval"),
        ]

        y = 190
        for name, description in options:
            text = self.font.render(name, True, DARK_GREEN)
            text_rect = text.get_rect(center=(self.width // 2, y))
            screen.blit(text, text_rect)

            desc = self.small_font.render(description, True, BLACK)
            desc_rect = desc.get_rect(center=(self.width // 2, y + 30))
            screen.blit(desc, desc_rect)

            y += 65

        instruction = self.small_font.render(
            "Press 1, 2, or 3 to start   |   Esc/Q to quit",
            True,
            BLACK
        )
        instruction_rect = instruction.get_rect(
            center=(self.width // 2, self.height - 35)
        )
        screen.blit(instruction, instruction_rect)

    def _render_game_over(self, screen):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        screen.blit(overlay, (0, 0))

        title = self.big_font.render("GAME OVER", True, RED)
        title_rect = title.get_rect(center=(self.width // 2, 100))
        screen.blit(title, title_rect)

        score = self.medium_font.render(
            f"Final Score: {self.score}",
            True,
            WHITE
        )
        score_rect = score.get_rect(center=(self.width // 2, 160))
        screen.blit(score, score_rect)

        difficulty = self.font.render(
            f"Difficulty: {self.selected_difficulty}",
            True,
            WHITE
        )
        difficulty_rect = difficulty.get_rect(center=(self.width // 2, 205))
        screen.blit(difficulty, difficulty_rect)

        restart = self.small_font.render(
            "R / Enter / Space - Replay same difficulty",
            True,
            YELLOW
        )
        restart_rect = restart.get_rect(center=(self.width // 2, 255))
        screen.blit(restart, restart_rect)

        choose = self.small_font.render(
            "1 - Easy   2 - Medium   3 - Hard",
            True,
            WHITE
        )
        choose_rect = choose.get_rect(center=(self.width // 2, 290))
        screen.blit(choose, choose_rect)

        menu = self.small_font.render(
            "Esc/Q - Return to menu",
            True,
            WHITE
        )
        menu_rect = menu.get_rect(center=(self.width // 2, 325))
        screen.blit(menu, menu_rect)
