from django.shortcuts import render
from .forms import ReportsForm
from .models import ReportTime

import scripts.harvest_api_MR as HarAPI


def reports(request):
    """
    Собираем и сохраняем данные по пользователям.
    :param request:
    :return: render из словаря
    """

    # Из форм получаем даты начала и конца отчета.
    form = ReportsForm(request.POST)
    context = {
        'form': form,
    }

    if form.is_valid():
        start_date = str(form.cleaned_data['date_start'])  # Получаем даты из формы
        end_date = str(form.cleaned_data['date_finish'])  # Получаем даты из формы

        # Считаем количество дней между датами, для дальнейших расчетов
        number_of_days_between_dates = form.cleaned_data['date_finish'].day - form.cleaned_data['date_start'].day
        try:
            data = HarAPI.get_reports(start_date, end_date)  # Вызываем функцию get_reports

            # Записываем полученные данные в базу или обновляем их по юзеру и датам (используя распаковку **)
            for i in data:
                ReportTime.objects.update_or_create(**i, defaults={
                    'total_hours': i['total_hours'],
                    'hours_work_in_vacations': i['hours_work_in_vacations'],
                    'hours_work_in_sick_leave': i['hours_work_in_sick_leave'],
                    'time_in_vacations': i['time_in_vacations'],
                    'time_in_sick_leave': i['time_in_sick_leave'],
                })

            # Если разница дней между датами больше 18, то считаем что это месяц и выводим данные из харвеста
            # за месяц и за полмесяца
            if number_of_days_between_dates > 18:
                date_of_month = ReportTime.objects.filter(start_date_report=start_date).filter(end_date_report=end_date)\
                    .order_by('user_id', 'start_date_report', 'end_date_report', '-updated_at').distinct('user_id')

                # Ищем за полмесяца
                date_of_half_month = ReportTime.objects.filter(end_date_report__range=(start_date, end_date))\
                    .order_by('user_id', 'start_date_report', 'end_date_report', '-updated_at').distinct('user_id')

                context['date_of_month'] = date_of_month
                context['date_of_half_month'] = date_of_half_month

            # Если разница дней между датами меньше 18, то считаем что это полмесяца и выводим данные из харвеста
            # за полмесяца
            elif number_of_days_between_dates < 18:

                date_of_half_month = ReportTime.objects.filter(start_date_report=start_date).filter(end_date_report=end_date) \
                    .order_by('user_id', 'start_date_report', 'end_date_report', '-updated_at').distinct('user_id')
                context['date_of_half_month'] = date_of_half_month

        except:
            print('Возникла ошибка при сохранении или выводе данных!')

    return render(request, fr'D:\PycharmProj\time_managment\templates\report_time.html', context=context)

