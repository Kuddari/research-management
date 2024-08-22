def format_money_thai(number):
    if number < 10000:
        return f"{number}", ""
    elif number < 100000:  # หมื่น to แสน
        return f"{number / 10000:.1f}", "หมื่น"
    elif number < 1000000:  # แสน
        return f"{number / 100000:.1f}", "แสน"
    elif number < 10000000000:  # ล้าน
        return f"{number / 1000000:.1f}", "ล้าน"
    elif number < 10000000000:  # พันล้าน
        return f"{number / 1000000000:.1f}", "พันล้าน"
    elif number < 100000000000:  # หมื่นล้าน
        return f"{number / 10000000000:.1f}", "หมื่นล้าน"
    elif number < 1000000000000:  # หมื่นล้าน
        return f"{number / 100000000000:.1f}", "แสนล้าน"
    else:  # ล้านล้าน or more
        return f"{number / 1000000000000}", "ล้านล้าน"