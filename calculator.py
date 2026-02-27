import json
import sys
from datetime import datetime

def load_salaries(country='UK'):
    """Load salary data for specified country"""
    filename = f'data/salaries_{country.lower()}.json'
    with open(filename, 'r') as f:
        return json.load(f)

def calculate_meeting_cost(attendees, duration_hours, country='UK', overheads=None):
    """
    Calculate total meeting cost
    
    attendees: list of tuples [(role, count), ...]
    duration_hours: float
    country: 'UK' or 'USA'
    overheads: dict of additional costs {'room': 50, 'travel': 100, ...}
    """
    data = load_salaries(country)
    currency = data['currency']
    
    salary_cost = 0
    breakdown = []
    
    for role, count in attendees:
        if role in data['roles']:
            hourly = data['roles'][role]['hourly_rate']
            cost = hourly * duration_hours * count
            salary_cost += cost
            breakdown.append({
                'role': role,
                'count': count,
                'hourly_rate': hourly,
                'duration': duration_hours,
                'cost': round(cost, 2)
            })
    
    overhead_cost = sum(overheads.values()) if overheads else 0
    total_cost = salary_cost + overhead_cost
    
    return {
        'currency': currency,
        'salary_cost': round(salary_cost, 2),
        'overhead_cost': round(overhead_cost, 2),
        'total_cost': round(total_cost, 2),
        'duration_hours': duration_hours,
        'attendee_count': sum(count for _, count in attendees),
        'breakdown': breakdown,
        'overheads': overheads or {}
    }

def format_currency(amount, currency='GBP'):
    """Format currency with symbol"""
    symbols = {'GBP': '£', 'USD': '$'}
    symbol = symbols.get(currency, '£')
    return f"{symbol}{amount:,.2f}"

def print_report(result):
    """Print formatted meeting cost report"""
    print("=" * 50)
    print("MEETING COST REPORT")
    print("=" * 50)
    print(f"Duration: {result['duration_hours']} hours")
    print(f"Attendees: {result['attendee_count']}")
    print(f"Currency: {result['currency']}")
    print("-" * 50)
    print("SALARY COSTS:")
    for item in result['breakdown']:
        print(f"  {item['role']} x{item['count']}: "
              f"{format_currency(item['cost'], result['currency'])} "
              f"(@ {format_currency(item['hourly_rate'], result['currency'])}/hr)")
    print(f"\n  Subtotal: {format_currency(result['salary_cost'], result['currency'])}")
    
    if result['overheads']:
        print("\nOVERHEADS:")
        for name, cost in result['overheads'].items():
            print(f"  {name.capitalize()}: {format_currency(cost, result['currency'])}")
        print(f"\n  Subtotal: {format_currency(result['overhead_cost'], result['currency'])}")
    
    print("=" * 50)
    print(f"TOTAL COST: {format_currency(result['total_cost'], result['currency'])}")
    print(f"COST PER MINUTE: {format_currency(result['total_cost'] / (result['duration_hours'] * 60), result['currency'])}")
    print("=" * 50)

if __name__ == '__main__':
    # Example: Project kickoff meeting
    attendees = [
        ('Project Manager', 1),
        ('Senior Project Manager', 1),
        ('Product Manager', 1),
        ('CTO', 1),
        ('Business Analyst', 2),
        ('Developer', 3)
    ]
    
    overheads = {
        'room': 100,
        'catering': 75,
        'tech': 25
    }
    
    # UK example
    result_uk = calculate_meeting_cost(attendees, 2, 'UK', overheads)
    print_report(result_uk)
    
    print("\n")
    
    # USA example
    result_usa = calculate_meeting_cost(attendees, 2, 'USA', overheads)
    print_report(result_usa)
