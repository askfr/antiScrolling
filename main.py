import pygame
import random
import os
import asyncio  # !!! ДЛЯ WEB !!! Обязательная библиотека для браузера

# --- ИНИЦИАЛИЗАЦИЯ ---
WIDTH, HEIGHT = 500, 700
WHITE, BLACK = (255, 255, 255), (20, 20, 20)
GOLD, GREEN, RED, BLUE = (255, 215, 0), (50, 200, 50), (200, 50, 50), (50, 150, 255)
GRAY, YELLOW = (150, 150, 150), (255, 255, 0)

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Шрифты
title_font = pygame.font.SysFont("Arial", 42, bold=True)
font = pygame.font.SysFont("Arial", 24, bold=True)
medium_font = pygame.font.SysFont("Arial", 30, bold=True)
small_font = pygame.font.SysFont("Arial", 18, bold=True)
tiny_font = pygame.font.SysFont("Arial", 15, bold=True)


def load_img(name, scale):
    if os.path.exists(name):
        img = pygame.image.load(name).convert_alpha()
        return pygame.transform.smoothscale(img, scale)
    return None


skull_img = load_img("skull.png", (140, 100))
bg_img = load_img("background.png", (WIDTH, HEIGHT))

# --- ЗАГРУЗКА РЕСУРСОВ (OGG для WEB) ---
# Проверяем наличие .ogg файлов, чтобы игра не вылетала в браузере
s_click = pygame.mixer.Sound("click.ogg") if os.path.exists("click.ogg") else None
s_fail = pygame.mixer.Sound("gameover.ogg") if os.path.exists("gameover.ogg") else None
s_restart = pygame.mixer.Sound("restart.ogg") if os.path.exists("restart.ogg") else None


# --- КЛАССЫ ЭФФЕКТОВ ---
class FloatEffect:
    def __init__(self, text, x, y, color, offset_y):
        self.text, self.x, self.y, self.color = text, x, y + offset_y, color
        self.alpha = 255

    def update(self):
        self.y -= 1.8
        self.alpha -= 5

    def draw(self, surf):
        if self.alpha > 0:
            txt = small_font.render(self.text, True, self.color)
            txt.set_alpha(self.alpha)
            surf.blit(txt, (self.x - txt.get_width() // 2, self.y))


class ReasonBox:
    def __init__(self, text, x, y, color):
        self.text, self.x, self.y, self.color = text, x, y, color
        self.alpha, self.life, self.target_y = 255, 160, y

    def update(self, i):
        self.target_y = 580 + (i * 45)
        self.y += (self.target_y - self.y) * 0.2
        if self.life < 30: self.alpha -= 8
        self.life -= 1

    def draw(self, surf):
        if self.alpha > 0:
            txt = tiny_font.render(self.text, True, WHITE)
            p_x, p_y = 12, 8
            rw, rh = txt.get_width() + p_x * 2, txt.get_height() + p_y * 2
            box = pygame.Surface((rw, rh), pygame.SRCALPHA)
            pygame.draw.rect(box, (30, 30, 30, self.alpha), (0, 0, rw, rh), border_radius=10)
            pygame.draw.rect(box, (self.color[0], self.color[1], self.color[2], self.alpha), (0, 0, rw, rh), width=2,
                             border_radius=10)
            txt.set_alpha(self.alpha)
            box.blit(txt, (p_x, p_y))
            surf.blit(box, (self.x - rw // 2, self.y))


# --- БАЗА КАРТОЧЕК (78 ТЕМ) ---
cards_db = [
    {"text": "Реклама: «Теневой заработок на крипте для новичков».", "money": 5, "int": -35, "color": GOLD,
     "rsn": "Зритель чует скам"},
    {"text": "Слот-машина: «Забери свои фриспины прямо сейчас!».", "money": 8, "int": -45, "color": GOLD,
     "rsn": "Гемблинг убивает охват"},
    {"text": "Курс: «Как выйти на 100к в месяц, лежа на диване».", "money": 3, "int": -25, "color": GOLD,
     "rsn": "Инфоцыгане"},
    {"text": "Реклама: «Чудо-пластырь, высасывающий токсины за ночь».", "money": 2, "int": -15, "color": GOLD,
     "rsn": "Био-мусор"},
    {"text": "Игра: «Только 1% людей дойдет до уровня с боссом».", "money": 1, "int": -10, "color": GOLD,
     "rsn": "Дешевая реклама"},
    {"text": "Спор: «Напиши в комментах, чей Крым, и начнется жара».", "money": 1, "int": 5, "color": RED,
     "rsn": "Актив на крови"},
    {"text": "Байт: «Жми лайк, если любишь маму, проигнорь, если ты монстр».", "money": 0, "int": 15, "color": RED,
     "rsn": "Манипуляция"},
    {"text": "Реклама: «Стоматологи в ярости от этого копеечного метода».", "money": 2, "int": -20, "color": GOLD,
     "rsn": "Желтуха"},
    {"text": "Шок-контент: «Вы не поверите, что нашли в животе у этой акулы...».", "money": 1, "int": 5, "color": RED,
     "rsn": "Кликбейт"},
    {"text": "Стрим: «Донать 100р, и я выпью литр уксуса (фейк)».", "money": 10, "int": -30, "color": RED,
     "rsn": "Треш-контент"},
    {"text": "Реклама: «Распродажа кроссовок со скидкой 90%».", "money": 4, "int": -25, "color": GOLD,
     "rsn": "Скам-магазин"},
    {"text": "Опрос: «Кто лучше: Влад А4 или мистер Бист? (Голосуй!)».", "money": 0, "int": 10, "color": RED,
     "rsn": "Байт на комменты"},
    {"text": "Реклама: «Узнай дату своей смерти по этой ссылке».", "money": 6, "int": -40, "color": GOLD,
     "rsn": "Мрачный фишинг"},
    {"text": "Хайп: «Разоблачение популярного блогера (часть 1)».", "money": 2, "int": 10, "color": RED,
     "rsn": "Драма"},
    {"text": "Резка кинетического песка ножом на кубики.", "money": 0, "int": 30, "color": BLUE,
     "rsn": "АСМР залипалово"},
    {"text": "Слухи из Reddit под геймплей Subway Surfers.", "money": 0, "int": 35, "color": BLUE,
     "rsn": "Фоновый гипноз"},
    {"text": "NPC-стрим: «Ммм, кукуруза! Ганг-ганг!».", "money": 3, "int": 15, "color": GRAY, "rsn": "Испанский стыд"},
    {"text": "Чистка экстремально грязного ковра под давлением.", "money": 0, "int": 25, "color": BLUE,
     "rsn": "Визуальный кайф"},
    {"text": "POV: Ты пытаешься незаметно выйти из класса.", "money": 0, "int": 15, "color": GRAY, "rsn": "Жиза"},
    {"text": "Распаковка «загадочной коробки» (Mystery Box).", "money": 1, "int": 20, "color": GRAY, "rsn": "Интрига"},
    {"text": "Лайфхак: Как починить бампер машины вантузом.", "money": 0, "int": 10, "color": RED,
     "rsn": "Смешно и глупо"},
    {"text": "АСМР: Поедание очень хрустящей еды.", "money": 0, "int": 25, "color": BLUE, "rsn": "Звуковой триггер"},
    {"text": "Нарезка смешных моментов со стримов.", "money": 0, "int": 20, "color": GRAY, "rsn": "Классика"},
    {"text": "Подборка видео: «Люди, которым очень повезло».", "money": 0, "int": 25, "color": GRAY, "rsn": "Удача"},
    {"text": "Бесконечное смешивание красок до идеала.", "money": 0, "int": 30, "color": BLUE, "rsn": "Перфекционизм"},
    {"text": "Топ 10 жутких вещей с камер домофонов.", "money": 0, "int": 20, "color": GRAY, "rsn": "Крипота"},
    {"text": "Чел строит бассейн из грязи и палок.", "money": 0, "int": 30, "color": GRAY,
     "rsn": "Primitive technology"},
    {"text": "Подборка видео с котами, которые ведут себя как люди.", "money": 0, "int": 40, "color": BLUE,
     "rsn": "Котики — это святое"},
    {"text": "Тизер: «Я ухожу с YouTube. Это конец».", "money": 0, "int": 45, "color": RED, "rsn": "Байт на жалость"},
    {"text": "Реклама: «Стань альфа-самцом за 3 дня (курс)».", "money": 7, "int": -30, "color": GOLD,
     "rsn": "Кринж-коучинг"},
    {"text": "Теория: «Земля на самом деле — это пончик».", "money": 0, "int": 25, "color": RED, "rsn": "Шизо-теории"},
    {"text": "Обзор: «Пробую еду из мусорки элитного ресторана».", "money": 2, "int": 15, "color": RED,
     "rsn": "Треш-обзор"},
    {"text": "Туториал: «Как взломать Wi-Fi соседа ложкой».", "money": 0, "int": 20, "color": GRAY,
     "rsn": "Фейк-гайды"},
    {"text": "Реклама: «Амулет на богатство от бабы Нины».", "money": 5, "int": -25, "color": GOLD,
     "rsn": "Мракобесие"},
    {"text": "Челлендж: «24 часа в ледяном плену из маршмэллоу».", "money": 1, "int": 35, "color": GRAY,
     "rsn": "Детский контент"},
    {"text": "Мистика: «Тварь за окном попала на видео».", "money": 0, "int": 20, "color": RED, "rsn": "Скримеры"},
    {"text": "АСМР: Шепот на ухо про квантовую физику.", "money": 0, "int": 15, "color": BLUE, "rsn": "Странный АСМР"},
    {"text": "Стрим: «Сплю, пока вы донатите на громкие звуки».", "money": 12, "int": -40, "color": RED,
     "rsn": "Сон за деньги"},
    {"text": "Лайфхак: Как сделать iPhone из старой Nokia.", "money": 0, "int": 10, "color": GRAY, "rsn": "Техно-фейк"},
    {"text": "Мемы: Сборка «Мемы, от которых сводит олдскулы».", "money": 0, "int": 30, "color": GRAY,
     "rsn": "Ностальгия"},
    {"text": "Нейросеть нарисовала города в виде злодеев.", "money": 0, "int": 40, "color": BLUE, "rsn": "Тренд с ИИ"},
    {"text": "Реклама: «Крем для увеличения IQ через кожу».", "money": 4, "int": -20, "color": GOLD,
     "rsn": "Псевдонаука"},
    {"text": "Подборка: «Самые неловкие моменты в прямом эфире».", "money": 0, "int": 25, "color": GRAY,
     "rsn": "Фейлы"},
    {"text": "Спор: «Кто сильнее: Кит или Слон? Битва века».", "money": 0, "int": 15, "color": RED,
     "rsn": "Бессмысленные споры"},
    {"text": "Реклама: «Подписка на воздух со скидкой 50%».", "money": 10, "int": -50, "color": GOLD,
     "rsn": "Наглый скам"},
    {"text": "Уборка: «Отмываю заброшенный дом маньяка».", "money": 0, "int": 30, "color": BLUE, "rsn": "Залипательно"},
    {"text": "POV: Ты — последний выживший в зомби-апокалипсисе.", "money": 0, "int": 20, "color": GRAY,
     "rsn": "Ролеплеи"},
    {"text": "Реклама: «Играй в наш симулятор камня бесплатно!».", "money": 2, "int": -10, "color": GOLD,
     "rsn": "Странные игры"},
    {"text": "Топ: «5 признаков, что твой кот — инопланетянин».", "money": 0, "int": 15, "color": RED,
     "rsn": "Желтая пресса"},
    {"text": "Шоу: «Угадай дешевое вино по запаху пробки».", "money": 1, "int": 10, "color": GRAY, "rsn": "Снобизм"},
    {"text": "Реклама: «Заряжаем кошельки через экран монитора».", "money": 6, "int": -35, "color": GOLD,
     "rsn": "Инфо-шиза"},
    {"text": "Честный отзыв на честный отзыв другого блогера.", "money": 0, "int": 5, "color": RED,
     "rsn": "Рекурсия хайпа"},
    {"text": "АСМР: Звуки лопающихся пузырьков на обоях.", "money": 0, "int": 25, "color": BLUE, "rsn": "Релакс"},
    {"text": "Гайд: «Как стать невидимым для военкомата».", "money": 0, "int": 50, "color": RED,
     "rsn": "Запретные темы"},
    {"text": "Реклама: «Тур в Антарктиду за 500 рублей (розыгрыш)».", "money": 3, "int": -15, "color": GOLD,
     "rsn": "Лохотрон"},
    {"text": "Мнение: «Почему Луна — это голограмма правительства».", "money": 0, "int": 10, "color": RED,
     "rsn": "Конспирология"},
    {"text": "Нарезка: «Самые быстрые рабочие в мире».", "money": 0, "int": 30, "color": BLUE, "rsn": "Перфекционизм"},
    {"text": "Реклама: «Таблетки от лени (курс 30 дней)».", "money": 5, "int": -20, "color": GOLD, "rsn": "Фарма-скам"},
    {"text": "Байт: «Напиши свое имя задом наперед, если ты гений».", "money": 0, "int": 15, "color": RED,
     "rsn": "Вовлечение"},
    {"text": "Интервью с человеком, который не спал 10 лет.", "money": 1, "int": 25, "color": GRAY,
     "rsn": "Фейк-интервью"},
    {"text": "Реклама: «Виртуальная жена в твоем браузере».", "money": 8, "int": -40, "color": GOLD,
     "rsn": "18+ реклама"},
    {"text": "Рецепт: «Готовим торт из доширака и колы».", "money": 0, "int": 20, "color": RED, "rsn": "Фуд-треш"},
    {"text": "Стрим: «Играю в Sims 4, пока не женюсь на смерти».", "money": 1, "int": 15, "color": GRAY,
     "rsn": "Геймплей"},
    {"text": "АСМР: Стрижка волос ржавыми ножницами.", "money": 0, "int": 10, "color": BLUE, "rsn": "Тревожный АСМР"},
    {"text": "Реклама: «Курс по дыханию маткой для успеха в бизнесе».", "money": 9, "int": -45, "color": GOLD,
     "rsn": "Дикий инфобиз"},
    {"text": "Топ: «Вещи, которые запрещены в КНДР».", "money": 0, "int": 25, "color": GRAY, "rsn": "Любопытство"},
    {"text": "Челлендж: «Повторяю тренировку Ван Дамма в 100 лет».", "money": 0, "int": 20, "color": GRAY,
     "rsn": "Спорт-хайп"},
    {"text": "Реклама: «Аренда iPhone 16 для фото в Instagram».", "money": 4, "int": -10, "color": GOLD,
     "rsn": "Казаться, а не быть"},
    {"text": "Шок: «Нашел золото в старом диване с помойки».", "money": 0, "int": 30, "color": RED,
     "rsn": "Кликбейт-поиск"},
    {"text": "Обзор: «Самая дорогая вода в мире за $10,000».", "money": 1, "int": 20, "color": GRAY,
     "rsn": "Дорого-богато"},
    {"text": "Реклама: «Удали жир за 5 минут с помощью соды».", "money": 3, "int": -25, "color": GOLD,
     "rsn": "Вредные советы"},
    {"text": "Спор: «Android или iPhone? Срач в комментариях».", "money": 0, "int": 35, "color": RED, "rsn": "Холивар"},
    {"text": "АСМР: Нарезание мыла на тонкие слайсы.", "money": 0, "int": 35, "color": BLUE, "rsn": "Классика АСМР"},
    {"text": "POV: Ты проснулся внутри видеоигры 90-х.", "money": 0, "int": 20, "color": GRAY, "rsn": "Ретро-вайб"},
    {"text": "Реклама: «Секретная кнопка 'Бабло' в твоем смартфоне».", "money": 10, "int": -60, "color": GOLD,
     "rsn": "Финальный босс скама"},
    {"text": "Мнение: «Почему Луна — это голограмма правительства».", "money": 0, "int": 15, "color": RED,
     "rsn": "Безумие"},
    {"text": "Туториал: «Как заработать миллион на продаже воздуха».", "money": 0, "int": 10, "color": GRAY,
     "rsn": "Ирония"},
    {"text": "Подборка: «Животные, которые ведут себя как гопники».", "money": 0, "int": 40, "color": BLUE,
     "rsn": "Милота и смех"}
]


def draw_text_centered(surf, text, font_obj, color, x, y, max_w=None):
    if max_w:
        words = text.split(' ')
        lines, cur = [], ""
        for w in words:
            if font_obj.size(cur + w)[0] < max_w:
                cur += w + " "
            else:
                lines.append(cur.strip());
                cur = w + " "
        lines.append(cur.strip())
        th = len(lines) * (font_obj.get_height() + 5)
        sy = y - th // 2
        for i, l in enumerate(lines):
            t = font_obj.render(l, True, color)
            surf.blit(t, (x - t.get_width() // 2, sy + i * (font_obj.get_height() + 5)))
    else:
        t = font_obj.render(text, True, color)
        surf.blit(t, (x - t.get_width() // 2, y - t.get_height() // 2))


def draw_button(surf, rect, color, text, scale):
    w, h = int(rect.width * scale), int(rect.height * scale)
    dr = pygame.Rect(rect.centerx - w // 2, rect.centery - h // 2, w, h)
    pygame.draw.rect(surf, color, dr, border_radius=15)
    pygame.draw.rect(surf, WHITE, dr, width=3, border_radius=15)
    t = pygame.font.SysFont("Arial", int(20 * scale), bold=True).render(text, True, WHITE)
    surf.blit(t, (dr.centerx - t.get_width() // 2, dr.centery - t.get_height() // 2))


# !!! ДЛЯ WEB !!! Весь запуск игры оборачиваем в асинхронную функцию
async def main():
    # --- СОСТОЯНИЕ ---
    interest, money, game_over, game_started = 100.0, 0, False, False
    float_fx, reason_fx_left, reason_fx_right = [], [], []
    btn_skip_scale, btn_show_scale, btn_start_scale = 1.0, 1.0, 1.0
    shake = 0

    current_card = random.choice(cards_db)
    card_pos = pygame.Vector2(50, 160)
    card_target = pygame.Vector2(50, 160)
    card_in_motion = False

    # --- ЦИКЛ ---
    running = True
    while running:
        game_scene = pygame.Surface((WIDTH, HEIGHT))
        if bg_img:
            game_scene.blit(bg_img, (0, 0))
        else:
            game_scene.fill(BLACK)

        pygame.draw.rect(game_scene, (40, 40, 40), (50, 40, 400, 25), border_radius=10)
        bar_w = int(max(0, min(100, interest)) * 4)
        pygame.draw.rect(game_scene, GREEN if interest > 30 else RED, (50, 40, bar_w, 25), border_radius=10)
        game_scene.blit(small_font.render(f"УДЕРЖАНИЕ: {int(interest)}%", True, WHITE), (50, 15))
        draw_text_centered(game_scene, f"ПРИБЫЛЬ: {money} ₽", font, GOLD, WIDTH // 2, 100)

        m_pos, m_click = pygame.mouse.get_pos(), pygame.mouse.get_pressed()[0]

        if not game_started:
            blur = pygame.transform.smoothscale(game_scene, (WIDTH // 10, HEIGHT // 10))
            screen.blit(pygame.transform.smoothscale(blur, (WIDTH, HEIGHT)), (0, 0))
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            btn_start_rect = pygame.Rect(WIDTH // 2 - 110, HEIGHT // 2 + 60, 220, 80)
            t_start = 0.85 if btn_start_rect.collidepoint(m_pos) and m_click else 1.0
            btn_start_scale += (t_start - btn_start_scale) * 0.2
            draw_text_centered(screen, "АЛГОРИТМУС", title_font, GOLD, WIDTH // 2, HEIGHT // 2 - 110)
            draw_text_centered(screen, "Готовы завлекать внимание", medium_font, WHITE, WIDTH // 2, HEIGHT // 2 - 40)
            draw_text_centered(screen, "пользователя?", medium_font, WHITE, WIDTH // 2, HEIGHT // 2 + 5)
            draw_button(screen, btn_start_rect, BLUE, "ЗАПУСТИТЬ", btn_start_scale)

        elif not game_over:
            screen.blit(game_scene, (0, 0))

            diff = card_target - card_pos
            if diff.length() > 2:
                card_pos += diff * (0.25 if card_in_motion else 0.15)
            else:
                if card_in_motion:
                    current_card = random.choice(cards_db)
                    card_pos = pygame.Vector2(50, HEIGHT + 100)
                    card_target = pygame.Vector2(50, 160)
                    card_in_motion = False

            pygame.draw.rect(screen, WHITE, (card_pos.x, card_pos.y, 400, 210), border_radius=20)
            pygame.draw.rect(screen, current_card["color"], (card_pos.x, card_pos.y, 400, 50),
                             border_top_left_radius=20,
                             border_top_right_radius=20)
            draw_text_centered(screen, current_card["text"], font, BLACK, card_pos.x + 200, card_pos.y + 130, 360)

            # Логика доступности кнопок (нажатие разрешено только в центре)
            is_ready = (card_pos - card_target).length() < 5 and not card_in_motion

            btn_skip_rect = pygame.Rect(50, 510, 180, 65)
            btn_show_rect = pygame.Rect(270, 510, 180, 65)

            t_skip = 0.85 if is_ready and btn_skip_rect.collidepoint(m_pos) and m_click else 1.0
            t_show = 0.85 if is_ready and btn_show_rect.collidepoint(m_pos) and m_click else 1.0

            btn_skip_scale += (t_skip - btn_skip_scale) * 0.2
            btn_show_scale += (t_show - btn_show_scale) * 0.2

            draw_button(screen, btn_skip_rect, RED, "ПРОПУСТИТЬ", btn_skip_scale)
            draw_button(screen, btn_show_rect, GREEN, "ПОКАЗАТЬ", btn_show_scale)

            interest -= 0.045
            if interest <= 0:
                interest, game_over, shake = 0, True, 20
                if s_fail: s_fail.play()

        else:
            # ЭКРАН ПРОИГРЫША
            screen.blit(game_scene, (0, 0))
            panel_w, panel_h = 400, 420
            panel_rect = pygame.Rect(WIDTH // 2 - panel_w // 2, HEIGHT // 2 - panel_h // 2 - 10, panel_w, panel_h)
            pygame.draw.rect(screen, WHITE, panel_rect, border_radius=30)

            if skull_img: screen.blit(skull_img, (WIDTH // 2 - 70, panel_rect.top + 30))

            st_text = "ПОЛЬЗОВАТЕЛЬ УБРАЛ ТЕЛЕФОН" if money < 100 else "АЛГОРИТМ ПОТЕРЯЛ ТРАФИК"
            draw_text_centered(screen, st_text, small_font, RED, WIDTH // 2, panel_rect.top + 210)
            draw_text_centered(screen, "ИТОГОВАЯ:", tiny_font, GRAY, WIDTH // 2, panel_rect.top + 255)
            draw_text_centered(screen, f"{money} ₽", medium_font, YELLOW, WIDTH // 2, panel_rect.top + 295)

            btn_restart_rect = pygame.Rect(WIDTH // 2 - 125, panel_rect.bottom - 75, 250, 60)
            pygame.draw.rect(screen, BLACK, btn_restart_rect, border_radius=15)
            draw_text_centered(screen, "ПЕРЕЗАГРУЗКА", small_font, WHITE, WIDTH // 2, btn_restart_rect.centery)

        if game_started and not game_over:
            for fx in float_fx[:]:
                fx.update();
                fx.draw(screen)
                if fx.alpha <= 0: float_fx.remove(fx)
            for i, rfx in enumerate(reason_fx_left[:]):
                rfx.update(i);
                rfx.draw(screen)
                if rfx.life <= 0: reason_fx_left.remove(rfx)
            for i, rfx in enumerate(reason_fx_right[:]):
                rfx.update(i);
                rfx.draw(screen)
                if rfx.life <= 0: reason_fx_right.remove(rfx)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if not game_started:
                    if btn_start_rect.collidepoint(m_pos):
                        if s_click: s_click.play()
                        game_started = True
                elif not game_over:
                    # Нажимать можно только когда карточка доехала (READY)
                    is_ready = (card_pos - card_target).length() < 5 and not card_in_motion
                    if is_ready:
                        if btn_show_rect.collidepoint(m_pos):
                            if s_click: s_click.play()
                            money += current_card["money"];
                            interest += current_card["int"]
                            if interest > 100: interest = 100
                            if current_card["money"] > 0: float_fx.append(
                                FloatEffect(f"+{current_card['money']} ₽", 360, 480, GOLD, 0))
                            float_fx.append(FloatEffect(f"{current_card['int']}% Инт.", 360, 480,
                                                        GREEN if current_card['int'] > 0 else RED, 22))
                            reason_fx_right.insert(0, ReasonBox(current_card["rsn"], 360, 580, current_card["color"]))
                            card_target = pygame.Vector2(WIDTH + 500, 160);
                            card_in_motion = True
                        elif btn_skip_rect.collidepoint(m_pos):
                            if s_click: s_click.play()
                            interest -= 5;
                            float_fx.append(FloatEffect("-5% Скука", 140, 480, RED, 0))
                            reason_fx_left.insert(0, ReasonBox("Пропущено", 140, 580, GRAY))
                            card_target = pygame.Vector2(-500, 160);
                            card_in_motion = True
                elif game_over:
                    btn_res = pygame.Rect(WIDTH // 2 - 125, panel_rect.bottom - 75, 250, 60)
                    if btn_res.collidepoint(m_pos):
                        if s_restart: s_restart.play()
                        interest, money, game_over = 100.0, 0, False
                        current_card = random.choice(cards_db)
                        card_pos, card_target = pygame.Vector2(50, 160), pygame.Vector2(50, 160)
                        card_in_motion = False
                        float_fx, reason_fx_left, reason_fx_right = [], [], []

        s_off = [random.randint(-shake, shake), random.randint(-shake, shake)] if shake > 0 else [0, 0]
        if shake > 0: shake -= 1
        temp = screen.copy()
        screen.fill(BLACK)
        screen.blit(temp, s_off)
        pygame.display.flip()

        await asyncio.sleep(0)  # !!! ДЛЯ WEB !!! Критически важная строка, дает браузеру работать
        clock.tick(60)

    pygame.quit()


# !!! ДЛЯ WEB !!! Запуск асинхронной функции
asyncio.run(main())