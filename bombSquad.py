import sys
import time
import array
from enum import IntEnum
from tkinter import *
import tkinter.messagebox
sys.path.append("./lib")
from fieldDisplay import FieldDisplay
sys.path.append("./lib/DecodeDemcon3")
from mineField import *


class FieldDifficulty(IntEnum):
    DEFAULT = 0
    BEGINNER = 1
    INTERMEDIATE = 2
    EXPERT = 3

class CellStatus(IntEnum):
    TRAP = -5
    FOUND = -4
    EXPLODE = -3
    FLAG = -2
    UNKNOWN = -1
    SAFE = 0

def touch_cell(mine_field, mine_field_data, actual_row, actual_column, field_width) -> None:
    '''Touch a specific cell and update this in the minefield data
       Stop the sweep if a bomb is detected

       TODO:
       Keyword arguments:
       width -- the width of the mine field
       height -- the height of the mine field
       number_of_mines -- hoe many mines will be generated'''

    global sweep_active
    if (actual_column >= 0) and (actual_column < field_width) and (sweep_active == True):
        try:
            mine_field_data[actual_row][actual_column] = mine_field.sweep_cell(actual_column, actual_row)
            if (mine_field_data[actual_row][actual_column] == CellStatus.EXPLODE):
                sweep_active = False
        except ExplosionException:
            mine_field_data[actual_row][actual_column] = CellStatus.EXPLODE
            sweep_active = False
        except:
            mine_field_data[actual_row][actual_column] = CellStatus.EXPLODE
            sweep_active = False

def check_adjacent_cells(mine_field, mine_field_data, analyse_position, touch_cells, actual_row, actual_column, field_height, field_width) -> None:
    '''Go through all the surrounded cells and only touch them if required.
       Always store the surroundings in an array anyway

       TODO:
       Keyword arguments:
       width -- the width of the mine field
       height -- the height of the mine field
       number_of_mines -- hoe many mines will be generated'''

    dummy_array = [ [ 0 ] * 3 for _ in range(3) ]
    actual_row_offset = actual_row
    actual_column_offset = actual_column

    # N
    if (actual_row > 0):
        actual_row_offset = actual_row - 1
        analyse_position[0][1] = mine_field_data[actual_row_offset][actual_column]
        if (touch_cells):
            touch_cell(mine_field, mine_field_data, actual_row_offset, actual_column, field_width)
    # S
    if (actual_row < (field_height - 1)):
        actual_row_offset = actual_row + 1
        analyse_position[2][1] = mine_field_data[actual_row_offset][actual_column]
        if (touch_cells):
            touch_cell(mine_field, mine_field_data, actual_row_offset, actual_column, field_width)
    # W
    if (actual_column > 0):
        actual_column_offset = actual_column - 1
        analyse_position[1][0] = mine_field_data[actual_row][actual_column_offset]
        if (touch_cells):
            touch_cell(mine_field, mine_field_data, actual_row, actual_column_offset, field_width)
    # E
    if (actual_column < (field_width - 1)):
        actual_column_offset = actual_column + 1
        analyse_position[1][2] = mine_field_data[actual_row][actual_column_offset]
        if (touch_cells):
            touch_cell(mine_field, mine_field_data, actual_row, actual_column_offset, field_width)
    # NW
    if (actual_row > 0) and (actual_column > 0):
        actual_row_offset = actual_row - 1
        actual_column_offset = actual_column - 1
        analyse_position[0][0] = mine_field_data[actual_row_offset][actual_column_offset]
        if (touch_cells):
            touch_cell(mine_field, mine_field_data, actual_row_offset, actual_column_offset, field_width)
    # NE
    if (actual_row > 0) and (actual_column < (field_width - 1)):
        actual_row_offset = actual_row - 1
        actual_column_offset = actual_column + 1
        analyse_position[0][2] = mine_field_data[actual_row_offset][actual_column_offset]
        if (touch_cells):
            touch_cell(mine_field, mine_field_data, actual_row_offset, actual_column_offset, field_width)
    # SE
    if (actual_row < (field_height - 1)) and (actual_column < (field_width - 1)):
        actual_row_offset = actual_row + 1
        actual_column_offset = actual_column + 1
        analyse_position[2][2] = mine_field_data[actual_row_offset][actual_column_offset]
        if (touch_cells):
            touch_cell(mine_field, mine_field_data, actual_row_offset, actual_column_offset, field_width)
    # SW
    if (actual_row < (field_height - 1)) and (actual_column > 0):
        actual_row_offset = actual_row + 1
        actual_column_offset = actual_column - 1
        analyse_position[2][0] = mine_field_data[actual_row_offset][actual_column_offset]
        if (touch_cells):
            touch_cell(mine_field, mine_field_data, actual_row_offset, actual_column_offset, field_width)
    #Center
    analyse_position[1][1] = mine_field_data[actual_row][actual_column]
    if (touch_cells):
        touch_cell(mine_field, mine_field_data, actual_row, actual_column, field_width)

def main():
    '''Main function of the bomb squad minefield sweeper'''

    global field_difficulty
    global sweep_active

    field_difficulty = FieldDifficulty.DEFAULT
    field_width = 0;
    field_height = 0;
    field_number_of_mines = 0
    screen_active = True

    #Create a window to ask a question about difficulty
    question_start_window = tkinter.Tk()

    def button_beginner_pressed():
        global field_difficulty
        field_difficulty = FieldDifficulty.BEGINNER
        question_start_window.destroy()
          
    def button_intermediate_pressed():
        global field_difficulty
        field_difficulty = FieldDifficulty.INTERMEDIATE
        question_start_window.destroy()
      
    def button_expert_pressed():
        global field_difficulty
        field_difficulty = FieldDifficulty.EXPERT
        question_start_window.destroy()

    question_start_window.title("Choose difficulty")
    question_start_window.geometry('100x130')
    
    button_beginner = Button(question_start_window, text="Beginner", command=button_beginner_pressed, pady=10)
    button_intermediate = Button(question_start_window, text="Intermediate", command=button_intermediate_pressed, pady=10)
    button_expert = Button(question_start_window, text="Expert", command=button_expert_pressed, pady=10)

    button_beginner.pack(side=TOP)
    button_intermediate.pack(side=TOP)
    button_expert.pack(side=TOP)

    question_start_window.mainloop()

    #Setup the minefield with the selected difficulty
    if (field_difficulty == FieldDifficulty.DEFAULT):
        return

    if (field_difficulty == FieldDifficulty.BEGINNER):
        field_width = BEGINNER_FIELD['width']
        field_height = BEGINNER_FIELD['height']
        field_number_of_mines = BEGINNER_FIELD['number_of_mines']

    if (field_difficulty == FieldDifficulty.INTERMEDIATE):
        field_width = INTERMEDIATE_FIELD['width']
        field_height = INTERMEDIATE_FIELD['height']
        field_number_of_mines = INTERMEDIATE_FIELD['number_of_mines']

    if (field_difficulty == FieldDifficulty.EXPERT):
        field_width = EXPERT_FIELD['width']
        field_height = EXPERT_FIELD['height']
        field_number_of_mines = EXPERT_FIELD['number_of_mines']

    #Create mine field data for sweeping
    mine_field_data = [ [ CellStatus.UNKNOWN ] * field_width for _ in range(field_height) ]
    #Array overlay for memorize data
    mine_field_data_overlay = [ [ CellStatus.UNKNOWN ] * field_width for _ in range(field_height) ]
    #Create mine field
    mine_field = MineField(width=field_width, height=field_height, number_of_mines=field_number_of_mines)
    #Create display
    mine_field_display = FieldDisplay(mine_field_data)

    #Variables for sweeping
    actual_column = 0
    actual_row = 0
    risk_sum = 0
    sweep_active = True
    wipe_done = False
    touch_cells = False
    display_count = 0
    #Create array where index is the height and shall store an actual width position
    sweep_position = [ 0 for _ in range(field_height) ]
    #Set start position
    sweep_position[0] = 0;

    #Main loop while sweeping
    while (screen_active == True):
        #Check cell position
        screen_active = mine_field_display.check_screen_active()
        #Update display field
        display_count = display_count + 1
        if (display_count >= field_height):
            mine_field_display.update_screen(mine_field_data)
            display_count = 0

        #Sweep
        if ((sweep_active == True) and (wipe_done == False)):
            #Check actual position
            actual_column = sweep_position[actual_row]

            #Sweep start position
            if (sweep_position[actual_row] == 0) and (actual_row == 0):
                touch_cell(mine_field, mine_field_data, actual_row, actual_column, field_width)

            # _ _ _
            #|_|_|_|
            #|_|X|_|
            #|_|_|_|
            #Store surroundings for analyses
            analyse_position = [ [ 0 ] * 3 for _ in range(3) ]

            #Check if column position is within range
            if (sweep_position[actual_row] >= 0) and (sweep_position[actual_row] < field_width):
                #Condition what to do when finding a clear position
                if ((mine_field_data[actual_row][actual_column] == CellStatus.SAFE) and (mine_field_data_overlay[actual_row][actual_column] != CellStatus.SAFE)):
                    touch_cells = True
                    mine_field_data_overlay[actual_row][actual_column] = CellStatus.SAFE

                #Go through all surrounding cells
                check_adjacent_cells(mine_field, mine_field_data, analyse_position, touch_cells, actual_row, actual_column, field_height, field_width)

                #Reset cell clearing
                touch_cells = False


            #Unknown cell analyze
            if (analyse_position[1][1] == CellStatus.UNKNOWN):
                #Clear all cells that have no ajacent numer
                for width_pos in range(3):
                    for height_pos in range(3):
                        if (analyse_position[height_pos][width_pos] < 0):
                            analyse_position[height_pos][width_pos] = 0

                #Top
                risk_sum = abs(analyse_position[0][0]) + abs(analyse_position[0][1]) + abs(analyse_position[0][2])
                if (risk_sum > 4):
                    mine_field_data[actual_row][actual_column] = CellStatus.FLAG
                #Left
                risk_sum = abs(analyse_position[0][0]) + abs(analyse_position[1][0]) + abs(analyse_position[2][0])
                if (risk_sum > 4):
                    mine_field_data[actual_row][actual_column] = CellStatus.FLAG
                #Bottom
                risk_sum = abs(analyse_position[2][0]) + abs(analyse_position[2][1]) + abs(analyse_position[2][2])
                if (risk_sum > 4):
                    mine_field_data[actual_row][actual_column] = CellStatus.FLAG
                #Right
                risk_sum = abs(analyse_position[0][2]) + abs(analyse_position[1][2]) + abs(analyse_position[2][2])
                if (risk_sum > 4):
                    mine_field_data[actual_row][actual_column] = CellStatus.FLAG
                #Spin around
                risk_sum = abs(analyse_position[0][0]) + abs(analyse_position[0][1]) + abs(analyse_position[0][2]) + abs(analyse_position[1][2]) + abs(analyse_position[2][2]) + abs(analyse_position[2][1]) + abs(analyse_position[2][0]) + abs(analyse_position[1][0])
                if (risk_sum > 3):
                    mine_field_data[actual_row][actual_column] = CellStatus.FLAG
                #Final option
                if (mine_field_data[actual_row][actual_column] != CellStatus.FLAG):
                    touch_cell(mine_field, mine_field_data, actual_row, actual_column, field_width)
                #Condition what to do when finding a clear position
                if (mine_field_data[actual_row][actual_column] == CellStatus.SAFE):
                    touch_cells = True
                if (mine_field_data[actual_row][actual_column] == CellStatus.EXPLODE):
                    mine_field_data[actual_row][actual_column] = CellStatus.TRAP

            #Update sweep position by checking actual and next column
            if ((mine_field_data[actual_row][actual_column] >= 0) or (mine_field_data[actual_row][actual_column] == CellStatus.FLAG)):
                sweep_position[actual_row] = sweep_position[actual_row] + 1
                if (sweep_position[actual_row] >= field_width):
                    sweep_position[actual_row] = 0
                

        #Check for next index
        actual_row = actual_row + 1
        if (actual_row >= field_height):
            actual_row = 0

        #Scan field for actions
        unknown_cell_found = False
        flag_count = 0
        for width_pos in range(field_width):
            for height_pos in range(field_height):
                if(mine_field_data[height_pos][width_pos] == CellStatus.FLAG):
                    flag_count = flag_count + 1
                if(mine_field_data[height_pos][width_pos] == CellStatus.UNKNOWN):
                    unknown_cell_found = True
                if((mine_field_data[height_pos][width_pos] == CellStatus.SAFE) and (mine_field_data_overlay[height_pos][width_pos] != CellStatus.SAFE)):
                    mine_field_data_overlay[height_pos][width_pos] = CellStatus.SAFE
                    check_adjacent_cells(mine_field, mine_field_data, analyse_position, True, height_pos, width_pos, field_height, field_width)
        if((unknown_cell_found == False) or (flag_count >= field_number_of_mines)):
            sweep_active = False

        #Show all mines in mine field after game is done
        if (sweep_active == False) and (wipe_done == False):
            wipe_done = True
            for width_pos in range(field_width):
                for height_pos in range(field_height):
                    stored_pos = mine_field_data[height_pos][width_pos]
                    sweep_active = True
                    touch_cell(mine_field, mine_field_data, height_pos, width_pos, field_width)
                    if (mine_field_data[height_pos][width_pos] == CellStatus.EXPLODE) and (stored_pos == CellStatus.FLAG):
                        mine_field_data[height_pos][width_pos] = CellStatus.FOUND
                    elif (mine_field_data[height_pos][width_pos] != CellStatus.EXPLODE) or (stored_pos == CellStatus.TRAP):
                        mine_field_data[height_pos][width_pos] = stored_pos

if __name__ == "__main__":
    main()
