from dotenv import load_dotenv
import requests
import os


load_dotenv(r"")
TOKEN = os.getenv("TOKEN")
ACCOUNT_ID = os.getenv("ACCOUNTID")


class Harvest:
    # Список юзеров, которых не надо учитывать.
    except_list = []

    url_address = "https://api.harvestapp.com/v2/"

    def __init__(self, f_token: str, f_accountid: str):
        """
        Создаем подключение к API Harvest по токену и id аккаунта из .env
        :param f_token:
        :param f_accountid:
        """
        self.projects = []
        self.headers = {
            "Authorization": "Bearer " + f_token,
            "Harvest-Account-Id": f_accountid
        }

    def get_by_user_id(self, f_user_id: str, f_start_date: str, f_end_date: str):
        """
        Тестовая недопилинная функция для проверки. Если у Арины возникнут вопросы.
        Чтобы по конкретному человеку посмотреть часы.
        :param f_user_id: ID юзера;
        :param f_start_date: Дата начала отчета;
        :param f_end_date: Дата конца отчета;
        :return: Пока не знаю куда лучше подкрутить фичу. Просто выкидает в консоль
        """
        # Подключение к Harvest(часы юзеров)
        entries = requests.get(
            url=self.url_address + f'time_entries?user_id={f_user_id}&from={f_start_date}&to={f_end_date}',
            headers=self.headers
        ).json()['time_entries']

        for entry in entries:
            print(entry)

    def get_active_users(self) -> list:
        """
        Получаем список активных юзеров, за исключением except_list(очень редко меняется, нужно вынести в .env)
        Email и должность юзера;
        :return: Список активных юзеров(кто участвует на проектах)
        """
        users_list = []
        # Подключение к Harvest(сотрудники)
        users = requests.get(
            url=self.url_address + 'users',
            headers=self.headers
        ).json()['users']

        for count, u in enumerate(users):
            if u['is_active'] and not u['email'] in self.except_list:
                user_obj = {
                    "id": u['id'],
                    "first_name": u['first_name'],
                    "last_name": u['last_name'],
                    "email": u['email'].lower(),
                    "roles": u['roles'],
                }
                users_list.append(user_obj)
        return users_list

    def get_hours(self, f_user_id: str, f_start_date: str, f_end_date: str) -> dict:
        """
        Собираем данные по одному сотруднику по user_id
        Узнаем общее время на проектах, на больничных, в отпуске
        :param f_user_id: ID юзера
        :param f_start_date: Дата начала отчета
        :param f_end_date: Дата конца отчета
        :return: Словарь на отдельного юзера, с общими расчетами по времени.
        """
        total_hours = 0
        hours_work_in_vacations = 0
        hours_work_in_sick_leave = 0
        list_date_vacations = []
        list_date_sick_leave = []

        # Подключение к Harvest(часы юзеров)
        entries = requests.get(
            url=self.url_address + f'time_entries?user_id={f_user_id}&from={f_start_date}&to={f_end_date}',
            headers=self.headers
        ).json()['time_entries']

        for entry in entries:

            # id - 16608456: id записи времени в Harvest по больничному листу
            # id - 5610020: id записи времени в Harvest по отпуску
            if entry['task']['id'] == 16608456:  # Если запись больничного листа, считаем часы на рабочих проектах
                list_date_sick_leave.append(entry['spent_date'])
            elif entry['task']['id'] == 5610020:  # Если запись отпуска, считаем часы на рабочих проектах
                list_date_vacations.append(entry['spent_date'])
            else:
                total_hours += entry['hours']

        list_date_sick_leave = sorted(list_date_sick_leave)
        list_date_vacations = sorted(list_date_vacations)

        for entry in entries:
            if entry['spent_date'] in list_date_sick_leave and entry['task']['id'] != 16608456:
                hours_work_in_sick_leave += entry['hours']
                total_hours -= entry['hours']
            elif entry['spent_date'] in list_date_vacations and entry['task']['id'] != 5610020:
                hours_work_in_vacations += entry['hours']
                total_hours -= entry['hours']

        result = {
            'total_hours': total_hours,
            'hours_work_in_vacations': hours_work_in_vacations,
            'hours_work_in_sick_leave': hours_work_in_sick_leave,
            'time_in_vacations': f'В отпуске с {list_date_vacations[0]} по {list_date_vacations[-1]}' if list_date_vacations else None,
            'time_in_sick_leave': f'Болел с {list_date_sick_leave[0]} по {list_date_sick_leave[-1]}' if list_date_sick_leave else None,
            }

        return result

    def get_date(self, f_start_date: str, f_end_date: str) -> dict:
        """
        Разбивает дату на день/месяц/год
        :param f_start_date: дата из формы в виде 01.02.2000
        :param f_end_date: дата из формы в виде 01.02.2000
        :return: {'start_date': [2000, 02, 01], 'end_date': [2000, 02, 01]}
        """
        dict_date = {'start_date': f_start_date.split('.'), 'end_date': f_end_date.split('.')}

        return dict_date


def get_reports(f_start_date: str, f_end_date: str) -> list:
    """
    Формируем список из словарей для записи в БД по всем юзерам;
    :param f_start_date: Дата начала отчета;
    :param f_end_date: Дата конца отчета;
    :return: список из словарей по каждому юзеру.
    """
    # Создаем подключение к API Harvest
    harvest = Harvest(TOKEN, ACCOUNT_ID)

    # Преобразуем дату вида 01.02.2000 в 20000101 для API Harvest
    start_date = f_start_date.replace('-', '')
    end_date = f_end_date.replace('-', '')

    print(start_date, end_date)

    # Получаем активных клиентов из харвеста, забираем id, имя и должность
    # и записываем в dict_users
    active_users = harvest.get_active_users()
    dict_users = []
    for user in active_users:
        employee = harvest.get_hours(user['id'], start_date, end_date)
        dict_users.append({
            'user_id': user['id'],
            'first_name': user['first_name'],
            'last_name': user['last_name'],
            'roles': ', '.join(user['roles']),
            'start_date_report': f_start_date,
            'end_date_report': f_end_date,
            'total_hours': employee['total_hours'],
            'hours_work_in_vacations': employee['hours_work_in_vacations'],
            'hours_work_in_sick_leave': employee['hours_work_in_sick_leave'],
            'time_in_vacations': employee['time_in_vacations'],
            'time_in_sick_leave': employee['time_in_sick_leave'],
        })

    return dict_users
