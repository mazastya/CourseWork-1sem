import os
import sys
from random import randrange
from random import choice

"""
Класс Game. Отвечает за поле игры и игроков. 
В данном классе будут задаваться координаты поля, его размерность, расстановка кораблей,
функции, которые будут отвечать за то, какой игрок ходит, смену позиций игрока -
- с ходящего, на ожидающего, добавление игрока-противника
Так же в этом классе будет отрисовка карты поля - то, как игру видит игрок:
свое поле и поле соперника, плюс поле для компьютера-противника, но оно скрыто от глаз игрока
"""


class Game(object):
    letters = ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J')  # английский будет задан по умолчанию,
    # либо можно выбрать русский (в игре будет выбор для игрока)
    ships_option = [1, 1, 1, 1, 2, 2, 2, 3, 3, 4]  # задаем кол-во палуб у кораблей, само кол-во кораблей
    play_ground_size = len(letters)  # поле квадратное и его размеры будут задаваться по кол-ву букв

    def __init__(self):  # будем использовать метод __init__ к объектам игрока, чтобы задать их параметры
        # не вызывая каждый раз
        # задаем какие-то начальные значения, на которые потом будем ссылаться
        self.players = []
        self.active_player = None  # игрок, делающий ход
        self.next_player = None  # игрок, который ходил за активным
        # позиции игроков будут меняться в функции ниже
        self.status = 'before game'

    def ships_placement(self, player):  # функиця, которая будет отвечать за расстановку кораблей
        for ship_size in Game.ships_option:  # расстановка кораблей будет по заданному в классе Game варианту
            attempts = 30  # зададим конечное число попыток при расстановке, чтобы не зациклиться в бесконечном цикле
            ship = Ship(ship_size, 0, 0, 0)  # заготовка корабля нужного нам размера,
            # далее мы можем присвоить ему координаты, которые ввел пользователь

            while 1:  # бесконечный цикл
                Game.clear_screen()  # чистка экрана
                if player.auto_ship_placement is not True:  # если игрок выбрал расстановку кораблей вручную
                    player.play_ground.draw_play_ground(Play_ground_mark.main)  # рисуем поле и обновляем его в --
                    # -- последующих ходах, пока не будут расставлены все корабли
                    player.message.append('Задайте координаты в формате XYZ, где \n'
                                          'Z - вариант рассположения: вертикально "V"/"Г" или горизонтально "H"/"В" \n'
                                          'X - буква, а Y - цифра.   Например G5Н \n'
                                          'Куда поставить {}-палубный корабль: '.format(
                        ship_size))  # объясняем пользователю как задать координаты корабля
                    for i in player.message:  # выводим сообщение на экран
                        print(i)
                else:
                    print('{}, Расставляем ваши корабли...'.format(player.name))
                player.message.clear()

                x, y, z = player.get_input('ship_placement')
                if x + y + z == 0:  # если игрок ввел неправльно данные, функция возвращает нули
                    continue  # значит просто просим ввести координаты еще раз
                ship.set_location(x, y, z)

                """
                если корабль помещается на заданной позиции, то добвляем его на поле игроку
                по мимо этого добавляем этот корабль в список кораблей игрока
                переходим к следующему кораблю для расстановки
                """
                if player.play_ground.check_fits_ship(ship, Play_ground_mark.main):
                    player.play_ground.add_ship_to_play_ground(ship, Play_ground_mark.main)
                    player.ships.append(ship)
                    break

                attempts -= 1  # если корабль не помещается на заданную позицию, то вычитает из счетчика attempts единицу
                if attempts < 0:
                    player.play_ground.map = [[Cell.empty_cell for _ in range(Game.play_ground_size)]
                                              for _ in range(Game.play_ground_size)]
                    player.ships = []
                    self.ships_placement(player)
                    return True

    def draw(self):  # просто функция, которая каждый ход занимается отрисовкой поля
        if not self.active_player.is_ai:
            self.active_player.play_ground.draw_play_ground(Play_ground_mark.main)
            self.active_player.play_ground.draw_play_ground(Play_ground_mark.radar)
            # self.active_player.play_ground.draw_play_ground(Play_ground_mark.weight) визуальное отображение ходов игрока

        for i in self.active_player.message:  # пишем в консоли пользователю что сделать
            print(i)  # выводим сообщение - действие для игрока

    def add_player(self, player):
        player.play_ground = Play_ground(Game.play_ground_size)  # при добавлении нового игрока создаем ему поле
        player.enemy_ships = list(Game.ships_option)  # добавляем корабли новому игроку
        self.ships_placement(player)  # расстановка кораблей
        player.play_ground.recalculate_weight_map(player.enemy_ships)  # перерасчет весов для клеток поля
        self.players.append(player)

    def start_game(self):  # в начале игры задаем позиции игроков
        self.active_player = self.players[0]
        self.next_player = self.players[1]

    def change_players(self):  # функция смены позиции игроков
        self.active_player, self.next_player = self.next_player, self.active_player

    def status_check(self):  # функция переключения статусов игроков в зависимости от момента в игре
        if self.status == 'before game' and len(self.players) >= 2:
            # если в игру добавлено 2 игрока, то переключаем ее статус на игровой
            self.status = 'game'
            self.start_game()  # задаем начальные позиции игроков
            return True

        if self.status == 'game' and len(self.next_player.ships) == 0:
            # если у следующего игрока заканчиваются корабли, то заканчиваем игру
            self.status = 'game over'
            return True

    # просто чистка экрана
    @staticmethod
    def clear_screen():
        os.system('cls' if os.name == 'nt' else 'clear')
        # os.system('cls')

"""
Класс Ship - отвечает за корабли. яих расстановку на поле и рассположение
либо горизонтальное, либо вертикальное

Комментрий к функции __init__:
Локальные свойства будут задавать нужные параметры такие как:
x и y будут задавать координаты
size, понятно, размер корабля (кол-во палуб)
spin рассположение корабля горизонтально или вертикально поворот задается от 0 до 1 в отдельной функции
"""


class Ship:
    def __init__(self, size, x, y, spin):  # инициализируем объекты, которые будем использовать
        self.size, self.health = size, size
        # местоположение будем задавать в декартовой системе координат через х и у
        self.x = x
        self.y = y
        self.spin = spin
        self.spin_set(spin)

    def __str__(self):  # создадим функцию, которая будет выводить нам корабли на поле
        # в виде ячеек, а не ссылок на классы
        return Cell.ship_cell

    def set_location(self, x, y, z):  # функция, задающая положение корабля
        self.x = x
        self.y = y
        self.spin_set(z)  # вращение

    def spin_set(self, z):  # функция, отвечающая за вращение корабля - горизонтально или вертикально
        self.spin = z  # координата определения степени вращения

        if self.spin == 0:  # вертикальный вниз вариант рассположения корабля
            self.height = 1
            self.width = self.size
        elif self.spin == 1:  # горизонтальный вправо вариант рассположения корабля
            self.width = 1
            self.height = self.size
        elif self.spin == 2:  # вертикальный вверх вариант рассположения корабля
            self.y = self.y - self.size + 1
            self.height = 1
            self.width = self.size
        elif self.spin == 3:  # горизонтальный влево вариант рассположения корабля
            self.x = self.x - self.size + 1
            self.width = 1
            self.height = self.size


"""
класс Color - отвечает за окрашивание условных символов в цвет, для различия знаков на поле игры.
имя локальных переменных не всегда совпадают с их цветовым решением, но зато к ним легко обращаться
"""


class Color:
    cage = '\033[48m'
    reset = '\033[0m'
    pond_blue = '\033[0;36m'
    yellow_1 = '\033[1;93m'
    yellow_2 = '\033[1;93m'
    miss = '\033[0;37m'

def set_color(text, color):  # так же создадим функцию, которая будет окрашивать нужные символы в заданный цвет
    return color + text + Color.reset

"""
создадим класс Play_ground_mark, который будет отвечать за какие-либо условные конкретные части игрового поля
# условные части: вес - для "ИИ", map, radar - список (из спсков) с путыми клетками
"""


class Play_ground_mark(object):
    main = 'map'
    weight = 'weight'
    radar = 'radar'


"""
создадим класс Сell - клетка, который будет отвечать за отображение всех символов, которые будут визуализировать игру
логика в том, что по визуальной составляющей будет определяться тип клетки
"""


class Cell(object):
    empty_cell = set_color('□', Color.cage)
    ship_cell = set_color('■', Color.pond_blue)
    destroyed_ship = set_color('X', Color.yellow_1)
    damaged_ship = set_color('⊡', Color.yellow_2)
    miss_cell = set_color('•', Color.miss)


"""
создаем класс Play_ground, который будет отвечать за игровое поле
состоит из трех основных частей, с которыми и будет взаимодействие
map - карта - расстановка кораблей игрока
radar - радар - физуальное отображение ходов и результатов игрока
weight - поле с весом клеток - используется для генерации ходов противника
Так же в этом классе будет происходить отрисовка поля, проверка на устанновку кораблей на поле
Отрисовка подбитого корабля (когда корабль уничтожен, то клетки вокруг него отмечаются битыми.
Рассчет весов для имитации ходов противника так же будет реализован в этом классе за счет функции recalculate_weight_map
более подробные комментарии для рассчетов будут уже внутри функции строчными комментариями.
"""

class Play_ground(object):
    def __init__(self, size):  # снова воспользуемся методом для инициализации локальных свойств объектов
        self.size = size
        self.map = [[Cell.empty_cell for i in range(size)] for j in range(size)]
        # создадим списки из списков размером с наше поле
        self.radar = [[Cell.empty_cell for i in range(size)] for j in range(size)]
        self.weight = [[1 for i in range(size)] for j in range(size)]
        # тут уже зададим значение для списка начиная с единицы, чтобы не было отрицательных весов

    def get_play_ground_part(self, element):  # в этой функции просто присваиваем значение карты, радара, весов
        if element == Play_ground_mark.main:
            return self.map
        if element == Play_ground_mark.radar:
            return self.radar
        if element == Play_ground_mark.weight:
            return self.weight

    def draw_play_ground(self, element):  # функция для отрисовки поля
        play_ground = self.get_play_ground_part(element)
        # weight = self.get_max_weight_cells()

        for x in range(-1, self.size):  # запускаем два цикла для перебора значений
            for y in range(-1, self.size):  # циклы от -1 до размером поля, где -1 = границы с  буквами и числами
                if x == (-1) and y == (-1):  # самую крайнюю верхнюю клетку делаем пустой
                    print(" ", end="")
                    continue
                if x == (-1) and y >= 0:
                    print(y + 1, end=" ")  # задаем на поле числовую ось
                    continue
                if y == (-1) and x >= 0:  # задаем ось буквенных значений
                    print(Game.letters[x], end='')
                    continue
                print(" " + str(play_ground[x][y]), end='')
            print("")

    print("")

    """
    Эта функция будет использоваться для проверки того, помещается ли корабль в заданные координаты поля или нет
    Если помещается, то возвращаем значение True, иначе возвращаем False
    Рассматривать будем расстановку и возможное рассположение на конкретном поле, а не на всех сразу
    Далее функция будет использоваться для другой функции расстановку кораблей, а так же для подсчета
    веса каждой клетки игрового поля
    """

    def check_fits_ship(self, ship, element):
        play_ground = self.get_play_ground_part(element)  # отдельно рассматриваем каждое поле

        if ship.x + ship.height - 1 >= self.size or ship.x < 0 or \
                ship.y + ship.width - 1 >= self.size or ship.y < 0:  # если корабль меньше минимального возможного
            # значения, то варинат расстановки такого корабля не рассматриваем
            return False

        for p_x in range(ship.x, ship.x + ship.height):  # еще два цикла на проверку помещаются ли корабли
            for p_y in range(ship.y, ship.y + ship.width):  # по заданным координатам
                if str(play_ground[p_x][p_y]) == Cell.miss_cell:  # если корабль "заходит" на границу рядом с другим
                    # кораблем (помечаются "промахами" на поле), то такой вариант тоже не подходит
                    return False

        for p_x in range(ship.x - 1, ship.x + ship.height + 1):  # еще два цикла на проверку вместимости координат
            for p_y in range(ship.y - 1, ship.y + ship.width + 1):
                if p_x < 0 or p_x >= len(play_ground) or p_y < 0 or p_y >= len(play_ground):
                    continue  # корабль помещается - нас устраивает - продолжаем
                if str(play_ground[p_x][p_y]) in (Cell.ship_cell, Cell.destroyed_ship):  # если указанные координаты -
                    # уже заняты другим кораблем или его разрушенной частью, то такой вариант тоже не подходит
                    return False
        return True  # корабль помещается

    """
    По правилам игры корабли не могут рассполагаться в любых соседних клетках от других кораблей, следовательно
    помечаем все клетки вокруг игрока как простреленные из класса Cell (Cell.miss_cell). В этой функции так же
    будем отмечать клетки, которые оказались не промахами - подбитым кораблем (Cell.destroyed_ship)
    """

    def mark_destroyed_ship(self, ship, element):
        play_ground = self.get_play_ground_part(element)

        x, y = ship.x, ship.y  # передаем координаты
        width, height = ship.width, ship.height  # если горизонатльно - то ширина, если вертикально - то высота

        for p_x in range(x - 1, x + height + 1):  # два цикла для определения границ - выше-ниже корабля
            for p_y in range(y - 1, y + width + 1):
                if p_x < 0 or p_x >= len(play_ground) or p_y < 0 or p_y >= len(play_ground):
                    # если мы находимся в границах корабельной зоны и игрового поля - продолжаем
                    continue
                play_ground[p_x][p_y] = Cell.miss_cell  # помечаем пустыми простреленными клетками

        for p_x in range(x, x + height):  # еще два цикла для отметки подбитых кораблей
            for p_y in range(y, y + width):
                play_ground[p_x][p_y] = Cell.destroyed_ship  # отечаем крестиками подбитые корабли

    def add_ship_to_play_ground(self, ship, element):  # функция добавления корабля на поле
        play_ground = self.get_play_ground_part(element)  # отдельно рассматриваем кажое поле

        for p_x in range(ship.x, ship.x + ship.height):  # запускаем два цикла чтобы пройтись ко всем высотам и широтам
            for p_y in range(ship.y, ship.y + ship.width):  # корабля и пометить их на игровых полях
                play_ground[p_x][p_y] = ship  # специально делаем ссылку на корабль, чтобы можно было отслежитьвать его
                # "здоровье" при обращении к заданной клетке

    def get_max_weight_cells(self):  # функция котороя будет возвращать список самых больших весов
        # с привязкой к координате
        weights = {}  # создадим словарь, каждый вес - ключ к координате
        max_weight = 0  # начальное значение 0, т.к. отрицательных весов у нас нет

        for x in range(self.size):  # два цикла чтобы пройтись по всем клеткам поля
            for y in range(self.size):
                if self.weight[x][y] > max_weight:  # если вес текущей клетки больше максимального
                    max_weight = self.weight[x][y]  # то обновляем переменную максимального значения
                weights.setdefault(self.weight[x][y], []).append((x, y)) # с помощью метода setdefault
                # делаем из словаря список координат с максимальными значениями
        return weights[max_weight]  # возвращаем список с максимальными весами

    """
    Тут понадобится подробное описание функции, чтобы понять логику расстановки весов в каждой клетке
    Из классических правил игры мы знаем, что корабли могут рассполагаться только по вертикали и горизонтали, на этом 
    и будут строиться наши расчеты. Если мы попадаем в корабль, то клетка помечается как "подбитая" (Cell.destroyed_ship)
    Если наша клетка подбита, то значит корабль может идти от нее либо вверх-низ, либо вправо-влево, следовательно этим
    клеткам мы увеличиваем веса так, чтобы они стали больше всех остальных по весу. Далее, мы знаем, что корабли в 
    классическом морском бое не идут по диагонали, а значит клетки, которые стоят в диагональной позиции от "подбитых"
    клеток, можно занулить, чтобы туда точне не был совершен выстрел.
    Далее работа с коэффициентами будет на счет того, какие корабли вообще остались у игрока на поле. Для этого 
    пробегаемся по доступным кораблям и проверяем каждую клетку на предмет того, может ли туда помещаться корабль из 
    оставшегося списка доступных или нет, если да, то прибавляем единицу
    """

    def recalculate_weight_map(self, available_ship):  # функция пересчета веса клеток
        self.weight = [[1 for _ in range(self.size)] for _ in range(self.size)]  # каждый раз расставляем всем клеткам
        # значение единицы. веса каждый раз будут обновляться т.е.  нам не обязательно знать что было на предыдущем ходе
        for x in range(self.size):  # два цикла чтобы пройтись по всем клеткам
            for y in range(self.size):
                if self.radar[x][y] == Cell.damaged_ship:  # если корабль "подбит"
                    self.weight[x][y] = 0  # вес самой клетки зануляем

                    if x - 1 >= 0:  # горизонатальное влево рассположение
                        if y - 1 >= 0:
                            self.weight[x - 1][y - 1] = 0  # диагональ вниз влево
                        self.weight[x - 1][y] *= 50  # позиция влево
                        if y + 1 < self.size:
                            self.weight[x - 1][y + 1] = 0  # диагональ вверх влево

                    if y - 1 >= 0:  # вертикальное рассположение
                        self.weight[x][y - 1] *= 50  # позиция вниз
                    if y + 1 < self.size:
                        self.weight[x][y + 1] *= 50  # позиция вверх

                    if x + 1 < self.size:  # горизонтальное вправо рассположение
                        if y - 1 >= 0:
                            self.weight[x + 1][y - 1] = 0  # диагональ вниз влево
                        self.weight[x + 1][y] *= 50  # позиция влево
                        if y + 1 < self.size:
                            self.weight[x + 1][y + 1] = 0  # диагональ вверх вправо

        for ship_size in available_ship:  # уикл по доступным кораблям у игрока
            ship = Ship(ship_size, 1, 1, 0)  # обращение к 1-палубному кораблю - самому маленькому
            for x in range(self.size):
                for y in range(self.size):
                    if self.radar[x][y] in (Cell.miss_cell, Cell.destroyed_ship, Cell.damaged_ship) \
                            or self.weight[x][y] == 0:  # если клетка занята или диагональная, то равна нулю
                        self.weight[x][y] = 0
                        continue
                    for spin in range(0, 4):  # проверяем все варианты вращение корабля
                        ship.set_location(x, y, spin)  # присваваем координаты и варинат вращения
                        if self.check_fits_ship(ship, Play_ground_mark.radar):  # проверяем помещается ли корабль
                            self.weight[x][y] += 1  # если да, то добавляем 1 к весу клетки, как возможную мишень


"""
class Player - здесь будет вся логика действий игрока.
В этом классе описана возможность игрока расставить корабли на поле автоматически или самомстоятельно, за раставноку 
кораблей автоматически будет отвечать параметр auto_ship_placement
Функции будут отвечать игроку прошел удар по корабли или выстрел прошел мимо
Если корабль убит, то будем возвращать class Ship, он был описан выше
Основная задача этого класс определять куда прошел выстрел и возвращать соответствующие значения, либо сообщения для 
игрока, если игрок ввел данные, которые не соответвтвуют требуему описанию для хода
"""


class Player(object):
    def __init__(self, name, is_ai, skill, auto_ship):  # как обычно сразу инициализируем, чтобы в дальнейшем было проще
        self.name = name  # имя игрока
        self.is_ai = is_ai  # имитация противника - "ИИ"
        self.skill = skill  # для противника параметр
        self.message = []  # консольное сообщение
        self.ships = []  # корабли в виде списка
        self.enemy_ships = []  # вражеские корабли в виде списка
        self.auto_ship_placement = auto_ship  # автоматическая расстановка кораблей
        self.play_ground = None  # игровое поле


    def get_input(self, input_type):  # функция, отвечающая за ход игрока. 2 варианта хода:
        # global x, y
        if input_type == 'ship_placement':  # 1 вариант - расстановка кораблей
            if self.is_ai or self.auto_ship_placement:  # если играет противник-компьютер
                # или выбрана автоматическая расстановка корблей, то рандомным образом расставляем корабли
                user_input = str(choice(Game.letters)) + str(randrange(0, self.play_ground.size)) + choice(['H', 'V', 'Г', 'В'])
            else:
                user_input = input().upper().replace(" ", "")  # если игрок сам хочет расставить корабли,
                # то он вводит координаты
            if len(user_input) < 3:  # если что-то ввели не так, то возвращем нули
                return 0, 0, 0

            x, y, z = user_input[0], user_input[1:-1], user_input[-1]  # присваиваем значения:
            # x - буква координатного поля, y - цифра координатного поля, z - положение(вертикально или горизонтально)

            if x not in Game.letters or not y.isdigit() or int(y) not in range(1, Game.play_ground_size + 1) \
                    or z not in ('H', 'Г', 'В', 'V'):
                self.message.append('Приказ непонятен, ошибка формата введенных данных')
                return 0, 0, 0
                # если ошибка ввода координат, то сообщаем об этом пользователю
            return Game.letters.index(x), int(y) - 1, 0 if z == ('H' or 'г' or 'Г') else 1  # возвращаем корректные значения

        if input_type == 'shot':  # 2 вариант - выстрел в противника
            if self.is_ai:  # если ход совершает противник-компьютер
                if self.skill == 1:
                    x, y = choice(self.play_ground.get_max_weight_cells())
                if self.skill == 0:
                    x, y = randrange(0, self.play_ground.size), randrange(0, self.play_ground.size)
            else:  # если ход соверщает игрок
                user_input = input().upper().replace(" ", "")  # повторяем шаги, которые были выше для
                # противника-компьютера
                x, y = user_input[0].upper(), user_input[1:]
                if x not in Game.letters or not y.isdigit() or int(y) not in range(1, Game.play_ground_size + 1):
                    self.message.append('Приказ непонятен, ошибка формата введенных данных')
                    return 500, 0  # именно такие цифры нам понадобятся в дальнейшем, для вычисления "промаха"
                x = Game.letters.index(x)
                y = int(y) - 1
            return x, y

    def make_shot(self, player_target):  # функция совершения "выстрела"
        sx, sy = self.get_input('shot')  # запрашиваем ввод данных с типом shot

        if sx + sy == 500 or self.play_ground.radar[sx][sy] != Cell.empty_cell:  # как раз то место, где нам пригодились
            # значения из предыдущей фунции get_input.
            # если прозошла ошибка ввода данных или если клетка пустая, то просим повторить
            return 'retry'
        shot_res = player_target.take_shot((sx, sy))

        if shot_res == 'catch':  # если результат выстрела - попадание в цель
            self.play_ground.radar[sx][sy] = Cell.damaged_ship
        if shot_res == 'miss':  # если результат выстрела - промах
            self.play_ground.radar[sx][sy] = Cell.miss_cell
        if type(shot_res) == Ship:  # если корабли убит, то будет возвращен класс корабль
            destroyed_ship = shot_res
            self.play_ground.mark_destroyed_ship(destroyed_ship, Play_ground_mark.radar)  # меняем карту
            self.enemy_ships.remove(destroyed_ship.size)  # удаляем элемент из списка с помощью метода remove
            shot_res = 'kill'

        self.play_ground.recalculate_weight_map(self.enemy_ships)  # пересчитываем карту весов после вычстрелов
        return shot_res  # возвращаем значение

    def take_shot(self, shot):
        sx, sy = shot  # просто передаем координаты

        if type(self.play_ground.map[sx][sy]) == Ship:  # выстрел по кораблю
            ship = self.play_ground.map[sx][sy]  # передаем координаты попадания
            ship.health -= 1  # если выстрел по кораблю, то забираем счетчик здоровья минус 1

            if ship.health <= 0:  # если у многопалубного корабля выбили все здоровье
                self.play_ground.mark_destroyed_ship(ship, Play_ground_mark.main)
                self.ships.remove(ship)  # удаляем корабль
                return ship  # возвращаем значение (координаты)

            self.play_ground.map[sx][sy] = Cell.damaged_ship  # если клетка помечена как раненый корабль
            return 'catch'  # возвращаем, что корабль ранен
        else:
            self.play_ground.map[sx][sy] = Cell.miss_cell  # если клетка помечена как пустая
            return 'miss'  # возвращаем, как пусто место


"""
Последний блок
В начале будут задаваться вопросы, которые помогут игроку определиться с тем, как к нему будут обращаться в течении игры,
будет решено игроком будет он расставлять корабли самостоятельно или автоматически, так же здесь будет представлен выбор
языка для раскладки поля. В бескончном цикле будет постоянно обновляться статус игрока и в зависимости от статуса и 
действий игрока будут выводиться сообщения для пользователя и просиходить сама игра. Выход из цикла будет когда игра 
закончится - получен статус 'game over'
"""
if __name__ == '__main__':  # проверяем запущена ли программа напрямую из этого файла
    print('Добро пожаловать в классчиескую версию игры морской бой! \n'
          'Выберите действие: \n'
          '1 - начать игру \n'
          '2 - выйти из игры :( \n'
          'Примечание: при ошибке ввода данных будет выбран выход из игры')

    first_choice = input()

    if first_choice == '1':
        print('\n Начнем игру!'
              '\n Введите имя игрока: ')
        opt_name = input()  # вводится имя игрока
        players = []  # создаем список из двух игроков и задаем им основные параметры

        print('\n Хотите расставить корабли на поле самомстоятельно или сделать это действие автоматически? \n'
              '1 - самостоятельно, вводя координаты каждого корабля \n'
              '2 - автоматически (расстановка кораблей случайным образом) \n'
              'Примечание: при ошибке ввода данных будет выбрана автоматическая расстановка кораблей')

        choice_auto_var = input()  # здесь просиходит выбор того, будет ли расстановка кораблей автоматической или нет
        if choice_auto_var == '1':
            opt_auto_ship = False
        else:
            opt_auto_ship = True

        players.append(Player(name=opt_name, is_ai=False, auto_ship=opt_auto_ship, skill=1))
        players.append(Player(name='Kапитан, мой капитан', is_ai=True, auto_ship=True, skill=1))
        # Капитан, мой капитан - обращение к профессору Киттингу из фильма "общество мертвый поэтов"

        game = Game()  # создаем игру
        print('\n Выберите какими буквами вы хотите задавать координаты поля: \n'
              '1 - Кириллица_ru \n'
              '2 - Латиница_eng (будет выбран по умолчанию при ошибке введенных данных)')

        letters_ru_eng = input()  # тут выбор для того, какими буквами будут задаваться координаты поля
        if letters_ru_eng == '1':
            Game.letters = ['А', 'Б', 'В', 'Г', 'Д', 'Е', 'Ж', 'З', 'И', 'К']

        while 1:  # создаем бесконечный цикл, который прервется только при завершении игры
            game.status_check()  # в начале каждого хода проверяем статус игры и основываясь на этом продолжаем

            if game.status == 'before game':  # перед началом игры добавляем игроков
                game.add_player(players.pop(0))  # новых добавляем на начальную позицию

            if game.status == 'game':  # если игра началась
                Game.clear_screen()  # очищаем экран каждый раз (работает только при запуске в консоле)
                game.active_player.message.append('Ждем приказа (введите сначала букву, затем цифру): ')  # сщщбщение пользователю
                game.draw()  # отрисовка поля
                game.active_player.message.clear()  # чистим список сообщений игрока для следующего хода
                shot_result = game.active_player.make_shot(game.next_player)  # получение результата выстрела на основе
                # выстрела текущего игрока в следующего. На этой основе следующие сообщения для игрока и сама игра

                if shot_result == 'miss':  # сообщения при промахе
                    game.next_player.message.append('На этот раз {} промахнулся! '.format(game.active_player.name))
                    game.next_player.message.append('Ваш ход, {}! '.format(game.next_player.name))
                    game.change_players()  # смена игроков
                    continue
                elif shot_result == 'retry':  # при ошибке введенных данных
                    game.active_player.message.append('Ошибка введенных данных. Попробуйте еще раз! ')
                    continue
                elif shot_result == 'catch':  # при попадании в корабль
                    game.active_player.message.append('Отличный выстрел! Продолжайте! ')
                    game.next_player.message.append('Наш корабль попал под обстрел :( ')
                    continue
                elif shot_result == 'kill':  # при уничтожении корабля
                    game.active_player.message.append('Корабль противника уничтожен! Продолжайте! ')
                    game.next_player.message.append('Плохие новости: наш корабль уничтожен :(')
                    continue

            if game.status == 'game over':  # если игра окончена
                Game.clear_screen()  # чистим экран для новых сообщений
                game.next_player.play_ground.draw_play_ground(Play_ground_mark.main)  # отрисовка поля с выявлением всех
                # кораблей, показываем неразбитые корабли при проигрыше
                game.active_player.play_ground.draw_play_ground(Play_ground_mark.main)  # отрисовка второго поля
                print('Это был последний корабль {}'.format(game.next_player.name))
                print('{} выиграл эту игру! Тут можно только поздравить победителя!'.format(game.active_player.name))
                break

        print('Спасибо за игру!'
              'Перезапустите программу, если хотите сыграть еще раз :)')
        input('')

    if first_choice != '1':  # если игрок выбрал выйти из игры
        print('Ну, сыграем в следующий раз')
        sys.exit()
