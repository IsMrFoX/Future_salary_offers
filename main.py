from __future__ import print_function
import requests
from itertools import count
import os
from dotenv import load_dotenv
from download_tools import calculate_mid_salary
from download_tools import get_salary_statistic
from download_tools import reformat
from download_tools import print_table_vac_statistic


def get_hh_vacancies(lang):
    hh_vacancies = []
    last_days = 30
    output_to_page = 100
    for page in count(0):
        page_response = requests.get('https://api.hh.ru/vacancies', params={
            'text': f'Разработчик {lang}',
            'period': last_days,
            'areas': {'id': '1', 'name': 'Москва'},
            'currency': 'RUR',
            'per_page': output_to_page,
            'page': page
        }
                                     )
        page_response.raise_for_status()
        page_payload = page_response.json()
        if page >= page_payload['pages'] - 1:
            break
        hh_vacancies.append(page_payload)
    return hh_vacancies


def get_hh_found_amount_average(all_vacancies):
    from_to_salary = [vacancies_content['salary'] for vacancies in all_vacancies for vacancies_content in vacancies['items']
                      if items['salary'] and items['salary']['currency'] == 'RUR']
    amount = vacancies[0]['found']
    mid_salaries = calculate_mid_salary(from_to_salary, 'from', 'to')

    return amount, len(mid_salaries), int(sum(mid_salaries)) // len(mid_salaries) \
        if len(mid_salaries) else 0


def get_sj_vacancies(lang, key):
    sj_vacancies = []
    output_to_page = 50
    header = {
        'X-Api-App-Id': key,
    }
    for page in count(0):
        params = {
            'keyword': f'Разработчик {lang}',
            'town': 'Москва',
            'page': page,
            'count': output_to_page,
            'currency': 'rub'
        }
        page_response = requests.get(
            'https://api.superjob.ru/2.0/vacancies/',
            headers=header,
            params=params
        )
        page_response.raise_for_status()
        page_payload = page_response.json()

        if page_payload['more']:
            sj_vacancies.append(page_payload)
        if page >= page_payload['total'] - 1:
            break
    return sj_vacancies


def get_sj_found_amount_average(sj_vacancies):
    sj_salaries = []
    amount = 0
    for vacancies in sj_vacancies:
        amount = vacancies['total']
        for vacancy_content in vacancies['objects']:
            if vacancy_content['payment_from'] and vacancy_content['payment_to']:
                sj_salaries.append({
                    'payment_from': vacancy_content['payment_from'],
                    'payment_to': vacancy_content['payment_to']
                }
                )
            elif vacancy_content['payment_from']:
                sj_salaries.append({
                    'payment_from': vacancy_content['payment_from'],
                    'payment_to': vacancy_content['payment_to']
                }
                )
            elif vacancy_content['payment_to']:
                sj_salaries.append({
                    'payment_from': vacancy_content['payment_from'],
                    'payment_to': vacancy_content['payment_to']
                }
                )
    mid_salaries = calculate_mid_salary(sj_salaries, 'payment_from', 'payment_to')

    return amount, len(mid_salaries), int(sum(mid_salaries)) // len(mid_salaries) if len(mid_salaries) else 0


def main():
    load_dotenv()
    secret_key = os.environ['SJ_SECRET_KEY']
    hh_salary_statistics = {}
    sj_salary_statistics = {}
    for lang in ['python', 'java', 'c++', 'javascript', 'c#', 'php']:
        hh_vacancies = get_hh_vacancies(lang)
        sj_vacancies = get_sj_vacancies(lang, secret_key)
        hh_amount_vacancies, hh_vacancies_processed, hh_average_salary = get_hh_found_amount_average(hh_vacancies)
        sj_amount_vacancies, sj_vacancies_processed, sj_average_salary = get_sj_found_amount_average(sj_vacancies)

        sj_salary_statistics[lang] = get_salary_statistic(
            sj_amount_vacancies,
            sj_vacancies_processed,
            sj_average_salary
        )
        hh_salary_statistics[lang] = get_salary_statistic(
            hh_amount_vacancies,
            hh_vacancies_processed,
            hh_average_salary
        )

    hh_sj_vacancies = [reformat(hh_salary_statistics), reformat(sj_salary_statistics)]
    titles = ['HeadHunter Moskow', 'SuperJob Moskow']

    for job_statistic, title in zip(hh_sj_vacancies, titles):
        print_table_vac_statistic(job_statistic, title)


if __name__ == "__main__":
    main()
