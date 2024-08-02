import pygame

from board import *
from libs import *
from rating import *

screen_size = (1280,720)

size = 5,5 #size of the board (in tiles)
board_size = 100,100 #size of the board (in pixels)
settings = {
    "init_amt": 50, #inital amount of boards
    "limit": 1, #left over from previous gen
    "new_amt": 40, #amt of new boards created each gen
    "crossovers": 10, #amt of crossover pairs made using best boards
    "dup_len": 1, #how many of the prev gens boards will be dupped
    "dup_multi": 50, #times the batch of prev gen boards will be dupped
    "wchance": 0.1, #chance for a wall to be mutated into air
    "achance": 0.1, #chance for air to be mutated into wall
    "schance": 0.1, #chance for start and end to be mutated into new positions
    "gen_end": 70 #how many gens the ai will go on for
}

base_board = np.zeros(size)
pygame.init()
pygame.font.init()
screen = pygame.display.set_mode(screen_size)


def astar_board(board):
    astar = AStar(board)
    path = astar.path_find()
    return astar

def select_boards(boards):
    #filter the boards and check if they are possible mazes
    filtered_boards = []
    for b in boards:
        astar = astar_board(b.board)
        if not astar.impossible:
            b.stats = astar.stats()
            filtered_boards.append(b)
    #order them by a certain value, in this case we are going to order by steps
    filtered_boards.sort(key = lambda b: (b.stats['steps'], b.stats['deadends']), reverse=True)

    return filtered_boards

def crossover_boards(crossovers, boards):
    #on top of the chosen boards, we will cross over a certain number of boards
    #this will be added ON TOP OF the existing boards
    #NOTE: WE WILL NOT CHECK THESE BOARDS FOR VALIDITY UNTIL THEY PASS OVER THE NEXT GENERATION!
    c_boards = []
    for i in range(0,min(crossovers*2, len(boards)-1),2):
        #combine boards
        c_board = Board(base_board)
        flat1, flat2 = boards[i].board.flatten(), boards[i+1].board.flatten()
        split = random.randint(1, flat1.shape[0] - 1)
        c_flat = np.concatenate((flat1[:split], flat2[split:]))
        c_board.board = c_flat.reshape(boards[i].board.shape)

        #clear start and end positions
        for n in np.argwhere(c_board.board==2):
            c_board.board[n[0]][n[1]]=0
        for n in np.argwhere(c_board.board==3):
            c_board.board[n[0]][n[1]]=0

        # get new start and end positions
        g = random.randint(0,1)
        start = boards[i+g].get_start()
        end = boards[i+g].get_end()
        c_board.board[start[0]][start[1]] = 2
        c_board.board[end[0]][end[1]] = 3

        c_boards.append(c_board)

    return c_boards

def dup_boards(boards, multi, length):
    #this makes multiple copies of the currently existing boards
    # so that the same board can be mutated in different ways
    extra_boards = []
    for m in range(multi):
        extra_boards += boards[:length]

    return extra_boards

def create_new_boards(boards, amt):
    for _ in range(amt):
        boards.append(Board(base_board))
    return boards

def mutate_boards(boards, wchance=0.2, achance=0.2, schance=0.1):
    #wchance is chance for air to become wall
    #achance is chance for wall to become air
    #schance is chance for start or end to be displaced
    m_boards = []

    for b in boards:
        m = Board(base_board)
        m.board = np.copy(b.board)
        for y in range(m.board.shape[1]):
            for x in range(m.board.shape[0]):
                if m.board[y][x]==0:
                    if random.random() <= wchance:
                        m.board[y][x] = 1
                if m.board[y][x]==1:
                    if random.random() <= achance:
                        m.board[y][x] = 0
                if m.board[y][x]==2 or m.board[y][x]==3:
                    if random.random() <= schance:
                        spots = []
                        for pos in [[1, 0], [-1, 0], [0, -1], [0, 1]]:
                            nX, nY = x+pos[0], y+pos[1]
                            if nX >= 0 and nY >= 0 and nX < m.board.shape[0] and nY < m.board.shape[1]:
                                if m.board[nY][nX] == 0 or m.board[nY][nX] == 1:
                                    spots.append((nX, nY))
                        c = random.choice(spots)

                        m.board[c[1]][c[0]] = m.board[y][x]
                        m.board[y][x] = 0
        m_boards.append(m)
    return m_boards

def destory_dups(boards):
    true_boards = np.array([])
    for board in boards:
        true_boards= np.append(true_boards, board.board)
    true_boards = true_boards.reshape(len(boards), size[0], size[1])
    _, counts = np.unique(true_boards, axis=0, return_index=True)
    dels = np.delete(np.arange(0, len(true_boards)), np.sort(counts))
    dels = np.flip(dels)
    for d in dels:
        boards.pop(d)
    return boards

boards = []
boards = create_new_boards(boards, settings['init_amt'])
def run_evolution(boards):
    # crossover the best boards with one another
    cross_boards = crossover_boards(settings['crossovers'], boards)
    # dup boards
    duped_boards = dup_boards(boards, settings['dup_multi'], settings['dup_len'])
    # make mutated versions of dupped boards
    mutated_boards = mutate_boards(duped_boards, settings['wchance'], settings['achance'], settings['schance'])
    #limit to the best boards
    boards = boards[:settings['limit']]
    # add entirely new boards
    new_boards = create_new_boards([], settings['new_amt'])
    # add it all together
    boards += cross_boards
    boards += mutated_boards
    boards += new_boards
    # filter and order the boards
    boards = select_boards(boards)
    # delete all the duplicates
    boards = destory_dups(boards)
    print(boards[0].stats['steps'])

    return boards

running = False
gen = 1
plots = []
take = 1

my_font = pygame.font.SysFont('Segeo UI Semibold', 30)
gen_txt = my_font.render(f'Gen: {gen}', False, (255, 255, 255))
take_txt = my_font.render(f'Take: {take}', False, (255, 255, 255))
steps_txt = my_font.render(f'Best Board Score: {0}', False, (255, 255, 255))

runWindow = True
while runWindow:
    screen.fill((80,80,100))

    # render the boards
    x, y = 0,0
    for i, board in enumerate(boards):
        screen.blit(board.render(board_size[0], board_size[1]), (x,y))
        x+= board_size[0]+10
        if x+board_size[0]>screen_size[0]:
            y += board_size[1]+10
            x = 0

    screen.blit(steps_txt, (10, screen_size[1]-100))
    screen.blit(gen_txt, (10, screen_size[1]-70))
    screen.blit(take_txt, (10, screen_size[1]-40))


    if running:

        print(f'Gen {gen}')
        boards = run_evolution(boards)
        plots.append(boards[0].stats['steps'])
        gen += 1
        steps_txt = my_font.render(f'Best Board Score: {boards[0].stats['steps']}', False, (255, 255, 255))

        if gen > settings['gen_end']:
            fig, ax = plt.subplots()
            ax.plot(np.arange(1, gen), plots)
            ax.set(xlabel='Generations', ylabel='steps',
                   title='Graph')
            ax.grid()

            name = f"board{take}_{size[0]}x{size[1]}_mxstps{plots[-1]}"
            fig.savefig(f"output/{name}_chart.png")
            pygame.image.save(boards[0].render(1000, 1000), f"output/{name}_lvlimg.jpg")
            DF = pd.DataFrame(boards[0].board)
            DF.to_csv(f"output/{name}_data.csv")
            plt.close(fig)

            gen = 1
            take+= 1
            plots = []
            boards = []
            boards = create_new_boards(boards, settings['init_amt'])
            take_txt = my_font.render(f'Take: {take}', False, (255, 255, 255))
        gen_txt = my_font.render(f'Gen: {gen}', False, (255, 255, 255))


    pygame.display.update()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            runWindow = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                pygame.image.save(screen, "screenshot.png")
                print("Screenshot saved.")
            if event.key == pygame.K_SPACE:
                running = not running
pygame.quit()



