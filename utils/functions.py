import math


def formatINR(number):
    """Formats the given number as an Indian Rupee amount.
    Args:
        number (str or int): The number to format as an Indian Rupee amount.
    Returns:
        str: The Indian Rupee amount as a string.
    """
    s, *d = str(number).partition(".")
    r = ",".join([s[x - 2:x] for x in range(-3, -len(s), -2)][::-1] + [s[-3:]])
    return "".join([r] + d)


def generate_emi_schedule(loan_amount, interest_rate, tenure):
    emi_schedule = []
    outstanding_principal = loan_amount
    rate = interest_rate / 1200.0  # monthly interest rate
    emi = calculate_emi(loan_amount, interest_rate, tenure)
    total_interest_paid = 0
    total_principal_paid = 0

    for month in range(1, tenure * 12 + 1):
        interest = outstanding_principal * rate
        principal_paid = emi - interest
        outstanding_principal -= principal_paid

        if outstanding_principal < 0:
            outstanding_principal = 0

        total_interest_paid += interest
        total_principal_paid += principal_paid

        emi_schedule.append({
            'month': month,
            'opening_balance': round(outstanding_principal + principal_paid, 2),
            'emi': round(emi, 2),
            'principal': round(principal_paid, 2),
            'interest': round(interest, 2),
            'closing_balance': round(outstanding_principal, 2),
        })
    total_emi = round(emi_schedule[0]['emi'] * len(emi_schedule), 2)
    total_principal = round(total_principal_paid, 2)
    total_interest = round(total_interest_paid, 2)

    return {
        'emi_schedule': emi_schedule,
        'total_emi': total_emi,
        'total_principal': total_principal,
        'total_interest': total_interest,
    }


def calculate_emi(loan_amount, interest_rate, tenure):
    r = interest_rate / (12 * 100)
    n = tenure * 12
    emi = (loan_amount * r * math.pow(1 + r, n)) / (math.pow(1 + r, n) - 1)
    return round(emi, 2)
