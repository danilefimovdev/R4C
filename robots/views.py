import io
import json
from datetime import timedelta

from django.http import JsonResponse, HttpResponse, HttpRequest
from django.views import View

from customers.models import Customer
from orders.models import Order
from robots.forms import RobotForm
from robots.models import Robot
from services import prepare_robots_data_for_xlsx_pages, get_time_filtered_robots, get_time_filtered_models_data, \
    create_week_repost_as_xlsx_file
from utils import get_datetime_with_timedelta_from_now


class RobotView(View):
    """ Получает данные в виде json, валидирует и создает запись в бд в случае успеха """

    def post(self, request, *args, **kwargs) -> JsonResponse:
        try:
            # отлов исключений при ошибке декодирования (не знаю нужно ли было, но сделал, так как поймал такую)
            data = json.loads(request.body)
        except Exception as ex:
            return JsonResponse(data={'Error': {'message': f'{ex.args[0]} in your JSON file'}}, status=400)

        form = RobotForm(data=data)
        if form.is_valid():
            validated_data = form.cleaned_data
            # serial точно будет валидна, так как составные части у нас валидные
            validated_data.update(
                {'serial': f'{str(data["model"])}-{str(data["version"])}'}
            )
            robot = Robot.objects.create(**validated_data)
            return JsonResponse(data={'Created': str(robot)}, status=201)
        else:
            errors_dict = {}
            for field, errors in form.errors.items():
                errors_dict.update(
                    {field: [str(error) for error in errors]}
                )
            return JsonResponse(data={'Errors': errors_dict}, status=400)


def get_week_report_xlsx(request: HttpRequest) -> HttpResponse:
    """ Формирует недельный отчет по прроизведенным роботам в виде xlsx файла """

    datetime_, timestamp = get_datetime_with_timedelta_from_now(timedelta_=timedelta(weeks=1))
    filtered_robots = get_time_filtered_robots(datetime_=datetime_)
    if not filtered_robots:
        return HttpResponse('No robot was produced in the past week')
    models_data = get_time_filtered_models_data(datetime_=datetime_)
    prepared_pages_data = prepare_robots_data_for_xlsx_pages(models=models_data, filtered_robots=filtered_robots)
    workbook = create_week_repost_as_xlsx_file(models=models_data, timestamp=timestamp,
                                               prepared_pages_data=prepared_pages_data)

    buffer = io.BytesIO()
    workbook.save(buffer)
    with buffer as stream:
        buffer.seek(0)
        response = HttpResponse(
            stream.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    response['Content-Disposition'] = f'attachment; filename={timestamp}.xlsx'

    return response


