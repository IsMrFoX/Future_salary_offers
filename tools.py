from operator import floordiv, add, mul
from terminaltables import AsciiTable


def calculate_mid_salary(from_to_salary, key_salary_from, key_salary_to, ):
    mid_salaries = []
    for salary in from_to_salary:
        if salary[key_salary_from] and salary[key_salary_to]:
            mid_salaries.append(floordiv(add(salary[key_salary_from], salary[key_salary_to]), 2))
        elif salary[key_salary_from]:
            mid_salaries.append(mul(salary[key_salary_from], 1.2))
        elif salary[key_salary_to]:
            mid_salaries.append(mul(salary[key_salary_to], 0.8))
    return mid_salaries


def reformat(dictionary):
    vacancies = []
    for language, vacancy_content in dictionary.items():
        row = [language] + [str(value) for value in vacancy_content.values()]
        vacancies.append(row)
    return vacancies


def print_table_vac_statistic(job_statistic, title):

    vacancy_table = [
                        [
                            'Язык программирования',
                            'Вакансий найдено',
                            'Вакансий обработано',
                            'Средняя зарплата'
                        ],
                    ] + job_statistic

    table_instance = AsciiTable(vacancy_table, title)
    table_instance.justify_columns[2] = 'left'
    print(table_instance.table)
