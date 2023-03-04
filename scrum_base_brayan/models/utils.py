from odoo.fields import Datetime
from datetime import datetime, timedelta


def is_work_day(datetime_obj: datetime, record):
    week_day = datetime_obj.weekday()

    current_hour = datetime_obj.hour
    current_minute = datetime_obj.minute
    current_second = datetime_obj.second

    if week_day != 5 and week_day != 6 and \
            (
                    (
                            (current_minute == 0 and current_second == 0) and
                            (
                                    (13 <= current_hour <= 17) or
                                    (19 <= current_hour <= 22)
                            )

                    ) or
                    (
                            (current_minute != 0 or current_second != 0) and
                            (
                                    (13 <= current_hour < 17) or
                                    (18 <= current_hour < 22)
                            )
                    )
            ):
        return True
    else:
        return False
