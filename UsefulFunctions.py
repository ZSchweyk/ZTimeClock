def count_dec_places(num):
    num_as_str = str(num)
    dec_index = num_as_str.index(".")
    dec = num_as_str[dec_index + 1:]
    return len(dec)

def round_to(num, nrst, limit):
    """
    Rounds a number to the nearest tenth, quarter..., and makes sure to not exceed a given limit.
    """
    dec = num - int(num)
    dec_remainder = round(dec % nrst, 5)

    print(dec_remainder)

    if dec_remainder == 0:
        return num
    if dec_remainder >= round(nrst / 2, 5):
        rounded_up = int(num) + (dec - dec_remainder) + nrst
        if rounded_up <= limit:
            return round(rounded_up, 5)
    rounded_down = int(num) + (dec - dec_remainder)
    return round(rounded_down if rounded_down <= limit else limit, 5)


print(round_to(80.149, .1, 80.5))

# num = 8.5
# print(f"{num} = {bin(num)}")

