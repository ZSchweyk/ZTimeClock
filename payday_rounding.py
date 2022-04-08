from datetime import datetime, timedelta


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


def round_down_to(num, nrst):
    round_to_x_dec = 15
    dec = num - int(num)
    dec_remainder = round(dec % nrst, round_to_x_dec)

    if dec_remainder == 0:
        return num
    return int(num) + (dec - dec_remainder)


def is_rounded_to(num, nrst):
    num_times = int(1 / nrst)
    for i in range(num_times):
        if num == int(num) + i * nrst:
            return True
    return False


def calculate_leave_time(clock_in: datetime, shift_end: datetime, max_day_hours, current_period_hours,
                         max_period_hours):
    if max_day_hours >= 6.5:
        max_day_hours += .5

    original_max_day_hours = max_day_hours
    original_current_period_hours = current_period_hours

    max_day_hours = round(max(min(max_day_hours, max_period_hours - current_period_hours), 0), 3)
    print(f"max_day_hours: {max_day_hours}")
    current_period_hours += max_day_hours
    print(f"current_period_hours: {current_period_hours}")
    rounded_total_period_hours_worked = round_to(current_period_hours, .25, 1000)
    print(f"rounded_total_period_hours_worked: {rounded_total_period_hours_worked}")
    difference = round(rounded_total_period_hours_worked - current_period_hours, 3)
    print(f"difference: {difference}")
    max_day_hours += difference
    print(f"max_day_hours: {max_day_hours}")
    if max_day_hours > original_max_day_hours:
        max_day_hours = original_max_day_hours
        print(f"max_day_hours: {max_day_hours}")
        rounded_total_period_hours_worked = round_down_to(current_period_hours, .25)
        print(f"rounded_total_period_hours_worked: {rounded_total_period_hours_worked}")
        difference = round(rounded_total_period_hours_worked - current_period_hours, 3)
        print(f"difference: {difference}")
        max_day_hours += difference
        print(f"max_day_hours: {max_day_hours}")

    total_period_hours_worked = original_current_period_hours + max_day_hours

    temp_clock_out = clock_in + timedelta(hours=max_day_hours)
    print(f"temp_clock_out: {temp_clock_out}")
    if temp_clock_out > shift_end:
        print("ENTERED CONDITION")
        max_day_hours -= (temp_clock_out - shift_end).seconds / 3600
        print(f"max_day_hours: {max_day_hours}")
        total_period_hours_worked = original_current_period_hours + max_day_hours
        print(f"total_period_hours_worked: {total_period_hours_worked}")
        rounded_down_total_period_hours_worked = round_down_to(original_current_period_hours + max_day_hours, .25)
        print(f"rounded_down_total_period_hours_worked: {rounded_down_total_period_hours_worked}")
        difference = total_period_hours_worked - rounded_down_total_period_hours_worked
        print(f"difference: {difference}")
        max_day_hours -= difference
        print(f"max_day_hours: {max_day_hours}")
        total_period_hours_worked = original_current_period_hours + max_day_hours
        print(f"total_period_hours_worked: {total_period_hours_worked}")

    final_clock_out = clock_in + timedelta(hours=max_day_hours)

    print()

    print(f"total_period_hours_worked {total_period_hours_worked}")

    if not (total_period_hours_worked <= max_period_hours and is_rounded_to(total_period_hours_worked, .25)):
        raise Exception("Something's Terribly Wrong!")

    return final_clock_out.strftime("%I:%M:%S %p")


clock_in = datetime.strptime("6:00:00 am", "%I:%M:%S %p")
shift_end = datetime.strptime("3:30:00 pm", "%I:%M:%S %p")
max_day_hours = 9
current_period_hours = 37.9
max_period_hours = 48

calculated_clock_out = calculate_leave_time(clock_in, shift_end, max_day_hours, current_period_hours, max_period_hours)

print()
print(f"Calculated Clock Out: {calculated_clock_out}")
