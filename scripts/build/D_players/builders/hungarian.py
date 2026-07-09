def pad_matrix(matrix, padding_value=None):

    rows = len(matrix)
    cols = len(matrix[0])

    size = max(rows, cols)

    if padding_value is None:
        padding_value = (
            max(
                max(row)
                for row in matrix
            ) + 1
        )

    padded = [
        row + [padding_value] * (size - cols)
        for row in matrix
    ]

    for _ in range(size - rows):
        padded.append(
            [padding_value] * size
        )

    return padded, rows, cols

def reduce_rows(matrix):

    for row in matrix:

        minimum = min(row)

        for j in range(len(row)):
            row[j] -= minimum

def reduce_columns(matrix):

    if not matrix:
        return

    rows = len(matrix)
    cols = len(matrix[0])

    for col in range(cols):

        minimum = min(
            matrix[row][col]
            for row in range(rows)
        )

        for row in range(rows):
            matrix[row][col] -= minimum

def find_independent_zeros(matrix):

    rows = len(matrix)
    cols = len(matrix[0])

    starred = set()
    used_cols = set()

    row_order = sorted(
        range(rows),
        key=lambda i: sum(value == 0 for value in matrix[i])
    )

    for i in row_order:
        for j in range(cols):

            if matrix[i][j] != 0:
                continue

            if j in used_cols:
                continue

            starred.add((i, j))
            used_cols.add(j)
            break

    return starred

def is_complete_assignment(starred, size):

    return len(starred) == size

def find_uncovered_zero(matrix, covered_rows, covered_cols):

    rows = len(matrix)
    cols = len(matrix[0])

    for i in range(rows):

        if i in covered_rows:
            continue

        for j in range(cols):

            if j in covered_cols:
                continue

            if matrix[i][j] == 0:
                return (i, j)

    return None

def find_star_in_row(starred, row):

    for i, j in starred:

        if i == row:
            return (i, j)

    return None

def find_star_in_col(starred, col):

    for i, j in starred:

        if j == col:
            return (i, j)

    return None

def find_prime_in_row(primed, row):

    for i, j in primed:

        if i == row:
            return (i, j)

    return None

def build_augmenting_path(primed, starred, start_prime):

    path = [start_prime]

    while True:

        _, col = path[-1]

        star = find_star_in_col(
            starred,
            col
        )

        if star is None:
            break

        path.append(star)

        prime = find_prime_in_row(
            primed,
            star[0]
        )

        assert prime is not None

        path.append(prime)

    return path

def augment_path(path, starred):

    for index, position in enumerate(path):

        if index % 2 == 0:
            starred.add(position)
        else:
            starred.remove(position)

def cover_starred_columns(starred):

    return {
        col
        for _, col in starred
    }

def find_smallest_uncovered(matrix, covered_rows, covered_cols):

    minimum = float("inf")

    rows = len(matrix)
    cols = len(matrix[0])

    for i in range(rows):

        if i in covered_rows:
            continue

        for j in range(cols):

            if j in covered_cols:
                continue

            minimum = min(
                minimum,
                matrix[i][j]
            )

    return minimum

def adjust_matrix(matrix, covered_rows, covered_cols):

    minimum = find_smallest_uncovered(
        matrix,
        covered_rows,
        covered_cols
    )

    rows = len(matrix)
    cols = len(matrix[0])

    for i in range(rows):

        for j in range(cols):

            row_covered = i in covered_rows
            col_covered = j in covered_cols

            if not row_covered and not col_covered:
                matrix[i][j] -= minimum

            elif row_covered and col_covered:
                matrix[i][j] += minimum

def prime_uncovered_zeros(matrix, primed, starred, covered_rows, covered_cols):

    while True:

        zero = find_uncovered_zero(
            matrix,
            covered_rows,
            covered_cols
        )

        if zero is None:

            adjust_matrix(
                matrix,
                covered_rows,
                covered_cols
            )

            continue

        primed.add(zero)

        star = find_star_in_row(
            starred,
            zero[0]
        )

        if star is None:
            return zero

        covered_rows.add(zero[0])

        covered_cols.discard(star[1])

def hungarian(cost_matrix):

    matrix, original_rows, original_cols = pad_matrix(cost_matrix)

    reduce_rows(matrix)
    reduce_columns(matrix)

    starred = find_independent_zeros(matrix)

    primed = set()

    covered_rows = set()
    covered_cols = cover_starred_columns(starred)

    while not is_complete_assignment(starred, len(matrix)):

        start_prime = prime_uncovered_zeros(
            matrix,
            primed,
            starred,
            covered_rows,
            covered_cols
        )

        path = build_augmenting_path(
            primed,
            starred,
            start_prime
        )

        augment_path(
            path,
            starred
        )

        primed.clear()

        covered_rows.clear()

        covered_cols = cover_starred_columns(starred)

    assignment = sorted(
        (row, col)
        for row, col in starred
        if row < original_rows and col < original_cols
    )

    return assignment

def print_matrix(matrix):
    for row in matrix:
        print(row)
    print()

def main():

    matrix = [
        [8, 5, 7, 6],
        [4, 6, 3, 7],
        [9, 8, 2, 5],
        [6, 4, 3, 8]
    ]

    print_matrix(hungarian(matrix))

if __name__ == "__main__":
    main()
