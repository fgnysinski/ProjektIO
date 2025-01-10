import requests
from bs4 import BeautifulSoup
import csv
from unidecode import unidecode

base_url = 'https://www.otomoto.pl/osobowe?page='
num_pages = 200

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

with open('cars.csv', 'w', newline='', encoding='utf-8') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(['NAZWA', 'CENA', 'PRZEBIEG', 'ROK', 'MIASTO', 'WOJEWODZTWO', 'PALIWO'])

    for page in range(1, num_pages + 1):
        url = '{}{}'.format(base_url, page)
        response = requests.get(url, headers=headers)

        response.encoding = 'utf-8'

        soup = BeautifulSoup(response.text, 'html.parser')

        for link in soup.find_all('a', href=True):
            if 'finansowanie' in link['href']:
                link.decompose()

        cars = soup.find_all('section', {'class': lambda class_name: class_name and 'ooa' in class_name})

        if not cars:
            print(f"Brak danych dla strony {url}. Sprawdzanie struktury HTML.")
            continue

        for car in cars:
            nazwa_element = car.find('a', {'href': True})
            cena_element = car.find('h3', {'class': 'e6r213i1 ooa-1n2paoq er34gjf0'})
            przebieg_element = car.find('dd', {'data-parameter': 'mileage'})
            paliwo_element = car.find('dd', {'data-parameter': 'fuel_type'})
            rok_element = car.find('dd', {'data-parameter': 'year'})
            miasto_element = car.find('p', {'class': 'ooa-gmxnzj'})

            if not (
                    nazwa_element and cena_element and przebieg_element and paliwo_element and rok_element and miasto_element):
                continue

            nazwa = unidecode(nazwa_element.text.strip()) if nazwa_element else None
            cena = unidecode(cena_element.text.strip()) if cena_element else None
            przebieg = unidecode(przebieg_element.text.strip()) if przebieg_element else None
            paliwo = unidecode(paliwo_element.text.strip()) if paliwo_element else None
            rok = unidecode(rok_element.text.strip()) if rok_element else None
            miasto = unidecode(miasto_element.text.strip()) if miasto_element else None

            if not nazwa:
                continue

            if miasto:
                if '(' in miasto and ')' in miasto:
                    miasto_czesc, wojewodztwo_czesc = miasto.split('(', 1)
                    miasto = miasto_czesc.strip()
                    wojewodztwo = wojewodztwo_czesc.replace(')', '').strip()

            csv_writer.writerow([nazwa, cena, przebieg, rok, miasto, wojewodztwo, paliwo])
