from __future__ import annotations
import json
import pygame
import pygame.locals
import tkinter
import tkinter.filedialog


def prompt_file(l=False):
    top = tkinter.Tk()
    top.withdraw()
    if l:
        file_name = tkinter.filedialog.askopenfilename(
            parent=top)
    else:
        file_name = tkinter.filedialog.asksaveasfilename(
            parent=top, defaultextension=".life")

    top.destroy()
    if file_name:
        return file_name
    return False


window_width, window_height = 800, 800

GRID_SIZE = 20

pygame.init()
screen = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Life")
clock = pygame.time.Clock()


class Cell:
    def __init__(self, alive=False) -> None:
        self.alive = alive
        self.should_change = False

    def toggle(self):
        self.alive = not self.alive

    def step(self):
        if self.should_change:
            self.should_change = False
            self.toggle()

    def process_nb(self, nb: list[bool]):
        if self.alive:
            self.should_change = True
            if nb.count(True) in [2, 3]:
                self.should_change = False

        else:
            self.should_change = False
            if nb.count(True) == 3:
                self.should_change = True


class Life:
    def __init__(self):
        self.reset()

    def new_board(self):
        return [Cell() for n in range((window_width//GRID_SIZE)*(window_height//GRID_SIZE))]

    def save_board(self, file_name):
        data = [cell.alive for cell in self.board]
        with open(file_name, "w") as f:
            json.dump(data, f, indent=4)

    def load_board(self, file_name):
        with open(file_name, "r") as f:
            data = json.load(f)
        self.reset()
        for idx, alive in enumerate(data):
            self.board[idx].alive = alive

    def reset(self):
        self.board = self.new_board()
        self.steps = 0

    def get_rects(self) -> list[pygame.Rect]:
        rects = []
        for idx, c in enumerate(self.board):
            x, y = self.__idx_to_x_y(idx)
            rects.append(pygame.Rect(x*GRID_SIZE,
                                     y*GRID_SIZE, GRID_SIZE, GRID_SIZE))
        return rects

    def draw_to(self, surface):
        colors = [(60, 60, 60), (220, 220, 220)]
        for idx, r in enumerate(self.get_rects()):
            pygame.draw.rect(surface, colors[self.board[idx].alive], r)

    def __idx_to_x_y(self, idx):
        x = idx % (window_width//GRID_SIZE)
        y = idx//(window_height//GRID_SIZE)
        return x, y

    def __x_y_to_idx(self, x, y):
        return x + y*GRID_SIZE*2

    def get_nb(self, idx):
        x, y = self.__idx_to_x_y(idx)

        # -1,-1  0,-1  1,-1
        # -1,0   0,0   1,0
        # -1,1   0,1   1,1

        m = [[-1, -1], [0, -1], [1, -1], [-1, 0],
             [1, 0], [-1, 1],   [0, 1],   [1, 1]]

        nb = []
        for x2, y2 in m:
            nx, ny = x+x2, y+y2
            if nx < 0 or ny < 0:
                continue
            if nx > (window_width//GRID_SIZE)-1 or ny > (window_height//GRID_SIZE)-1:
                continue

            ni = self.__x_y_to_idx(nx, ny)
            nb.append(self.board[ni].alive)

        return nb

    def step_simulation(self):
        for idx, c in enumerate(self.board):
            self.board[idx].process_nb(self.get_nb(idx))

        for idx, c in enumerate(self.board):
            self.board[idx].step()

        self.steps += 1


def simple_grid():
    for x in range(0, window_width, GRID_SIZE):
        pygame.draw.line(screen, (33, 33, 33), (x, 0), (x, window_height))

    for y in range(0, window_height, GRID_SIZE):
        pygame.draw.line(screen, (33, 33, 33), (0, y), (window_width, y))


def change_title(text):
    pygame.display.set_caption(f"Life{text}")


life = Life()

run = True
play = False


class Dif:
    def __init__(self, d=60):
        self.d = d
        self.reset()

    def inc_d(self, val):
        self.d += val
        self.d = max(0, self.d)

    def reset(self):
        self.c = self.d

    def woop(self):
        self.c -= 1

    def __lt__(self, other):
        return self.c < other


cc = Dif(15)
while run:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        elif event.type == pygame.MOUSEBUTTONUP and not play:
            pos = pygame.mouse.get_pos()

            for idx, r in enumerate(life.get_rects()):
                if r.collidepoint(pos):
                    life.board[idx].toggle()
                    life.get_nb(idx)
                    break

        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_s and event.mod & pygame.KMOD_CTRL:
                file_name = prompt_file()
                if file_name:
                    life.save_board(file_name)

            elif event.key == pygame.K_l and event.mod & pygame.KMOD_CTRL:
                file_name = prompt_file(l=True)
                if file_name:
                    life.load_board(file_name)

            elif event.key == pygame.K_s and not play:
                life.step_simulation()

            elif event.key == pygame.K_LEFT:
                cc.inc_d(5)

            elif event.key == pygame.K_RIGHT:
                cc.inc_d(-5)

            elif event.key == pygame.K_SPACE:
                play = not play

            elif event.key == pygame.K_r:
                play = False
                life.reset()

    if play and cc < 0:
        cc.reset()
        life.step_simulation()

    life.draw_to(screen)
    simple_grid()

    change_title(f" -- steps: {life.steps}" +
                 f" -- playing f={cc.d}" * play)

    pygame.display.update()
    cc.woop()
    clock.tick(60)

pygame.quit()
