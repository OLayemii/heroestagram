def findfirstodd(seq):
    for i in range(len(seq) - 1):
        if seq[i+1] <= seq[i]:
            return i
    return -1


def almostIncreasingSequence(sequence):
    j = findfirstodd(sequence)
    print(j)
    k = -1
    m = sequence[:]
    if j >= 0:
        m.pop(j+1)
        k = findfirstodd(m)
    if k == -1:
        return True
    else:
        return False
    return False

print(almostIncreasingSequence([10, 1, 2, 3, 4, 5]))