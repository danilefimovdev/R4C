from datetime import timedelta, datetime
from typing import Tuple


def get_datetime_with_timedelta_from_now(timedelta_: timedelta) -> Tuple[datetime, str]:
    """ получаем datetime для использования в запросах к бд,
    а также timestamp (используется в качестве названия xlsx файла) """

    now = datetime.utcnow()
    strf_format = "%m-%d-%Y"
    one_week_ago = now - timedelta_
    time_stamp = f'{now.strftime(strf_format)}_{one_week_ago.strftime(strf_format)}'
    return one_week_ago, time_stamp
