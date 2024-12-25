import pathlib
import random
import typing as tp

import pygame
from pygame.locals import *

Cell = tp.Tuple[int, int]
Cells = tp.List[int]
Grid = tp.List[Cells]


class GameOfLife:
    def __init__(
        self,
        size: tp.Tuple[int, int],
        randomize: bool = True,
        max_generations: tp.Optional[float] = float("inf"),
    ) -> None:
        # Размер клеточного поля
        self.rows, self.cols = size
        # Предыдущее поколение клеток
        self.prev_generation = self.create_grid()
        # Текущее поколение клеток
        self.curr_generation = self.create_grid(randomize=randomize)
        # Максимальное число поколений
        self.max_generations = max_generations
        # Текущее число поколений
        self.generations = 1

    def create_grid(self, randomize: bool = False) -> Grid:
        return [[random.randint(0, randomize) for _ in range(self.cols)] for _ in range(self.rows)]

    def get_neighbours(self, cell: Cell) -> Cells:
        y, x = cell
        return [
            self.curr_generation[i][j]
            for i in range(max(y - 1, 0), min(y + 1, self.rows - 1) + 1)
            for j in range(max(x - 1, 0), min(x + 1, self.cols - 1) + 1)
            if (i, j) != (y, x)
        ]

    def get_next_generation(self) -> Grid:
        new_grid = self.create_grid()

        for y, row in enumerate(self.curr_generation):
            for x, cell in enumerate(row):
                match cell:
                    case 0:
                        new_grid[y][x] = sum(self.get_neighbours((y, x))) == 3
                    case 1:
                        new_grid[y][x] = sum(self.get_neighbours((y, x))) in (2, 3)
        return new_grid

    def step(self) -> None:
        """
        Выполнить один шаг игры.
        """
        if not self.is_max_generations_exceeded and self.is_changing:
            self.prev_generation = self.curr_generation
            self.curr_generation = self.get_next_generation()
            self.generations += 1

    @property
    def is_max_generations_exceeded(self) -> bool:
        """
        Не превысило ли текущее число поколений максимально допустимое.
        """
        return self.max_generations is not None and self.generations >= self.max_generations

    @property
    def is_changing(self) -> bool:
        """
        Изменилось ли состояние клеток с предыдущего шага.
        """
        return self.prev_generation != self.curr_generation

    @staticmethod
    def from_file(filename: pathlib.Path) -> "GameOfLife":
        """
        Прочитать состояние клеток из указанного файла.
        """
        with open(filename, "rb") as f:
            file = f.readlines()
            grid = []
            for _, row in enumerate(file):
                if (49 in row) or (48 in row):
                    rw = []
                for _, val in enumerate(row):
                    if val == 49 or val == 48:
                        rw.append(int(chr(val)))
                grid.append(rw)
            print(grid)
            game = GameOfLife((len(grid), len(grid[0])), randomize=False)
            game.curr_generation = grid
            return game

    def save(self, filename: pathlib.Path) -> None:
        """
        Сохранить текущее состояние клеток в указанный файл
        """
        try:
            with open(filename, "w") as f:
                for _, row in enumerate(self.curr_generation):
                    for _, val in enumerate(row):
                        f.write(str(val) + " ")
                    f.write("\n")
            f.close()
        except Exception as e:
            print("Error saving file", e)
