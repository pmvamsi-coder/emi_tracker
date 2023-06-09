import math
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from sqlalchemy import text
from functools import wraps

def approved_only(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_approved:
            abort(403)
        return func(*args, **kwargs)
    return decorated_function

  
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


def calculate_emi(loan_amount, interest_rate, tenure):
  r = interest_rate / (12 * 100)
  n = tenure * 12
  emi = (loan_amount * r * math.pow(1 + r, n)) / (math.pow(1 + r, n) - 1)
  return round(emi, 2)


def emi_repayment_schedule_calc(loan_amount, interest_rate, tenure):
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
      'month':
      month,
      'opening_balance':
      round(outstanding_principal + principal_paid, 2),
      'emi':
      round(emi, 2),
      'principal':
      round(principal_paid, 2),
      'interest':
      round(interest, 2),
      'closing_balance':
      round(outstanding_principal, 2),
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


def generate_emi_schedule(loan_amount, interest_rate, tenure, emi_start_date):
  # Calculate the monthly interest rate
  monthly_interest_rate = interest_rate / 1200

  # Calculate the total number of months
  num_payments = tenure * 12

  # Calculate the EMI using the formula
  # EMI = [P x R x (1+R)^N]/[(1+R)^N-1]
  emi = (loan_amount * monthly_interest_rate *
         ((1 + monthly_interest_rate)**num_payments)) / ((
           (1 + monthly_interest_rate)**num_payments) - 1)
  emi = round(emi, 2)

  # Create an empty list to store the EMI schedule
  emi_schedule = []

  # Calculate the opening balance for the first month
  opening_balance = loan_amount

  # Convert the emi start date string to datetime object
  emi_date = datetime.strptime(emi_start_date, '%Y-%m-%d')
  print(emi_date)

  # Loop through each month and calculate the EMI schedule
  for i in range(num_payments):
    # Calculate the interest for the current month
    interest = round(opening_balance * monthly_interest_rate, 2)

    # Calculate the principal for the current month
    principal = round(emi - interest, 2)

    # Calculate the closing balance for the current month
    closing_balance = round(opening_balance - principal, 2)

    # Append the EMI schedule for the current month to the list
    emi_schedule.append({
      'month': i + 1,
      'opening_balance': opening_balance,
      'emi': emi,
      'principal': principal,
      'interest': interest,
      'closing_balance': closing_balance,
      'emi_date': emi_date.strftime('%Y-%m-%d')
    })

    # Update the opening balance for the next month
    opening_balance = closing_balance

    # Calculate the date for the next month
    # emi_date += timedelta(days=30)
    # Increment the month by 1
    # print(emi_date, type(emi_date))
    emi_date = emi_date + relativedelta(months=1)

  return emi_schedule


def get_emi_status(loan_name, db):
  loan_name = loan_name
  sql_query = text(f"""SELECT    
    loan_name,    
    round(SUM(CASE WHEN emi_date <= datetime('now') THEN emi ELSE 0 END),2) AS total_emi_paid,    
    round(SUM(CASE WHEN emi_date <= datetime('now') THEN interest ELSE 0 END),2) AS total_interest_paid,    
    round(SUM(CASE WHEN emi_date <= datetime('now') THEN principal ELSE 0 END),2) AS total_principal_paid,   
    round((SELECT sum(emi) FROM emi_schedule WHERE loan_name = '{loan_name}'),2) AS total_to_be_paid_in_loan_tenure,   
    round((SELECT sum(principal) FROM emi_schedule WHERE loan_name = '{loan_name}' AND emi_date > datetime('now') ORDER BY month LIMIT 1),2) AS remaining_principal,   
    round(SUM(CASE WHEN emi_date > datetime('now') THEN interest ELSE 0 END),2) AS remaining_interest,   
    round((SELECT sum(emi) FROM emi_schedule WHERE loan_name = '{loan_name}' AND emi_date > datetime('now')),2) AS outstanding_emis_sum_to_be_paid,
    (SELECT COUNT(*) FROM emi_schedule WHERE loan_name = '{loan_name}' AND emi_date > datetime('now')) AS remaining_emi_months,   
    (SELECT emi_date FROM emi_schedule WHERE loan_name = '{loan_name}' ORDER BY month DESC LIMIT 1) AS last_emi_date 
    FROM emi_schedule 
    WHERE loan_name = '{loan_name}' 
    GROUP BY loan_name; """)
  # Execute the SQL query and fetch the results
  results = db.session.execute(sql_query).fetchall()
  result_dict = dict(results[0]._mapping)
  result_dict['total_emi_paid'] = formatINR(result_dict['total_emi_paid'])
  result_dict['total_principal_paid'] = formatINR(
    result_dict['total_principal_paid'])
  result_dict['total_interest_paid'] = formatINR(
    result_dict['total_interest_paid'])
  result_dict['total_to_be_paid_in_loan_tenure'] = formatINR(
    result_dict['total_to_be_paid_in_loan_tenure'])
  result_dict['remaining_principal'] = formatINR(
    result_dict['remaining_principal'])
  result_dict['remaining_interest'] = formatINR(
    result_dict['remaining_interest'])
  result_dict['outstanding_emis_sum_to_be_paid'] = formatINR(
    result_dict['outstanding_emis_sum_to_be_paid'])
  result_dict[
    'remaining_emi_months'] = f"{result_dict['remaining_emi_months']} ({get_years_months(int(result_dict['remaining_emi_months']))})"
  return result_dict


def get_years_months(num_months):
  years = num_months // 12
  months = num_months % 12
  if years == 0:
    return f"{months} months"
  elif years == 1 and months == 0:
    return "1 year"
  elif years == 1 and months == 1:
    return "1 year, 1 month"
  elif years == 1:
    return f"1 year, {months} months"
  elif months == 0:
    return f"{years} years"
  elif months == 1:
    return f"{years} years, 1 month"
  else:
    return f"{years} years, {months} months"
