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


def calculate_leave_time(clock_in: datetime, shift_end: datetime, max_day_hours, current_period_hours, max_period_hours):
    max_day_hours = max(min(max_day_hours, max_period_hours - current_period_hours), 0)
    current_period_hours += max_day_hours
    print(f"current_period_hours: {current_period_hours}")
    rounded_total_period_hours_worked = round_to(current_period_hours, .25, 1000)
    print(f"rounded_total_period_hours_worked: {rounded_total_period_hours_worked}")
    difference = rounded_total_period_hours_worked - current_period_hours
    max_day_hours += difference
    temp_clock_out = clock_in + timedelta(hours=max_day_hours)
    if temp_clock_out > shift_end:
        max_day_hours -= (temp_clock_out - shift_end).seconds / 3600
    final_clock_out = clock_in + timedelta(hours=max_day_hours)
    return final_clock_out.strftime("%I:%M:%S %p")


clock_in = datetime.strptime("6:00:00 am", "%I:%M:%S %p")
shift_end = datetime.strptime("3:30:00 pm", "%I:%M:%S %p")
max_day_hours = 8
current_period_hours = 70.15
max_period_hours = 80

calculated_clock_out = calculate_leave_time(clock_in, shift_end, max_day_hours, current_period_hours, max_period_hours)

print(f"Calculated Clock Out: {calculated_clock_out}")

