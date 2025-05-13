import re
import random
from datetime import datetime

def generate_specific_mac():
    # 生成6个随机的十六进制数
    hex_digits = [random.choice('0123456789ABCDEF') for _ in range(12)]
    # 将12个十六进制数分组，每组两个数字，然后用冒号连接
    mac_address = ':'.join([''.join(hex_digits[i:i+2]) for i in range(0, 12, 2)])
    return mac_address

def validate_mac(mac):
    if not re.match(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$', mac):
        return False
    return True

def validate_latitude(latitude):
    if not re.match(r'^-?([1-8]?\d(\.\d+)?|90(\.0+)?)$', latitude):
        return False
    return True

def validate_longitude(longitude):
    if not re.match(r'^-?((1?[0-7]?|[1-9])?\d(\.\d+)?|180(\.0+)?)$', longitude):
        return False
    return True

def validate_phone(phone):
    if not re.match(r'^1[3-9]\d{9}$', phone):
        return False
    return True

def validate_time(time):
    try:
        datetime.strptime(time, '%H:%M')
        return True
    except ValueError:
        return False

def validate_date(date):
    try:
        datetime.strptime(date, '%Y-%m')
        return True
    except ValueError:
        return False

def format_data(data):
    # 使用正则表达式提取字段值
    name = re.search(r'姓名∶\s*(\S+)', data).group(1)
    student_id = re.search(r'学号∶\s*(\S+)', data).group(1)
    password = re.search(r'密码∶(\S+)', data).group(1)
    model = re.search(r'设备名∶(\S+)', data).group(1)
    phone = re.search(r'手机号:(\S+)', data).group(1)
    sign_in_time = re.search(r'签到时间:(\S+)', data).group(1)
    valid_moth = re.search(r'签到有效月份:(\S+)', data).group(1)
    work_latitude = re.search(r'上班签到纬度:(\S+)', data).group(1)
    work_longitude = re.search(r'上班签到经度:(\S+)', data).group(1)
    work_location = re.search(r'上班签到地名:(\S+)', data).group(1)
    work_location_guishu = re.search(r'上班签到归属地名∶(\S+)', data).group(1)
    vacation_latitude = re.search(r'假期签到纬度∶(\S+)', data).group(1)
    vacation_longitude = re.search(r'假期签到经度∶(\S+)', data).group(1)
    vacation_location = re.search(r'假期签到地名∶(\S+)', data).group(1)
    vacation_location_guishu = re.search(r'假期签到归属地名∶(\S+)', data).group(1)
    days_off = re.search(r'月休几天∶(\S+)', data).group(1)
    mac_match = re.search(r'mac:(随机|\S+)', data)
    if mac_match is None:
        return "MAC地址信息不合格"
    mac = mac_match.group(1)

    # 验证和生成MAC地址
    if mac.lower() == "随机":
        mac = generate_specific_mac()
    elif not validate_mac(mac):
        return "MAC地址信息不合格"

    # 检查并转换签到有效月份格式
    if ":" in valid_moth:
        start_month, end_month = valid_moth.split(":")
        start_month = start_month.zfill(2)  # 补零
        end_month = end_month.zfill(2)  # 补零
        valid_moth = f"{start_month}:{end_month}"

    # 验证经纬度
    if not validate_latitude(work_latitude) or not validate_longitude(work_longitude):
        return "上班签到经纬度信息不合格"
    if not validate_latitude(vacation_latitude) or not validate_longitude(vacation_longitude):
        return "假期签到经纬度信息不合格"

    # 验证手机号
    if not validate_phone(phone):
        return "手机号信息不合格"

    # 验证签到时间
    if not validate_time(sign_in_time):
        return "签到时间信息不合格"

    # 验证日期
    if not all(validate_date(date) for date in valid_moth.split(":")):
        return "签到有效月份信息不合格"

    # 格式化成目标格式
    formatted_data = f"school_id=查阅school_id,name={name},account={student_id},model={model},phone={phone},password={password},time={sign_in_time},moth={valid_moth},word_long={work_longitude},word_latit={work_latitude},word_name={work_location},word_name_guishu={work_location_guishu},home_latit={vacation_latitude},home_long={vacation_longitude},home_name={vacation_location},home_name_guishu={vacation_location_guishu},mothxiu={days_off},mac={mac}"
    return formatted_data


data = '''
姓名∶ 小明
学号∶ 1151155115
密码∶11515
设备名∶iPhone 15 Pro Max
手机号:18745505910
签到时间:9:00
签到有效月份:2024-01:2024-06
上班签到纬度:32.261551
上班签到经度:102.151551
上班签到地名:地点名 如某个地方的名字
上班签到归属地名∶归属地名字 如 省市区街道
假期签到纬度∶20.451551
假期签到经度∶106.454551
假期签到地名∶郫都区顺江社区(清源北巷南)
假期签到归属地名∶四川省成都市郫都区清源北巷
月休几天∶4
mac:随机
'''
#mac 直接写随机  会自动生成随机值
print(format_data(data))