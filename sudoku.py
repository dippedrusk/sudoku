import curses
import random
from copy import deepcopy
from curses import wrapper
from enum import Enum
from itertools import product
from timeit import default_timer as time_now

DIM='\x1b[2m'
BOLD='\x1b[1m'
RESET='\x1b[22m'

class Command(Enum):
    LOOK = ord('l')
    GUESS = ord('g')
    HINT = ord('h')
    SOLVE = ord('s')
    NEW = ord('n')
    QUIT = ord('q')

class Sudoku:
    def __init__(self, puzzle):
        self.puzzle = puzzle
        self.fixed = puzzle
        self.solution = None

    @classmethod
    def from_empty(cls):
        puzzle = [[0] * 9 for _ in range(9)]
        return cls(puzzle)

    @classmethod
    def from_puzzle(cls, puzzle):
        return cls(puzzle)

    def get_box_coords(self, x, y):
        start_x = x // 3 * 3
        start_y = y // 3 * 3
        return product(range(start_x, start_x+3), range(start_y, start_y+3))

    def is_valid(self, x, y, n):
        for i in range(0,9):
            if self.puzzle[x][i] == n:
                return False
            if self.puzzle[i][y] == n:
                return False
        for (_x, _y) in self.get_box_coords(x, y):
            if self.puzzle[_x][_y] == n:
                return False
        return True

    def is_empty(self, x, y):
        return self.puzzle[x][y] == 0

    def set(self, x, y, n):
        if n == 0:
            self.puzzle[x][y] = n
        elif self.is_valid(x, y, n):
            self.puzzle[x][y] = n
        else:
            raise ValueError

    def reveal(self, n=None):
        if not n:
            self.puzzle = self.solution
        else:
            coords = [(x,y) for (x,y) in product(range(0,9), repeat=2) if self.is_empty(x, y)]
            random.shuffle(coords)
            for i in range(min(n, len(coords))):
                (x,y) = coords[i]
                self.set(x, y, self.solution[x][y])
                self.fixed[x][y] = self.solution[x][y]

    def __str__(self):
        puzzle = f'  {DIM}' + '— '*13 + f'{RESET}\n'
        for i, row in enumerate(self.puzzle):
            if i and i % 3 == 0:
                puzzle += f'  {DIM}' + '-'*25 + f'{RESET}\n'
            puzzle += '  '
            for j, number in enumerate(row):
                if j % 3 == 0:
                    puzzle += f'{DIM}|{RESET} '
                puzzle += f'{DIM if number == 0 else BOLD}{number}{RESET} '
            puzzle += f'{DIM}|{RESET}\n'
        puzzle += f'  {DIM}' + '— '*13 + RESET
        return puzzle

def generate(n_clues):
    sudoku = Sudoku.from_empty()
    coordss = set()
    while len(coordss) != n_clues:
        x = random.choice(range(0,9))
        y = random.choice(range(0,9))
        coordss.add((x,y))
    for (x,y) in coordss:
        numbers = list(range(1,10))
        random.shuffle(numbers)
        for n in numbers:
            try:
                sudoku.set(x, y, n)
            except ValueError:
                continue
    solution = solve(deepcopy(sudoku), finish_by=time_now()+0.1)
    if not solution:
        return generate(n_clues)
    sudoku.fixed = deepcopy(sudoku.puzzle)
    sudoku.solution = solution.puzzle
    return sudoku

def solve(sudoku, finish_by=None):
    if time_now() > finish_by:
        return None
    for (x, y) in product(range(0,9), repeat=2):
        if sudoku.is_empty(x, y):
            for n in range(1,10):
                try:
                    sudoku.set(x, y, n)
                except ValueError:
                    continue
                else:
                    solution = solve(sudoku, finish_by=finish_by)
                    if solution:
                        return solution
                    sudoku.set(x, y, 0)
            return None
    return sudoku

def print_sudoku(win, sudoku):
    for i, row in enumerate(sudoku.puzzle):
        for j, number in enumerate(row):
            x_offset = i // 3
            y_offset = (j // 3) * 2
            n = '' if number == 0 else str(number)
            win.addstr(i+x_offset+1, j*2+y_offset+2, n, curses.color_pair(1))

def draw_borders(window, cx=0, cy=0):
    window.addstr(cx, cy, '— '*13, curses.A_DIM)
    window.addstr(cx+12, cy, '— '*13, curses.A_DIM)
    for x in range(cx+1, cx+12):
        window.addstr(x, cy, '|', curses.A_DIM)
        window.addstr(x, cy+8, '|', curses.A_DIM)
        window.addstr(x, cy+16, '|', curses.A_DIM)
        window.addstr(x, cy+24, '|', curses.A_DIM)
    window.addstr(cx+4, cy, '-'*25, curses.A_DIM)
    window.addstr(cx+8, cy, '-'*25, curses.A_DIM)
    window.addstr(cx+4, cy+24, '-', curses.A_DIM)
    window.addstr(cx+8, cy+24, '-', curses.A_DIM)

def convert(x, y):
    x_offset = x // 3
    y_offset = (y // 3) * 2
    return x + x_offset + 1, y*2 + y_offset + 2

def guess_loop(sudoku_win, sudoku):
    staged_guesses = {}
    x,y = 4,4
    wx,wy = convert(x,y)
    sudoku_win.move(wx, wy)
    sudoku_win.refresh()
    sudoku_win.keypad(True)
    while True:
        inp = sudoku_win.getch(wx, wy)
        if inp == 27: # escape
            # commit staged guesses
            for (x, y), n in staged_guesses.items():
                try:
                    sudoku.set(x, y, n)
                    sudoku.fixed[x][y] = n
                except ValueError:
                    pass
            break
        # navigation
        if inp == curses.KEY_UP:
            x = max(0, x-1)
        elif inp == curses.KEY_DOWN:
            x = min(x+1, 8)
        elif inp == curses.KEY_LEFT:
            y = max(0, y-1)
        elif inp == curses.KEY_RIGHT:
            y = min(y+1, 8)
        elif inp == ord('\t'): # tab
            y, prev_y = min(y+1, 8), y
            if y == prev_y:
                x = min(x+1, 8)
                y = 0
        # entry / deletion
        elif sudoku.fixed[x][y] == 0 and inp in range(ord('0'), ord('9')+1):
            n = int(chr(inp))
            if n == 0:
                del staged_guesses[(x, y)]
                sudoku_win.addch(' ')
            else:
                staged_guesses[(x, y)] = n
                sudoku_win.addch(str(n))
        wx,wy = convert(x,y)
        sudoku_win.move(wx, wy)
        sudoku_win.refresh()
    sudoku_win.keypad(False)

def main(stdscr):
    stdscr.clear()
    sudoku = generate(19)

    # initialize some colours
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)

    err_win = curses.newwin(1, 0, 1, 0)

    # create sudoku window
    height, width = 14, 25
    sudoku_win = curses.newwin(height, width, 2, 2)

    while True:
        stdscr.addstr(0, 0, f"What should I do? ({' | '.join([c.name for c in list(Command)])}) ", curses.color_pair(1))
        stdscr.refresh()
        curses.echo()
        inp = stdscr.getch()
        curses.noecho()

        if inp not in [c.value for c in list(Command)]:
            err_win.clear()
            err_win.addstr("I couldn't parse your input :( try again", curses.color_pair(2))
            err_win.refresh()
            continue

        err_win.clear()
        err_win.refresh()
        if inp == Command.LOOK.value:
            pass
        elif inp == Command.GUESS.value:
            guess_loop(sudoku_win, sudoku)
        elif inp == Command.HINT.value:
            sudoku.reveal(1)
        elif inp == Command.SOLVE.value:
            if not sudoku.solution:
                sudoku.solution = solve(deepcopy(sudoku)).puzzle
            sudoku.reveal()
        elif inp == Command.NEW.value:
            sudoku_win.clear()
            sudoku = generate(19)
        elif inp == Command.QUIT.value:
            break
        draw_borders(sudoku_win)
        print_sudoku(sudoku_win, sudoku)
        sudoku_win.refresh()

if __name__ == '__main__':
    try:
        wrapper(main)
    except KeyboardInterrupt:
        print()
        print('Goodbye!')
