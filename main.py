from random import randint

class BoardException(Exception):
    pass

class BoardOutException(BoardException):
    def BoardOut(self):
        return "Координата за пределами доски"

class BoardEngagedException(BoardException):
    def BoardEngaged(self):
        return "Точка уже поражена"

class BoardWrongShipException(BoardException):
    def BoardWrongShip(self):
        return "Неправильное расположение корабля"

class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"Dot({self.x}, {self.y})"

class Ship:
    def __init__(self, lenght, x1, y1, direction):
        self.lenght = lenght
        self.x1 = x1
        self.y1 = y1
        self.direction = direction
        self.hp = lenght

    @property
    def dots(self):
        ship_cords = []
        for i in range(self.lenght):
            cord_x = self.x1
            cord_y = self.y1

            if self.direction == 0:
                cord_x += i
                cord_y = self.y1
            else:
                cord_x = self.x1
                cord_y += i

            ship_cords.append(Dot(cord_x, cord_y))
        return ship_cords

class Board:
    def __init__(self, hid, live_ships):
        self.hid = hid
        self.live_ships = live_ships

        self.cells = [["0"]*6 for i in range(6)]

        self.busy = []
        self.ships = []
        self.count = 0

    def __str__(self):
        all_board = ""
        all_board += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        all_board += "\n---------------------------"
        for i in range(6):
            row = " | ".join(self.cells[i])
            all_board += f"\n{i + 1} | {row} |"

        if self.hid:
            all_board = all_board.replace("■", "0")
        return all_board

    def out(self, d):
        return not ((0 <= d.x < 6) and (0 <= d.y < 6))

    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not(self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.cells[cur.x][cur.y] = "."
                    self.busy.append(cur)

    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()

        for d in ship.dots:
            self.cells[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()

        if d in self.busy:
            raise BoardEngagedException()

        self.busy.append(d)

        for ship in self.ships:
            if d in ship.dots:
                self.cells[d.x][d.y] = "X"
                if ship.hp == 1:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Уничтожен!")
                    return False
                else:
                    ship.hp -= 1
                    print("Попадание!")
                    return True

        self.cells[d.x][d.y] = "T"
        print("Мимо!")
        return False

    def begin(self):
        self.busy = []

class Player:
    def __init__(self, my_board, enemy_board):
        self.my_board = my_board
        self.enemy_board = enemy_board

    def ask(self):
        pass

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy_board.shot(target)
                return repeat
            except BoardException as e:
                print(e)

class User(Player):
    def ask(self):
        while True:
            crds = input("Ваш ход: ").split()

            if len(crds) != 2:
                print(" Введите 2 координаты! ")
                continue

            x, y = crds

            if not (x.isdigit()) or not (y.isdigit()):
                print("Координаты должны быть в формате чисел")
                continue

            x, y = int(x), int(y)

            return Dot(x-1, y-1)

class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {d.x+1}, {d.y +1}")
        return d

class Game:
    def __init__(self):
        user_board = self.board_generation()
        ai_board = self.board_generation()
        ai_board.hid = True

        self.user = User(user_board, ai_board)
        self.ai = AI(ai_board, user_board)


    def random_board(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(False, 5)
        attempts = 0
        for i in lens:
            while True:
                attempts += 1
                if attempts > 3000:
                    return None
                ship = Ship(i, (randint(0, 6)), (randint(0, 6)), (randint(0, 1)))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def board_generation(self):
        board = None
        while board is None:
            board = self.random_board()
        return board

    def greet(self):
        print("-------------------")
        print("  Приветсвуем Вас  ")
        print("      в игре       ")
        print('   "Морской бой"  ')
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")

    def loop(self):
        num = 0
        while True:
            print("-" * 20)
            print("Доска пользователя:")
            print(self.user.my_board)
            print("-" * 20)
            print("Доска компьютера:")
            print(self.ai.my_board)
            if num % 2 == 0:
                print("-" * 20)
                print("Ходит пользователь!")
                repeat = self.user.move()
            else:
                print("-" * 20)
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.my_board.count == 7:
                print("-" * 20)
                print("Пользователь выиграл!")
                break

            if self.user.my_board.count == 7:
                print("-" * 20)
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()

g = Game()
g.start()