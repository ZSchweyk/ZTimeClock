def round_to(num, nrst, limit):
    """
    Rounds a number to the nearest tenth, quarter..., and makes sure to not exceed a given limit.
    """
    dec = num - int(num)
    dec_remainder = dec % nrst

    if dec_remainder == 0:
        return num
    if dec_remainder >= nrst / 2:
        result = int(num) + (dec - dec_remainder) + nrst
        if result <= limit:
            return result
    return int(num) + (dec - dec_remainder)


print(round_to(80.46, .1, 80.5))
