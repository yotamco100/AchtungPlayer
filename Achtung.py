import pygame
from Sprites import Player1B
from random import *
from datetime import datetime
#import achtung_mapping
from time import time, sleep
WINDOW_WIDTH = 1080
WINDOW_HEIGHT = 720
MIDDLE = [WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2]  # the middle point of the screen
LEFT = 1
FLIP = True
RELATIVE_REFRESH = 2
REFRESH_RATE = 199 #* RELATIVE_REFRESH  # tickrate of the game
MIN_COLOR = 0
MAX_COLOR = 255
FLAGS = pygame.DOUBLEBUF | pygame.HWSURFACE
# FLAGS = pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE
# FLAGS = pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.RESIZABLE
COUNTDOWN = 3
JUMPS = {
    "x": [120, 250, 175, 175],
    "y": [120] + ([100] * 6)
}
ORIGINAL_WINDOW = (720, 720)
x_mul = 1
y_mul = 1
if sum(JUMPS["x"]) != WINDOW_WIDTH or sum(JUMPS["y"]) != WINDOW_HEIGHT:
    # Map?
    x_mul = WINDOW_WIDTH / float(ORIGINAL_WINDOW[0])
    for j in xrange(len(JUMPS["x"])):
        JUMPS["x"][j] *= x_mul
        JUMPS["x"][j] = int(round(JUMPS["x"][j]))
    y_mul = WINDOW_HEIGHT / float(ORIGINAL_WINDOW[1])
    for j in xrange(len(JUMPS["y"])):
        JUMPS["y"][j] *= y_mul
        JUMPS["y"][j] = int(round(JUMPS["y"][j]))
RELATIVE = [int(min(x_mul, y_mul))] * 2
STRINGS = [
    "Used", "Color", "Left", "Right",
    "Red", "a", "d",
    "Blue", "left", "right",
    "Yellow", "", "",
    "Pink", "z", "x",
    "Orange", "", "",
    "White", "", ""
]
BLACK = (0, 0, 0, 1)
BLACK_PIXEL = (0, 0, 0, 255)
WHITE = (255, 255, 255, 0.8)
FUCHSIA = (255, 0, 255, 0.9)
BLUE = (0, 0, 238, 0.96)
ORANGE = (255, 140, 0, 0.9)
YELLOW = (255, 255, 0, 0.8)
RED = (255, 0, 0, 0.9)
GREEN = (0, 100, 0, 0.9)
COLORS = [
    GREEN, RED, BLUE, YELLOW, FUCHSIA, ORANGE, WHITE
]
PATH = pygame.font.match_font('comicsansms')
#ICON = "Extras\\icon.png"
DEAD_SPACE = 10
COUNT_SIZE = min(WINDOW_WIDTH / 7, WINDOW_HEIGHT / 7)
LIMIT = 25
STARTING_VEL = 100.0 #/ RELATIVE_REFRESH
change_angle = 3.0 #/ RELATIVE_REFRESH
MAX_ROUNDS = 10
WIN_SCORE = 15
BLANK_SPACE = 10  #  * RELATIVE_REFRESH
GREETING = "Congratulations, You beat yourself! " \
           "I hope you are proud of yourself! " \
           "You are the best player ever! " \
           "You are incredible!" \
           "Amazing player! " \
           "Bravo, Just bravo!"
RAND_SPEED = 400
RAND_ANG = 30
FORBID_MULTIBIND = False
RANDOM_STATS = False
vel = STARTING_VEL


def initiate_screen():
    """
    Name: initiate_screen
    Purpose: Initiate screen, gets pygame clock
    """
    pygame.init()
    size = (WINDOW_WIDTH, WINDOW_HEIGHT)
    screen = pygame.display.set_mode(size, FLAGS)
    #icon = pygame.image.load(ICON)
    #pygame.display.set_icon(icon)
    pygame.display.set_caption("Minecraft")
    screen.fill(BLACK)
    clock = pygame.time.Clock()
    return screen, clock


def fair_square(screen, r1, color):
    """
    Name: fair_square
    Purpose: Fill a given square in a given color
    """
    screen.fill(color, r1)


def draw_lines(screen):
    x = 0
    y = 0
    for m in JUMPS["x"]:
        x += m
        y0 = 0
        y1 = WINDOW_HEIGHT - 1
        pygame.draw.line(screen, WHITE, (x, y0), (x, y1))
    for l in JUMPS["y"]:
        y += l
        x0 = 0
        x1 = WINDOW_WIDTH - 1
        pygame.draw.line(screen, WHITE, (x0, y), (x1, y))


def separate_rects(rects):
    pointer = 0
    texts = []
    circles = []
    for stuff in rects:
        if stuff[-2] == "Text":
            size = min(stuff[1].width, stuff[1].height) - (2 * DEAD_SPACE)
            size /= 2
            # size = 30
            font = pygame.font.Font(PATH, size)
            color = COLORS[stuff[0][1]]
            text = font.render(STRINGS[pointer], True, color)
            # text = font.render("1", True, color)
            meaningful_name2 = (stuff[0], stuff[1], text, color, font)
            texts.append(meaningful_name2)
            pointer += 1
        elif stuff[-2] == "Circle":
            radius = min(stuff[1].width, stuff[1].height) - (2 * DEAD_SPACE)
            radius /= 2
            mid = stuff[1].center
            color = COLORS[stuff[0][1]]
            meaningful_name3 = (stuff[0], color, mid, radius, False)
            circles.append(meaningful_name3)
    return texts, circles


def tap_and_type(texts, circles, rects):
    combo = texts + circles
    combos = sorted(combo, key=lambda tup: (tup[0][1], tup[0][0]))
    strings_point_func = lambda tup: (tup[1] - 1) * 3 + tup[0] - 2
    pointer = 0
    strings_pointer = 5
    new_list = []
    for r in rects:
        if r[0] == combos[pointer][0]:
            if r[-1]:
                if r[-2] == "Text":
                    st = "Type"
                    loc = strings_point_func(list(r[0]))
                    state = STRINGS[strings_pointer + loc]
                    size = combos[pointer][4]
                    color = combos[pointer][3]
                else:
                    st = "Tap"
                    state = False
                    size = combos[pointer][3]
                    color = combos[pointer][1]
                new_list.append(([r[1]] + [st] + [state] + [size] + [color]))
            pointer += 1
    return new_list


def start_menu(screen):
    rects = []
    x = 0
    x_tup = 0
    while x + JUMPS["x"][x_tup] <= sum(JUMPS["x"]):
        y = 0
        y_tup = 0
        while y + JUMPS["y"][y_tup] <= sum(JUMPS["y"]):
            r = pygame.Rect(x, y, JUMPS["x"][x_tup], JUMPS["y"][y_tup])
            changeable = False
            if (x_tup < 1 or x_tup > 1) and y_tup > 0:
                changeable = True
            st = "Text"
            if x_tup == 0 and y_tup > 0:
                st = "Circle"
            meaningful_name = ((x_tup, y_tup), r, st, changeable)
            rects.append(meaningful_name)
            y += JUMPS["y"][y_tup]
            y_tup += 1
            if y_tup == len(JUMPS["y"]):
                break
        x += JUMPS["x"][x_tup]
        x_tup += 1
        if x_tup == len(JUMPS["x"]):
            break
    rects = sorted(rects, key=lambda tup: (tup[0][1], tup[0][0]))
    texts, circles = separate_rects(rects)
    refresh_rects = []
    for t in texts:
        loc = t[2].get_rect()
        loc.center = t[1].center
        refresh_rects.append(screen.blit(t[2], loc))
    for c in circles:
        color = c[1]
        mid = c[2]
        radius = c[3]
        width = not c[4]
        refresh_rects.append(pygame.draw.circle(screen, color, mid,
                                                radius, width))
    draw_lines(screen)
    #pygame.display.flip()
    new_list = tap_and_type(texts, circles, rects)
    return new_list


def rand_start():
    x = randint(LIMIT * 4, WINDOW_WIDTH - LIMIT * 4)
    y = randint(LIMIT * 4, WINDOW_HEIGHT - LIMIT * 4)
    return x, y


def rand_angle():
    return randint(0, 360)


def update_all(screen, rects):
    for r in rects:
        if r[1] == "Type":
            text = r[3].render(r[2], True, r[-1], BLACK)
            loc = text.get_rect()
            loc.center = r[0].center
            screen.blit(text, loc)
        else:
            color = r[-1]
            pos = r[0].center
            radius = r[-2]
            width = not r[2]
            if width == 1:
                width = 0
                radius -= 1
                color = BLACK
            pygame.draw.circle(screen, color, pos, radius, width)
    if FLIP:

	pygame.display.flip()


def binder(screen, r, dictionary, key):
    t = r[3].render(r[2], True, BLACK, BLACK)
    loc = t.get_rect()
    loc.center = r[0].center
    screen.blit(t, loc)
    pygame.display.update(loc)
    r[2] = str(key)
    place = r[0].centerx
    c = 0
    for loc in JUMPS["x"]:
        if place - loc < 0:
            break
        place -= loc
        c += 1
    c -= 2
    if all(num in '01' for num in str(c)):
        keys = dictionary.keys()
        values = dictionary.values()
        i = keys.index(r[-1])
        values[i][c] = r[2]
        dictionary = dict(zip(keys, values))
    return dictionary


def something(screen, r, dictionary):
    space_pressed = False
    condition = True
    while condition:
        for event2 in pygame.event.get():
            if event2.type == pygame.QUIT:
                space_pressed = True
                condition = False
            elif event2.type == pygame.KEYDOWN:
                condition2 = True
                key = str(pygame.key.name(event2.key))
                if not len(key) > 6:
                    for value in dictionary.values():
                        if key in value and FORBID_MULTIBIND:
                            condition2 = False
                            break
                    if condition2:
                        dictionary = binder(screen, r, dictionary, key)
                        condition = False
                        break
    return space_pressed, dictionary


def binds(screen, clock, rects):
    # ([r[1]] + [st] + [state] + [size] + [color])
    space_pressed = False
    colors_counter = []
    on = []
    for i in xrange(4, len(STRINGS) - 1, 3):
        colors_counter.append([STRINGS[i + 1], STRINGS[i + 2]])
    for i in xrange(1, len(COLORS)):
        on.append((COLORS[i], False))
    on = dict(on)
    colors_counter = [(COLORS[i + 1], colors_counter[i])
                      for i in xrange(0, len(COLORS) - 1)]
    dictionary = dict(colors_counter)
    x = 0
    y = 0
    done = False
    print rects
    while not space_pressed:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                space_pressed = True
                done = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Left mouse button pressed
                if event.button == LEFT:
                    x, y = pygame.mouse.get_pos()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    space_pressed = True
                if event.key == pygame.K_ESCAPE:
                    space_pressed = True
                    done = True
            elif x != 0 or y != 0:
                for index, r in enumerate(rects):
                    if r[0].collidepoint(x, y):
                        if r[1] == "Tap":
                            r[2] = not r[2]
                            on[r[-1]] = not on[r[-1]]
                        elif r[1] == "Type":
                            space_pressed, dictionary = something(screen, r,
                                                                  dictionary)
                    rects[index] = r
                x = y = 0
        update_all(screen, rects)
        if FLIP:

            pygame.display.flip()
        clock.tick(REFRESH_RATE)
    for color, condition in on.items():
        if (not condition) or ("" in dictionary[color]):
            del(dictionary[color])
    colors_counter = dictionary.items()
    if len(colors_counter) == 0:
        done = True
    print colors_counter, done
    return colors_counter, done


def countdown(screen, number, font):
    sec = int(datetime.now().second)
    new_sec = sec
    rect = screen.get_rect()
    for x in xrange(1, number + 1):
        while ((sec + x) % 60) != new_sec:
            new_sec = int(datetime.now().second)
        s = number - x + 1
        pygame.display.update(rect)
        count = font.render(str(s), True, FUCHSIA)
        rect = count.get_rect()
        rect.x = MIDDLE[0] - (rect.width / 2)
        rect.y = MIDDLE[1] - (rect.height / 2)
        screen.blit(count, rect.topleft)
        pygame.display.update(rect)
        fair_square(screen, rect, BLACK)
    for x in xrange(1, 3):
        while ((sec + number + x) % 60) != (new_sec % 60):
            new_sec = int(datetime.now().second)
        pygame.display.update(rect)
        if x == 1:
            go = font.render("Go!", True, FUCHSIA)
            rect = go.get_rect()
            rect.x = MIDDLE[0] - (rect.width / 2)
            rect.y = MIDDLE[1] - (rect.height / 2)
            screen.blit(go, rect.topleft)
            pygame.display.update(rect)
            fair_square(screen, rect, BLACK)


def shape_mask_by_player(player):
    w, h = player.mask.get_size()
    points = []
    p_x, p_y = player.get_pos()
    for y in xrange(h):
        for x in xrange(w):
            if player.mask.get_at((x, y)):
                points.append((x + p_x, y + p_y))
    return points


def update_sprites(screen, players, scores,
                   angles, players_count, masks):
    new_players = pygame.sprite.Group()
    dead = pygame.sprite.Group()
    array = pygame.PixelArray(screen)
    for player in players:
        old_mask = set(shape_mask_by_player(player))
        player.update_a(angles.get(player.get_color(), 0))
        masks[player.get_color()].append(old_mask)
        if len(masks[player.get_color()]) > 10:
            del(masks[player.get_color()][0])
        player.update_v_a()
        player.update_loc()
        """My father's idea
        if player.get_color() == RED:
            new_players.add(player)
            continue
        """
        condition = True
        mask = set(shape_mask_by_player(player))

        mask = mask.difference(*masks[player.get_color()])
        
        for m2 in mask:
            try:
                color = array[m2]
                if color != 0 and color != BLACK_PIXEL and color != BLACK and color != (66, 244, 167, 255):
                    condition = False
                    break
            except:
                condition = False
                break
        if condition:
            new_players.add(player)
        else:
            dead.add(player)
    for player in dead:
        scores[player.get_color()] += (players_count - len(new_players)) - 1
    return new_players, scores, masks


def prevent_failure(keys):
    events = pygame.event.get()
    pressed = []
    conditions = []
    space = False
    event_types = []
    for event in events:
        event_types.append(event.type)
    if pygame.QUIT in event_types:
        conditions.append(False)
    else:
        conditions.append(True)
    if pygame.KEYDOWN in event_types:
        bot_used_keys = {97: pygame.key.get_pressed()[97], 100:pygame.key.get_pressed()[100]}
        for key, state in bot_used_keys.iteritems():
            if str(pygame.key.name(key)) in keys and state:
                # print "key:", key, "state:", state
                pressed.append(str(pygame.key.name(key)))
            elif key == pygame.K_ESCAPE and state:
                conditions[0] = False
            elif key == pygame.K_SPACE and state:
                space = True
    if len(pressed) > 0:
        conditions.append((True, pressed))
    else:
        conditions.append((False, []))
    conditions += [space]
    return conditions


def draw_borders(screen):
    pygame.Rect(LIMIT, LIMIT, WINDOW_WIDTH - (2 * LIMIT),
                WINDOW_HEIGHT - (2 * LIMIT))
    pygame.draw.rect(screen, WHITE, screen.get_rect(), LIMIT)
    if FLIP:

	pygame.display.flip()


def get_line(condition):
    if condition:
        return BLANK_SPACE
    distance = []
    for i in xrange(20):
        if i < 4:
            distance.append(randint(6, 10))
        else:
            distance.append(randint(18, 30))
    return choice(distance) * BLANK_SPACE

def one_round(screen, players, masks, font, scores, angles,
              keys_that_matter, clock):
    #my_time = time()
    keys_that_matter = sorted(keys_that_matter)
    global alive
    alive = players.copy()
    players_count = len(players)
    screen.fill(BLACK)
    draw_borders(screen)
    #countdown(screen, COUNTDOWN, font)
    alive.draw(screen)
    blank = {}
    blank_players = pygame.sprite.GroupSingle()
    global change_angle
    for player in alive:
        blank[player.get_color()] = get_line(False)
    while len(alive) > 0:
        #my_time = time()
        #bot_player = achtung_mapping.get_my_player(alive)
        #achtung_mapping.prepare_data(bot_player)
        # The bot gets the state of the game
        """
        # YOTOM'S SHIT
        bot = None
        for player in alive:
            if player.get_color() == RED:
                bot = player
        if bot is not None:
            pos_x, pos_y = player.rect.center
            min_row = max(pos_y - 50, 0)
            max_row = min(min_row + 100, 720)
            min_row = max(max_row - 100, 0)
            min_col = max(pos_x - 50, 0)
            max_col = min(min_col + 100, 1080)
            min_col = max(max_col - 100, 0)
            print min_col, min_row
            print max_col, max_row
            my_rect = pygame.Rect(min_col, min_row, 100, 100)
            pygame.draw.rect(screen, RED, my_rect, 2)
        # END YOTOMS SHIT
        """
        #print "----------------------------------------------------------------------------------------"
        t = pygame.time.get_ticks()
        #print t
        conditions = prevent_failure(keys_that_matter)
        if not conditions[0]:
            return scores, True
        # Binds
        
        if conditions[1][0]:
            pressed = set(conditions[1][1])
            # print pressed
            for player in alive:
                player_binds = player.get_binds()
                set_binds = set(player_binds)
                new_set = set_binds.intersection(pressed)
                if len(new_set) != 1:
                    continue
                angle = -change_angle
                if player_binds.index(new_set.pop()) == 0:
                    angle = change_angle
                angles[player.get_color()] = angle
        t2 = pygame.time.get_ticks()
        #print t2 - t
        t = t2
        # Space pressed (freeze)
        if conditions[-1]:
            condition = True
            while condition:
                for event2 in pygame.event.get():
                    if event2.type == pygame.KEYUP:
                        if event2.key == pygame.K_SPACE:
                            condition = False
        t2 = pygame.time.get_ticks()
        #print t2 - t
        t = t2
        alive, scores, masks = update_sprites(screen, alive, scores, angles,
                                              players_count, masks)
        alive.draw(screen)
        if FLIP:

            pygame.display.flip()
        blank_players.empty()
        for player in alive:
            color = player.get_color()
            if blank[color] == 0:
                player.change_blank_line()
                blank[color] = get_line(player.get_blank_line())
            if player.get_blank_line():
                shadow = shadow_player(player)
                screen.blit(shadow.get_image(), shadow.get_pos())
            blank[color] -= 1
        for key in angles.keys():
            angles[key] = 0
        #print clock.get_fps()
        #print time()-my_time
        clock.tick(REFRESH_RATE)
        #The screen finishes updating here. next_state is available
    for player in alive:
        scores[player.get_color()] += players_count - 1
    return scores, False


def shadow_player(player):
    copy_p = Player1B(player.get_mid(), STARTING_VEL, player.get_angle(),
                      BLACK, ("", ""), RELATIVE + [])
    return copy_p


def new_player(player):
    global vel
    new_p = Player1B(rand_start(), vel, rand_angle(),
                     player.get_color(), player.get_binds(), RELATIVE + [])
    return new_p


def score_board(screen, scores):
    colors_list = []
    scores_list = []
    texts = []
    for color in COLORS:
        if color in scores.keys():
            colors_list.append(COLORS.index(color))
            texts.append(STRINGS[(3 * colors_list[-1]) + 1])
            scores_list.append(scores[color])
    all_list = []
    for score, text, color in zip(scores_list, texts, colors_list):
        all_list.append((score, text, color))
    all_list = sorted(all_list, key=lambda tup2: (-tup2[0], tup2[-1]))
    scores_list = []
    texts = []
    colors_list = []
    for tup in all_list:
        scores_list.append(tup[0])
        texts.append(tup[1])
        colors_list.append(COLORS[tup[2]])
    size = WINDOW_HEIGHT / (len(texts) + DEAD_SPACE)
    font = pygame.font.Font(PATH, size)
    board = []
    mid_y = DEAD_SPACE
    for x in xrange(len(colors_list)):
        st = texts[x] + ": " + str(scores_list[x])
        text = font.render(st, True, colors_list[x], BLACK)
        mid_y += text.get_height() + DEAD_SPACE
        board.append(text)
    y = (WINDOW_HEIGHT - mid_y) / 2
    for i in xrange(len(board)):
        rect = board[i].get_rect()
        rect.x = MIDDLE[0] - (rect.width / 2)
        rect.y = y
        y += DEAD_SPACE + rect.height
        screen.blit(board[i], rect.topleft)
    if FLIP:

	pygame.display.flip()


def get_winner(screen, scores):
    screen.fill(BLACK)
    draw_borders(screen)
    players_scores = scores.values()
    max_score = max(players_scores)
    if players_scores.count(max_score) > 1:
        title = "The winners are: "
    else:
        title = "The winner is: "
    winners = [title]
    indexes = [GREEN]
    for color, value in scores.items():
        if value == max_score:
            index = COLORS.index(color)
            indexes.append(COLORS[index])
            index *= 3
            index += 1
            winners.append(STRINGS[index])
    size = WINDOW_HEIGHT / (len(winners) + DEAD_SPACE)
    font = pygame.font.Font(PATH, size)
    texts = []
    mid_y = DEAD_SPACE
    for i, v in enumerate(winners):
        text = font.render(v, True, indexes[i])
        mid_y += text.get_height() + DEAD_SPACE
        texts.append(text)
    y = (WINDOW_HEIGHT - mid_y) / 2
    for text in texts:
        rect = text.get_rect()
        rect.x = MIDDLE[0] - (rect.width / 2)
        rect.y = y
        y += DEAD_SPACE + rect.height
        screen.blit(text, rect.topleft)
        pygame.display.update(rect)


def separator_by_line(text, sep=" "):
    """
    Find average length of strings in list
    """
    length = len(text)
    text = text.split(sep)
    avg = len(text) / length
    new_text = [""]
    print text
    for word in text:
        new_text[-1] += word + sep
        if len(new_text[-1]) > avg:
            if sep == " ":
                new_text[-1] = new_text[-1]
            new_text.append("")
    text = []
    for word in new_text:
        if len(word) > 1:
            text.append(word)
    return text


def proud_of_yourself(screen, player):
    fair_square(screen, screen.get_rect(), BLACK)
    color = player.get_color()
    text = separator_by_line(GREETING, "!")
    index = COLORS.index(color) * 3 + 1
    text.append(STRINGS[index])
    size = min(WINDOW_WIDTH, WINDOW_HEIGHT)
    size /= (len(text) + DEAD_SPACE)
    font = pygame.font.Font(PATH, size)
    texts = []
    mid_y = DEAD_SPACE
    for line in text:
        rendered = font.render(line, True, color)
        mid_y += rendered.get_height() + DEAD_SPACE
        texts.append(rendered)
    y = (WINDOW_HEIGHT - mid_y) / 2
    for string in texts:
        rect = string.get_rect()
        rect.x = MIDDLE[0] - (rect.width / 2)
        rect.y = y
        y += DEAD_SPACE + rect.height
        screen.blit(string, rect.topleft)
    if FLIP:

	pygame.display.flip()


def random_is_funny():
    return randint(-RAND_SPEED, RAND_SPEED), randint(-RAND_ANG, RAND_ANG)


def endless(screen, clock):
    rects = start_menu(screen)
    font = pygame.font.Font(PATH, COUNT_SIZE)
    pygame.key.set_repeat(1, 0)
    binds_list, done = binds(screen, clock, rects)
    print binds_list
    if done:
        return
    keys_that_matter = []
    rounds = 0
    scores = {}
    angles = {}
    masks = {}
    empty = {}
    players = pygame.sprite.Group()
    new_players = pygame.sprite.Group()
    pygame.mouse.set_visible(0)
    if RANDOM_STATS:
        global change_angle
        global vel
        vel, change_angle = random_is_funny()
        print "VEL: {}\nANGLE: {}".format(vel, change_angle)
    for x in xrange(len(binds_list)):
        color = binds_list[x][0]
        print color
        scores[color] = 0
        angles[color] = 0
        keys_that_matter.append(binds_list[x][1][0])
        keys_that_matter.append(binds_list[x][1][1])
        print "R:", RELATIVE
        player = Player1B(rand_start(), vel, rand_angle(),
                          color, binds_list[x][1], RELATIVE + [])
        players.add(player)
        masks[color] = []
        empty[color] = []
    show_winners = len(players) != 1
    if len(players) == 1:
        proud_of_yourself(screen, players.sprites()[0])
        done = True
    while (not done) and (rounds < MAX_ROUNDS)\
            and max(scores.values()) < WIN_SCORE:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    scores, done = one_round(screen, players, masks,
                                             font, scores, angles,
                                             keys_that_matter, clock)
                    for key in masks.keys():
                        masks[key] = []
                    rounds += 1
                    new_players.empty()
                    if RANDOM_STATS:
                        vel, change_angle = random_is_funny()
                        print "VEL: {}\nANGLE: {}".format(vel, change_angle)
                    for player in players:
                        player.kill()
                        player = new_player(player)
                        new_players.add(player)
                    players = new_players.copy()
                    score_board(screen, scores)
                    break
                elif event.key == pygame.K_ESCAPE:
                    done = True
    condition = True
    if show_winners:
        get_winner(screen, scores)
    pygame.time.delay(1000)
    while condition:
        events = [event.type for event in pygame.event.get()]
        if pygame.QUIT in events or pygame.KEYDOWN in events:
            condition = False
        clock.tick(REFRESH_RATE)
    pygame.quit()
    return


def quickstart(screen, clock):
    #rects = start_menu(screen)
    font = pygame.font.Font(PATH, COUNT_SIZE)
    pygame.key.set_repeat(1, 0)
    binds_list, done = [((255, 0, 0, 0.9), ['a', 'd'])], False  # , ((0, 0, 238, 0.96), ['left', 'right'])], False)
    if done:
        return
    keys_that_matter = []
    rounds = 0
    scores = {}
    angles = {}
    masks = {}
    empty = {}
    players = pygame.sprite.Group()
    new_players = pygame.sprite.Group()
    pygame.mouse.set_visible(0)
    if RANDOM_STATS:
        global change_angle
        global vel
        vel, change_angle = random_is_funny()
        print "VEL: {}\nANGLE: {}".format(vel, change_angle)

    #TECH's BULLSHIT
    player = Player1B(rand_start(), vel, rand_angle(),
                      (255, 0, 0, 0.9), ['a', 'd'], RELATIVE + [])
    players.add(player)
    """
    player = Player1B(rand_start(), vel, rand_angle(),
                      (0, 0, 238, 0.96), ['left', 'right'], RELATIVE + [])
    players.add(player)
    """
    #QUICKSTART
    masks = {(255, 0, 0, 0.9): []}  # , (0, 0, 238, 0.96): []}
    font = pygame.font.Font(PATH, COUNT_SIZE)
    scores = {(255, 0, 0, 0.9): 0}  # , (0, 0, 238, 0.96): 0}
    angles = {(255, 0, 0, 0.9): 0}  #  ,(0, 0, 238, 0.96): 0}
    keys_that_matter = ['a', 'd']  # , 'left', 'right']
    #END
    show_winners = len(players) != 1
    while (not done):
        scores, done = one_round(screen, players, masks,
                                 font, scores, angles,
                                 keys_that_matter, clock)
        for key in masks.keys():
            masks[key] = []
        rounds += 1
        new_players.empty()
        if RANDOM_STATS:
            vel, change_angle = random_is_funny()
            print "VEL: {}\nANGLE: {}".format(vel, change_angle)
        for player in players:
            player.kill()
            player = new_player(player)
            new_players.add(player)
        players = new_players.copy()
        #score_board(screen, scores)
    condition = True
    if show_winners:
        get_winner(screen, scores)
    #pygame.time.delay(1000)
    while condition:
        events = [event.type for event in pygame.event.get()]
        if pygame.QUIT in events or pygame.KEYDOWN in events:
            condition = False
        clock.tick(REFRESH_RATE)
    pygame.quit()
    return


def main():
    screen, clock = initiate_screen()
    quickstart(screen, clock)


if __name__ == '__main__':
    main()
