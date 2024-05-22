import pygame
import random

from objects import Player, Bar, Ball, Block, ScoreCard, Message, Particle, generate_particles

pygame.init()
SCREEN = WIDTH, HEIGHT = 288, 512

info = pygame.display.Info()
width = info.current_w
height = info.current_h

if width >= height:
    win = pygame.display.set_mode(SCREEN, pygame.NOFRAME)
else:
    # cоздание окна в полноэкранном режиме с масштабированием
    win = pygame.display.set_mode(SCREEN, pygame.NOFRAME | pygame.SCALED | pygame.FULLSCREEN)

clock = pygame.time.Clock()
FPS = 45

# цвета
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (54, 69, 79)
c_list = [RED, BLACK, WHITE]

# fonts
pygame.font.init()
score_font = pygame.font.Font('Fonts/BubblegumSans-Regular.ttf', 50)

# sounds

coin_fx = pygame.mixer.Sound('Sounds/coin.mp3')
death_fx = pygame.mixer.Sound('Sounds/death.mp3')
move_fx = pygame.mixer.Sound('Sounds/move.mp3')

# backgrounds

bg_list = []
for i in range(1, 5):
    if i == 2:
        ext = "jpeg"
    else:
        ext = "jpg"
    img = pygame.image.load(f"Assets/Backgrounds/bg{i}.{ext}")
    img = pygame.transform.scale(img, (WIDTH, HEIGHT))
    bg_list.append(img)

# загрузка изображения фона
home_bg = pygame.image.load(f"Assets/Backgrounds/home.jpeg")

bg = home_bg

# objects
bar_group = pygame.sprite.Group()
ball_group = pygame.sprite.Group()
block_group = pygame.sprite.Group()
destruct_group = pygame.sprite.Group()
win_particle_group = pygame.sprite.Group()
# расстояние между верхней и нижней преградой
bar_gap = 120

particles = []

p = Player(win)
score_card = ScoreCard(140, 40, win)


# functions

def destroy_bird():
    x, y = p.rect.center
    for i in range(50):
        c = random.choice(c_list)
        particle = Particle(x, y, 1, c, win)
        destruct_group.add(particle)


def win_particles():
    for x, y in [(40, 120), (WIDTH - 20, 240), (15, HEIGHT - 30)]:
        for i in range(10):
            particle = Particle(x, y, 2, WHITE, win)
            win_particle_group.add(particle)


# messages
title_font = "Fonts/Robus-BWqOd.otf"
dodgy = Message(134, 90, 100, "Birds&", title_font, WHITE, win)
walls = Message(164, 145, 80, "Walls", title_font, WHITE, win)

tap_to_play_font = "Fonts/DebugFreeTrial-MVdYB.otf"
tap_to_play = Message(144, 400, 32, "Tap to play", tap_to_play_font, WHITE, win)
tap_to_replay = Message(144, 400, 30, "Tap to replay", tap_to_play_font, WHITE, win)

# variables

bar_width_list = [i for i in range(40, 150, 10)]
# частотf появления новых преград (стен) в игре
bar_frequency = 1200
# скорость движения преград (стен) в игре
bar_speed = 4
# логическая переменная, которая указывает, коснулась ли птица экрана или нет
touched = False
# переменная, хранящая позицию, в которой было совершено касание экрана
pos = None
# логическая переменная, которая указывает, находится ли игра на домашнем экране (начальный экран) или нет
home_page = True
# логическая переменная, которая указывает, отображается ли экран с результатами игры или нет
score_page = False
bird_dead = False
score = 0
high_score = 0
# логические переменные, которые указывают, отображается ли экран с результатами игры или нет
move_left = False
move_right = True
# число, представляющее предыдущее значение координаты x при движении птицы по экрану
prev_x = 0
# число, которое используется для отслеживания числа кадров или итераций в игре
p_count = 0

running = True
while running:
    win.blit(bg, (0, 0))

    for event in pygame.event.get():
        # закрытие окна
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            # клавиша ESC
            if event.key == pygame.K_ESCAPE:
                running = False

        if event.type == pygame.MOUSEBUTTONDOWN and (home_page or score_page):
            # частицы (если они есть) очищаются
            home_page = False
            score_page = False
            win_particle_group.empty()

            # выбирается новый случайный задний фон
            bg = random.choice(bg_list)

            particles = []  # пустой список для хранения частиц
            last_bar = pygame.time.get_ticks() - bar_frequency  # время последнего создания препятствия
            next_bar = 0
            bar_speed = 4
            bar_frequency = 1200  # частота
            bird_dead = False
            score = 0
            p_count = 0  # счетчик частиц
            score_list = []  # список для хранения результатов

            for _ in range(15):
                # координаты
                x = random.randint(30, WIDTH - 30)
                y = random.randint(60, HEIGHT - 60)
                max = random.randint(8, 16)
                # cоздает новый блок с заданными координатами и максимальной высотой, используя класс Block
                b = Block(x, y, max, win)
                # добавляет созданный блок в группу block_group
                block_group.add(b)

        if event.type == pygame.MOUSEBUTTONDOWN and not home_page:
            if p.rect.collidepoint(event.pos):
                touched = True
                x, y = event.pos
                offset_x = p.rect.x - x

        if event.type == pygame.MOUSEBUTTONUP and not home_page:
            # кнопка мыши была отпущена
            touched = False

        # код проверяет, было ли нажатие на объект (проверяется переменная touched)
        if event.type == pygame.MOUSEMOTION and not home_page:
            if touched:
                x, y = event.pos
                # предыдущая координата x (prev x)
                if move_right and prev_x > x:
                    move_right = False
                    move_left = True
                    # звуковой эффект
                    move_fx.play()
                if move_left and prev_x < x:
                    move_right = True
                    move_left = False
                    # звуковой эффект
                    move_fx.play()

                prev_x = x
                p.rect.x = x + offset_x

    if home_page:
        bg = home_bg
        particles = generate_particles(p, particles, WHITE, win)
        dodgy.update()
        walls.update()
        tap_to_play.update()
        p.update()

    elif score_page:
        bg = home_bg
        particles = generate_particles(p, particles, WHITE, win)
        tap_to_replay.update()
        p.update()
        score_msg.update()
        score_point.update()
        if p_count % 5 == 0:
            win_particles()
        p_count += 1
        # обновляет группу частиц победы.
        win_particle_group.update()

    else:

        # текущее время в миллисекундах с момента запуска Pygame
        next_bar = pygame.time.get_ticks()
        # gроверяет, прошло ли достаточно времени с момента последнего создания барьера
        if next_bar - last_bar >= bar_frequency and not bird_dead:
            # выбирает случайную ширину для барьера из списка bar_width_list
            bwidth = random.choice(bar_width_list)

            b1prime = Bar(0, 0, bwidth + 3, GRAY, win)
            b1 = Bar(0, -3, bwidth, WHITE, win)

            b2prime = Bar(bwidth + bar_gap + 3, 0, WIDTH - bwidth - bar_gap, GRAY, win)
            b2 = Bar(bwidth + bar_gap, -3, WIDTH - bwidth - bar_gap, WHITE, win)

            bar_group.add(b1prime)  # добавляет первый барьер с окантовкой в группу барьеров.
            bar_group.add(b1)  # первый основной барьер в группу барьеров
            bar_group.add(b2prime)
            bar_group.add(b2)

            color = random.choice(["red", "white"])
            pos = random.choice([0, 1])
            if pos == 0:
                x = bwidth + 12
            elif pos == 1:
                x = bwidth + bar_gap - 12
            ball = Ball(x, 10, 1, color, win)

            ball_group.add(ball)
            # обновляет время последнего барьера
            last_bar = next_bar

        for ball in ball_group:
            if ball.rect.colliderect(p):
                if ball.color == "white":
                    # удаляет шарик из группы и экрана
                    ball.kill()
                    coin_fx.play()
                    score += 1
                    if score > high_score:
                        high_score += 1
                    score_card.animate = True
                elif ball.color == "red":
                    if not bird_dead:
                        death_fx.play()
                        destroy_bird()

                    bird_dead = True
                    bar_speed = 0

        # проверяет, происходит ли столкновение прямоугольника птицы (p) с любым из барьеров в группе bar_group
        if pygame.sprite.spritecollide(p, bar_group, False):
            if not bird_dead:
                # dоспроизводит звуковой эффект
                death_fx.play()
                destroy_bird()

            bird_dead = True
            bar_speed = 0

        block_group.update()
        bar_group.update(bar_speed)
        ball_group.update(bar_speed)

        if bird_dead:
            destruct_group.update()

        score_card.update(score)

        if not bird_dead:
            particles = generate_particles(p, particles, WHITE, win)
            p.update()

        if score and score % 10 == 0:
            rem = score // 10
            if rem not in score_list:
                score_list.append(rem)
                bar_speed += 1
                bar_frequency -= 200

        if bird_dead and len(destruct_group) == 0:
            score_page = True
            font = "Fonts/BubblegumSans-Regular.ttf"
            if score < high_score:
                score_msg = Message(144, 60, 55, "Score", font, WHITE, win)
            else:
                score_msg = Message(144, 60, 55, "New High", font, WHITE, win)

            score_point = Message(144, 110, 45, f"{score}", font, WHITE, win)

        if score_page:
            block_group.empty()
            bar_group.empty()
            ball_group.empty()

            p.reset()

    clock.tick(FPS)
    pygame.display.update()

pygame.quit()