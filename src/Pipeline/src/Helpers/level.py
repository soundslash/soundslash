
def get_level(listeners, max_listeners):
    level = 0
    max_level = 0
    i = max_listeners
    j = 2
    first_skip = True
    while i >= 0:
        if i >= listeners and listeners > i-j:
            level = max_level
        max_level += 1
        i = i - j
        if first_skip:
            first_skip = False
        else:
            j = j * 2
    level = max_level - level
    level -= 1
    max_level -= 1
    level = float(level * 10 / max_level)
    max_level = 10
    return level

def round_max_listeners(max_listeners):
    i = 8
    j = 0
    while max_listeners >= i:
        j = i
        i = i * 2
    return j
