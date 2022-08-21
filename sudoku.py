import random
from copy import deepcopy
from itertools import product
from timeit import default_timer as time_now

DIM='\x1b[2m'
BOLD='\x1b[1m'
RESET='\x1b[22m'

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
    for command in ['see', 'solve']:
        if command in string:
            return command
    return 'help'

def main():
    sudoku = generate(19)

    while True:
        inp = clean_input(input('What should I do? (see | solve) '))
        if inp == 'see':
            print(sudoku)
        elif inp == 'solve':
            if not sudoku.solution:
                sudoku.solution = solve(deepcopy(sudoku)).puzzle
            print(sudoku.solution)
        else:
            print("I couldn't parse your input :( try again")
        print()

if __name__ == '__main__':
    main()
