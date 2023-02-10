import requests
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
                elif salary['from'] and salary['to']:
                    avg_salary = (salary['from'] + salary['to']) / 2
                elif not salary['from']:
                    avg_salary = salary['to'] * 0.8
                else:
                    avg_salary = salary['from'] * 1.2
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


print(get_hh_salary())
