"""Simple Snake game implementation using Tkinter.

Run this module directly to start the game::

    python snake_game.py

Use the arrow keys or WASD to control the snake. Collect the food to grow
longer and avoid colliding with the walls or the snake's own body.
"""

from __future__ import annotations

import random
import tkinter as tk
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class Point:
    """Represents a position on the grid."""

    x: int
    y: int


class SnakeGame:
    """Tkinter based Snake game."""

    def __init__(
        self,
        width: int = 24,
        height: int = 18,
        cell_size: int = 24,
        initial_speed_ms: int = 150,
    ) -> None:
        self.grid_width = width
        self.grid_height = height
        self.cell_size = cell_size
        self.initial_speed_ms = initial_speed_ms
        self.speed_ms = initial_speed_ms

        self.window = tk.Tk()
        self.window.title("Snake Game")
        self.window.resizable(False, False)

        self.score_var = tk.StringVar(value="Score: 0")
        score_label = tk.Label(
            self.window,
            textvariable=self.score_var,
            font=("Helvetica", 14),
            anchor="w",
        )
        score_label.pack(fill=tk.X, padx=10, pady=(10, 0))

        canvas_width = self.grid_width * self.cell_size
        canvas_height = self.grid_height * self.cell_size
        self.canvas = tk.Canvas(
            self.window,
            width=canvas_width,
            height=canvas_height,
            bg="#1e1e1e",
        )
        self.canvas.pack(padx=10, pady=10)

        self.window.bind("<Up>", lambda _event: self.change_direction(Point(0, -1)))
        self.window.bind("<Down>", lambda _event: self.change_direction(Point(0, 1)))
        self.window.bind("<Left>", lambda _event: self.change_direction(Point(-1, 0)))
        self.window.bind("<Right>", lambda _event: self.change_direction(Point(1, 0)))
        self.window.bind("w", lambda _event: self.change_direction(Point(0, -1)))
        self.window.bind("s", lambda _event: self.change_direction(Point(0, 1)))
        self.window.bind("a", lambda _event: self.change_direction(Point(-1, 0)))
        self.window.bind("d", lambda _event: self.change_direction(Point(1, 0)))
        self.window.bind("<space>", lambda _event: self.reset())

        self.running = True
        self.score = 0
        self.snake: List[Point] = []
        self.direction = Point(1, 0)
        self.food = Point(0, 0)

        self.reset()

    def reset(self) -> None:
        """Reset the game state to start a new game."""

        self.running = True
        self.score = 0
        self.speed_ms = self.initial_speed_ms
        self.direction = Point(1, 0)
        center_x = self.grid_width // 2
        center_y = self.grid_height // 2
        self.snake = [Point(center_x, center_y)]
        self.score_var.set("Score: 0")
        self.spawn_food()
        self.draw()

    def spawn_food(self) -> None:
        """Place food in a random empty grid cell."""

        available = {
            Point(x, y)
            for x in range(self.grid_width)
            for y in range(self.grid_height)
        } - set(self.snake)
        if not available:
            # Player filled the board - treat as win state.
            self.running = False
            self.score_var.set(f"Score: {self.score} (You win!)")
            return
        self.food = random.choice(tuple(available))

    def change_direction(self, new_direction: Point) -> None:
        """Update the snake's direction if it isn't opposite to current."""

        if not self.running:
            return
        head = self.snake[0]
        next_pos = Point(head.x + new_direction.x, head.y + new_direction.y)
        if len(self.snake) > 1 and next_pos == self.snake[1]:
            return
        self.direction = new_direction

    def step(self) -> None:
        """Advance the game state by one tick."""

        if not self.running:
            return

        head = self.snake[0]
        new_head = Point(head.x + self.direction.x, head.y + self.direction.y)

        hit_wall = not (
            0 <= new_head.x < self.grid_width
            and 0 <= new_head.y < self.grid_height
        )
        hit_self = new_head in self.snake

        if hit_wall or hit_self:
            self.running = False
            self.score_var.set(f"Score: {self.score} (Game Over - press Space)")
            return

        self.snake.insert(0, new_head)

        if new_head == self.food:
            self.score += 1
            self.score_var.set(f"Score: {self.score}")
            # Slightly speed up to increase difficulty, but cap at reasonable speed.
            self.speed_ms = max(60, int(self.speed_ms * 0.95))
            self.spawn_food()
        else:
            self.snake.pop()

        self.draw()

    def draw(self) -> None:
        """Render the current game state to the canvas."""

        self.canvas.delete("all")

        # Draw food.
        self._draw_cell(self.food, fill="#d94e41")

        # Draw snake.
        for index, segment in enumerate(self.snake):
            color = "#68c44a" if index else "#4a9d31"
            self._draw_cell(segment, fill=color)

    def _draw_cell(self, point: Point, fill: str) -> None:
        x1 = point.x * self.cell_size
        y1 = point.y * self.cell_size
        x2 = x1 + self.cell_size
        y2 = y1 + self.cell_size
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline="#1a1a1a")

    def game_loop(self) -> None:
        """Main loop that advances the game at fixed intervals."""

        self.step()
        delay = self.speed_ms if self.running else 200
        self.window.after(delay, self.game_loop)

    def run(self) -> None:
        """Start the Tkinter main loop."""

        self.window.after(self.speed_ms, self.game_loop)
        self.window.mainloop()


def main() -> None:
    SnakeGame().run()


if __name__ == "__main__":
    main()
