import json

from django.http import JsonResponse
from django.views import View

from robots.forms import RobotForm
from robots.models import Robot


class RobotView(View):

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