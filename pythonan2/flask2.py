from flask import Flask, render_template, request
import requests
import xml.etree.ElementTree as ET

app = Flask(__name__)
last_results = []  # Lista pentru stocarea ultimelor trei rezultate
app.static_folder = 'static'

def get_exchange_rates():
    url = 'https://www.bnm.md/en/official_exchange_rates?get_xml=1&date=21.12.2023'
    response = requests.get(url)
    
    if response.status_code == 200:
        root = ET.fromstring(response.content)
        exchange_rates = {}
        
        # Procesează XML-ul pentru a obține ratele valutare
        for cube in root.findall('.//Valute'):
            currency = cube.find('CharCode').text
            value = cube.find('Value').text
            exchange_rates[currency] = value
            
        print("Datele obținute de la BNM sunt:", exchange_rates)  
        return exchange_rates
    else:
        print("Eroare în obținerea datelor de la BNM!")
        return None


@app.route('/', methods=['GET', 'POST'])
def index():
    global last_results

    currencies = get_exchange_rates()
    alert_message = None
    from_currency = request.form.get('from_currency', 'RON')  # Valorile alese pentru monedele de plecare
    to_currency = request.form.get('to_currency', 'USD')  # Valorile alese pentru monedele de destinație

    if request.method == 'POST':
        if 'convert_submit' in request.form:
            return convert(currencies)
        
        if 'calc_submit' in request.form:
            result = calculate()
            last_results.append(result)
            if len(last_results) > 3:
                last_results = last_results[-3:]

            return render_template('index.html', currencies=currencies, result=result, last_results=last_results)

        if 'alert_submit' in request.form:
            alert_message = check_alert(currencies)

    return render_template('index.html', currencies=currencies, last_results=last_results, alert_message=alert_message, from_currency=from_currency, to_currency=to_currency)

def convert(currencies):
    amount = float(request.form['amount'])
    from_currency = request.form['from_currency'].upper()
    to_currency = request.form['to_currency'].upper()

    if currencies:
        if from_currency in currencies and to_currency in currencies:
            if from_currency == to_currency:
                return "Introduceți valute diferite pentru conversie!"
            
            exchange_rate_from = float(currencies[from_currency].replace(',', '.'))
            exchange_rate_to = float(currencies[to_currency].replace(',', '.'))
            
            converted_amount = amount * (exchange_rate_from / exchange_rate_to)
            
            return render_template('index.html', converted_amount=converted_amount, from_currency=from_currency, to_currency=to_currency, amount=amount, currencies=currencies)
        else:
            return "Valută nevalidă!"
    else:
        return "Eroare în obținerea cursurilor valutare de la BNM!"

def check_alert(currencies):
    from_currency = request.form['from_currency'].upper()
    to_currency = request.form['to_currency'].upper()

    if currencies:
        if from_currency in currencies and to_currency in currencies:
            exchange_rate_from = float(currencies[from_currency].replace(',', '.'))
            exchange_rate_to = float(currencies[to_currency].replace(',', '.'))

            converted_amount = exchange_rate_from / exchange_rate_to
            alert_value = float(request.form['alert_value'])

            if converted_amount > alert_value:
                return "Te vom anunța când va apărea o rată mai favorabilă!"
            else:
                return "Rată favorabilă!"
        else:
            return "Valută nevalidă!"
    else:
        return "Eroare în obținerea cursurilor valutare de la BNM!"

def calculate():
    num1 = float(request.form['num1'])
    num2 = float(request.form['num2'])
    operator = request.form['operator']

    if operator == '+':
        result = num1 + num2
    elif operator == '-':
        result = num1 - num2
    elif operator == '*':
        result = num1 * num2
    elif operator == '/':
        if num2 != 0:
            result = num1 / num2
        else:
            return "Împărțirea la zero nu este permisă!"
    elif operator == '%':
        result = (num1 * num2) / 100
    else:
        return "Operator nevalid!"

    return result

if __name__ == '__main__':
    app.run(debug=True)