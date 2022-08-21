from itertools import product

DIM='\x1b[2m'
BOLD='\x1b[1m'
RESET='\x1b[22m'

class Sudoku:
    def __init__(self, puzzle):
        self.puzzle = puzzle

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

def solve(sudoku):
    for (x, y) in product(range(0,9), repeat=2):
        if sudoku.is_empty(x, y):
            for n in range(1,10):
                try:
                    sudoku.set(x, y, n)
                except ValueError:
                    continue
                else:
                    solution = solve(sudoku)
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
    puzzle = [[1, 2, 3, 4, 5, 6, 7, 8, 9],
              [0, 0, 0, 7, 0, 8, 0, 0, 0],
              [0, 0, 0, 1, 0, 0, 0, 0, 0],
              [0, 0, 0, 2, 0, 0, 0, 0, 0],
              [0, 0, 0, 3, 0, 0, 0, 0, 0],
              [0, 0, 0, 8, 0, 0, 0, 0, 0],
              [0, 0, 0, 9, 0, 0, 0, 0, 0],
              [9, 7, 8, 5, 4, 1, 3, 6, 2],
              [5, 4, 1, 6, 3, 2, 9, 7, 8]]
    sudoku = Sudoku.from_puzzle(puzzle)

    while True:
        inp = clean_input(input('What should I do? (see | solve) '))
        if inp == 'see':
            print(sudoku)
        elif inp == 'solve':
            solution = solve(sudoku)
            print(solution)
        else:
            print("I couldn't parse your input :( try again")
        print()

if __name__ == '__main__':
    main()
