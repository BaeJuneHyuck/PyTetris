import random
from tkinter import *
import threading


S = [['.....',
      '.....',
      '..00.',
      '.00..',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '...0.',
      '.....']]

Z = [['.....',
      '.....',
      '.00..',
      '..00.',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '.0...',
      '.....']]

I = [['..0..',
      '..0..',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '0000.',
      '.....',
      '.....']]

O = [['.....',
      '.....',
      '.00..',
      '.00..',
      '.....']]

J = [['.....',
      '.0...',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..00.',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '...0.',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '.00..',
      '.....']]

L = [['.....',
      '...0.',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '..00.',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '.0...',
      '.....'],
     ['.....',
      '.00..',
      '..0..',
      '..0..',
      '.....']]

T = [['.....',
      '..0..',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '..0..',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '..0..',
      '.....']]

shapes = [S, Z, I, O, J, L, T]
colors = [(0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 255, 0), (255, 165, 0), (0, 0, 255), (128, 0, 128), (0, 0, 0)]
shape_colors = ["#00FF00", "#FF0000", "#00FFFF", "#FFFF00", "#FFA500", "#0000FF", "#800080", "#fff"]
shape_rotate = [2, 2, 2, 1, 4, 4, 4]


class tetromino:
    def __init__(self, column, row, shape):
        self.x = column
        self.y = row
        self.shape = shape
        self.color = shape_colors[shape]
        self.rotation = 0

    def getCoordinates(self):
        block = []
        for row in range(-2, 3, 1):
            for col in range(-2, 3, 1):
                if shapes[self.shape][self.rotation][col + 2][row + 2] == '0':
                    block.append({'r':row+self.y, 'c':col+self.x})
        return block

class GameWindow:
    started = False
    timer = None
    totalTime = 0
    gamescore = 0
    currentBlock = None
    holdBlock = None
    holdUsed = False
    nextBlockShape = 0
    holdBlockShape = 0

    gamemap = None
    combo = 0

    root = None
    mainFrame = None
    gameFrame = None
    subFrame = None
    timerFrame = None
    scoreFrame = None
    nextBlockFrame = None
    nextBlockImage = None
    holdBlockFrame = None
    holdBlockImage = None

    messageFrame = None
    gameMessage= None

    def __init__(self):
        """
        기본 UI를 구성하고 게임 스레드를 시작합니다
        """

        # grid (10x20)은 비어잇을때 7 그외엔 0~6의 색깔(테트로미노종류)을 기억합니다
        self.gamemap = [[7 for i in range(10)] for j in range(20)]

        self.root = Tk()
        self.root.title('pyTetris')
        self.root.geometry('{}x{}'.format(399, 640))
        self.nextBlockShape = random.randint(0,6)
        self.mainFrame = Frame(self.root, bg='#FFF', width=350, height=600)
        self.messageFrame = Frame(self.root, bg='gray', width=350, height=30)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # 메인 프레임은 좌우로 게임프레임, 서브프레임(사이드바) 로 나눠집니다
        self.mainFrame.grid(row=0, sticky="nsew", pady=(0,10))
        self.mainFrame.grid_rowconfigure(0, weight=1)
        self.mainFrame.grid_columnconfigure(1, weight=1)

        self.gameFrame = Canvas(self.mainFrame, bg='white', width=350, height=600)
        self.subFrame = Frame(self.mainFrame, bg='gray', width=150, height=600)

        self.gameFrame.grid(row=0, column=1, sticky="nsew")
        self.subFrame.grid(row=0, column=2, sticky="ns")

        # 서브프레임은 시간, 점수, 다음블럭, 홀드블럭, 게임시작(종료)버튼 으로 나눠집니다
        self.subFrame.grid_rowconfigure(6, weight=1)
        self.subFrame.grid_columnconfigure(0, weight=1)

        timerWrapper = Frame(self.subFrame)
        timerWrapper.grid(row=0, column=0, pady=10)
        self.timerFrame = Label(timerWrapper, text="00:00", font=("Helvetica", 20))
        self.timerFrame.grid()

        scoreWrapper = Frame(self.subFrame)
        scoreWrapper.grid(row=1, column=0, pady=10)
        scoreTitle = Label(scoreWrapper, text="score", font=("Helvetica", 16))
        scoreTitle.grid(row=0, column=0)
        self.scoreFrame = Label(scoreWrapper, text="00000")
        self.scoreFrame.grid(row=1, column=0)

        nextblockWrapper = Frame(self.subFrame)
        nextblockWrapper.grid(row=2, column=0, pady= 10)
        nextblockTitle = Label(nextblockWrapper, text="next block", font=("Helvetica", 16))
        nextblockTitle.grid()
        self.nextBlockShape = random.randint(0, 6)
        path = 'source/b' + str(self.nextBlockShape) + '.png'
        self.nextBlockImage = PhotoImage(file=path)
        self.nextBlockFrame = Label(nextblockWrapper, image=self.nextBlockImage)
        self.nextBlockFrame.grid()

        holdblockWrapper = Frame(self.subFrame)
        holdblockWrapper.grid(row=3, column=0, pady=10)
        holdblockTitle = Label(holdblockWrapper, text="hold block", font=("Helvetica", 16))
        holdblockTitle.grid()
        self.holdBlockShape = 2
        path2 = 'source/b' + str(self.holdBlockShape) + '.png'
        self.holdBlockImage=PhotoImage(file=path2)
        self.holdBlockFrame = Label(holdblockWrapper, image=self.holdBlockImage)
        self.holdBlockFrame.grid()

        textWrapper = Frame(self.subFrame)
        textWrapper.grid(row=4, column=0)
        text = Label(textWrapper, text="""
→, ←, ↓: move block 
   ↑     : rotate block 
   h      : hold block 
        """)
        text.grid()

        startbuttonWrapper = Frame(self.subFrame)
        startbuttonWrapper.grid(row=5, column=0, pady= 10)
        self.startButton = Button(startbuttonWrapper, text="start", command=self.gameStart, width=15)
        self.startButton.grid()

        # 메세지 프레임은 최하단에 위치
        self.messageFrame.grid(row=1, sticky="nsew")
        self.gameMessage = Label(self.messageFrame, text="click 'start' button", font=("Helvetica", 14))
        self.gameMessage.pack(fill='both')

        # 버튼을 바인드 함수를 처리하고
        # 창을 보여줍니다
        self.root.mainloop()

    def gameStart(self):
        """
        시작 버튼 눌러지면 게임을 시작하거나, 종료
        """
        if self.started:
            self.timer.cancel()
            self.root.quit()
            self.gameMessage.config(text="Good bye")
            return
        self.started = True
        self.startButton.config(text="quit")

        self.root.bind("<Any-KeyPress>", self.keyPressed)
        self.makeNextBlock()
        self.gameLoop()
        self.makeGrid()
        self.gameMessage.config(text="Let's go!")

    def gameLoop(self):
        """
         게임 종료시 스레드를 종료하고 창 종료
        """
        if not self.started:
            self.timer.cancel()
            self.root.quit()
        else:
            # print total time
            self.totalTime = self.totalTime + 1
            timestr = "{:02d}:{:02d}".format(self.totalTime // 60, self.totalTime % 60)

            # timer
            self.timerFrame.config(text=timestr)
            self.timer = threading.Timer(1, self.gameLoop)
            self.timer.start()
            if self.check_valid():
                self.blockDown()
            self.drawBlcok()

    def keyPressed(self, event):
        key = event.keysym
        if key == "Right":
            self.blockMove(right=True)
        elif key == "Left":
            self.blockMove(right=False)
        elif key == "Up":
            self.blockRotate()
        elif key == "Down":
            self.blockDown()
        elif key == "h":
            self.hold()
        self.drawBlcok()


    def blockDown(self):
        """
        ↓키 입력시, 매초마다 호출됨
        이동 불가능하면 그위치에 블럭을 멈추고 새로운 블럭생성, 줄 지우기 확인
        """
        self.currentBlock.y = self.currentBlock.y + 1
        if self.check_collision():
            self.currentBlock.y = self.currentBlock.y - 1
            self.drawOtherBlock()
            self.check_line_clear()
            self.makeNextBlock()

    def blockMove(self, right=False):
        """
         →,← 입력시 호출
        :param right: right or left
        """
        if right:
            move = 1
        else:
            move = -1
        self.currentBlock.x = self.currentBlock.x + move
        if self.check_collision():
            # 이동 불가능하면 원위치
            self.currentBlock.x = self.currentBlock.x - move

    def blockRotate(self):
        """
        ↑ 입력시 호출
        각 블록 타입별 회전가능 한종류로 회전, 회전 불가능한 위치에있을때는 원위치
        """
        prev = self.currentBlock.rotation
        self.currentBlock.rotation = (self.currentBlock.rotation + 1) % (shape_rotate[self.currentBlock.shape])
        if not self.check_valid():
            self.currentBlock.rotation = prev

    def makeNextBlock(self):
        """
        랜덤한 모양의 블럭을 생성하고 다음블럭 종류를 결정, 그림을 보여줌
        홀드기능을 다시 사용할수있게함
        """
        self.holdUsed = False
        self.currentBlock = tetromino(5, 1, self.nextBlockShape)
        self.nextBlockShape = random.randint(0, 6)
        path = 'source/b' + str(self.nextBlockShape) + '.png'
        self.nextBlockImage = PhotoImage(file=path)
        self.nextBlockFrame.config(image = self.nextBlockImage)
        if not self.check_valid() or self.check_collision():
            self.gameOver()

    def makeGrid(self):
        """
        창 크기를 이용하여 30x30의 grid를 생성
        """
        w = self.gameFrame.winfo_width()  # Get current width of canvas
        h = self.gameFrame.winfo_height()  # Get current height of canvas
        self.gameFrame.delete('grid_line')  # Will only remove the grid_line

        # Creates all vertical
        for i in range(0, w, 30):
            self.gameFrame.create_line([(i, 0), (i, h)], tag='grid_line')

        # Creates all horizontal
        for i in range(0, h, 30):
            self.gameFrame.create_line([(0, i), (w, i)], tag='grid_line')

    def check_valid(self):
        """
        블럭이 있는위치가 valid 할시 True 리턴
        """
        block = self.currentBlock.getCoordinates()
        for cord in block:
            r = cord['r']
            c = cord['c']
            if r > 19 or r < 0 or c > 8 or c < 0 :
                return False
        return True


    def check_collision(self):
        """
        블럭이 땅에 도착하거나 다른 블럭과 충돌할시 True 리턴
        """
        block = self.currentBlock.getCoordinates()
        for cord in block:
            row = cord['r']
            col = cord['c']
            if col < 0 or col > 8:
                return True
            if row == 20:
                return True
            if self.gamemap[row][col] != 7:
                if row == 1:
                    self.gameOver()
                return True
        return False


    def gameOver(self):
        self.started = False
        self.gameMessage.config(text="Game Over")

    def check_line_clear(self):
        """
        row가 가득 차면 지우고 점수를 추가해줌
        한번에 여러줄이 지워지면 더 큰 점수를줌
        """
        # 블럭이 있는 row를 리스트로 정리
        block = self.currentBlock.getCoordinates()
        list = []
        deleted_line = 0
        deleted_row =[]
        for cord in block:
            row = cord['r']
            if row not in list:
                list.append(row)

        # 블럭있는 row에 대해서 지워져야할지 체크
        for row in list:
            rowcheck = True
            for col in range(9):
                if self.gamemap[row][col] == 7:
                    rowcheck = False
                    break
            if rowcheck:
                deleted_line = deleted_line + 1
                self.gamescore = self.gamescore + ((1000 + (500 * self.combo)) * deleted_line)
                self.scoreFrame.config(text="{:05d}".format(self.gamescore))
                deleted_row.append(row)

        # 지워져야할 row들을 지우고 채워줌
        deleted = 0
        deleted_row = sorted(deleted_row, reverse=True)
        for row in reversed(range(20)):
            if row in deleted_row:
                deleted = deleted + 1
            else:
                for col in range(10):
                    self.gamemap[row + deleted][col] = self.gamemap[row][col]
        self.redraw()
        if deleted >= 1:
            self.combo = self.combo + 1
            self.gameMessage.config(text="good!")
            if self.combo > 1:
                if self.combo > 2:
                    self.gameMessage.config(text="amazing! {} combo!".format(self.combo))
                else:
                    self.gameMessage.config(text="nice! {} combo!".format(self.combo))
        else:
            self.combo = 0

    def redraw(self):
        """
        줄을 지우고 새로 그림
        """
        self.gameFrame.delete('all')
        self.makeGrid()
        for row in range(20):
            for col in range(10):
                shape = self.gamemap[row][col]
                if(shape == 7):
                    continue
                start_x = (col) * 30
                start_y = (row) * 30
                end_x = start_x + 30
                end_y = start_y + 30
                self.gameFrame.create_rectangle(start_x, start_y, end_x, end_y, fill=shape_colors[shape], tag='prev')

    def drawBlcok(self):
        """
        current block은 매번 새로 그려줌
        미리 정의된 block shape 를 통해서 차지하고잇는부분에 색을 칠해줌
        """
        shape = self.currentBlock.shape
        self.gameFrame.delete('current')
        block = self.currentBlock.getCoordinates()
        for cord in block:
            row = cord['r']
            col = cord['c']
            start_x = (col) * 30
            start_y = (row) * 30
            end_x = start_x + 30
            end_y = start_y + 30
            self.gameFrame.create_rectangle(start_x, start_y, end_x, end_y, fill=shape_colors[shape], tag='current')

    def drawOtherBlock(self):
        """
        이미 땅에 도착한 블럭은 prev로써 계속 쌓임
        gamemap에 색깔(shape)과 함께 저장된다
        """
        shape = self.currentBlock.shape
        block = self.currentBlock.getCoordinates()
        for cord in block:
            row = cord['r']
            col = cord['c']
            start_x = col * 30
            start_y = row * 30
            end_x = start_x + 30
            end_y = start_y + 30
            self.gamemap[row][col]=shape
            self.gameFrame.create_rectangle(start_x, start_y, end_x, end_y, fill=shape_colors[shape], tag='prev')


    def hold(self):
        """
        이전에 홀드한 블럭과 지금 블럭을 바꾸고 새로그림
        """
        if self.holdUsed:
            self.gameMessage.config(text="Can't hold any more")
            return
        if self.holdBlockShape == self.currentBlock.shape:
            self.gameMessage.config(text="Can't hold same block!")
            return
        self.holdUsed = True

        print(self.currentBlock.shape, self.holdBlockShape)
        path = 'source/b' + str(self.currentBlock.shape) + '.png'
        self.holdBlockImage = PhotoImage(file=path)
        self.holdBlockFrame.config(image=self.holdBlockImage)
        self.currentBlock.shape, self.holdBlockShape = self.holdBlockShape, self.currentBlock.shape
        self.currentBlock.y = 1
        self.currentBlock.x = 5
        self.currentBlock.rotation = 0
        self.drawBlcok()
        self.gameMessage.config(text="Block holded")


class ResultWindow:
    def __init__(self, score):
        self.root=Tk()
        self.root.title('Game Over')
        self.root.geometry('{}x{}'.format(400, 100))
        lbl = Label(self.root, text="game over")
        lbl2 = Label(self.root, text="your score : {}".format(score), font=("Helvetica", 20))
        btn = Button(self.root, text="Quit", command=lambda: self.root.quit())
        lbl.pack()
        lbl2.pack()
        btn.pack()
        self.root.mainloop()


def main():
    game = GameWindow()
    score = game.gamescore
    ResultWindow(score)

if __name__ == '__main__':
    main()