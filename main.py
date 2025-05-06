import pygame
import sys
import itertools
import math

# Инициализация Pygame
pygame.init()

# Настройки окна
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Выпуклая оболочка - Алгоритм полного перебора")

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
GRAY = (200, 200, 200)

# Переменные для хранения точек и рёбер
points = []              # Список всех точек
edges = []               # Все возможные пары точек (кандидаты на рёбра)
hull_edges = []          # Рёбра, входящие в выпуклую оболочку
current_edge_index = 0   # Индекс текущего ребра, которое проверяется
mode = "setup"           # Режим: "setup" — расстановка точек, "visualization" — шаги алгоритма
font = pygame.font.SysFont('Arial', 24)

# Функция ccw (counter-clockwise) вычисляет ориентацию трёх точек:
# > 0: точка c слева от AB
# < 0: точка c справа от AB
# = 0: точка лежит на одной прямой с AB
def ccw(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])

# Проверяет, является ли данное ребро частью выпуклой оболочки
# Алгоритм: проверяет, лежат ли все остальные точки по одну сторону от прямой AB
def is_edge_on_hull(edge, points):
    a, b = edge
    side = None  # запоминаем сторону, на которой лежит первая точка

    for p in points:
        if p == a or p == b:
            continue  # не проверяем сами точки ребра

        cross = ccw(a, b, p)

        if cross == 0:
            # Точка лежит на прямой AB
            # Проверяем, не находится ли она строго между A и B — тогда это не край оболочки
            if (min(a[0], b[0]) <= p[0] <= max(a[0], b[0])) and \
               (min(a[1], b[1]) <= p[1] <= max(a[1], b[1])):
                return False
        else:
            if side is None:
                side = cross > 0  # первая "сторона"
            elif (cross > 0) != side:
                # Найдена точка с другой стороны — ребро не часть оболочки
                return False

    # Если все точки по одну сторону или на прямой, это ребро входит в выпуклую оболочку
    return True

# Подготовка к визуализации: перебираем все пары точек и сбрасываем прогресс
def prepare_visualization():
    global edges, hull_edges, current_edge_index, mode
    if len(points) < 2:
        return

    # Все возможные пары точек (C(N, 2))
    edges = list(itertools.combinations(points, 2))
    hull_edges = []              # сбрасываем оболочку
    current_edge_index = 0       # начинаем с первого ребра
    mode = "visualization"       # включаем режим визуализации

# Следующий шаг алгоритма: проверка следующего ребра на принадлежность оболочке
def next_step():
    global current_edge_index, hull_edges

    if current_edge_index < len(edges):
        edge = edges[current_edge_index]
        if is_edge_on_hull(edge, points):
            hull_edges.append(edge)  # если ребро подходит — добавляем
        current_edge_index += 1      # переходим к следующему

# Рисует все точки на экране
def draw_points():
    for point in points:
        pygame.draw.circle(screen, BLACK, point, 5)
        pygame.draw.circle(screen, RED, point, 4)

# Рисует рёбра выпуклой оболочки и выделяет вершины оболочки зелёным
def draw_hull():
    if len(hull_edges) > 0:
        for edge in hull_edges:
            pygame.draw.line(screen, BLUE, edge[0], edge[1], 3)

        # Получаем уникальные точки оболочки
        hull_points = set()
        for edge in hull_edges:
            hull_points.add(edge[0])
            hull_points.add(edge[1])

        # Рисуем их зелёным
        for point in hull_points:
            pygame.draw.circle(screen, GREEN, point, 6)
            pygame.draw.circle(screen, BLACK, point, 5)

# Отрисовывает текущее обрабатываемое ребро (жёлтым)
def draw_current_edge():
    if 0 <= current_edge_index < len(edges):
        edge = edges[current_edge_index]
        pygame.draw.line(screen, YELLOW, edge[0], edge[1], 2)

        # Подсветка концов ребра
        pygame.draw.circle(screen, YELLOW, edge[0], 8)
        pygame.draw.circle(screen, YELLOW, edge[1], 8)

# Отображает информационный текст и инструкции
def draw_info():
    if mode == "setup":
        text = font.render("Режим расстановки точек. Нажмите SPACE для начала визуализации", True, BLACK)
    else:
        text = font.render(f"Шаг {current_edge_index + 1}/{len(edges)}. Нажмите SPACE для следующего шага", True, BLACK)

    screen.blit(text, (10, 10))

    # Инструкции управления
    instructions = [
        "ЛКМ: Добавить точку",
        "R: Сбросить все точки",
        "SPACE: Начать/следующий шаг"
    ]

    for i, instr in enumerate(instructions):
        text = font.render(instr, True, BLACK)
        screen.blit(text, (10, 40 + i * 30))

# Основной цикл программы
clock = pygame.time.Clock()
running = True
while running:
    screen.fill(WHITE)  # Очистка экрана

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False  # Закрытие окна
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and mode == "setup":
                points.append(event.pos)  # Добавление точки по клику
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                # Сброс состояния
                points = []
                mode = "setup"
            elif event.key == pygame.K_SPACE:
                # Пробел: старт или переход к следующему шагу
                if mode == "setup":
                    prepare_visualization()
                else:
                    next_step()

    # Отрисовка всех элементов
    draw_points()

    if mode == "visualization":
        draw_current_edge()
        draw_hull()

    draw_info()
    pygame.display.flip()
    clock.tick(60)

# Завершение Pygame
pygame.quit()
sys.exit()
