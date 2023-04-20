from __future__ import print_function
import requests
from operator import *
from itertools import count
from terminaltables import AsciiTable
import os
from dotenv import load_dotenv


def get_hh_vacancies(lang):
    all_files = []

    for page in count(0):
        page_response = requests.get('https://api.hh.ru/vacancies', params={
            'text': f'Разработчик {lang}',
            'period': 30,
            'areas': {'id': '1', 'name': 'Москва'},
            'currency': 'RUR',
            'per_page': 100,
            'page': page
        })
        page_response.raise_for_status()
        page_payload = page_response.json()
        if page >= page_payload['pages'] - 1:
            break
        all_files.append(page_payload)
    return all_files


def get_hh_found_amount_average(list_files):
    mid_salary = []
    from_to_salary = [items['salary'] for files in list_files for items in files['items']
                      if items['salary'] and items['salary']['currency'] == 'RUR']
    for item in from_to_salary:
        if item['from'] and item['to']:
            mid_salary.append(floordiv(add(item['from'], item['to']), 2))
        elif item['to'] is None:
            mid_salary.append(mul(item['from'], 1.2))
        elif item['from'] is None:
            mid_salary.append(mul(item['to'], 0.8))
    return list_files[0]['found'], len(mid_salary), int(sum(mid_salary))//len(mid_salary) if len(mid_salary) != 0 else 0


def get_sj_vacancies(lang, key):
    all_files = []
    header = {
        'X-Api-App-Id': key,
    }
    for page in count(0):
        params = {
            'keyword': f'Разработчик {lang}',
            'town': 'Москва',
            'page': page,
            'count': 50,
            'currency': 'rub'
        }
        page_response = requests.get('https://api.superjob.ru/2.0/vacancies/', headers=header, params=params)
        page_response.raise_for_status()
        page_payload = page_response.json()

        if page_payload['more']:
            all_files.append(page_payload)
        if page >= page_payload['total'] - 1:
            break

    return all_files


def get_sj_found_amount_average(list_files):
    mid_salary = []
    sj_salary = []
    amount = 0
    for files in list_files:
        amount = files['total']
        for items in files['objects']:
            if items['payment_from'] not in [False, None] and items['payment_to'] not in [False, None]:
                sj_salary.append({'payment_from': items['payment_from'], 'payment_to': items['payment_to']})
            elif items['payment_to'] is None and items['payment_from'] != 0:
                sj_salary.append({'payment_from': items['payment_from'], 'payment_to': items['payment_to']})
            elif items['payment_from'] is None and items['payment_to'] != 0:
                sj_salary.append({'payment_from': items['payment_from'], 'payment_to': items['payment_to']})

    for item in sj_salary:
        if item['payment_from'] and item['payment_to']:
            mid_salary.append(floordiv(add(item['payment_from'], item['payment_to']), 2))
        elif item['payment_to'] is None:
            mid_salary.append(mul(item['payment_from'], 1.2))
        else:
            mid_salary.append(mul(item['payment_to'], 0.8))

    return amount, len(mid_salary), int(sum(mid_salary)) // len(mid_salary) if len(mid_salary) != 0 else 0


def reformat_dict_to_list(dictionary):
    vacancies = []
    for language, values in dictionary.items():
        row = [language] + [str(value) for value in values.values()]
        vacancies.append(row)
    return vacancies


def main():
    load_dotenv()
    secret_key = os.environ['SJ_SECRET_KEY']
    hh_salary_statistics = {}
    sj_salary_statistics = {}
    for lang in ['python', 'java', 'c++', 'javascript', 'c#', 'php']:
        hh_files = get_hh_vacancies(lang)
        sj_files = get_sj_vacancies(lang, secret_key)
        hh_amount_vacancies, hh_vacancies_processed, hh_average_salary = get_hh_found_amount_average(hh_files)
        sj_amount_vacancies, sj_vacancies_processed, sj_average_salary = get_sj_found_amount_average(sj_files)

        sj_salary_statistics[lang] = sj_salary_statistics.get(lang, {
            "vacancies_found": sj_amount_vacancies,
            "vacancies_processed": sj_vacancies_processed,
            "average_salary": sj_average_salary

        }
                                                            )
        hh_salary_statistics[lang] = hh_salary_statistics.get(lang, {
            "vacancies_found": hh_amount_vacancies,
            "vacancies_processed": hh_vacancies_processed,
            "average_salary": hh_average_salary

        }
                                                            )

    data_vacancies = [reformat_dict_to_list(hh_salary_statistics), reformat_dict_to_list(sj_salary_statistics)]

    for i in range(len(data_vacancies)):
        TABLE_DATA = [
                         ['Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата'],
                     ] + data_vacancies[i]

        title = ['HeadHunter Mockow', 'SuperJob Moskow'][i]
        table_instance = AsciiTable(TABLE_DATA, title)
        table_instance.justify_columns[2] = 'left'
        print(table_instance.table)


if __name__ == "__main__":
    main()
