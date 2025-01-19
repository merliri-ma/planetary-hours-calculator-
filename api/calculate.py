from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from typing import List, Tuple, Dict
from calendar import monthrange

app = Flask(__name__)

PLANETARY_ORDER = [
    "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"
]

def adjust_for_past_midnight(sunset_time: datetime, sunrise_time: datetime) -> datetime:
    """Adjusts sunset time if it occurs before sunrise."""
    if sunset_time < sunrise_time:
        return sunset_time + timedelta(days=1)
    return sunset_time

def parse_time(time_str: str) -> datetime:
    """Validates and converts time string to datetime object."""
    try:
        return datetime.strptime(time_str, "%H:%M")
    except ValueError:
        raise ValueError(f"Invalid time format: {time_str}. Expected HH:MM format.")

def calculate_planetary_hours(
    sunrise: str, 
    sunset: str, 
    day_of_week: int
) -> List[Tuple[str, str]]:
    """
    Calculates planetary hours for a given day.
    
    Args:
        sunrise: Sunrise time in HH:MM format
        sunset: Sunset time in HH:MM format
        day_of_week: Day of week (0=Sunday, 1=Monday, ..., 6=Saturday)
        
    Returns:
        List of tuples containing (time, planet) pairs
    """
    sunrise_time = parse_time(sunrise)
    sunset_time = parse_time(sunset)
    sunset_time = adjust_for_past_midnight(sunset_time, sunrise_time)

    day_length = (sunset_time - sunrise_time).total_seconds() / 60
    next_day_sunrise_time = sunrise_time + timedelta(days=1)
    night_length = (next_day_sunrise_time - sunset_time).total_seconds() / 60

    day_planetary_hour_length = day_length / 12
    night_planetary_hour_length = night_length / 12
    start_planet_index = (day_of_week + 6) % 7

    planetary_hours: List[Tuple[str, str]] = []

    current_time = sunrise_time
    for i in range(12):
        planet = PLANETARY_ORDER[(start_planet_index + i) % 7]
        planetary_hours.append((current_time.strftime("%I:%M %p"), planet))
        current_time += timedelta(minutes=day_planetary_hour_length)

    current_time = sunset_time
    for i in range(12):
        planet = PLANETARY_ORDER[(start_planet_index + 12 + i) % 7]
        planetary_hours.append((current_time.strftime("%I:%M %p"), planet))
        current_time += timedelta(minutes=night_planetary_hour_length)

    return planetary_hours

def calculate_monthly_planetary_hours(
    month: int, 
    year: int, 
    sunrise_sunset_times: List[Tuple[str, str]]
) -> List[Dict]:
    """
    Calculates planetary hours for an entire month.
    
    Args:
        month: Month number (1-12)
        year: Year
        sunrise_sunset_times: List of (sunrise, sunset) time pairs
        
    Returns:
        List of dictionaries containing date and planetary hours
    """
    _, num_days = monthrange(year, month)
    all_planetary_hours = []

    for day in range(1, num_days + 1):
        if day > len(sunrise_sunset_times):
            raise IndexError(f"Missing sunrise/sunset times for day {day}.")

        day_of_week = datetime(year, month, day).weekday()
        sunrise, sunset = sunrise_sunset_times[day - 1]

        planetary_hours = calculate_planetary_hours(sunrise, sunset, day_of_week)
        all_planetary_hours.append({
            "date": datetime(year, month, day).strftime("%Y-%m-%d"),
            "planetary_hours": planetary_hours
        })

    return all_planetary_hours

@app.route('/api/calculate', methods=['POST'])
def calculate():
    data = request.get_json()
    choice = data.get('choice')

    if choice == "1":  # Single Day
        year = data.get('year')
        month = data.get('month')
        day = data.get('day')
        sunrise = data.get('sunrise')
        sunset = data.get('sunset')

        day_of_week = datetime(year, month, day).weekday()
        hours = calculate_planetary_hours(sunrise, sunset, day_of_week)
        return jsonify({"planetary_hours": hours})

    elif choice == "2":  # Week
        year = data.get('year')
        month = data.get('month')
        day = data.get('day')
        sunrise_sunset_times = data.get('sunrise_sunset_times')

        current_date = datetime(year, month, day)
        weekly_hours = calculate_monthly_planetary_hours(
            current_date.month,
            current_date.year,
            sunrise_sunset_times
        )
        return jsonify({"weekly_hours": weekly_hours})

    elif choice == "3":  # Month
        year = data.get('year')
        month = data.get('month')
        sunrise_sunset_times = data.get('sunrise_sunset_times')

        monthly_hours = calculate_monthly_planetary_hours(month, year, sunrise_sunset_times)
        return jsonify({"monthly_hours": monthly_hours})

    elif choice == "4":  # Year
        year = data.get('year')
        all_monthly_hours = []
        for month in range(1, 13):
            sunrise_sunset_times = data.get(f'sunrise_sunset_times_{month}')
            monthly_hours = calculate_monthly_planetary_hours(month, year, sunrise_sunset_times)
            all_monthly_hours.extend(monthly_hours)
        return jsonify({"yearly_hours": all_monthly_hours})
    else:
        return jsonify({"error": "Invalid choice"}), 400

if __name__ == '__main__':
    app.run(debug=True)
