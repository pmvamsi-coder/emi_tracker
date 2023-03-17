from flask import Flask, render_template, request
from utils.functions import *

app = Flask(__name__)


@app.route('/emi_calculator', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        loan_amount = request.form.get('loan_amount')
        interest_rate = request.form.get('interest_rate')
        tenure = request.form.get('tenure')

        # Check if any of the required fields are empty
        if not all([loan_amount, interest_rate, tenure]):
            error_message = "Please enter all the required fields."
            return render_template('test.html', error_message=error_message)

        # Check if loan amount is a valid float value
        try:
            loan_amount = float(loan_amount.replace(',', ''))
        except ValueError:
            error_message = "Invalid loan amount. Please enter a valid number."
            return render_template('test.html', error_message=error_message)

        # Check if interest rate is a valid float value
        try:
            interest_rate = float(interest_rate)
        except ValueError:
            error_message = "Invalid interest rate. Please enter a valid number."
            return render_template('test.html', error_message=error_message)

        # Check if tenure is a valid integer value
        try:
            tenure = int(tenure)
        except ValueError:
            error_message = "Invalid tenure. Please enter a valid integer."
            return render_template('test.html', error_message=error_message)

        # Check if the values are within acceptable ranges
        if loan_amount <= 0 or interest_rate <= 0 or tenure <= 0:
            error_message = "Invalid values. Please enter values greater than 0."
            return render_template('test.html', error_message=error_message)

        emi = formatINR(calculate_emi(loan_amount, interest_rate, tenure))
        emi_info = {
            'loan_amount': formatINR(str(loan_amount)),
            'interest_rate': interest_rate,
            'tenure': tenure,
        }
        result = generate_emi_schedule(loan_amount, interest_rate, tenure)
        emi_schedule = result['emi_schedule']
        for item in emi_schedule:
            for k, v in item.items():
                if k not in ['month']:
                    item[k] = formatINR(v)
        emi_info['total_emi'] = result['total_emi']
        emi_info['total_principal'] = result['total_principal']
        emi_info['total_interest'] = result['total_interest']
        return render_template('test.html',
                               emi=emi,
                               emi_info=emi_info,
                               emi_schedule=emi_schedule,
                               total_emi=formatINR(emi_info['total_emi']),
                               total_interest=formatINR(emi_info['total_interest']),
                               total_principal=formatINR(emi_info['total_principal']))

    return render_template('test.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
