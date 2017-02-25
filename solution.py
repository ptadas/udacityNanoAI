assignments = []


def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """
    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values


def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    # find the twins
    twins = []
    for unit in unitlist:
        twins_temp = {}
        # for each box in unit check if its length == 2
        # if yes, add it's value as key and append box to list
        for box in unit:
            box_val = values[box]
            if len(box_val) == 2:
                if box_val not in twins_temp:
                    twins_temp[box_val] = [box]
                else:
                    twins_temp[box_val].append(box)

        # when done iterating over the unit
        # find the twins: they are the items in
        # the dict which vals len == 2
        for vals, boxes in twins_temp.items():
            if len(boxes) == 2:
                twins.append([
                    boxes,
                    vals,
                    # save unit so that one can iterate over it
                    unit
                ])

    # remove the twin val from unit boxes
    for boxes, vals, unit in twins:
        for box in unit:
            if box in boxes:
                continue

            for v in vals:
                if v in values[box]:
                    values = assign_value(values, box, values[box].replace(v, ''))

    return values


def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [s + str(t) for s in A for t in B]


def diagonals(rows, cols):
    diag1 = []
    diag2 = []

    lenr = len(rows) - 1
    # build diagonal lists in one go
    for indx, r in enumerate(rows):
        diag1.append(r + cols[indx])
        diag2.append(r + cols[lenr - indx])

    return [diag1, diag2]


rows = 'ABCDEFGHI'
cols = '123456789'
boxes = cross(rows, cols)

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
diagonal_units = diagonals(rows, cols)

unitlist = row_units + column_units + square_units + diagonal_units

units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[])) - set([s])) for s in boxes)


def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    val_dict = dict(zip(boxes, grid))

    for key, val in val_dict.items():
        if val == '.':
            val_dict[key] = '123456789'

    return val_dict


def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1 + max(len(values[s]) for s in boxes)
    line = '+'.join(['-' * (width * 3)] * 3)
    for r in rows:
        print(''.join(values[r + c].center(width) + ('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return


def eliminate(values):
    """
    Eliminate values from peers of each box with a single value.

    Go through all the boxes, and whenever there is a box with a single value,
    eliminate this value from the set of values of all its peers.

    Args:
        values: Sudoku in dictionary form.
    Returns:
        Resulting Sudoku in dictionary form after eliminating values.
    """
    for key, val in values.copy().items():
        if len(val) == 1:
            for peer in peers[key]:
                values = assign_value(values, peer, values[peer].replace(val, ''))

    return values


def only_choice(values):
    """
    Finalize all values that are the only choice for a unit.

    Go through all the units, and whenever there is a unit with a value
    that only fits in one box, assign the value to this box.

    Input: Sudoku in dictionary form.
    Output: Resulting Sudoku in dictionary form after filling in only choices.
    """
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]

            if len(dplaces) == 1:
                values = assign_value(values, dplaces[0], digit)
    return values


def reduce_puzzle(values):
    """
    Iterate eliminate() and only_choice(). If at some point, there is a box with no available values, return False.
    If the sudoku is solved, return the sudoku.
    If after an iteration of both functions, the sudoku remains the same, return the sudoku.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    solved_before = 1
    solved_after = 0
    while solved_before != solved_after:
        # get the count of solved vals before and after the solving process
        # if the len before == len after then stop as nothing has changed
        solved_before = sum(len(vals) for key, vals in values.items())

        values = eliminate(values)
        values = only_choice(values)
        values = naked_twins(values)

        solved_after = sum(len(vals) for key, vals in values.items())

    return values


def search(values):
    "Using depth-first search and propagation, create a search tree and solve the sudoku."

    # try reducing the puzzle first
    values = reduce_puzzle(values)
    if not values:
        return False

    # great, the sudoku is solved if true
    if sum(len(vals) for key, vals in values.items()) == len(values):
        return values

    # Choose one of the unfilled squares with the fewest possibilities
    n, s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)

    # try to solve for each value
    # return first solved
    for value in values[s]:
        new_values = values.copy()
        new_values[s] = value
        solution = search(new_values)
        if solution:
            return solution


def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    return search(grid_values(grid))


if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
