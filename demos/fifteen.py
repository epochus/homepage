"""
Fifteen Puzzle
"""

class FifteenSolver:
    """
    Class representation for the Fifteen puzzle
    """

    def __init__(self, puzzle_height, puzzle_width, initial_grid=None):
        """
        Initialize puzzle with default height and width
        Returns a Puzzle object
        """
        self._height = puzzle_height
        self._width = puzzle_width
        self._grid = [[col + puzzle_width * row
                       for col in range(self._width)]
                      for row in range(self._height)]

        if initial_grid != None:
            for row in range(puzzle_height):
                for col in range(puzzle_width):
                    self._grid[row][col] = initial_grid[row][col]

    def __str__(self):
        """
        Generate string representaion for puzzle
        Returns a string
        """
        ans = ""
        for row in range(self._height):
            ans += str(self._grid[row])
            ans += "\n"
        return ans

    #####################################
    # GUI methods

    def get_height(self):
        """
        Getter for puzzle height
        Returns an integer
        """
        return self._height

    def get_width(self):
        """
        Getter for puzzle width
        Returns an integer
        """
        return self._width

    def get_number(self, row, col):
        """
        Getter for the number at tile position pos
        Returns an integer
        """
        return self._grid[row][col]

    def set_number(self, row, col, value):
        """
        Setter for the number at tile position pos
        """
        self._grid[row][col] = value

    def clone(self):
        """
        Make a copy of the puzzle to update during solving
        Returns a Puzzle object
        """
        new_puzzle = FifteenSolver(self._height, self._width, self._grid)
        return new_puzzle

    ########################################################
    # Core puzzle methods

    def current_position(self, solved_row, solved_col):
        """
        Locate the current position of the tile that will be at
        position (solved_row, solved_col) when the puzzle is solved
        Returns a tuple of two integers
        """
        solved_value = (solved_col + self._width * solved_row)

        for row in range(self._height):
            for col in range(self._width):
                if self._grid[row][col] == solved_value:
                    return (row, col)
        assert False, "Value " + str(solved_value) + " not found"

    def update_puzzle(self, move_string):
        """
        Updates the puzzle state based on the provided move string
        """
        zero_row, zero_col = self.current_position(0, 0)
        for direction in move_string:
            if direction == "l":
                assert zero_col > 0, "move off grid: " + direction
                self._grid[zero_row][zero_col] = self._grid[zero_row][zero_col - 1]
                self._grid[zero_row][zero_col - 1] = 0
                zero_col -= 1
            elif direction == "r":
                assert zero_col < self._width - 1, "move off grid: " + direction
                self._grid[zero_row][zero_col] = self._grid[zero_row][zero_col + 1]
                self._grid[zero_row][zero_col + 1] = 0
                zero_col += 1
            elif direction == "u":
                assert zero_row > 0, "move off grid: " + direction
                self._grid[zero_row][zero_col] = self._grid[zero_row - 1][zero_col]
                self._grid[zero_row - 1][zero_col] = 0
                zero_row -= 1
            elif direction == "d":
                assert zero_row < self._height - 1, "move off grid: " + direction
                self._grid[zero_row][zero_col] = self._grid[zero_row + 1][zero_col]
                self._grid[zero_row + 1][zero_col] = 0
                zero_row += 1
            else:
                assert False, "invalid direction: " + direction

    ##################################################################
    # Phase one methods

    def lower_row_invariant(self, target_row, target_col):
        """
        Check whether the puzzle satisfies the specified invariant
        at the given position in the bottom rows of the puzzle (target_row > 1)
        Tile zero is positioned at (i,j)
        All tiles in rows i+1 or below are positioned in solved location
        All tiles in rows i to the right of pos (i,j) are positioned correctly
        Returns a boolean
        """
        zero = (self.get_number(target_row, target_col) == 0)
        if zero == False:
            return False

        height = self.get_height()
        width = self.get_width()

        row = height-1
        col = width-1

        # Checks if puzzle satisfies invariant
        while row != target_row or col != target_col:
            solved_value = col + (self.get_width() * row)
            if self.get_number(row, col) != solved_value:
                return False, (row, col)
            col -= 1
            if col < 0:
                row -= 1
                col = self.get_width() - 1

        return zero

    def solve_interior_tile(self, target_row, target_col):
        """
        Place correct tile at target position
        Updates puzzle and returns a move string
        """
        move_str = ""
        cur_row, cur_col = self.current_position(target_row, target_col)

        # Target tile is left of zero tile
        if (cur_row == target_row):
            left_dist = target_col - cur_col
            move_str += left_dist * 'l'

            while left_dist-1 > 0:
                move_str += 'urrdl'
                left_dist -= 1
        # Target tile is directly above target position
        elif (cur_col == target_col):
            up_dist = target_row - cur_row
            move_str += up_dist * 'u'
            move_str = self.down_cycle(move_str, up_dist, 'left')
        else:
            # Target tile is to the right, two or more rows above, and
            # not above target position
            if (cur_col-1 >= target_col and cur_row+2 <= target_row):
                up_dist = target_row - cur_row
                move_str += up_dist * 'u'
                right_dist = cur_col - target_col
                move_str += right_dist * 'r'

                while right_dist-1 > 0:
                    move_str += 'dllur'
                    right_dist -= 1
                move_str += 'dlu'

                move_str = self.down_cycle(move_str, up_dist, 'left')

            # Target tile is to the right, one row above,
            # and not above target postion
            if (cur_col-1 >= target_col and cur_row+1 == target_row):
                up_dist = target_row - cur_row
                move_str += up_dist * 'u'
                right_dist = cur_col - target_col
                move_str += right_dist * 'r'

                while right_dist-1 > 0:
                    move_str += 'ulldr'
                    right_dist -= 1
                move_str += 'ullddruld'

            # Target tile is to the left, more than one row above
            # and one or more columns apart
            if (cur_col+1 <= target_col and cur_row+2 <= target_row):
                up_dist = target_row - cur_row
                move_str += up_dist * 'u'
                left_dist = target_col - cur_col
                move_str += left_dist * 'l'

                while left_dist-1 > 0:
                    move_str += 'drrul'
                    left_dist -= 1
                move_str += 'dru'

                move_str = self.down_cycle(move_str, up_dist, 'left')

            # Target tile is to the left, one row above, and
            # no less than 2 columns apart from zero tile
            if (cur_col+1 <= target_col and cur_row+1 == target_row):
                left_dist = target_col - cur_col
                move_str += left_dist * 'l'
                move_str += 'urdl'

                while left_dist-1 > 0:
                    move_str += 'urrdl'
                    left_dist -= 1
        
        #print move_str
        self.update_puzzle(move_str)
        return move_str

    def solve_col0_tile(self, target_row):
        """
        Solve tile in column zero on specified row (> 1)
        Updates puzzle and returns a move string
        """
        move_str = ""
        zero_row, zero_col = self.current_position(0, 0)
        cur_row, cur_col = self.current_position(zero_row, zero_col)
        width = self.get_width()

        move_str += 'ur'

        # Assume zero tile is on col 0, either on row 2 or row 3

        # tile is on immediate top right corner
        if (cur_row+1 == zero_row and cur_col-1 == zero_col):
            move_str += 'uldrdlurdluurddlur'
        # tile is on row 2, right of zero tile after moving 'ur'
        elif (cur_row+1 == zero_row and cur_col-2 >= zero_col):
            right_dist = cur_col - zero_col - 1
            move_str += right_dist * 'r'

            while right_dist-1 > 0:
                move_str += 'ulldr'
                right_dist -= 1

            move_str += 'ulld'
            move_str += 'ruldrdlurdluurddlur'
        # Target tile is on row 0 or row 1
        else:
            up_dist = zero_row - cur_row - 1
            move_str += up_dist * 'u'

            # Target tile is left after moving 'ur' and 'u' more
            if (cur_row+2 <= zero_row and cur_col == zero_col):

                if up_dist > 0:
                    move_str += 'ldru'

                move_str = self.down_cycle(move_str, up_dist, 'right')
                move_str += 'ruldrdlurdluurddlur'

            # Target tile is far right
            elif (cur_row+3 <= zero_row and cur_col-2 >= zero_col):

                right_dist = cur_col - zero_col - 1
                move_str += right_dist * 'r'

                while right_dist-1 > 0:
                    move_str += 'dllur'
                    right_dist -= 1
                move_str += 'dlu'

                move_str = self.down_cycle(move_str, up_dist, 'right')
                move_str += 'ruldrdlurdluurddlur'
            # Target tile is on row 0 or 1 and col 2 or 3
            elif (cur_row+2 == target_row and cur_col-2 >= zero_col):
                right_dist = cur_col - zero_col - 1
                move_str += right_dist * 'r'
                while right_dist-1 > 0:
                    move_str += 'dllur'
                    right_dist -= 1
                move_str += 'dluld'
                move_str += 'ruldrdlurdluurddlur'
            # Target tile is directly above after moving 'ur'
            elif (cur_col-1 == zero_col and cur_row+2 <= target_row):
                move_str = self.down_cycle(move_str, up_dist, 'right')
                move_str += 'ruldrdlurdluurddlur'

        move_str += (width-2) * 'r'
        #print move_str
        self.update_puzzle(move_str)
        return move_str

    def down_cycle(self, move_str, up_dist, direction):
        """
        Helper method that cycles tile downward depending on direction
        Assumes tile to move is directly below zero tile
        """
        if direction == 'left':
            while up_dist-1 > 0:
                move_str += 'lddru'
                up_dist -= 1
            move_str += 'ld'

        if direction == 'right':
            while up_dist-1 > 0:
                move_str += 'rddlu'
                up_dist -= 1
            move_str += 'ld'

        return move_str

    #############################################################
    # Phase two methods

    def row0_invariant(self, target_col):
        """
        Check whether the puzzle satisfies the row zero invariant
        at the given column (col > 1)
        Returns a boolean
        """
        height = self.get_height()
        width = self.get_width()
        zero = (self.get_number(0, target_col) == 0)
        if zero == False:
            return False

        # Checks first and second row
        row0 = self._grid[0]
        for col in range(target_col+1, width):
            solved_value = col
            if row0[col] != solved_value:
                return False
        row1 = self._grid[1]
        for col in range(target_col, width):
            solved_value = (col + width)
            if row1[col] != solved_value:
                return False

        row = height-1
        col = 0
        # Checks n-2 rows
        while row != 1:
            solved_value = col + (width * row)
            if self.get_number(row, col) != solved_value:
                return False
            col -= 1
            if col < 0:
                row -= 1
                col = self.get_width() - 1

        return zero

    def row1_invariant(self, target_col):
        """
        Check whether the puzzle satisfies the row one invariant
        at the given column (col > 1)
        Returns a boolean
        """
        height = self.get_height()
        width = self.get_width()
        zero = (self.get_number(1, target_col) == 0)
        if zero == False:
            return False

        # Checks first and second row
        row0 = self._grid[0]
        for col in range(target_col+1, width):
            solved_value = col
            if row0[col] != solved_value:
                return False
        row1 = self._grid[1]
        for col in range(target_col+1, width):
            solved_value = (col + width)
            if row1[col] != solved_value:
                return False

        row = height-1
        col = 0
        # Checks n-2 rows
        while row != 1:
            solved_value = col + (width * row)
            if self.get_number(row, col) != solved_value:
                return False
            col -= 1
            if col < 0:
                row -= 1
                col = self.get_width() - 1

        return zero

    def solve_row0_tile(self, target_col):
        """
        Solve the tile in row zero at the specified column
        Updates puzzle and returns a move string
        """
        # replace with your code
        move_str = ""
        cur_row, cur_col = self.current_position(0, target_col)

        # Target tile is at immediate left of zero tile
        if (cur_row == 0 and cur_col+1 == target_col):
            move_str += 'dluldrru'
            move_str += 'ldl'
        # Target tile is at bottom left corner of zero tile
        elif (cur_row-1 == 0 and cur_col+1 == target_col):
            move_str += 'lld'
        # Target tile one row below and two columns away
        elif (cur_row-1 == 0 and cur_col+2 == target_col):
            move_str += 'ldl'
        # Target tile is farther left of zero tile
        else:
            if (cur_row == 1):
                move_str += 'ld'
                left_dist = target_col - cur_col - 1
                move_str += left_dist * 'l'

                while left_dist-1 > 0:
                    move_str += 'urrdl'
                    left_dist -= 1
            else:
                left_dist = target_col - cur_col
                move_str += left_dist * 'l'
                while left_dist-2 > 0:
                    move_str += 'drrul'
                    left_dist -= 1
                move_str += 'druld'

        move_str += 'urdlurrdluldrruld'
        self.update_puzzle(move_str)
        return move_str

    def solve_row1_tile(self, target_col):
        """
        Solve the tile in row one at the specified column
        Updates puzzle and returns a move string
        """
        move_str = ""
        cur_row, cur_col = self.current_position(1, target_col)

        # Target tile is left of zero tile
        if (cur_row == 1):
            left_dist = target_col - cur_col
            move_str += left_dist * 'l'

            while left_dist-1 > 0:
                move_str += 'urrdl'
                left_dist -= 1
            move_str += 'ur'
        # Target tile is above and to the left
        else:
            move_str += 'u'
            if (cur_col != target_col):
                left_dist = target_col - cur_col
                move_str += left_dist * 'l'
                while left_dist-1 > 0:
                    move_str += 'drrul'
                    left_dist -= 1
                move_str += 'dru'

        self.update_puzzle(move_str)
        return move_str

    ###########################################################
    # Phase 3 methods

    def solve_2x2(self):
        """
        Solve the upper left 2x2 part of the puzzle
        Updates the puzzle and returns a move string
        """
        move_str = ""
        row0 = self._grid[0][:2]
        row1 = self._grid[1][:2]
        config = row0 + row1

        if (config[1] > config[2] and config[2] > config[0]):
            move_str += 'ul'
        elif (config[2] > config[0] and config[0] > config[1]):
            move_str += 'lu'
        elif (config[0] > config[1] and config[1] > config[2]):
            move_str += 'lurdlu'
        else:
            move_str += 'lu'
            print("This board can't be solved.")

        self.update_puzzle(move_str)
        return move_str

    def check_pos(self, row, col):
        """
        Checks the position that needs to be moved first
        """
        start = True

        # Checks starting from highest number
        while row != 0 or col != 0:
            solved_value = col + (self.get_width() * row)
            if self.get_number(row, col) != solved_value:
                return False, (row, col)
            col -= 1
            if col < 0:
                row -= 1
                col = self.get_width() - 1

        return start, (row, col)

    def solve_puzzle(self):
        """
        Generate a solution string for a puzzle
        Updates the puzzle and returns a move string
        """
        row = self.get_height()-1
        col = self.get_width()-1

        final_str = ""
        move_str = ""
        zero_row, zero_col = self.current_position(0, 0)

        # Return state and first position that is wrong starting from last
        check = self.check_pos(row, col)

        # Board is already solved
        if (check[0] == True):
            return final_str
        # pos is row, col of first wrong tile
        pos = check[1]

        # The position that needs to be moved is in the lower half of
        # the board
        if pos[0] > 1:
            # Moves zero tile to first wrong position
            horiz_dist = pos[1] - zero_col
            if horiz_dist > 0:
                move_str += horiz_dist * 'r'
            if horiz_dist < 0:
                move_str += abs(horiz_dist) * 'l'
            down_dist = abs(pos[0] - zero_row)
            move_str += (down_dist * 'd')
            final_str += move_str
            self.update_puzzle(move_str)
            zero_row = pos[0]
            zero_col = pos[1]

            #print final_str
            while zero_row > 1:
            # assert self.lower_row_invariant(zero_row, zero_col)
                if zero_col == 0:
                    move_str = self.solve_col0_tile(zero_row)
                    final_str += move_str
                    zero_col = col
                    zero_row -= 1
                else:
                    move_str = self.solve_interior_tile(zero_row, zero_col)
                    final_str += move_str
                    zero_col -= 1

        move_str = ''
        if zero_row <= 1:
            # Moves zero tile to row1, col3
            horiz_dist = col - zero_col
            move_str += 'r' * horiz_dist
            down_dist = abs(1 - zero_row)
            move_str += down_dist * 'd'
            final_str += move_str
            self.update_puzzle(move_str)
            zero_row = 1
            zero_col = col

            while zero_col != 1:
                #assert self.row1_invariant(zero_col)
                move_str = self.solve_row1_tile(zero_col)
                final_str += move_str
                #assert self.row0_invariant(zero_col)
                move_str = self.solve_row0_tile(zero_col)
                final_str += move_str
                zero_col -= 1
            move_str = self.solve_2x2()
            final_str += move_str


        return final_str
