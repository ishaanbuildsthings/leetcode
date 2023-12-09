# pretty print a matrix

def pprint(matrix):
    print('\n'.join(['\t'.join([str(cell) for cell in row]) for row in matrix]))