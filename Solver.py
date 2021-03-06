import colorama
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt


class SearchNode:
    def __init__(self, parent, snake, priority, target):
        self.snake = snake
        self.priority = priority
        self.parent = parent
        self.target = target

    def compareTo(self, otherSearchNode):
        if self.priority < otherSearchNode.priority:
            return -1
        elif self.priority > otherSearchNode.priority:
            return 1
        else:
            return 0

    def isGoal(self):
        return self.snake.score >= self.target


class Solver(QtWidgets.QWidget):

    def __init__(self, snake, target, debug, recursion):
        super().__init__()
        self.target = target
        self.debug = debug
        self.recursion = recursion

        self.initialSnake = snake
        self.solution = None
        self.AStar()
        self.qp = QtGui.QPainter()

    def progress_bar(self, progress, total, color=colorama.Fore.YELLOW):
        percent = 100 * (progress / float(total))
        bar = '█' * int(percent) + '-' * int(100 - int(percent))
        print(color + f"\r|{bar}| {percent:.2f}%", end="\r")
        if progress == total:
            print(colorama.Fore.GREEN + f"\r|{bar}| {percent:.2f}%", end="\r")

    def AStar(self):
        global best_score_yet  # global variable to keep track of the best score (for loading bar)
        startSearchN = SearchNode(None, self.initialSnake, 0, self.target)
        nodeArray = [startSearchN]
        current = nodeArray.pop()
        best_score_yet = 0
        is_stuck = False
        stuck = 0
        i = 0
        self.progress_bar(best_score_yet, self.target)

        while not current.isGoal():
            self.addNext(nodeArray, current, is_stuck)
            max = 0
            index = 0
            maxNodeIndex = 0
            for node in nodeArray:
                if node.priority > max:
                    max = node.priority
                    maxNodeIndex = index
                index += 1

            current = nodeArray[maxNodeIndex]
            # update best_score_yet
            if current.snake.score > best_score_yet:
                stuck = 0
                is_stuck = False
                best_score_yet = current.snake.score
                self.progress_bar(best_score_yet, self.target)
            else:
                stuck += 1

                # Solver is stuck with the closest food
                if stuck == self.recursion and not is_stuck:
                    is_stuck = True  # set stuck to true so that the snake will not focus on the closest food
                    stuck = 0

                # Solver is stuck with both the closest food and the furthest food
                if stuck == self.recursion and is_stuck:
                    print("\nSolver could not find a solution for this score on this map... :'(\n"
                          "Here's the best solution found so far (" + str(best_score_yet) + "):")
                    self.solution = current
                    break
            nodeArray.pop(maxNodeIndex)
            nearestFood = current.snake.getNearestFood()
            if self.debug:
                print("Current position: " + str(current.snake.x) + ", " + str(current.snake.y))
                print("Nearest food selected: " + str(nearestFood[2]) + " at position: " + str(nearestFood[0]) + ", " + str(
                    nearestFood[1]))
                print("Priority: " + str(current.priority) + " Score: " + str(current.snake.score))
                print("Snake: ")
                for block in current.snake.snakeArray:
                    print(str(block))
                print("\n")
            i += 1

        if current.isGoal():
            print("\nFound a solution !")
            self.solution = current

    def addNext(self, nodeArray, current, is_stuck=False):
        for next in current.snake.getNeighbors():
            if (current.parent is None) or (not next.equals(current.parent.snake)):
                nearestFood = next.getNearestFood(is_stuck)
                moves = next.get_moves()
                priority = ((1 / (nearestFood[2] + 1))) + ((1 / ((moves + 1)))) + next.score * 10000
                nodeArray.append(SearchNode(current, next, priority, self.target))

    def getSolution(self):
        res = []
        current = self.solution
        while current is not None:
            res.insert(0, current.snake)
            current = current.parent
        return res

    # def initUI(self):
    #     self.setStyleSheet("QWidget { background: #A9F5D0 }")
    #     self.setFixedSize(self.initialSnake.windowSize, self.initialSnake.windowSize)
    #     self.setWindowTitle('Snake')
    #     self.show()

    # def paintEvent(self, event):
    #     self.qp.begin(self)
    #     self.scoreBoard()
    #     self.drawRocks()
    #     self.drawFood()
    #     self.drawSnake()
    #     self.scoreText()
    #     if self.initialSnake.isOver:
    #         self.gameOver()
    #     self.qp.end()

    def direction(self, dir):
        if dir == "DOWN" and self.snake.checkStatus(self.snake.x, self.snake.y + self.snake.squareSize):
            self.snake.y += self.snake.squareSize
            self.repaint()
            self.snake.snakeArray.insert(0, [self.snake.x, self.snake.y])
        elif dir == "UP" and self.snake.checkStatus(self.snake.x, self.snake.y - self.snake.squareSize):
            self.snake.y -= self.snake.squareSize
            self.repaint()
            self.snake.snakeArray.insert(0, [self.snake.x, self.snake.y])
        elif dir == "RIGHT" and self.snake.checkStatus(self.snake.x + self.snake.squareSize, self.snake.y):
            self.snake.x += self.snake.squareSize
            self.repaint()
            self.snake.snakeArray.insert(0, [self.snake.x, self.snake.y])
        elif dir == "LEFT" and self.snake.checkStatus(self.snake.x - self.snake.squareSize, self.snake.y):
            self.snake.x -= self.snake.squareSize
            self.repaint()
            self.snake.snakeArray.insert(0, [self.snake.x, self.snake.y])

    def scoreBoard(self):
        self.qp.setPen(Qt.NoPen)
        self.qp.setBrush(QtGui.QColor(25, 80, 0, 160))
        self.qp.drawRect(0, 0, self.snake.windowSize, self.snake.squareSize)

    def scoreText(self):
        self.qp.setPen(QtGui.QColor(255, 255, 255))
        self.qp.setFont(QtGui.QFont('Arial', 10))
        self.qp.drawText(8, 17, "SCORE: " + str(self.snake.score))
        self.qp.drawText(195, 17, "HIGHSCORE: " + str(self.snake.highscore))

    def gameOver(self):
        self.highscore = max(self.snake.highscore, self.snake.score)

    def drawRocks(self):
        self.qp.setBrush(QtGui.QColor(45, 45, 45, 255))
        # Draw rocks on the map
        for rock in self.snake.rocks:
            self.qp.drawRect(rock["x"], rock["y"], self.snake.squareSize, self.snake.squareSize)

    def drawFood(self):
        if self.snake.fruits["food1_type"] == "Pomme":
            self.qp.setBrush(QtGui.QColor(80, 180, 0, 160))
        else:
            self.qp.setBrush(QtGui.QColor(255, 0, 0, 160))
        self.qp.drawRect(self.snake.fruits["food1_x"], self.snake.fruits["food1_y"], self.snake.squareSize,
                         self.snake.squareSize)

        if self.snake.fruits["food2_type"] == "Pomme":
            self.qp.setBrush(QtGui.QColor(80, 180, 0, 160))
        else:
            self.qp.setBrush(QtGui.QColor(255, 0, 0, 160))
        self.qp.drawRect(self.snake.fruits["food2_x"], self.snake.fruits["food2_y"], self.snake.squareSize,
                         self.snake.squareSize)

    # draws each component of the snake
    def drawSnake(self):
        self.qp.setPen(Qt.NoPen)
        self.qp.setBrush(QtGui.QColor(0, 80, 255, 255))
        tete = 0
        for i in self.snake.snakeArray:
            if (tete == 0):
                self.qp.setBrush(QtGui.QColor(255, 255, 255, 255))
                tete = 1
            else:
                self.qp.setBrush(QtGui.QColor(0, 80, 255, 255))
            #print("x : " + str(i[0] / self.snake.squareSize) + "\t y : " + str(i[1] / self.snake.squareSize))
            self.qp.drawRect(i[0], i[1], self.snake.squareSize, self.snake.squareSize)
