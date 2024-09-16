from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash, send_file
from pandas import pandas as pd
from groq import Groq
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

client = Groq(
    api_key="INSERT API KEY"
)

emission_factors = {
    'coal': 2.45,
    'diesel': 2.68,
    'natural_gas': 2.75,
    'electricity': 0.92, 
    'heat': {
        'natural_gas': 50.3,
        'coal': 94.6,
        'electricity': 92.0 
    },
    'explosives': 1.0
}

def calculate_emissions(df):
    total_emissions = 0

    for index, row in df.iterrows():
        category = row[0]
        input_data = row[4]
        amount = row[3]

        try:
            amount = float(amount)
        except ValueError:
            print(f"Non-numeric amount found in row {index}: {amount}")
            continue

        # Fuel Combustion emissions
        if pd.notna(input_data) and 'Fuel Combustion' in category:
            fuel_type = row[4].lower()
            if fuel_type in emission_factors:
                total_emissions += amount * emission_factors[fuel_type]
            else:
                print(f"Fuel type {fuel_type} not found in emission factors at row {index}")

        # Coal Extraction emissions
        elif pd.notna(input_data) and 'Coal Extraction' in category:
            energy_type = row[4].lower()
            if energy_type in emission_factors:
                total_emissions += amount * emission_factors[energy_type]
            else:
                print(f"Energy type {energy_type} not found in emission factors at row {index}")

        # Blasting Operation emissions
        elif pd.notna(input_data) and 'Blasting Operation' in category:
            total_emissions += amount * emission_factors['explosives']

        # Ventilation emissions
        elif pd.notna(input_data) and 'Ventilation' in category:
            total_emissions += amount * emission_factors['electricity']

        # Onsite Power Generation emissions
        elif pd.notna(input_data) and 'Onsite Power Generation' in category:
            fuel_type = row[4].lower()
            if fuel_type in emission_factors:
                total_emissions += amount * emission_factors[fuel_type]
            else:
                print(f"Fuel type {fuel_type} not found in emission factors at row {index}")

        # Purchased Energy emissions
        elif pd.notna(input_data) and 'Purchased Energy' in category:
            total_emissions += amount * emission_factors['electricity']

        # Purchased Heat emissions
        elif pd.notna(input_data) and 'Purchased Heat' in category:
            fuel_type = row[4].lower()
            if fuel_type in emission_factors['heat']:
                total_emissions += amount * emission_factors['heat'][fuel_type]
            else:
                print(f"Fuel type {fuel_type} not found in heat emission factors at row {index}")

        # Coal Transportation emissions
        elif pd.notna(input_data) and 'Coal Transportation' in category:
            fuel_type = row[4].lower()
            if fuel_type in emission_factors:
                total_emissions += amount * emission_factors[fuel_type]
            else:
                print(f"Fuel type {fuel_type} not found in emission factors at row {index}")

        # Supply Chain Activities emissions
        elif pd.notna(input_data) and 'Supply Chain Activities' in category:
            energy_type = row[4].lower()
            if energy_type in emission_factors:
                total_emissions += amount * emission_factors[energy_type]
            else:
                print(f"Energy type {energy_type} not found in emission factors at row {index}")

        # Waste Disposal emissions
        elif pd.notna(input_data) and 'Waste Disposal' in category:
            energy_type = row[4].lower()
            if energy_type in emission_factors:
                total_emissions += amount * emission_factors[energy_type]
            else:
                print(f"Energy type {energy_type} not found in emission factors at row {index}")

    return total_emissions

def get_groq_suggestions(df,total_emissions):
    
    fuel_combustion = []
    electricity_consumption = []
    coal_extraction_energy = []
    transportation = []
    purchased_heat = []

    for index, row in df.iterrows():
        category = row[0]
        fuel_type = row[4]
        amount = row[3]
        
        try:
            amount = float(amount)
        except ValueError:
            continue

        if 'Fuel Combustion' in category:
            fuel_combustion.append(f"{fuel_type}: {amount} units")
        elif 'Ventilation' in category or 'Electricity' in category:
            electricity_consumption.append(f"{fuel_type}: {amount} kWh")
        elif 'Coal Extraction' in category:
            coal_extraction_energy.append(f"{fuel_type}: {amount} units")
        elif 'Coal Transportation' in category:
            transportation.append(f"{fuel_type}: {amount} units")
        elif 'Purchased Heat' in category:
            purchased_heat.append(f"{fuel_type}: {amount} GJ")

    messages = [
        {"role":"user",
        "content":f"""Our coal mine is actively looking to reduce its carbon emissions and improve energy efficiency. Here are the specific details of our energy usage and carbon footprint:
        Fuel combustion (diesel, natural gas): {'; '.join(fuel_combustion)}
        Electricity consumption (ventilation, power generation, etc.): {'; '.join(electricity_consumption)}
        Coal extraction energy (electricity, diesel):{'; '.join(coal_extraction_energy)}
        Transportation (fuel used for moving coal): {'; '.join(transportation)}
        Heat and steam purchased: {'; '.join(purchased_heat)}
        We are particularly interested in:
        - Energy-efficient technologies or practices for mining operations
        - Ways to optimize fuel use in power generation and transportation
        - Alternatives to diesel and natural gas, including renewable energy options
        - Ideas for minimizing emissions from waste disposal and supply chain activities
        Please take into account that we need feasible solutions we can implement in the short and long term, and suggestions for specific technologies or practices would be helpful.Also refrence the amount and type of fuel emitted.Number of suggestions should be 4 under 75 words. Each point should start in a new line"""
        }
    ]
    
    chat_completion = client.chat.completions.create(
        messages=messages,
        model="llama3-8b-8192",
    )
    
    suggestions = chat_completion.choices[0].message.content
    suggestions= suggestions.replace('*','')
    points = suggestions.split('. ')
    suggestions = '\n'.join(points)
    return suggestions


USERNAME = "admin"
PASSWORD = "password123"

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(f"Attempting login with username: {username} and password: {password}")
        if username == USERNAME and password == PASSWORD:
            session['user_id'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/index')
def index():
    if 'user_id' not in session:
        flash('You need to log in first.', 'warning')
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/Inputpage', methods=['GET', 'POST'])
def Input():
    
    return render_template('Inputpage.html')

@app.route('/upload', methods=['GET', 'POST'] )
def upload():
    if 'file' not in request.files:
        return "No file uploaded"
    
    file = request.files['file']
    if file.filename == '':
        return "No selected file"
    
    df = pd.read_excel(file)

    total_emissions = calculate_emissions(df)

    suggestions=get_groq_suggestions(df,total_emissions)
    
    return render_template("result.html", data = total_emissions, suggestions=suggestions)

@app.route('/download-excel')
def download_excel():
    path_to_file = "static/emissions_data_template.xlsx"
    return send_file(path_to_file, as_attachment=True)  

    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)