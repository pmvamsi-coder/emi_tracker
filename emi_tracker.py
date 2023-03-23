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
def index():
  if request.method == "POST":
    loan_amount = request.form.get("loan_amount")
    interest_rate = request.form.get("interest_rate")
    tenure = request.form.get("tenure")

    # Check if any of the required fields are empty
    if not all([loan_amount, interest_rate, tenure]):
      error_message = "Please enter all the required fields."
      return render_template("index.html", error_message=error_message)

    # Check if loan amount is a valid float value
    try:
      loan_amount = float(loan_amount.replace(",", ""))
    except ValueError:
      error_message = "Invalid loan amount. Please enter a valid number."
      return render_template("index.html", error_message=error_message)

    # Check if interest rate is a valid float value
    try:
      interest_rate = float(interest_rate)
    except ValueError:
      error_message = "Invalid interest rate. Please enter a valid number."
      return render_template("index.html", error_message=error_message)

    # Check if tenure is a valid integer value
    try:
      tenure = int(tenure)
    except ValueError:
      error_message = "Invalid tenure. Please enter a valid integer."
      return render_template("index.html", error_message=error_message)

    # Check if the values are within acceptable ranges
    if loan_amount <= 0 or interest_rate <= 0 or tenure <= 0:
      error_message = "Invalid values. Please enter values greater than 0."
      return render_template("index.html", error_message=error_message)

    emi = formatINR(calculate_emi(loan_amount, interest_rate, tenure))
    emi_info = {
      "loan_amount": formatINR(str(loan_amount)),
      "interest_rate": interest_rate,
      "tenure": tenure,
    }
    result = generate_emi_schedule(loan_amount, interest_rate, tenure)
    emi_schedule = result["emi_schedule"]
    for item in emi_schedule:
      for k, v in item.items():
        if k not in ["month"]:
          item[k] = formatINR(v)
    emi_info["total_emi"] = result["total_emi"]
    emi_info["total_principal"] = result["total_principal"]
    emi_info["total_interest"] = result["total_interest"]
    return render_template(
      "index.html",
      emi=emi,
      emi_info=emi_info,
      emi_schedule=emi_schedule,
      total_emi=formatINR(emi_info["total_emi"]),
      total_interest=formatINR(emi_info["total_interest"]),
      total_principal=formatINR(emi_info["total_principal"]),
    )

  return render_template("index.html")

  # @app.route('/add_emi', methods=['POST'])
  # def add_emi():
  #     loan_name = request.form['loan_name']
  #     loan_amount = request.form['loan_amount']
  #     interest_rate = request.form['interest_rate']
  #     loan_term = request.form['loan_term']
  #     start_date = request.form['start_date']
  #     emi_amount = calculate_emi(loan_amount, interest_rate, loan_term)

  #     emi = Emi(loan_name=loan_name, loan_amount=loan_amount, interest_rate=interest_rate,
  #               loan_term=loan_term, start_date=start_date, emi_amount=emi_amount)

  #     db.session.add(emi)
  #     db.session.commit()
  #   # Insert data into the database
  #     emi_data = EmiSchedule(
  #             month=month,
  #             opening_balance=round(outstanding_principal + principal_paid, 2),
  #             emi=round(emi, 2),
  #             principal=round(principal_paid, 2),
  #             interest=round(interest, 2),
  #             closing_balance=round(outstanding_principal, 2),
  #         )
  #     db.session.add(emi_data)
  #     db.session.commit()

  return "EMI information added successfully!"


@app.route("/emi", methods=["GET", "POST"])
def emi():
  if request.method == "POST":
    loan_name = request.form["loan_name"]
    loan_amount = float(request.form["loan_amount"])
    interest_rate = float(request.form["interest_rate"])
    tenure = int(request.form["tenure"])
    emi_start_date = request.form["emi_start_date"]
    # emi_start_date = datetime.strptime(emi_start_date, '%Y-%m-%d')

    # emi_schedule = generate_emi_schedule(loan_amount, interest_rate, tenure)
    emi_schedule = generate_emi_schedule1(loan_amount, interest_rate, tenure,
                                          emi_start_date)

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

    return redirect(url_for("emi"))
    # return emi_schedule
  return render_template("emi.html")


# @app.route('/existing_emis')
# def existing_emis():
#     # Get the distinct loan names from the EmiSchedule table
#     loan_names = db.session.query(EmiSchedule.loan_name).distinct().all()

#     # Render the HTML page with the dropdown menu
#     return render_template('existing_emis.html', loan_names=loan_names)

# @app.route('/existing_emis/result', methods=['POST'])
# def existing_emis_result():
#     # Get the selected loan name from the dropdown menu
#     loan_name = request.form['loan_name']

#     # Get the data from the EmiSchedule table based on the selected loan name
#     emis = EmiSchedule.query.filter_by(loan_name=loan_name).all()

#     # Render the HTML page with the data in a table
#     return render_template('existing_emis_result.html', emis=emis)

# from datetime import datetime, date
# from flask import render_template, request


@app.route("/existing_emis", methods=["GET", "POST"])
def existing_emis():
  # loan_names = EmiSchedule.query.distinct(EmiSchedule.loan_name).order_by(EmiSchedule.loan_name).all()
  loan_names = db.session.query(EmiSchedule.loan_name).distinct().all()

  if request.method == "POST":
    selected_loan_name = request.form["loan_name"]
    emis = EmiSchedule.query.filter_by(loan_name=selected_loan_name).all()
    # return render_template('existing_emis_result.html', emis=emis, date=date)
    return render_template("existing_emis.html",
                           loan_names=loan_names,
                           emis=emis,
                           date=date,
                           selected_loan_name=selected_loan_name,
                           loan_details=get_emi_status(
                             loan_name=selected_loan_name, db=db))

  return render_template("existing_emis.html", loan_names=loan_names)


@app.route("/")
def home():
  return render_template("home.html")


if __name__ == "__main__":
  app.run(debug=True, host="0.0.0.0", port=5000)
