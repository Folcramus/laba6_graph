
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

# Переменные
points = []
edges = []
hull_edges = []
current_edge_index = 0
mode = "setup"  # "setup" или "visualization"
font = pygame.font.SysFont('Arial', 24)


def ccw(a, b, c):
    """Проверка ориентации трех точек (a, b, c)"""
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def is_edge_on_hull(edge, points):
    """Проверяет, является ли ребро частью выпуклой оболочки"""
    a, b = edge
    side = None
    for p in points:
        if p == a or p == b:
            continue

        cross = ccw(a, b, p)
        if cross == 0:  # Точка на прямой
            if (min(a[0], b[0]) <= p[0] <= max(a[0], b[0])) and \
                    (min(a[1], b[1]) <= p[1] <= max(a[1], b[1])):
                return False
        else:
            if side is None:
                side = cross > 0
            elif (cross > 0) != side:
                return False
    return True


def prepare_visualization():
    """Подготавливает данные для визуализации"""
    global edges, hull_edges, current_edge_index, mode
    if len(points) < 2:
        return

    edges = list(itertools.combinations(points, 2))
    hull_edges = []
    current_edge_index = 0
    mode = "visualization"


def next_step():
    """Переход к следующему шагу визуализации"""
    global current_edge_index, hull_edges

    if current_edge_index < len(edges):
        edge = edges[current_edge_index]
        if is_edge_on_hull(edge, points):
            hull_edges.append(edge)
        current_edge_index += 1


def draw_points():
    """Отрисовка точек"""
    for point in points:
        pygame.draw.circle(screen, BLACK, point, 5)
        pygame.draw.circle(screen, RED, point, 4)


def draw_hull():
    """Отрисовка выпуклой оболочки"""
    if len(hull_edges) > 0:
        for edge in hull_edges:
            pygame.draw.line(screen, BLUE, edge[0], edge[1], 3)

        # Рисуем точки оболочки зеленым
        hull_points = set()
        for edge in hull_edges:
            hull_points.add(edge[0])
            hull_points.add(edge[1])

        for point in hull_points:
            pygame.draw.circle(screen, GREEN, point, 6)
            pygame.draw.circle(screen, BLACK, point, 5)


def draw_current_edge():
    """Отрисовка текущего проверяемого ребра"""
    if 0 <= current_edge_index < len(edges):
        edge = edges[current_edge_index]
        pygame.draw.line(screen, YELLOW, edge[0], edge[1], 2)

        # Подсвечиваем точки текущего ребра
        pygame.draw.circle(screen, YELLOW, edge[0], 8)
        pygame.draw.circle(screen, YELLOW, edge[1], 8)


def draw_info():
    """Отрисовка информации о состоянии"""
    if mode == "setup":
        text = font.render("Режим расстановки точек. Нажмите SPACE для начала визуализации", True, BLACK)
    else:
        text = font.render(f"Шаг {current_edge_index + 1}/{len(edges)}. Нажмите SPACE для следующего шага", True, BLACK)

    screen.blit(text, (10, 10))

    # Инструкция
    instructions = [
        "ЛКМ: Добавить точку",
        "R: Сбросить все точки",
        "SPACE: Начать/следующий шаг"
    ]

    for i, instr in enumerate(instructions):
        text = font.render(instr, True, BLACK)
        screen.blit(text, (10, 40 + i * 30))


# Основной цикл
clock = pygame.time.Clock()
running = True
while running:
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and mode == "setup":  # ЛКМ - добавить точку
                points.append(event.pos)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:  # R - сбросить
                points = []
                mode = "setup"
            elif event.key == pygame.K_SPACE:  # Пробел - следующий шаг
                if mode == "setup":
                    prepare_visualization()
                else:
                    next_step()

    # Отрисовка
    draw_points()

    if mode == "visualization":
        draw_current_edge()
        draw_hull()

    draw_info()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()

