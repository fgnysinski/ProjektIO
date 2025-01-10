from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)


def load_data():
    data = pd.read_csv('cars.csv')

    data['CENA'] = data['CENA'].str.replace(' ', '', regex=False).str.replace('zł', '', regex=False).astype(int)
    data['PRZEBIEG'] = data['PRZEBIEG'].str.replace(' ', '', regex=False).str.replace('km', '', regex=False).astype(
        int)

    wojewodztwa_data = data.groupby('WOJEWODZTWO').size().to_dict()  # Liczba aut w każdym województwie
    return data, wojewodztwa_data


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/list', methods=['GET', 'POST'])
def car_list():
    data, _ = load_data()

    if request.method == 'POST':
        nazwa = request.form.get('nazwa', '')
        rok = request.form.get('rok', '')
        miasto = request.form.get('miasto', '')
        wojewodztwo = request.form.get('wojewodztwo', '')
        paliwo = request.form.get('paliwo', '')
        cena_od = request.form.get('cena_od', '')
        cena_do = request.form.get('cena_do', '')
        przebieg_od = request.form.get('przebieg_od', '')
        przebieg_do = request.form.get('przebieg_do', '')

        if nazwa:
            data = data[data['NAZWA'].str.contains(nazwa, case=False, na=False)]
        if rok:
            data = data[data['ROK'] == int(rok)]
        if miasto:
            data = data[data['MIASTO'].str.contains(miasto, case=False, na=False)]
        if wojewodztwo:
            data = data[data['WOJEWODZTWO'].str.contains(wojewodztwo, case=False, na=False)]
        if paliwo:
            data = data[data['PALIWO'].str.contains(paliwo.strip(), case=False, na=False)]

        if cena_od:
            try:
                cena_od = float(cena_od.replace(" ", "").replace("zł", ""))
                data = data[data['CENA'] >= cena_od]
            except ValueError:
                pass
        if cena_do:
            try:
                cena_do = float(cena_do.replace(" ", "").replace("zł", ""))
                data = data[data['CENA'] <= cena_do]
            except ValueError:
                pass

        if przebieg_od:
            try:
                przebieg_od = float(przebieg_od.replace(" ", ""))
                data = data[data['PRZEBIEG'] >= przebieg_od]
            except ValueError:
                pass
        if przebieg_do:
            try:
                przebieg_do = float(przebieg_do.replace(" ", ""))
                data = data[data['PRZEBIEG'] <= przebieg_do]
            except ValueError:
                pass

    cars = data.to_dict(orient='records')
    return render_template('list.html', cars=cars)


@app.route('/stats', methods=['GET', 'POST'])
def stats():
    data, _ = load_data()

    avg_price = None
    avg_mileage = None
    brand_count = {}
    year_count = {}
    city_count = {}
    province_count = {}
    fuel_count = {}

    if request.method == 'POST':
        nazwa = request.form.get('nazwa', '')
        rok = request.form.get('rok', '')
        miasto = request.form.get('miasto', '')
        wojewodztwo = request.form.get('wojewodztwo', '')
        paliwo = request.form.get('paliwo', '')

        if nazwa:
            data = data[data['NAZWA'].str.contains(nazwa, case=False, na=False)]
        if rok:
            data = data[data['ROK'] == int(rok)]
        if miasto:
            data = data[data['MIASTO'].str.contains(miasto, case=False, na=False)]
        if wojewodztwo:
            data = data[data['WOJEWODZTWO'].str.contains(wojewodztwo, case=False, na=False)]
        if paliwo:
            data = data[data['PALIWO'].str.contains(paliwo.strip(), case=False, na=False)]

        avg_price = data['CENA'].mean()
        avg_mileage = data['PRZEBIEG'].mean()

        avg_price = round(avg_price, 1)
        avg_mileage = round(avg_mileage, 1)

        brand_count = data['NAZWA'].value_counts().to_dict()
        year_count = data['ROK'].value_counts().to_dict()
        others_count = 0
        filtered_year_count = {}

        for year, count in year_count.items():
            if count < 5:
                others_count += count
            else:
                filtered_year_count[year] = count

        if others_count > 0:
            filtered_year_count['Pozostałe'] = others_count

        year_count = filtered_year_count
        city_count = data['MIASTO'].value_counts().to_dict()
        province_count = data['WOJEWODZTWO'].value_counts().to_dict()
        fuel_count = data['PALIWO'].value_counts().to_dict()


    return render_template('stats.html',
                           avg_price=avg_price,
                           avg_mileage=avg_mileage,
                           brand_count=brand_count,
                           year_count=year_count,
                           city_count=city_count,
                           province_count=province_count,
                           fuel_count=fuel_count)


@app.route('/charts', methods=['GET', 'POST'])
def charts():
    data, _ = load_data()
    data['MARKA'] = data['NAZWA'].str.split().str[0]
    avg_price_by_year = data.groupby('ROK')['CENA'].mean().to_dict()

    selected_brand = request.form.get('brand', '')
    selected_city = request.form.get('city', '')
    selected_province = request.form.get('province', '')

    if selected_brand:
        data = data[data['MARKA'].str.contains(selected_brand, case=False, na=False)]
    if selected_city:
        data = data[data['MIASTO'].str.contains(selected_city, case=False, na=False)]
    if selected_province:
        data = data[data['WOJEWODZTWO'].str.contains(selected_province, case=False, na=False)]

    avg_price = data.groupby('MARKA')['CENA'].mean().to_dict()
    avg_mileage = data.groupby('MARKA')['PRZEBIEG'].mean().to_dict()
    cars_by_year = data.groupby('ROK').size().to_dict()
    fuel_counts = data['PALIWO'].value_counts().to_dict()

    total_cars = len(data)

    chart_data = {
        "avg_price": avg_price,
        "avg_mileage": avg_mileage,
        "cars_by_year": cars_by_year,
        "fuel_counts": fuel_counts,
        "avg_price_by_year": avg_price_by_year,
        "total_cars": total_cars,
    }

    return render_template(
        'charts.html',
        chart_data=chart_data,
        selected_brand=selected_brand,
        selected_city=selected_city,
        selected_province=selected_province,
    )


@app.route('/map')
def map_view():
    data, wojewodztwa_data = load_data()
    return render_template('map.html', wojewodztwa_data=wojewodztwa_data)


if __name__ == '__main__':
    app.run(debug=True)
