from flask import Flask, render_template, request
from utils.functions import *
from models import *

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# https://flask-sqlalchemy.palletsprojects.com/en/3.0.x/config/#connection-url-format
# 3 slashes relative path( created in the same path). 4 slashes - needs to give absolute path
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///emi.db'
db.init_app(app)

with app.app_context():
    db.create_all()


@app.route('/emi_calculator', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        loan_amount = request.form.get('loan_amount')
        interest_rate = request.form.get('interest_rate')
        tenure = request.form.get('tenure')

        # Check if any of the required fields are empty
        if not all([loan_amount, interest_rate, tenure]):
            error_message = "Please enter all the required fields."
            return render_template('index.html', error_message=error_message)

        # Check if loan amount is a valid float value
        try:
            loan_amount = float(loan_amount.replace(',', ''))
        except ValueError:
            error_message = "Invalid loan amount. Please enter a valid number."
            return render_template('index.html', error_message=error_message)

        # Check if interest rate is a valid float value
        try:
            interest_rate = float(interest_rate)
        except ValueError:
            error_message = "Invalid interest rate. Please enter a valid number."
            return render_template('index.html', error_message=error_message)

        # Check if tenure is a valid integer value
        try:
            tenure = int(tenure)
        except ValueError:
            error_message = "Invalid tenure. Please enter a valid integer."
            return render_template('index.html', error_message=error_message)

        # Check if the values are within acceptable ranges
        if loan_amount <= 0 or interest_rate <= 0 or tenure <= 0:
            error_message = "Invalid values. Please enter values greater than 0."
            return render_template('index.html', error_message=error_message)

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
        return render_template('index.html',
                               emi=emi,
                               emi_info=emi_info,
                               emi_schedule=emi_schedule,
                               total_emi=formatINR(emi_info['total_emi']),
                               total_interest=formatINR(emi_info['total_interest']),
                               total_principal=formatINR(emi_info['total_principal']))

    return render_template('index.html')


@app.route('/add_emi', methods=['POST'])
def add_emi():
    loan_name = request.form['loan_name']
    loan_amount = request.form['loan_amount']
    interest_rate = request.form['interest_rate']
    loan_term = request.form['loan_term']
    start_date = request.form['start_date']
    emi_amount = calculate_emi(loan_amount, interest_rate, loan_term)

    emi = Emi(loan_name=loan_name, loan_amount=loan_amount, interest_rate=interest_rate,
              loan_term=loan_term, start_date=start_date, emi_amount=emi_amount)

    db.session.add(emi)
    db.session.commit()

    return "EMI information added successfully!"


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
