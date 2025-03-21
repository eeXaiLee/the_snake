import sys
from random import choice

import pygame

SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

DIRECTION_CHANGE = {
    pygame.K_UP: (UP, DOWN),
    pygame.K_DOWN: (DOWN, UP),
    pygame.K_LEFT: (LEFT, RIGHT),
    pygame.K_RIGHT: (RIGHT, LEFT)
}

INVALID_POSITION = (-1, -1)

BOARD_BACKGROUND_COLOR = (0, 0, 0)


BORDER_COLOR = (93, 216, 228)

APPLE_COLOR = (255, 0, 0)

SNAKE_COLOR = (0, 255, 0)

SPEED = 10

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

pygame.display.set_caption('Змейка')

clock = pygame.time.Clock()


class GameObject:
    """Базовый тип объектов, используемых в игре."""

    def __init__(self) -> None:
        """Инициализирует объект с начальной позицией и цветом."""
        self.position = ((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))
        self.body_color = BOARD_BACKGROUND_COLOR

    def draw_cell(
            self,
            position: tuple[int, int],
            color: tuple[int, int, int],
            cell_boundary: bool = True
    ) -> None:
        """Отрисовывает одну ячейку объекта.

        Args:
            position (tuple[int, int]): Позиция ячейки.
            color (tuple[int, int, int]): Цвет ячейки.
            cell_boundary (bool): Нужно ли отрисовывать границу ячейки.
        """
        rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, color, rect)
        if cell_boundary:
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

    def draw(self) -> None:
        """Отображает объект на игровом поле."""


class Apple(GameObject):
    """Съедобный объект(яблоко).

    При попадании головы змейки на позицию яблока, длина змейки увеличивается,
    а яблоко перемещается на новую случайную позицию, исключая занятые змейкой
    клетки.
    """

    def __init__(
            self,
            color: tuple[int, int, int] = APPLE_COLOR,
            occupied_positions: list[tuple[int, int]] | None = None
    ) -> None:
        """Инициализирует яблоко с заданным цветом и позицией.

        Args:
            color (tuple[int, int, int]): Цвет яблока.
            occupied_positions (list | None): Список занятых позиций.
        """
        super().__init__()
        self.body_color = color
        self.randomize_position(occupied_positions)

    def randomize_position(
            self,
            occupied_positions: list[tuple[int, int]] | None = None
    ) -> None:
        """Генерирует новую позицию яблока.

        Исключает занятые змейкой клетки для предотвращения наложения объектов.

        Args:
            occupied_positions (list | None): Список занятых змейкой позиций.
        """
        if occupied_positions is None:
            occupied_positions = [self.position]

        occupied = set(occupied_positions)

        while True:
            x = choice(range(0, SCREEN_WIDTH, GRID_SIZE))
            y = choice(range(0, SCREEN_HEIGHT, GRID_SIZE))
            if (x, y) not in occupied:
                self.position = (x, y)
                break

    def draw(self) -> None:
        """Отрисовка яблока на игровом поле."""
        self.draw_cell(self.position, self.body_color)


class Snake(GameObject):
    """Игровой объект(змейка).

    Змейка управляется стрелками клавиатуры и перемещается по игровому полю.
    При поедании яблок длина змейки увеличивается. При столкновении с собой
    змейка сбрасывается в начальное состояние.
    """

    def __init__(self, color: tuple[int, int, int] = SNAKE_COLOR) -> None:
        """Инициализирует змейку с заданным цветом и начальной позицией.

        Args:
            color (tuple[int, int, int]): Цвет змейки.
        """
        super().__init__()
        self.reset()
        self.body_color = color
        self.last = INVALID_POSITION

    def update_direction(
            self,
            next_direction: tuple[int, int] | None
    ) -> None:
        """Обновляет текущее направление движения змейки.

        Args:
            next_direction (tuple[int, int] | None): Новое направление.
        """
        if next_direction:
            self.direction = next_direction

    def move(self) -> None:
        """Перемещает змейку в соответствии с текущим направлением."""
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction
        new_head_position = (
            (head_x + dx * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT
        )
        self.positions.insert(0, new_head_position)
        if len(self.positions) > self.length + 1:
            self.last = self.positions.pop()
        else:
            self.last = INVALID_POSITION

    def draw(self) -> None:
        """Отрисовывает тело и голову змейки.

        Затирает след от предыдущего положения при перемещении.
        """
        for position in self.positions[:-1]:
            self.draw_cell(position, self.body_color)

        self.draw_cell(
            self.get_head_position(),
            self.body_color
        )

        if self.last != INVALID_POSITION:
            self.draw_cell(self.last,
                           BOARD_BACKGROUND_COLOR,
                           False)

    def get_head_position(self) -> tuple[int, int]:
        """Возвращает позицию головы змейки.

        Returns:
            tuple[int, int]: Позиция головы змейки
        """
        return self.positions[0]

    def reset(self) -> None:
        """Сбрасывает змейку в начальное состояние."""
        self.length = 1
        self.positions = [self.position]
        self.direction = choice([UP, DOWN, LEFT, RIGHT])


class GameExit(Exception):
    """Завершение игры."""


def handle_keys(game_object: 'Snake') -> tuple | None:
    """Обрабатывает нажатия клавиш для управления змейкой.

    Args:
        game_object (Snake): Объект змейки, которым управляет игрок.

    Returns:
        tuple | None: Новое направление движения змейки или None, если
        направление не изменилось.

    Raises:
        GameExit: Если игрок закрывает окно игры.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            raise GameExit

        elif event.type == pygame.KEYDOWN:
            current_direction = game_object.direction
            next_direction, forbidden_direction = DIRECTION_CHANGE.get(
                event.key, (current_direction, current_direction)
            )
            if current_direction != forbidden_direction:
                return next_direction
    return None


def main() -> None:
    """Основной игровой цикл."""
    pygame.init()

    apple = Apple()
    snake = Snake()

    try:
        while True:
            clock.tick(SPEED)

            try:
                next_direction = handle_keys(snake)
            except GameExit:
                sys.exit('Игра завершена пользователем.')
            snake.update_direction(next_direction)
            snake.move()

            head_position = snake.get_head_position()
            if head_position == apple.position:
                snake.length += 1
                apple.randomize_position(snake.positions)

            if head_position in snake.positions[1:]:
                snake.reset()
                apple.randomize_position(snake.positions)

            screen.fill(BOARD_BACKGROUND_COLOR)
            apple.draw()
            snake.draw()

            pygame.display.update()
    finally:
        pygame.quit()


if __name__ == '__main__':
    main()
