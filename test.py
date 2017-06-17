import wx
import copy
from scipy import misc
from PIL import Image
app = wx.App()


def get_screen(num_screen):
    img = screenshot_screen(num_screen)
    # img = Image.open('backup_screenshot.png')
    return img
    # screen = wx.ScreenDC()
    # geometry = wx.Display(num_screen).GetGeometry()
    # return screen, geometry


def screenshot_screen(num_screen):
    screen = wx.ScreenDC()
    geometry = wx.Display(num_screen).GetGeometry()
    # size = screen.GetSize()
    bmp = wx.Bitmap(geometry.GetWidth(), geometry.GetHeight())
    mem = wx.MemoryDC(bmp)
    mem.Blit(0, 0, geometry.GetWidth(), geometry.GetHeight(),
             screen, geometry.GetX(), geometry.GetY())
    bmp.SaveFile('screenshot2.png', wx.BITMAP_TYPE_PNG)
    img = Image.open('screenshot2.png')
    return img


def get_gem(img, x, y):
    width = 119
    height = 119
    crop_x = 62
    crop_y = 62
    start_x = 485
    start_y = 80
    gem_x = x * width
    gem_y = y * height
    area = (start_x + gem_x + 22,
            start_y + gem_y + 32,
            start_x + gem_x + 22 + crop_x,
            start_y + gem_y + 32 + crop_y
            )
    img = img.crop(area)
    filename = './tmp/gem_{}-{}.png'.format(y, x)
    img.save(filename)
    # bmp = wx.Bitmap(crop_x, crop_y)
    # mem = wx.MemoryDC(bmp)
    # mem.Blit(0, 0, crop_x, crop_y, src[0],
    #          src[1].GetX() + start_x + gem_x + 22,
    #          src[1].GetY() + start_y + gem_y + 32)
    # # from ipdb import set_trace; set_trace()
    # del mem
    # bmp.SaveFile(filename, wx.BITMAP_TYPE_PNG)
    return filename


def get_board():
    s = get_screen(2)
    y = 0
    board = []
    for y in range(8):
        row = []
        for x in range(8):
            filename = get_gem(s, x, y)
            color = average_color(filename)
            if color == "brown":
                row.append('O')
            else:
                row.append(color[0].capitalize())
            # print(x, y, color)
        board.append(row)
    return board


types = {
    'gold': {
        'red': (215, 225),
        'green': (155, 170),
        'blue': (55, 65),
        },
    'bronze': {
        'red': (155, 175),
        'green': (70, 90),
        'blue': (50, 70),
        },
    'bag': {
        'red': (100, 110),
        'green': (60, 80),
        'blue': (50, 65),
        },
    'silver': {
        'red': (120, 140),
        'green': (155, 175),
        'blue': (165, 185),
        },
    'blue': {
        'red': (40, 50),
        'green': (115, 130),
        'blue': (185, 200),
        },
    'red': {
        'red': (190, 210),
        'green': (40, 60),
        'blue': (40, 50),
        },
    'green': {
        'red': (60, 70),
        'green': (150, 165),
        'blue': (30, 40),
        },
    'yellow': {
        'red': (225, 235),
        'green': (185, 195),
        'blue': (65, 80),
        },
    'purple': {
        'red': (120, 130),
        'green': (30, 45),
        'blue': (170, 180),
        },
    'skull': {
        'red': (120, 135),
        'green': (120, 135),
        'blue': (120, 130),
        },
    'brown': {
        'red': (95, 105),
        'green': (65, 75),
        'blue': (60, 70),
        },
}


def decide_color(rgb):
    r, g, b = rgb
    for name, color in types.items():
        if color['red'][0] < r < color['red'][1]:
            if color['green'][0] < g < color['green'][1]:
                if color['blue'][0] < b < color['blue'][1]:
                    return name
    return "?"


def average_color(image):
    img = misc.imread(image)
    rgb = img.mean(axis=(0, 1))
    # print(rgb)
    color = decide_color(rgb)
    return color


def ascii_board(board):
    print('  0 1 2 3 4 5 6 7')
    for i, row in enumerate(board):
        print('{} {}'.format(i, " ".join(row)))
    print("")


def generate_checks():
    checks = []
    for y in range(8):
        for x in range(6):
            checks.append(((y, x), (y, x + 1), (y, x + 2)))
    for y in range(6):
        for x in range(8):
            checks.append(((y, x), (y + 1, x), (y + 2, x)))
    return checks


def generate_moves():
    moves = []
    for y in range(8):
        for x in range(7):
            moves.append(((y, x), (y, x + 1)))
    for y in range(7):
        for x in range(8):
            moves.append(((y, x), (y + 1, x)))
    return moves


def resolve(board):
    checks = generate_checks()
    new_board = copy.deepcopy(board)
    for check in checks:
        (y1, x1), (y2, x2), (y3, x3) = check
        if board[y1][x1] == board[y2][x2] == board[y3][x3]:
            if board[y1][x1] == '-' or\
                board[y2][x2] == '-' or\
                    board[y3][x3] == '-':
                    continue
            # print("Match from {}-{} to {}-{}".format(
            #     x1, y1, x3, y3
            # ))
            # print(check)
            new_board[y1][x1] = '_'
            new_board[y2][x2] = '_'
            new_board[y3][x3] = '_'
    # ascii_board(new_board)
    changed = False
    for x in range(8):
        for y in range(7, 0, -1):
            if new_board[y][x] == '_':
                cur_y = y
                while new_board[cur_y][x] == '_' and cur_y >= 0:
                    cur_y -= 1
                if cur_y == -1:
                    continue
                new_board[cur_y][x], new_board[y][x] = \
                    new_board[y][x], new_board[cur_y][x]
                if new_board[y][x] != '_':
                    changed = True
    if changed:
        return resolve(new_board)
    # ascii_board(new_board)
    matches = 0
    for row in board:
        matches += "".join(row).count('_')
    return new_board, matches


# def switch(board, x1, y1, x2, y2):
#     board[y1][x1], board[y2][x2] = board[y2][x2], board[y1][x1]
#     return board
def switch(board, gem1, gem2):
    board[gem1[0]][gem1[1]], board[gem2[0]][gem2[1]] =\
        board[gem2[0]][gem2[1]], board[gem1[0]][gem1[1]]
    return board


def fill_board(board):
    for row in board:
        for i, color in enumerate(row):
            if color == '_':
                row[i] = '-'
    return board


def test_moves(board, moves):
    best_move, best_matches = None, 0
    for move in moves:
        (y1, x1), (y2, x2) = move
        new_board = copy.deepcopy(board)
        switch(new_board, (y1, x1), (y2, x2))
        new_board, matches = resolve(new_board)
        if matches > best_matches:
            best_matches = matches
            best_move = move
            # print("Best Move: {} with {} matches".format(best_move, matches))
    print("Best Move: {} with {} matches".format(best_move, best_matches))
    return best_move, best_matches


moves = generate_moves()

board = get_board()
ascii_board(board)

move, matches = test_moves(board, moves)
board = switch(board, move[0], move[1])
ascii_board(board)
board, matches = resolve(board)
ascii_board(board)

# board = switch(board, 1, 6, 1, 5)
# ascii_board(board)
# board, matches = resolve(board)
# print(matches)
#
# board = fill_board(board)
# board = switch(board, 3, 3, 4, 3)
# ascii_board(board)
# board, matches = resolve(board)
# print(matches)

# To get the count of displays

# num_displays = wx.Display.GetCount()
#
# # Open a frame on each display
# for display_num in range(num_displays):
#     # Get a display object
#     display = wx.Display(display_num)
#
#     # To get a wx.Rect that gives the geometry of a display
#     geometry = display.GetGeometry()
#
#     # Create a frame on the display
#     frame = wx.Frame(None,
#                      -1,
#                      "Display %d" % display_num,
#                      geometry.GetTopLeft(),
#                      geometry.GetSize()
#                      )
#
#     # Make the frame visible
#     frame.Show()
#
# app.MainLoop()
