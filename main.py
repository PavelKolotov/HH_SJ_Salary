import os
import requests

from dotenv import load_dotenv
from itertools import count
from terminaltables import AsciiTable


def main():
    languages = [
        'JavaScript',
        'Java',
        'Python',
        'Ruby',
        'PHP',
        'C++',
        'C#',
        'GO',
        'TypeScript'
    ]
    print(get_salary_statistics_hh(languages))
    print(get_salary_statistics_sj(languages))


def predict_rub_salary(salary_from, salary_to):
    if not salary_from and not salary_to:
        avg_salary = None
    elif salary_from and salary_to:
        avg_salary = (salary_from + salary_to) / 2
    elif not salary_from:
        avg_salary = salary_to * 0.8
    else:
        avg_salary = salary_from * 1.2
    return avg_salary


def preparation_for_table(salary):
    table_headers = [["Язык", "Всего вакансий", "Использовано в расчете", "Средняя зарплата"], ]
    for language, item in salary.items():
        table_statistics = [language] + list(item.values())
        table_headers.append(table_statistics)
    return table_headers


def get_salary_statistics_hh(languages):
    statistics = {}
    url = 'https://api.hh.ru/vacancies/'
    header = {'User-Agent': 'PavelKolotov (kolotovbms@mail.ru)'}
    for language in languages:
        salaries = []
        for page in count(0):
            params = {
                'text': language,
                'period': 30,
                'area': 1,
                'page': page,
            }
            response = requests.get(url, headers=header, params=params)
            response.raise_for_status()

            vacancies_found = response.json()['found']
            vacancies = response.json()['items']
            pages = response.json()['pages']

            for vacancy in vacancies:
                salary = vacancy['salary']
                if not salary or salary['currency'] != 'RUR':
                    avg_salary = None
                else:
                    avg_salary = predict_rub_salary(salary['from'], salary['to'])
                if avg_salary:
                    salaries.append(avg_salary)
            if page >= pages - 1:
                break

            vacancies_processed = len(salaries)
            average_salary = int(sum(salaries) / vacancies_processed)

            statistics[language] = {
                'vacancies_found': vacancies_found,
                'vacancies_processed': vacancies_processed,
                'average_salary': average_salary
            }

    table_hh = AsciiTable(preparation_for_table(statistics), 'HH Moscow')
    return table_hh.table


def get_salary_statistics_sj(languages):
    load_dotenv()
    sj_key = os.environ['SJ_API_KEY']
    statistics = {}
    url = 'https://api.superjob.ru/2.0/vacancies/'
    header = {'X-Api-App-Id': sj_key}
    for language in languages:
        salaries = []

        for page in count(0):
            params = {
                'keyword': f'{language}',
                'town': 'Москва',
                'catalogues': 48,
                'currency': 'rub',
                'page': 0,
                'count': 100
            }
            response = requests.get(url, headers=header, params=params)
            response.raise_for_status()

            vacancies = response.json()['objects']
            vacancies_found = response.json()['total']

            for vacancy in vacancies:
                avg_salary = predict_rub_salary(vacancy['payment_from'], vacancy['payment_to'])
                if avg_salary:
                    salaries.append(avg_salary)

            if not response.json()['more']:
                break

        vacancies_processed = len(salaries)

        if vacancies_processed:
            average_salary = int(sum(salaries) / vacancies_processed)

        if vacancies_found:
            statistics[language] = {
                                'vacancies_found': vacancies_found,
                                'vacancies_processed': vacancies_processed,
                                'average_salary': average_salary
                                }
        table_sj = AsciiTable(preparation_for_table(statistics), 'SuperJob Moscow')
    return table_sj.table


if __name__ == "__main__":
    main()
