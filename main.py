import os
import requests

from dotenv import load_dotenv
from itertools import count



languages = [
    'JavaScript',
    # 'Java',
    # 'Python',
    # 'Ruby',
    # 'PHP',
    # 'C++',
    # 'C#',
    # 'C',
    # 'GO',
    # 'TypeScript'
]

def predict_rub_salary(salary_from, salary_to):
    if salary_from and salary_to:
        avg_salary = (salary_from + salary_to) / 2
    elif not salary_from:
        avg_salary = salary_to * 0.8
    else:
        avg_salary = salary_from * 1.2
    return avg_salary


def get_hh_salary():
    result = {}
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
            print(page)
            vacancies_processed = len(salaries)
            average_salary = int(sum(salaries) / vacancies_processed)

            result[language] = {
                'vacancies_found': vacancies_found,
                'vacancies_processed': vacancies_processed,
                'average_salary': average_salary
            }

    return result

#
# def get_sj_salary():
#     load_dotenv()
#     SJ_KEY = os.environ['SJ_API_KEY']
#     result = {}
#     url = 'https://api.superjob.ru/2.0/vacancies/'
#     header = {'X-Api-App-Id': SJ_KEY}
#     for language in languages:
#         salaries = []
#         for page in count(0):
#             params = {
#                 'keyword': language,
#                 'town': 'Москва',
#                 'catalogues': 48,
#                 'page': 0,
#                 'count': 100
#             }
#             response = requests.get(url, headers=header, params=params)
#             response.raise_for_status()
#
#             print(response.status_code)
#



print(get_hh_salary())
# print(get_sj_salary())
