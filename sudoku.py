import curses
import random
from copy import deepcopy
from curses import wrapper
from itertools import product
from timeit import default_timer as time_now

DIM='\x1b[2m'
BOLD='\x1b[1m'
RESET='\x1b[22m'
COMMANDS = ['look', 'guess', 'hint', 'solve', 'new', 'quit']

class Sudoku:
    def __init__(self, puzzle):
        self.puzzle = puzzle
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

def clean_input(string):
    string = string.strip().lower()
    for command in COMMANDS:
        if command in string or command[0] == string:
            return command[0]
    return 'help'

def main(stdscr):
    stdscr.clear()
    sudoku = generate(19)

    # initialize some colours
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)

    err_win = curses.newwin(1, 0, 1, 0)

    while True:
        stdscr.addstr(0, 0, f"What should I do? ({' | '.join(COMMANDS)}) ", curses.color_pair(1))
        err_win.refresh()
        stdscr.refresh()
        curses.echo()
        inp = stdscr.getch()
        if inp == ord('l'):
            pass
        elif inp == ord('g'):
            err_win.clear()
            err_win.addstr('Not implemented yet :(', curses.color_pair(2))
            continue
        elif inp == ord('h'):
            sudoku.reveal(1)
        elif inp == ord('s'):
            if not sudoku.solution:
                sudoku.solution = solve(deepcopy(sudoku)).puzzle
            sudoku.reveal()
        elif inp == ord('n'):
            sudoku = generate(19)
        elif inp == ord('q'):
            break
        else:
            err_win.clear()
            err_win.addstr("I couldn't parse your input :( try again", curses.color_pair(2))
            continue
        err_win.clear()

if __name__ == '__main__':
    try:
        wrapper(main)
    except KeyboardInterrupt:
        print()
        print('Goodbye!')
