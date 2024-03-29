from random import randint, choice
from demineur import Demineur


class Solver:
    def __init__(self, dem: Demineur, verbose=True):
        self.border = []
        self.dem = dem
        self.width, self.height = self.dem.get_board_size()
        self.random_sec_pass = 0
        self.v = verbose

    def solve(self):
        # First thing pick a random case
        x = randint(0, self.width - 1)
        y = randint(0, self.height - 1)
        end = self.dem.reveal_bomb(x, y)
        if not end:
            self.__update_border()
            assert len(self.border) != 0, "Logic exception border cannot be empty"
        else:
            if self.v: print("Sadly first guess was a bomb...")
            return 2

        nb_zeros_cell = 0
        while not end:
            second_pass = True
            # First pass simple check
            bordercpy = self.border.copy()
            done_smthing = False

            for x, y in bordercpy:
                cell = self.dem.get_cell(x, y)
                neighbours = cell.get_neighbours()
                flagged_neighbours = [(x, y) for x, y in neighbours if self.dem.get_cell(x, y).is_flagged()]
                unrevealed_neighbours = [(x, y) for x, y in neighbours if not self.dem.get_cell(x, y).is_revealed()]
                
                nb_neighbour_bombs = cell.get_number_bombs()

                if len(flagged_neighbours) == nb_neighbour_bombs == len(unrevealed_neighbours):
                    done_smthing = True
                    self.border.remove((x, y))
                elif len(unrevealed_neighbours) == nb_neighbour_bombs:
                    done_smthing = True
                    # Great easy one we just got a simple case there
                    self.border.remove((x, y))
                    for x2, y2 in unrevealed_neighbours:
                        n_cell = self.dem.get_cell(x2, y2)
                        n_cell.set_flag()
                elif len(flagged_neighbours) == nb_neighbour_bombs:
                    done_smthing = True
                    # Great again simple case !
                    self.border.remove((x, y))
                    for x2, y2 in neighbours:
                        n_cell = self.dem.get_cell(x2, y2)
                        if not n_cell.is_revealed() and not n_cell.is_flagged():
                            if self.dem.reveal_bomb(x2, y2):
                                if self.v: print("The robot has lost miserably ...")
                                return 3
                        self.__update_border()
                else:
                    # Now we analyse the patterns
                    if nb_neighbour_bombs - len(flagged_neighbours) == 1:
                        # assert len(flagged_neighbours) == 0, "logic exception, cannot be with {} flagged neighbours".format(len(flagged_neighbours))
                        
                        # First we try to detect the 1-1 pattern
                        for x2,y2 in neighbours:
                            ncell = self.dem.get_cell(x2,y2)
                            # Automatically implies it have been revealed !
                            ncell_flagged_neighbours = sum([1 for x, y in ncell.get_neighbours() if self.dem.get_cell(x, y).is_flagged()])
                            if ncell.is_revealed() and ncell.get_number_bombs() - ncell_flagged_neighbours == 1:
                                # Not in the diagonal
                                if x2 == x or y2 == y:
                                    dx = x2 - x
                                    dy = y2 - y
                                    if dy == 0:
                                        # We count all cells that have not been revealed upper or downer
                                        upper = sum([1 for ex,ey in neighbours if ey < y and not self.dem.get_cell(ex,ey).is_revealed() and not self.dem.get_cell(ex,ey).is_flagged()]) 
                                        under = sum([1 for ex,ey in neighbours if ey > y and not self.dem.get_cell(ex,ey).is_revealed() and not self.dem.get_cell(ex,ey).is_flagged()])
                                        expected_upper = 3
                                        expected_under = 3
                                        if x == 0 or x == self.width - 1:
                                            expected_upper = expected_under = 2
                                        if y == 0:
                                            expected_upper = 0
                                        elif y == self.height - 1:
                                            expected_under = 0
                                        if (under == 0 and upper == expected_upper) or (upper == 0 and under == expected_under):
                                            assert not (under == 0 and upper == 0), "Logic exception, upper and under cannot both be 0"
                                            side_of_sidecell = sum([1 for ex,ey in ncell.get_neighbours() if ex == x2 + dx and not self.dem.get_cell(ex,ey).is_revealed() and not self.dem.get_cell(ex,ey).is_flagged()])
                                            if side_of_sidecell == 0 and upper == 0 and 0 <= x - dx < self.width and 0 <= y + 1 < self.height:
                                                done_smthing = True
                                                # assert 0 <= x - dx < self.width, "x-dx {} is not in 0 {} for ({},{})".format(x-dx, self.width - 1, x, y)
                                                # assert 0 <= y + 1 < self.height, "y+1 {} is not in 0 {} for ({},{})".format(y+1, self.height - 1, x, y)
                                                end = end or self.dem.reveal_bomb(x - dx, y + 1)
                                                self.__update_border()
                                            elif side_of_sidecell == 0 and under == 0 and 0 <= x - dx < self.width and 0 <= y - 1 < self.height:
                                                done_smthing = True
                                                # assert 0 <= x - dx < self.width, "x-dx {} is not in 0 {} for ({},{})".format(x-dx, self.width - 1, x, y)
                                                # assert 0 <= y - 1 < self.height, "y-1 {} is not in 0 {} for ({},{})".format(y-1, self.height - 1, x, y)
                                                end = end or self.dem.reveal_bomb(x - dx,y - 1)
                                                self.__update_border()
                                            assert not end, "Lost in line 84 because of wrong 1-1 solution"
                                    elif dx == 0:
                                        # We count all cells that have not been revealed right or left
                                        left = sum([1 for ex,ey in neighbours if ex < x and not self.dem.get_cell(ex,ey).is_revealed()]) 
                                        right = sum([1 for ex,ey in neighbours if ex > x and not self.dem.get_cell(ex,ey).is_revealed()])
                                        expected_left = 3
                                        expected_right = 3
                                        if y == 0 or y == self.height - 1:
                                            expected_left = expected_right = 2
                                        if x == 0:
                                            expected_upper = 0
                                        elif x == self.width - 1:
                                            expected_under = 0
                                        if (left == 0 and right == expected_right) or (right == 0 and left == expected_left):
                                            assert not (left == 0 and right == 0), "Logic exception, right and left cannot both be 0"
                                            side_of_sidecell = sum([1 for ex,ey in ncell.get_neighbours() if ey == y2 + dy and not self.dem.get_cell(ex,ey).is_revealed() and not self.dem.get_cell(ex,ey).is_flagged()])
                                            if side_of_sidecell == 0 and right == 0 and 0 <= x - 1 < self.width and 0 <= y - dy < self.height:
                                                done_smthing = True
                                                # assert 0 <= x - 1 < self.width, "x-1 {} is not in 0 {} for ({},{})".format(x-1, self.width - 1, x, y)
                                                # assert 0 <= y - dy < self.height, "y-dy {} is not in 0 {} for ({},{})".format(y-dy, self.height - 1, x, y)
                                                end = end or self.dem.reveal_bomb(x - 1,y - dy)
                                                self.__update_border()
                                            elif side_of_sidecell == 0 and left == 0  and 0 <= x + 1 < self.width and 0 <= y - dy < self.height:
                                                done_smthing = True
                                                # assert 0 <= x + 1 < self.width, "x+1 {} is not in 0 {} for ({},{})".format(x+1, self.width - 1, x, y)
                                                # assert 0 <= y - dy < self.height, "y-dy {} is not in 0 {} for ({},{})".format(y-dy, self.height - 1, x, y)
                                                end = end or self.dem.reveal_bomb(x + 1,y - dy)
                                                self.__update_border()
                                            assert not end, "Lost in line 98 because of wrong 1-1 solution"
                    if nb_neighbour_bombs - len(flagged_neighbours) == 2:
                        # Ok for 2-1 tactics
                        for x2,y2 in neighbours:
                            ncell = self.dem.get_cell(x2,y2)
                            # Automatically implies it have been revealed !
                            ncell_flagged_neighbours = sum([1 for x, y in ncell.get_neighbours() if self.dem.get_cell(x, y).is_flagged()])
                            if ncell.is_revealed() and ncell.get_number_bombs() - ncell_flagged_neighbours == 1:
                                # Not in the diagonal
                                if x2 == x or y2 == y:

                                    dx = x2 - x
                                    dy = y2 - y

                                    if dy == 0:
                                        # We count all cells that have not been revealed upper or downer
                                        upper = sum([1 for ex,ey in neighbours if ey < y and not self.dem.get_cell(ex,ey).is_revealed() and not self.dem.get_cell(ex,ey).is_flagged()]) 
                                        under = sum([1 for ex,ey in neighbours if ey > y and not self.dem.get_cell(ex,ey).is_revealed() and not self.dem.get_cell(ex,ey).is_flagged()])
                                        if ((under == 0 and upper == 3) or (upper == 0 and under == 3)) and self.dem.get_cell(x-dx,y).is_revealed():
                                            assert not (under == 0 and upper == 0), "Logic exception, upper and under cannot both be 0"
                                            if upper == 0:
                                                done_smthing = True
                                                end = end or self.dem.flag_bomb(x - dx, y + 1)
                                            elif under == 0:
                                                done_smthing = True
                                                end = end or self.dem.flag_bomb(x - dx,y - 1)
                                            assert not end, "Lost in line 84 because of wrong 1-2 solution"
                                    elif dx == 0:
                                        # We count all cells that have not been revealed right or left
                                        left = sum([1 for ex,ey in neighbours if ex < x and not self.dem.get_cell(ex,ey).is_revealed() and not self.dem.get_cell(ex,ey).is_flagged()]) 
                                        right = sum([1 for ex,ey in neighbours if ex > x and not self.dem.get_cell(ex,ey).is_revealed() and not self.dem.get_cell(ex,ey).is_flagged()])
                                        if ((left == 0 and right == 3) or (right == 0 and left == 3)) and self.dem.get_cell(x,y-dy).is_revealed():
                                            assert not (left == 0 and right == 0), "Logic exception, right and left cannot both be 0"
                                            if right == 0:
                                                done_smthing = True
                                                end = end or self.dem.flag_bomb(x - 1,y - dy)
                                            elif left == 0:
                                                done_smthing = True
                                                end = end or self.dem.flag_bomb(x + 1,y - dy)
                                            assert not end, "Lost in line 98 because of wrong 1-1 solution"

            if self.dem.is_it_over():
                if self.v: print("Well done you won !")
                return 1

            if nb_zeros_cell == 0:
                for y in range(self.height):
                    for x in range(self.width):
                        cell = self.dem.get_cell(x, y)
                        if cell.is_revealed() and cell.get_number_bombs() == 0:
                            nb_zeros_cell += 1
                if nb_zeros_cell == 0:
                    done_smthing = True
                    x = randint(0, self.width - 1)
                    y = randint(0, self.height - 1)
                    end = self.dem.reveal_bomb(x, y)
                    if not end:
                        self.__update_border()
                    else:
                        if self.v: "Random gave a bomb (2 try)"

            if not done_smthing:
                if self.v: print("Needs more than the 1-1")
                if self.v: print("Border : ", self.border)
                # Assuming nothing can be done we reveal a random cell
                end = end or self.__reveal_random_cell()

                # self.dem.get_true_board()
                # print("\n")
                # print(self.dem)
                # raise Exception("Error !")
                if end:
                    return 5


            if end:
                return 4

            # if second_pass:
            #     bordercpy = self.border.copy()
            #     # This part works with probability, flagging the most probable cell
            #     # The idea is to try every possibility and see if there is one that works
            #     # For that we take the "2nd order neighbours"
            #     nb_zeros_cell = 0
            #     for y in range(self.height):
            #         for x in range(self.width):
            #             cell = self.dem.get_cell(x, y)
            #             if cell.is_revealed() and cell.get_number_bombs() == 0:
            #                 nb_zeros_cell += 1

            #     if nb_zeros_cell == 0:
            #         self.random_sec_pass += 1
            #         if self.random_sec_pass >= 5:
            #             if self.random_sec_pass % 5 == 0:
            #                 if self.v: print(self.dem)
            #         # Well this I can't do a lot so random again !
            #         if self.v: print("Need a random second pass sadly !")
            #         x = randint(0, self.width - 1)
            #         y = randint(0, self.height - 1)
            #         end = self.dem.reveal_bomb(x, y)
            #         if not end:
            #             self.border.append((x, y))
            #         else:
            #             if self.v: print("Unluckily this was a bomb on the second pass")
            #             return 4
                    
                   
        return False

    def __update_border(self):
        for y in range(self.height):
            for x in range(self.width):
                cell = self.dem.get_cell(x, y)
                neighbours = cell.get_neighbours()
                number_flagged = [(x, y) for x, y in neighbours if self.dem.get_cell(x, y).is_flagged()]
                if cell.is_revealed() and cell.get_number_bombs() != len(number_flagged):
                    self.border.append((x, y))

    def __reveal_random_cell(self):
        unrevealed_cells = []
        for y in range(self.height):
            for x in range(self.width):
                cell = self.dem.get_cell(x, y)
                if not cell.is_revealed() and not cell.is_flagged():
                    unrevealed_cells.append((x,y))
        x,y = choice(unrevealed_cells)
        return self.dem.reveal_bomb(x, y)

