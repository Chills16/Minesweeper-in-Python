
#Minesweeper
#Dávid Buko, I. ročník Bc.
#zimný semester 2022/23
#Programování NPRG030


#import needed modules which are used for the program

#to display the game and its parameters
import pygame

#in this program: 1. to displace mines when generating minefield randomly
#                 2. to place the initial position of the pc solver 
import random

#to correctly display the timer for the game
import time

#used for a proper exit out of a window in a moment of the user quitting
import sys


#initialize the pygame window    
pygame.init()


#define default values for the number of rows, columns, number of mines, and size of the tiles
rows = 10
cols = 10
mines = 10
tile_size = 40


#define colors used in the program

#for the background
background_color = 'white'

#a dictionary for the numbers displayed in the tiles, where number == number of mines around the tile
number_colors = {1: 'black', 2: 'red', 3: 'green', 4: 'blue', 5: 'orange', 6: 'yellow', 7: 'cyan', 8: 'purple'}

#since in pygame we are able to specify colors as strings (words) or as tuples (numbers),
#we are able to use a custom combination of three integers below 255 (RGB) to generate color of our choice

#custom color, for the tiles when covered (somewhat like light gray)
rectangle_color = (200, 200, 200)

#custom color, for the tiles when uncovered (somewhat like dark gray)
clicked_rectangle_color = (100, 100, 100)

#define colors for if the user/pc solver flags a tile, or if we/pc discover/s a bomb
flag_color = 'red'
bomb_color = 'black'


#set-up values for diferent fonts used in the game
#the font is defined as a string in apostrophes = name of the font, and an integer = size of the font, divided by a comma

#font which is displayed when the user/pc ends the game (winning/losing and for pc - if cant solve)
game_over_font = pygame.font.SysFont('arial', 40)

#font for the text on specified buttons in the program
button_font = pygame.font.SysFont('arial', 30)

#font used for the numbers specifying the number of mines around them
number_font = pygame.font.SysFont('arial', 20)

#display the window of the game, the dimensions depend on the way the game is started up (they are passed as parameters)
window = pygame.display.set_mode((rows * tile_size, cols * tile_size))

#create a caption for the game window, whcih in this case is the name of the game
pygame.display.set_caption('Minesweeper')

#setup some values for the text displayed on the buttons used in the program
#the parameters passed are a string = name of the button (text displayed), an integer specifying the chosen antialiasing (1 for True (sharper image of the character)
#and 0 for False), followed by the color for the text   

#back to menu text is a text used on a 'back to menu' button which is used in some cases in the program (to return the user to the menu)
back_to_menu_text = button_font.render('Back to menu', 1, 'white')

#quit text is used on the 'quit' buttons when the user wants to quit the game window
quit_text = button_font.render('Quit', 1, 'white')


#this function takes in a row and column index and returns a list of tuples representing the indices of the neighbors of the tile at the given row and column
def get_neighbors(row, col, rows, cols):
    
    #when traversing => top-left, top, top-right, left, right, bottom-left, bottom, bottom-right
    neighbors = [(row - 1, col - 1), (row - 1, col), (row - 1, col + 1), (row, col - 1), (row, col + 1), (row + 1, col - 1), (row + 1, col), (row + 1, col + 1)]

    #filter out neighbors with out-of-bounds indices
    neighbors = [(r, c) for r, c in neighbors if 0 <= r < rows and 0 <= c < cols]

    #return the specified values
    return neighbors


#this function generates a two-dimensional list representing the game field with a certain number of mines placed randomly on the field 
#it uses the get_neighbors function to count the number of mines surrounding each tile and stores that count in the tile
def create_minefield(rows, cols, mines):
    
    #generate the minefield
    field = [[0 for _ in range(cols)] for _ in range(rows)]

    #a list to store the generated positions of the mines
    mine_positions = list()   

    #generate the mines in random positions, while the number of mines generated is specified (default value, or user custom input)
    while len(mine_positions) < mines:
        row = random.randrange(0, rows)
        col = random.randrange(0, cols)
        pos = row, col

        #check if the generated position for mine placement is already used (containing a mine), and continue on to next random choice of a tile
        if pos in mine_positions:
            continue

        #if after checking the new generated posiiton of the mine was not previously occupied (by a mine), we can append (add) the position of this mine to the list
        mine_positions.append(pos)

        #we store the information about the item stored in each tile accordingly: -1 if mine, 0 if nothing (empty), rest of the numbers (1-8) specify the number of mines around
        field[row][col] = -1

    #this loop is used to populate the minefield by the numbers (which specify their surrounding) as specified beforehand
    for mine in mine_positions:

        #the * operator is used to unpack the contents of the tuple mine and pass each element as separate positional arguments to the function get_neighbors
        neighbors = get_neighbors(*mine, rows, cols)  

        #we iterate through all the rows and columns of each neighbor
        for r, c in neighbors:
            
            #while in each iteration we check if the chosen tile is not a bomb - because we dont need to store a new number in that tile (already contains a value for bomb)
            if field[r][c] != -1:   
                field[r][c] += 1

    #at the end of the iteration returns a list of neighboring tiles' coordinates in the form of (row, column) tuples
    return field 


#this function loops through each tile in the game field and cover field, and draws a rectangle representing the tile on the window 
#if the tile has been clicked on, it draws the tile with a different color, if the tile contains a mine, it draws a bomb symbol on the tile, if the tile contains a number, it draws the number on the tile
#this function takes in some parameters: the game window, the game field and the cover field (a two-dimensional list representing the cells that have not yet been clicked on by the player) 
#and draws the game field on the window
def draw(window, field, cover_field, tile_size):  
    
    #fill the window with a white color initially
    window.fill(background_color)   

    #calculate the tile size and store these values (in this case they are equal because they are squares)
    #later used to correctly create the game, and correctly display the generated minefield
    tile_width = tile_size
    tile_height = tile_size

    #this loop iterates through the minefield, while checking the value in the tile (-1, 0, 1-8), then specifying whats drawn (displayed) if the user clicks on each type of tile accordingly
    #the enumerate function is used to keep track of both the index and the value of elements within an iterable, it returns an iterator that yields pairs of the form (index, value) for each element in the iterable
    for i, row in enumerate(field): 
        y = tile_height * i
        for j, value in enumerate(row): 
            x = tile_width * j    

            #store the possible values in the tiles into variables

            #if covered
            is_covered = cover_field[i][j] == 0
            
            #if flagged 
            is_flag = cover_field[i][j] == -2

            #if mine   
            is_bomb = value == -1      

            #according to the current situation or value in the tile, we display the tile in a specific way
            if is_flag:

                #if the player right-clicks on a tile, the tile will be colored red 
                pygame.draw.rect(window, flag_color, (x, y, tile_width, tile_height))
                pygame.draw.rect(window, 'black', (x, y, tile_width, tile_height), 2)
                continue

            #here we color the tile according to the state = covered, or uncovered (else)
            if is_covered:  
                pygame.draw.rect(window, rectangle_color, (x, y, tile_width, tile_height))

                #number 2 specifies the thickness of the drawn object
                pygame.draw.rect(window, 'black', (x, y, tile_width, tile_height), 2)
                continue    
            else:
                pygame.draw.rect(window, clicked_rectangle_color, (x, y, tile_width, tile_height))

                #number 2 specifies the thickness of the drawn object
                pygame.draw.rect(window, 'black', (x, y, tile_width, tile_height), 2)  

            #if the players clicks on the bomb, we display a black circle    
            if is_bomb:
                
                #we divide the values width and height by 2, to display the bomb in the middle of the tile, and the last parameters specifies the radius of the bomb
                pygame.draw.circle(window, bomb_color, (x + tile_width/2, y + tile_height/2), min(tile_width, tile_height)/2 - 4) 
                
            #if the value in the tile is a number (in range 1-8), meaning not empty or mine, we specify the font for these numbers, and color (according to the list specified beforehand)
            if value > 0:

                #1 is antialiasing, causes the text to be drawn with smoother, less pixelated edges, but may increase the time required to render the text
                text = number_font.render(str(value), 1, number_colors[value])
                
                #center the number to the middle of the tile
                window.blit(text, (x + (tile_width/2 - text.get_width()/2), y + (tile_height/2 - text.get_height()/2)))
    
    #we update the window, because we need to keep track of the situation after every change in the game (user creates a flag, then removes for example)
    pygame.display.update()


#the function takes four input parameters: mouse_pos, rows, cols, and tile_size: mouse_pos is a tuple containing the x and y coordinates of the mouse position, 
#rows and cols are the dimensions of the grid (number of rows and columns), and tile_size is the size of each tile in the grid
#it then defines which tile we clicked on
def get_grid_pos(mouse_pos, rows, cols, tile_size):

    #store the x and y coordinates into variables mx and my
    mx, my = mouse_pos 

    #determine the index of the tile the mouse is currently positioned on 
    row = int(my // tile_size)
    col = int(mx // tile_size)

    #here we check if the position of the click is a valid position of a tile (for example if user clicks outside the game window)
    row = min(max(row, 0), rows - 1)
    col = min(max(col, 0), cols - 1)

    #return the valid row and col indices as a tuple (the tile the mouse is on)
    return row, col


#this function uses breadth-first-search to uncover tiles starting from the given position and expanding outwards as long as adjacent tiles have a value of 0 
#(meaning they have no mines as neighbors)
def uncover_from_position(row, col, cover_field, field):
    
    #initialize a queue with the starting position
    q = [(row, col)]

    #create a list to keep track of the visited tiles   
    visited = []
    
    #keep working until there are elements left in the queue
    while q:
        
        #dequeue the first element and store it into the 'current' list
        current = q.pop(0)

        #calculate the neighbors of the current tile, to know which tiles to focus on next
        #calling the get_neighbors function, unpacking the tuple values of the list 'current', next two parameters are rows, cols
        neighbors = get_neighbors(*current, len(field), len(field[0])) 

        #iterate through the neighbors of the current tile, do nothing if the tile was already recognized (dealt with)
        for r, c in neighbors:

            #skip the tile if it was already visited
            if (r, c) in visited:
                continue
            
            #store the value of the tile in the field variable
            value = field[r][c]

            #add the current tile in the queue, if it still is an empty tile, wasnt visited yet, and not a flag
            if value == 0 and cover_field[r][c] != -2:    
                q.append((r, c))

            #if the neighboring tile is still not flagged, we set its state to be 1 == visited
            if cover_field[r][c] != -2: 
                cover_field[r][c] = 1

            #add the neighbor to the list of visited tiles if it passed all the requirements
            visited.append((r, c))


#this function is used to check if the player won the game, by iterating through the whole minefield and checking if there are any covered tiles left
def won(cover_field):
    for row in cover_field:
        for tile in row:

            #0 was specified to signify the tile is covered, beforehand
            if tile == 0:  
                return False
    #if we find a covered field, the state of the game is still not won, otherwise we won, and the function returns the True boolean
    return True


#this function is used to generate a simple menu after the player finishes the game (winning, losing, and not being able to finish the game (in case of the pc solver))
def draw_game_over(window, window_width, window_height, back_to_menu_button, quit_button, game_result_text):

    #fill the background color of the menu to be white
    window.fill('white')

    #render the font to display the result of the game
    text = game_over_font.render(game_result_text, 1, 'black')
    
    #display the text on the window
    window.blit(text, (window_width / 2 - text.get_width() / 2, window_height / 2 - text.get_height() / 2 - 100))

    #draw buttons for 'Back to menu' and 'Quit'
    pygame.draw.rect(window, 'blue', back_to_menu_button)
    pygame.draw.rect(window, 'red', quit_button) 

    #display the drawn buttons on the window
    window.blit(back_to_menu_text, (back_to_menu_button.x + (back_to_menu_button.width / 2) - back_to_menu_text.get_width() / 2,
                                     back_to_menu_button.y + (back_to_menu_button.height / 2) - back_to_menu_text.get_height() / 2))
    window.blit(quit_text, (quit_button.x + (quit_button.width / 2) - quit_text.get_width() / 2,
                             quit_button.y + (quit_button.height / 2) - quit_text.get_height() / 2))

    #update the display, which needs to be added after any modifications to the pygame window
    pygame.display.update()


#this function is used when the user choses to define the dimensions and number of mines for the game in their custom choice
#it takes in 3 inputs: (integer) value for number of mines, rows, and columns, and later generate the minefield accordingly
def grid_customize(rows, cols, mines):

    #specify the color used for the input boxes for the user-input dimensions and number of mines, in this case white
    input_box_color = (255, 255, 255) #we could also use 'white'

    #define the parameters for the input boxes (color, dimension, position, text drawn) using a dictionary
    input_boxes = [
        {
            'rect': pygame.Rect(100, 50, 150, 40),
            'color': input_box_color,
            'text': '',
        },
        {
            'rect': pygame.Rect(100, 100, 150, 40),
            'color': input_box_color,
            'text': '',
        },
        {
            'rect': pygame.Rect(100, 150, 150, 40),
            'color': input_box_color,
            'text': '',
        }
    ]

    #at the end of the customization, user confirms the selection by clicking a 'Confirm' button

    #we draw this button on the window, on specified coordinations, assigning the color to be also white
    button_rect = pygame.Rect(100, 200, 150, 40)
    button_color = input_box_color

    #since the number of rows and columns is custom now, we calculate the new dimensions of the window accordingly
    window_width = cols * tile_size
    window_height = rows * tile_size

    #initialize the pygame window to display the game
    pygame.init()

    #create the window for the game, with the updated dimensions
    window = pygame.display.set_mode((window_width, window_height))
    
    #defining a font for the text on the 'Confirm' button
    font = pygame.font.SysFont('arial', 35)

    #fill the window with black background color 
    window.fill('black')

    #set a variable to check which box is being used currently (to handle the input)
    active_box = None

    #create a string variable to store the user-input-integer in the input boxes
    input_text = '' 

    #boolean to handle the loop, determine if the user exits the window, or closes the program
    running = True

    #loop to handle the input, draw the boxes and the button
    while running:
        
        #default event handling for pygame window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            #if the user clicks on the window, the program checks for the position of the mouse-click, to know which input box is being used currently
            #when the user clicks on an input box, its highlighted
            if event.type == pygame.MOUSEBUTTONDOWN:
                for box in input_boxes:
                    if box['rect'].collidepoint(event.pos):
                        active_box = box
                        active_box['color'] = input_box_color
                    else:
                        box['color'] = (200, 200, 200)
                
                #if the user clicks on the 'Confirm' button to finish the customization, the loop handles the integers in the input boxes, stores the dimension of the 
                #window-to-be-created, and runs the main function to run the game, with the updated values
                if button_rect.collidepoint(pygame.mouse.get_pos()) and event.type == pygame.MOUSEBUTTONDOWN:
                    rows = int(input_boxes[0]['text'])
                    cols = int(input_boxes[1]['text'])
                    mines = int(input_boxes[2]['text'])
                    window_width = cols * tile_size
                    window_height = rows * tile_size
                    window = pygame.display.set_mode((window_width, window_height))
                    main(rows, cols, mines)

            #this loop handles the input in specified box, where the program checks for if the user clicks a key on keyboard, if on an input box,
            #and handles if the user tries to input an incorrect value (any character other than integer), and also handles the use of backspace
            elif event.type == pygame.KEYDOWN:
                if active_box:
                    if event.key == pygame.K_BACKSPACE: 
                        active_box['text'] = active_box['text'][:-1]
                    elif not event.unicode.isnumeric():
                        continue
                    
                    #if the input is correct (an integer), we store the value    
                    elif event.unicode.isnumeric(): 
                        active_box['text'] += event.unicode
        
        for row in range(rows):
            for col in range(cols):
                tile_x = col * tile_size
                tile_y = row * tile_size
                pygame.draw.rect(window, (255, 255, 255), (tile_x, tile_y, tile_size, tile_size))

        #color the window around the input boxes and confirm button, to be black
        window.fill((0, 0, 0))

        #this loops draws the input boxes on specified coordinates in the window
        for box in input_boxes:

            #update input_text with the text from the current box
            input_text = box['text']

            #render the input values from the user (integers)
            input_surface = font.render(input_text, True, (0, 0, 0))

            #we draw the input boxes, handle the correct display of the typed-in integers from the user
            pygame.draw.rect(window, box['color'], box['rect'])
            window.blit(input_surface, (box['rect'].x + 5, box['rect'].y + 5))
            pygame.draw.rect(window, box['color'], box['rect'])
            pygame.draw.rect(window, box['color'], box['rect'])
            window.blit(input_surface, (box['rect'].x+2, box['rect'].y+2))

        #draw the button on the window and display it
        pygame.draw.rect(window, button_color, button_rect)
        window.blit(font.render('Confirm', 1, (0, 0, 0)), (button_rect.x+20, button_rect.y))
        
        #update the display, which needs to be added after any modifications to the pygame window
        pygame.display.update()

    #close the game window if the user clicks the exit sign
    pygame.quit()

    #function returns the custom number of rows, columns and mines, to be worked with 
    return rows, cols, mines


#this function is an algorithm which tries to play and win the game, simulating an artificial player
def pc_solver(rows, cols, mines):

    #calculate the window dimensions
    window_width = cols * tile_size
    window_height = rows * tile_size

    #initialize the game window
    pygame.init()
    
    #create the window of specified dimensions
    window = pygame.display.set_mode((window_width, window_height))
    
    #create the minefield for the pc solver
    field = create_minefield(rows, cols, mines)

    #and create the cover for the whole minefield
    cover_field = [[0 for _ in range(cols)] for _ in range(rows)]

    #define buttons to be displayed in the simple menu after game is finished
    back_to_menu_button = pygame.Rect(window_width / 2 - 100, window_height / 2, 200, 50)
    quit_button = pygame.Rect(window_width / 2 - 100, window_height / 2 + 60, 200, 50)

    #draw the minefield on the window
    draw(window, field, cover_field, tile_size)

    #update the window to correctly handle the display of the minefield
    pygame.display.update()

    #added a delay, when the user choses the 'Solve by pc' option, for the program to wait 2 seconds, before starting to reveal the solution to the game
    pygame.time.delay(2000)
    
    #this loop cheats a little bit, because it looks into the values of the field (mines, number, empty) to find a safe start position
    #if the randomly chosen initial position is a mine, the loop choses a new random tile
    safe_start = False
    while not safe_start:
        start_row, start_col = random.randint(0, rows - 1), random.randint(0, cols - 1)
        if field[start_row][start_col] == 0:
            uncover_from_position(start_row, start_col, cover_field, field)

            #after finding a safe initial starting position for the solver, the loop ends
            safe_start = True

    #booleans to store the state of the game 
    game_solved = False
    game_lost = False

    #continue the loop until the algorithm didnt finish the game, or didnt click on a bomb
    while not game_solved and not game_lost:

        #create a variable to check if the game was changed (uncovered new tiles, flagged some..)
        #helps identify if the game progressed, so some iterations dont stay in a loop, crashing the program
        changed = False

        #iterate through all tiles 
        for row in range(rows):
            for col in range(cols):

                #analyze the neighbors of the tile, if its not a bomb, or empty
                if field[row][col] > 0:
                    
                    #get the values of the neighbors using the previously defined function
                    neighbors = get_neighbors(row, col, rows, cols)
                    
                    #identify state of neighbors
                    covered_neighbors = [n for n in neighbors if cover_field[n[0]][n[1]] == 0]
                    flagged_neighbors = [n for n in neighbors if cover_field[n[0]][n[1]] == -2]

                    #this loop flags all neighbors of a chosen tile initially, if tile number == number of covered neighbors + number of flagged neighbors 
                    #and number of flagged neighbors < number of mines
                    if len(covered_neighbors) + len(flagged_neighbors) == field[row][col] and len(flagged_neighbors) < mines:
                        
                        for n in covered_neighbors:
                            
                            #here mark all the neighbors with flags
                            cover_field[n[0]][n[1]] = -2

                            #remember the game state
                            changed = True
                            
                            #draw the updated field
                            draw(window, field, cover_field, tile_size)

                            #update the window after changes
                            pygame.display.flip()
                            
                            #added a 1 second delay between each step of the algorithm, to simulate the behavior of a human player, and to see the progress
                            pygame.time.delay(1000)  

                    #if the number of flagged neighbors is equal to the tiles' number, open all covered neighbors
                    #here we uncover the unflagged neighbors, where we introduce the risk that one of them could be a mine
                    elif len(flagged_neighbors) == field[row][col]:
                        
                        #iterate through the unopened neighbors
                        for n in covered_neighbors:

                            #set the state of all unopened neighboring tiles to the state 'uncovered'
                            cover_field[n[0]][n[1]] = 1

                            #if a neighbor is an empty tile, call the uncover from position function to handle the situation
                            if field[n[0]][n[1]] == 0:
                                uncover_from_position(n[0], n[1], cover_field, field)
                            
                            #if even after precautions, the neighboring tile opened is a bomb, draw a bomb, and after 1,5 sec delay, display the text and menu 
                            if field[n[0]][n[1]] == -1:
                                cover_field[n[0]][n[1]] = 1
                                draw(window, field, cover_field, tile_size)
                                pygame.display.flip()
                                pygame.time.delay(1500)

                                #set the boolean to True to exit the loop
                                game_lost = True

                            #change the state of variable, to prevent the cycle from endlessly iterating 
                            changed = True

                            #draw the updated version
                            draw(window, field, cover_field, tile_size)

                            #update the minefield
                            pygame.display.flip()

                            #added a 1 second delay before the program announces the pc solver managed to solve the game
                            pygame.time.delay(1000)
                            break
                
                #break out of the loop if a change has been made
                if changed: 
                    break
            
            #break out of the loop if a change has been made
            if changed:
                break
        
        #terminate the loop if no changes have been made during the whole iteration, to not end up in infinite loop
        if not changed: 
            break

        #check if the game is solved by counting the number of covered tiles
        game_solved = True
        for row in range(rows):
            for col in range(cols):
                if cover_field[row][col] == 0:
                    game_solved = False

    #according to the game outcome, the game displays a window with simple menu, and the text informing of the game outcome
    if game_solved:
        draw_game_over(window, window_width, window_height, back_to_menu_button, quit_button, 'Solved the game :D')
    elif game_lost:
        draw_game_over(window, window_width, window_height, back_to_menu_button, quit_button, 'I lost :c')

    #if it reaches a point where it cant determine where the mine would be, for example a 50/50 state, it just gives up
    else:  
        draw_game_over(window, window_width, window_height, back_to_menu_button, quit_button, 'Cant solve :/')
    
    #update the window accordingly
    pygame.display.flip()
    
    #event handling
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            #this loop checks for user mouse-clicks, if the user clicks on the 'back to menu' button - returns the user to menu, if user clicks on quit - exits the game window
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if back_to_menu_button.collidepoint(mouse_pos):
                    menu()
                elif quit_button.collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()


#this function handles the creation of the menu for the game, which is displayed after starting up the game, the menu offers 4 options for the user:
# - customize grid - if user wants to play the game with custom dimensions and number of mines
# - start game - upon clicking, the user will play a standard minesweeper game in a 10x10 grid with 10 mines
# - quit - to quit the game
# - solve by pc - calls an algorithm, where the (pc) will try to solve the game (of default dimensions and number of mines)
def menu():
    
    #initialize the window
    pygame.init()

    #calculate the dimensions of the window
    window_width = cols * tile_size
    window_height = rows * tile_size

    #create the window 
    window = pygame.display.set_mode((window_width, window_height))
    
    #section for colors used in the menu

    #color for the text in the buttons
    text_color = (255, 255, 255) 

    #color for the buttons, when idle (not hovered upon)
    color_not_hovered_over = (120, 120, 120) 
    
    #color for the buttons, thats changed-to, when user hovers the mouse over 
    color_hovered_over = (200, 200, 200) 
    
    #color the window with black 
    window.fill((0,0,0))
    
    #this loop draws the buttons in the menu, and handles the events when the user clicks on one of the buttons, or exits the window
    while True:

        #store the position of the mouse click in a variable, which has an x and y coordinations
        mouse_click_position = pygame.mouse.get_pos()

        #loop to handle events
        for ev in pygame.event.get(): 
            
            #instance where the user quits the window by using the 'x' in top right corner
            if ev.type == pygame.QUIT: 
                pygame.quit()
                sys.exit() 

            #if the user clicks a button on the mouse, the program checks if the button pressed was a left-click, then checks for the coordinates of the click
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed()[0]:

                    #customize grid button clicked
                    if 75 <= mouse_click_position[0] <= 325 and 100 - 40 <= mouse_click_position[1] <= 150 - 40:  
                        grid_customize(rows, cols, mines)

                    #start game button clicked
                    elif 75 <= mouse_click_position[0] <= 325 and 175 - 40 <= mouse_click_position[1] <= 225 - 40:  
                        main(rows, cols, mines)

                    #quit button clicked
                    elif 75 <= mouse_click_position[0] <= 325 and 210 <= mouse_click_position[1] <= 260:  
                        pygame.quit()
                        sys.exit()

                    #solve by pc button clicked
                    elif 75 <= mouse_click_position[0] <= 325 and 325 - 40 <= mouse_click_position[1] <= 375 - 40:  
                        pc_solver(rows, cols, mines)
    
        #this section draws the buttons in the menu, while also changing their color if the mouse is/is not hovered upon

        #for the quit button
        if window_width/2 - 125 <= mouse_click_position[0] <= window_width/2 + 125 and window_height/2 + 10 <= mouse_click_position[1] <= window_height/2 + 60:
            pygame.draw.rect(window, color_hovered_over, (75, 210, 250, 50))
        else:
            pygame.draw.rect(window, color_not_hovered_over, (75, 210, 250, 50))

        #render the text on the button
        quit_text = button_font.render('Quit', True, text_color)

        #display the text
        window.blit(quit_text, (window_width/2 - 25, window_height/2 + 15))


        #for the start button
        if window_width/2 - 125 <= mouse_click_position[0] <= window_width/2 + 125 and window_height/2 - 25 - 40 <= mouse_click_position[1] <= window_height/2 + 25 - 40:
            pygame.draw.rect(window, color_hovered_over, [75, 175 - 40, 250, 50])
        else:
            pygame.draw.rect(window, color_not_hovered_over, [75, 175 - 40, 250, 50])

        #render the text on the button
        start_game_text = button_font.render('Start Game', True, text_color)

        #display the text
        window.blit(start_game_text, (window_width/2 - 65, window_height/2 - 60))


        #for the customize grid button
        if window_width/2 - 125 <= mouse_click_position[0] <= window_width/2 + 125 and window_height/2 - 100 - 40 <= mouse_click_position[1] <= window_height/2 - 50 - 40:
            pygame.draw.rect(window, color_hovered_over, [75, 100 - 40, 250, 50])
        else:
            pygame.draw.rect(window, color_not_hovered_over, [75, 100 - 40, 250, 50])

        #render the text on the button
        customize_grid_text = button_font.render('Customize Grid', True, text_color)

        #display the text
        window.blit(customize_grid_text, (window_width/2 - 87.5, window_height/2 - 95 - 40))

        # if the mouse is hovered on the solve by pc button, it changes to a lighter shade
        if window_width/2 - 125 <= mouse_click_position[0] <= window_width/2 + 125 and window_height/2 + 125 - 40 <= mouse_click_position[1] <= window_height/2 + 175 - 40:
            pygame.draw.rect(window, color_hovered_over, [75, 325 - 40, 250, 50])
        else:
            pygame.draw.rect(window, color_not_hovered_over, [75, 325 - 40, 250, 50])

        #render the text on the button
        solve_by_pc_text = button_font.render('Solve by PC', True, text_color)

        #display the text
        window.blit(solve_by_pc_text, (window_width/2 - 70, window_height/2 + 90))

        #update the window continuously to correctly display the buttons
        pygame.display.update()   


#this function is the main driver of the program, runs the game
def main(rows, cols, mines): 

    #calculate the window dimensions
    window_width = cols * tile_size
    window_height = rows * tile_size

    #display the window
    window = pygame.display.set_mode((window_width, window_height))

    #initialize the window
    pygame.init()

    #create the minefield
    field = create_minefield(rows, cols, mines)

    #cover the minefield to hide the numbers and mines
    cover_field = [[0 for _ in range(cols)] for _ in range(rows)]

    #boolean variables to store the states of the game
    run = True
    lost = False

    #section to calculate the time elapsed from the start of the game
    timer_event = pygame.USEREVENT + 1
    pygame.time.set_timer(timer_event, 1000) 
    start_time = time.time()

    #initialize the buttons for the simple menu after the game is finished
    back_to_menu_button = pygame.Rect(window_width / 2 - 100, window_height / 2, 200, 50)
    quit_button = pygame.Rect(window_width / 2 - 100, window_height / 2 + 60, 200, 50)

    #main loop, which runs the game
    while run:
        
        #basic event handler for when the user quits the game while playing
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()
            
            #if the user clicks a mouse-button, the loop checks for the position of the mouseclick
            if event.type == pygame.MOUSEBUTTONDOWN:
                
                #remember the position of the mouse click
                row, col = get_grid_pos(pygame.mouse.get_pos(), rows, cols, tile_size)
                
                #this loop continuously checks if the user is clicking inside the minefield
                #if the user clicks outside the minefield, the program continues (does nothing)
                if row >= rows or col >= cols:  
                    continue
               
                #store the coordinations of the mouse click
                mouse_pressed = pygame.mouse.get_pressed()

                #if user left-clicks (uncovers the tile), and the tile is not a flag or a mine, program sets the tile as uncovered (and uncovers it)
                if mouse_pressed[0] and cover_field[row][col] != -2 and cover_field[row][col] != -1:    
                    cover_field[row][col] = 1
                
                #if the uncovered field is 0, we call the uncover from position function to handle uncovering all empty tiles
                if mouse_pressed[0] and field[row][col] == 0: 
                    uncover_from_position(row, col, cover_field, field)

                #if user clicks on a bomb, the program displays the bomb, and ends the game after 1,5 second delay
                elif mouse_pressed[0] and field[row][col] == -1:   
                    cover_field[row][col] = 1
                    draw(window, field, cover_field, tile_size)
                    pygame.display.flip()
                    pygame.time.delay(1500) 
                    lost = True  
                
                #if the user right-clicks, the game draws a flag (if the tile which was clicked-on already had flag, the tile is un-flagged)
                elif mouse_pressed[2]:
                    if cover_field[row][col] == -2:
                        cover_field[row][col] = 0
                    else:
                        cover_field[row][col] = -2

            #section to display the timer (along with the caption of the game)               
            if event.type == timer_event:
                current_time = time.time()
                timer = current_time - start_time

                #the timer is displayed 30 empty strings to the right of the caption of the window
                #since there seems to be no proper way to center a string in the pygame caption section, i set the position of the timer manually by offsetting 
                pygame.display.set_caption('Minesweeper' + (' ' * 30) + str(int(timer)))

                #update the window for the timer to continue showing correct time
                pygame.display.flip()
        
        #this section handles the aftermath of the changed game state (won, lost)
        #when the booleans are set to True, the simple menu is displayed accordingly

        #this loop is used if the user wins the game, displaying the simple menu with the 'You won' text
        if won(cover_field): 
            
            #display the simple menu
            draw_game_over(window, window_width, window_height, back_to_menu_button, quit_button, 'You won! :D')

        #this loop is used if the user loses the game, displaying the simple menu with the 'You lost' text
        if lost:

            #display the simple menu
            draw_game_over(window, window_width, window_height, back_to_menu_button, quit_button, 'You lost :c')

        #after the menu is displayed (after the game was finished) we add an event-handling loop - for if the user exits the window, and for when the user clicks on buttons
        if won(cover_field) or lost:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if back_to_menu_button.collidepoint(mouse_pos):
                        menu()
                    elif quit_button.collidepoint(mouse_pos):
                        pygame.quit()
                        sys.exit()
        
        #if the game was not won or lost yet, the game is updated, and the window is refreshed
        else:
            draw(window, field, cover_field, tile_size)
            pygame.display.flip()

    #just to be sure, avoid unforeseen problems when quitting the game at any instance
    pygame.quit()
    sys.exit()


#entry-point guard to run the game   
if __name__ == '__main__':
    menu()