def round_to(num, nrst, limit):
    """
    Rounds a number to the nearest tenth, quarter..., and makes sure to not exceed a given limit.
    """
    round_to_x_dec = 15

    dec = num - int(num)
    dec_remainder = round(dec % nrst, round_to_x_dec)

    if dec_remainder == 0:
        return num
    if dec_remainder >= round(nrst / 2, round_to_x_dec):
        rounded_up = int(num) + (dec - dec_remainder) + nrst
        if rounded_up <= limit:
            return round(rounded_up, round_to_x_dec)
    rounded_down = int(num) + (dec - dec_remainder)
    return round(rounded_down if rounded_down <= limit else limit, round_to_x_dec)


def calculate_leave_time(clock_in: datetime, shift_end: datetime, max_day_hours, current_period_hours, max_period_hours):
    current_period_hours += max_day_hours


