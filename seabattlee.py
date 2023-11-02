from random import randint
class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за доску!"


class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"


class BoardWrongShipException(BoardException):
    pass

class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

class Ship:
    def __init__(self, length, nose, direction):
        self.length = length
        self.nose = nose
        self.direction = direction
        self.hp = length

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.length):
            pos_x = self.nose.x
            pos_y = self.nose.y

            if self.direction == 0:
                pos_x += i

            elif self.direction == 1:
                pos_y += i

            ship_dots.append(Dot(pos_x, pos_y))
        return ship_dots

    def shooten(self, shot):
        return shot in self.dots

class Board:
    def __init__(self, hid=False, size=6):
        self.hid = hid
        self.size = size
        self.count = 0
        self.field = [["O"]*size for _ in range(size)]
        self.busy = []
        self.ships = []

    def __str__(self):
        res = ''
        res += '  | 1 | 2 | 3 | 4 | 5 | 6 |'
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} | " + " | ".join(row) + " | "

        if self.hid:
            res = res.replace("■", "O")

        return res

    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.y][d.x] = '■'
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, verb=False):
        near = [(-1, -1), (-1, 0), (-1, 1),
                (0, -1), (0, 0), (0, 1),
                (1, -1), (1, 0), (1, 1)
                ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.y + dy, d.x + dx)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.y][cur.x] = '.'
                    self.busy.append(cur)

    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()

        if d in self.busy:
            raise BoardUsedException()

        self.busy.append(d)

        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.y][d.x] = 'X'
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print('Корабль уничтожен!')
                    return False
                else:
                    print('Корабль ранен!')
                    return True

        self.field[d.y][d.x] = 'T'
        print('Мимо!')
        return False

    def begin(self):
        self.busy = []

    def defeat(self):
        return self.count == len(self.ships)

class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f'Ход компьютера: {d.y+1} {d.x+1}')
        return d


class User(Player):
    def ask(self):
        while True:
            cords = input('Ваш ход: ').split()

            if len(cords) != 2:
                print('Введите 2 координаты!')
                continue

            y, x = cords

            if not(y.isdigit()) or not(x.isdigit()):
                print('Введите числа!')
                continue

            y, x = int(y), int(x)

            return Dot(y-1, x-1)

class Game:
    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True

        self.ai = AI(co, pl)
        self.user = User(pl, co)

    def greet(self):
        print("-------------------")
        print("  Приветсвуем вас в игре морской бой ")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")

    def try_board(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board

    def print_boards(self):
        print("-" * 20)
        print('Доска пользователя:')
        print(self.user.board)
        print("-" * 20)
        print('Доска компьютера:')
        print(self.ai.board)
        print("-" * 20)

    def loop(self):
        num = 0
        while True:
            self.print_boards()
            if num % 2 == 0:
                print('Ходит пользователь!')
                repeat = self.user.move()
            else:
                print('Ходит компьютер!')
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.defeat():
                self.print_boards()
                print("-" * 20)
                print('Пользователь выиграл!')
                break

            if self.user.board.defeat():
                self.print_boards()
                print("-" * 20)
                print('Компьютер выиграл!')
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()