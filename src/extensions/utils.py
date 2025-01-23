from dateutil.parser import ParserError

from . import jalali
from django.utils import timezone
from dateutil import parser
import math
from datetime import datetime
import datetime as fdatetime
import jdatetime
import re


def persian_numbers_converter(mystr):
    numbers = {
        "0": "۰",
        "1": "۱",
        "2": "۲",
        "3": "۳",
        "4": "۴",
        "5": "۵",
        "6": "۶",
        "7": "۷",
        "8": "۸",
        "9": "۹",
    }

    for e, p in numbers.items():
        mystr = mystr.replace(e, p)

    return mystr


def jalali_converter(time):

    time = timezone.localtime(time)
    time_to_str = "{},{},{}".format(time.year, time.month, time.day)
    time_to_tuple = jalali.Gregorian(time_to_str).persian_tuple()

    time_to_list = list(time_to_tuple)

    # for index, month in enumerate(jmonths):
    # 	if time_to_list[1] == index + 1:
    # 		time_to_list[1] = month
    # 		break
    output = "{}-{}-{} {}:{}:{}".format(
        "{0:0=4d}".format(time_to_list[0]),
        "{0:0=2d}".format(time_to_list[1]),
        "{0:0=2d}".format(time_to_list[2]),
        "{0:0=2d}".format(time.hour),
        "{0:0=2d}".format(time.minute),
        "{0:0=2d}".format(time.second),

    )

    return output


def jalali_converter_date(date):
    time_to_str = "{},{},{}".format(date.year, date.month, date.day)
    time_to_tuple = jalali.Gregorian(time_to_str).persian_tuple()

    time_to_list = list(time_to_tuple)

    output = "{}-{}-{}".format(
        time_to_list[0],
        time_to_list[1],
        time_to_list[2],
    )

    return persian_numbers_converter(output)


def jalali_converter_standard(time):
    time = timezone.localtime(time)
    time_to_str = "{},{},{}".format(time.year, time.month, time.day)
    time_to_tuple = jalali.Gregorian(time_to_str).persian_tuple()
    time_to_list = list(time_to_tuple)

    output = "{}-{}-{} {}:{}".format(
        time_to_list[0],
        time_to_list[1],
        time_to_list[2],
        time.hour,
        time.minute,
    )

    return persian_numbers_converter(output)


def jalali_converter_to_Gregorian(time):
    time = timezone.localtime(time)
    time_to_str = "{},{},{}".format(time.year, time.month, time.day)
    time_to_tuple = jalali.Persian(time_to_str).gregorian_tuple()

    time_to_list = list(time_to_tuple)

    output = "{}-{}-{} {}:{}".format(
        time_to_list[0],
        time_to_list[1],
        time_to_list[2],
        time.hour,
        time.minute,
    )

    return output


def jalali_converter_to_Gregorian_date(date):
    # 1401-01-01
    time_to_str = "{},{},{}".format(date.split('-')[0], date.split('-')[1], date.split('-')[2])
    time_to_tuple = jalali.Persian(time_to_str).gregorian_tuple()
    time_to_list = list(time_to_tuple)

    output = "{}-{}-{}".format(
        time_to_list[0],
        time_to_list[1],
        time_to_list[2],
    )

    return output


def check_queryset(requestGET):
    allowedChars = "abcdefghijklmnopqrstuvwxyz1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ-:."

    try:
        var = requestGET.dict()
        qry = {key: var[key] for key in var if var[key]}

        for key in qry:
            for s in qry[key]:
                if not s in allowedChars:
                    print(qry[key])
                    return False

        return True
    except Exception as e:
        return False


def is_ajax(request):
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'


def _get_date_sections_of_string(input_str: str):
    date_separator = ['.', '-', '/', '\\']
    date_time_separator = ['-', ' - ', ' ']

    date_pattern = r'\d{1,4}[-./\\]\d{1,2}[-./\\]\d{1,2}'

    time_pattern = r'(1[0-2]|0?[1-9]):([0-5]?[0-9]):([0-5]?[0-9])'

    date_matches = re.findall(date_pattern, input_str)
    time_matches = re.findall(time_pattern, input_str)

    for date_str in date_matches:
        for separator in date_separator:
            date_str = date_str.replace(separator, '-')
        for separator in date_time_separator:
            date_str = date_str.replace(separator, '-')

        date_parts = date_str.split("-")

        year = date_parts[0].strip()
        month = date_parts[1].strip()
        day = date_parts[2].strip()

    hour = time_matches[0][0].strip()
    minute = time_matches[0][1].strip()
    sec = time_matches[0][2].strip()
    if len(sec) == 0:
        sec = "00"

    return (year.zfill(4), month.zfill(2), day.zfill(2), hour.zfill(2), minute.zfill(2), sec.zfill(2))


def _is_jalali(date: datetime) -> bool:
    try:
        if 1300 <= date.year <= 1500:
            return True
        else:
            return False
    except:
        return False


def _get_gregorian_from_jalali_str(input_str, aware=True):
    sections_of_str = _get_date_sections_of_string(input_str)
    gd = jdatetime.JalaliToGregorian(int(sections_of_str[0]), int(sections_of_str[1]), int(sections_of_str[2]))
    output_date = f'{gd.gyear}-{gd.gmonth}-{gd.gday}'
    output_time = f'{sections_of_str[3]}:{sections_of_str[4]}:{sections_of_str[5]}'
    if aware:
        return timezone.make_aware(datetime.strptime(f'{output_date} - {output_time}', "%Y-%m-%d - %H:%M:%S"),
                                   timezone.get_current_timezone())
    else:
        return datetime.strptime(f'{output_date} - {output_time}')


def _get_gregorian_from_jalali_date(input_date, aware=True):
    gd = jdatetime.JalaliToGregorian(input_date.year, input_date.month, input_date.day)
    output_date = f'{gd.gyear}-{gd.gmonth}-{gd.gday}'
    output_time = f'{input_date.hour}:{input_date.minute}:{input_date.second}'
    if aware:
        return timezone.make_aware(datetime.strptime(f'{output_date} - {output_time}', "%Y-%m-%d - %H:%M:%S"),
                                   timezone.get_current_timezone())
    else:
        return datetime.strptime(f'{output_date} - {output_time}')


def get_datetime_from_str(string: str, aware=True) -> datetime:
    """
    try to convert string input to datetime object using dateutil library
    auto-detect and convert jalali to gregorian date
    Args:
        string (str): string datetime input
        aware (bool): make aware or not

    Returns:
        datetime: converted datetime object or None
    """
    try:
        parsed_date = parser.parse(string)

        if _is_jalali(parsed_date):
            return _get_gregorian_from_jalali_date(parsed_date, aware)
        else:
            if aware:
                return timezone.make_aware(parsed_date, timezone.get_current_timezone())
            else:
                return parsed_date

    except ParserError:
        return _get_gregorian_from_jalali_str(string)


def get_int_from_str(value) -> int:
    try:
        if isinstance(value, int) or isinstance(value, float) and not math.isnan(value):
            return int(value) if value > 0 else -1
        if isinstance(value, str) and (value.isdigit() or
                                       (value.replace('.', '', 1).isdigit() and value.count(',') <= 1)):
            return int(value)
        else:
            return -1
    except ValueError as e:
        return -1


def get_float_from_str(value: str) -> float:
    try:
        if isinstance(value, int) or isinstance(value, float) and not math.isnan(value):
            return float(value) if value > 0 else -1
        if isinstance(value, str) and (value.isdigit() or
                                       (value.replace('.', '', 1).isdigit() and value.count(',') <= 1)):
            return float(value)
        else:
            return -1
    except ValueError as e:
        print(e)
        return -1


def validate_ranged_float(input_value: str) -> tuple[bool, list[float]]:
    """

    :param input_value: str like 12-15,
    sort input and return as list[float]
    if one item passed (like 12), it set for both min and max
    only numeric, dot (.) and (-) allowed
    :return: (input_is_valid:bool, list_of_floats_parts)
    """

    allowed_chars = '1234567890-.'
    float_list = []
    for ch in input_value:
        if not allowed_chars.__contains__(ch):
            return False, float_list
    parts = input_value.split('-')
    if len(parts) > 2 or len(parts) < 1:
        return False, float_list
    for part in parts:
        if len(part.split('.')) > 2:
            return False, float_list
        for pp in part.split('.'):
            if not pp.isdigit():
                return False, float_list
        float_list.append(float(part))

    if len(float_list) == 1:
        float_list.append(float_list[0])

    return True, sorted(float_list)


def validate_float_list(input_value: str) -> tuple[bool, str | None]:
    """

    :param input_value: input str like 12,13,14.5,15,19 or 12-13-14.5-15-19
    sort items, return comma separated str of values
    :return: (input_is_valid:bool, list_of_floats_parts)
    """

    if input_value is None or input_value == '':
        return False, None

    float_list = []
    if input_value is None:
        return False, None
    input_value.replace(' ', '')
    allowed_chars = '1234567890-.,'
    for ch in input_value:
        if not allowed_chars.__contains__(ch):
            return False, None

    input_value = input_value.replace('-', ',')
    parts = input_value.split(',')
    for part in parts:
        if len(part.split('.')) > 2:
            return False, None
        for pp in part.split('.'):
            if not pp.isdigit():
                return False, None
        float_list.append(float(part))

    strValue = ','.join([str(f) for f in sorted(float_list)])

    return True, strValue


def validate_time(input_value: str):
    """

    :param input_value: str like 12:12 or 12:12:12
    :return: if validated, time else None
    """
    if len(input_value.split(':')) < 2:
        return False, None
    hour = input_value.split(':')[0]
    minute = input_value.split(':')[1]

    if not hour.isdigit() or not minute.isdigit():
        return False, None

    int_hour = int(hour)
    int_min = int(minute)

    if int_hour < 0 or int_hour > 24 or int_min < 0 or int_min > 59:
        return False, None

    return True, fdatetime.time(int_hour, int_min)

