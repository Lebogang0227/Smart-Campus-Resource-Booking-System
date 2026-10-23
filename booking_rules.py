from datetime import datetime, timedelta

CAMPUS_RULES = {
    "Centurion": {
        "max_duration": 180,
        "open_hour": 8,
        "closing_hour": 17,
        "priority": "Teaching bookings take priority over events",

    },
    "Brynston": {
        "max_duration": 180,
        "open_hour": 8,
        "closing_hour": 18,
        "priority": "Teaching bookings take priority over events",
    },
    "Pretoria": {
        "max_duration": 180,
        "open_hour": 6,
        "closing_hour": 18,
        "priority": "Teaching bookings take priority over events",
    },
}

def get_rules(campus):
    return CAMPUS_RULES.get(
        campus,
        {"max_duration": 120, "open_hour": 8, "closing_hour":17, "priority": "Standard Rules"},

    )

def describe_rules(campus):
    rules = get_rules(campus)
    return (
        f"Max duration: {rules['max_duration']} minutes | "
        f"Open: {rules['open_hour']:02d}:00 - {rules['closing_hour']:02d}:00 | "
        f"Priority: {rules['priority']}"
    )

def validate_booking(campus, booking_date, start_time, duration):

    rules = get_rules(campus)
    try:
        date_obj = datetime.strptime(booking_date, "%Y-%m-%d").date()
    except ValueError:
        return False, "Date must be in YYYY-MM-DD format."

    #Validate the time format
    try:
        start_obj = datetime.strptime(start_time, "%H:%M").time()
    except ValueError:
        return False, "Time must be in HH:MM format (24-hour)."

    #Check the duration limit
    if duration <= 0:
        return False, "Duration must be greater than 0."
    if duration > rules["max_duration"]:
        return False, (
            f"{campus} allows a maximum booking of "
            f"{rules['max_duration']} minutes."
        )

    #Check opening and closing hours
    start_hour = start_obj.hour
    end_dt = datetime.combine(date_obj, start_obj) + timedelta(minutes=duration)
    end_hour = end_dt.hour

    if start_hour < rules["open_hour"]:
        return False, f"{campus} opens at {rules['open_hour']:02d}:00."
    if end_hour > rules["closing_hour"]:
        return False, f"{campus} closes at {rules['closing_hour']:02d}:00."
    if end_dt.date() != date_obj:
        return False, "Booking must end on the same day it starts."

    #Booking cannot be in the past
    now = datetime.now()
    start_dt = datetime.combine(date_obj, start_obj)
    if start_dt < now:
        return False, "You cannot book a date/time in the past."

    return True, "OK"


def times_overlap(date1, start1, dur1, date2, start2, dur2):
    if date1 != date2:
        return False
    s1 = datetime.strptime(f"{date1} {start1}", "%Y-%m-%d %H:%M")
    e1 = s1 + timedelta(minutes=dur1)
    s2 = datetime.strptime(f"{date2} {start2}", "%Y-%m-%d %H:%M")
    e2 = s2 + timedelta(minutes=dur2)
    return s1 < e2 and s2 < e1