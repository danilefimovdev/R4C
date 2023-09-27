from datetime import datetime
from typing import List, Dict

from django.db.models import Count, QuerySet

from robots.models import Robot
from dataclasses import dataclass


@dataclass
class RobotDTO:
    model: str
    version: str
    total: int


def _convert_robot_queryset_to_robot_dto_list(queryset: QuerySet) -> List[RobotDTO]:
    robot_dto_list = list()
    for item in queryset.values('model', 'version', 'total_per_version'):
        robot_dto = RobotDTO(
            model=item['model'],
            version=item['version'],
            total=item['total_per_version']
        )
        robot_dto_list.append(robot_dto)
    return robot_dto_list


def _extrude_model_data_from_robot_queryset_to_list(queryset: QuerySet) -> List[dict]:
    models_dict = dict()
    for model in queryset:
        key = model['model']
        if models_dict.get(key) is None:
            models_dict.update(
                {model['model']: 1}
            )
        else:
            models_dict[model['model']] += 1

    models_data = list()
    for name, qty in models_dict.items():
        models_data.append(
            {'name': name, 'versions_count': qty}
        )

    return models_data


def get_time_filtered_robots(datetime_: datetime) -> List[RobotDTO]:
    """ получаем отфильтрованных робатов и конвертируем их в список DTO """

    robots = Robot.objects.filter(created__gt=datetime_) \
        .values('model', 'version') \
        .annotate(total_per_version=Count('created')) \
        .order_by('serial')
    robots_dto_list = _convert_robot_queryset_to_robot_dto_list(queryset=robots)

    return robots_dto_list


def get_time_filtered_models_data(datetime_: datetime) -> List[dict]:
    """ получаем отфильтрованные данные по моделям роботов в виде вложенный dict в списке"""

    models = Robot.objects.filter(created__gt=datetime_) \
        .values('model', 'version') \
        .order_by('model').distinct()
    models_data = _extrude_model_data_from_robot_queryset_to_list(queryset=models)
    return models_data


def prepare_robots_data_for_xlsx_pages(models: list, filtered_robots: List[RobotDTO]) -> Dict[str, list]:
    """ Создаем словарь с данными для заполнения по помоделям """

    prepared_pages_data = {}
    last_robot_number = 0
    titles = ['Модель', 'Версия', 'Количество за неделю']

    for model in models:
        start = last_robot_number
        end = last_robot_number + model['versions_count']
        # из отсортированного списка получаем роботов модели 'model'
        robots_per_model = [robot for robot in filtered_robots[start:end]]
        # смещаем нижнюю границу среза списка роботов
        last_robot_number += model['versions_count']
        # формируем список из списков-строк
        robots_dto_list = [[robot.model, robot.version, robot.total] for robot in robots_per_model]
        robots_dto_list.insert(0, titles)
        prepared_pages_data.update(
            {
                model['name']: robots_dto_list
            }
        )
    return prepared_pages_data
