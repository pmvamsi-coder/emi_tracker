from flask import Flask, render_template, request, url_for, redirect, flash, jsonify
from utils.functions import *
from models import *
from datetime import datetime, timedelta, date
import js

app = Flask(__name__)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = "ertwerg43t52ggrg24tdsfvvw45twrefwe424t"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///emi.db"
db.init_app(app)

with app.app_context():
  db.create_all()


@app.route("/emi_calculator", methods=["GET", "POST"])
def emi_repayment_calculator():
  if request.method == "POST":
    loan_amount = request.form.get("loan_amount")
    interest_rate = request.form.get("interest_rate")
    tenure = request.form.get("tenure")

    # Check if any of the required fields are empty
    if not all([loan_amount, interest_rate, tenure]):
      error_message = "Please enter all the required fields."
      return render_template("emi_calculator.html", error_message=error_message)

    # Check if loan amount is a valid float value
    try:
      loan_amount = float(loan_amount.replace(",", ""))
    except ValueError:
      error_message = "Invalid loan amount. Please enter a valid number."
      return render_template("emi_calculator.html", error_message=error_message)

    # Check if interest rate is a valid float value
    try:
      interest_rate = float(interest_rate)
    except ValueError:
      error_message = "Invalid interest rate. Please enter a valid number."
      return render_template("emi_calculator.html", error_message=error_message)

    # Check if tenure is a valid integer value
    try:
      tenure = int(tenure)
    except ValueError:
      error_message = "Invalid tenure. Please enter a valid integer."
      return render_template("emi_calculator.html", error_message=error_message)

    # Check if the values are within acceptable ranges
    if loan_amount <= 0 or interest_rate <= 0 or tenure <= 0:
      error_message = "Invalid values. Please enter values greater than 0."
      return render_template("emi_calculator.html", error_message=error_message)

    emi = formatINR(calculate_emi(loan_amount, interest_rate, tenure))
    emi_info = {
      "loan_amount": formatINR(str(loan_amount)),
      "interest_rate": interest_rate,
      "tenure": tenure,
    }
    result = emi_repayment_schedule_calc(loan_amount=loan_amount, interest_rate=interest_rate, tenure=tenure)
    emi_schedule = result["emi_schedule"]
    for item in emi_schedule:
      for k, v in item.items():
        if k not in ["month"]:
          item[k] = formatINR(v)
    emi_info["total_emi"] = result["total_emi"]
    emi_info["total_principal"] = result["total_principal"]
    emi_info["total_interest"] = result["total_interest"]
    return render_template(
      "emi_calculator.html",
      emi=emi,
      emi_info=emi_info,
      emi_schedule=emi_schedule,
      total_emi=formatINR(emi_info["total_emi"]),
      total_interest=formatINR(emi_info["total_interest"]),
      total_principal=formatINR(emi_info["total_principal"]),
    )

  return render_template("emi_calculator.html")


@app.route("/add_emi", methods=["GET", "POST"])
def add_emi():
  if request.method == "POST":
    loan_name = request.form["loan_name"]
    loan_amount = float(request.form["loan_amount"])
    interest_rate = float(request.form["interest_rate"])
    tenure = int(request.form["tenure"])
    emi_start_date = request.form["emi_start_date"]
    # emi_start_date = datetime.strptime(emi_start_date, '%Y-%m-%d')

    # Check if the loan name already exists in the database
    existing_loan = Emi.query.filter_by(loan_name=loan_name).first()

    if existing_loan:
      # If the loan name already exists, display an error message
      error_msg = f"A loan with the name '{loan_name}' already exists in the database..!!!"
      flash(error_msg, category='warning')
      return render_template('add_emi.html', error=error_msg)

    # emi_schedule = generate_emi_schedule(loan_amount, interest_rate, tenure)
    emi_schedule = generate_emi_schedule1(loan_amount, interest_rate, tenure,
                                         emi_start_date)

    new_emi_info = Emi(loan_name=loan_name,
                       loan_amount=loan_amount,
                       interest_rate=interest_rate,
                       loan_term=tenure,
                       start_date=datetime.strptime(emi_start_date,
                                                    "%Y-%m-%d"),
                       emi_amount=calculate_emi(loan_amount=loan_amount,
                                                interest_rate=interest_rate,
                                                tenure=tenure))
    db.session.add(new_emi_info)

    for emi in emi_schedule:
      new_emi = EmiSchedule(
        loan_name=loan_name,
        month=emi["month"],
        opening_balance=emi["opening_balance"],
        emi=emi["emi"],
        principal=emi["principal"],
        interest=emi["interest"],
        closing_balance=emi["closing_balance"],
        emi_date=datetime.strptime(emi["emi_date"], "%Y-%m-%d"),
      )
      db.session.add(new_emi)

    db.session.commit()
    flash("EMI schedule added successfully!", "success")

    return redirect(url_for("add_emi"))
    # return emi_schedule
  return render_template("add_emi.html")


@app.route("/existing_emis", methods=["GET", "POST"])
def existing_emis():
  loan_names = db.session.query(EmiSchedule.loan_name).distinct().all()

  if request.method == "POST":
    selected_loan_name = request.form["loan_name"]

    emis = EmiSchedule.query.filter_by(loan_name=selected_loan_name).all()

    emi_data = Emi.query.filter_by(loan_name=selected_loan_name).first()
    
    loan_info = {}
    if emi_data:
      loan_info = {
        'loan_name': emi_data.loan_name,
        'loan_amount': emi_data.loan_amount,
        'interest_rate': emi_data.interest_rate,
        'loan_term': emi_data.loan_term,
        'start_date': emi_data.start_date.strftime('%Y-%m-%d'),
        'emi_amount': emi_data.emi_amount,
        'paid_off': emi_data.paid_off,
        'created_date': emi_data.created_date.strftime('%Y-%m-%d')
      }
    else:
      print('No data found for loan name: my_loan')

    loan_info['loan_status'] = get_emi_status(loan_name=selected_loan_name,
                                              db=db)

    return render_template("existing_emis.html",
                           loan_names=loan_names,
                           emis=emis,
                           date=date,
                           selected_loan_name=selected_loan_name,
                           loan_info=loan_info)

    print(emi_dict)

  return render_template("existing_emis.html", loan_names=loan_names)


@app.route("/")
def home():
  return render_template("home.html")


if __name__ == "__main__":
  app.run(debug=True, host="0.0.0.0", port=5000)
