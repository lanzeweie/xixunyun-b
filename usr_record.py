import requests
from datetime import datetime
import os
import json
weizhi = os.path.dirname(os.path.abspath(__file__))
##################导入配置文件#####################
try:
    with open(f'{weizhi}{os.sep}data{os.sep}config.json', 'r',encoding="utf-8") as file:
        data = json.load(file)
        config = data['config'][0]
        version_config = config['version']
        from_config = config['from']
        platform_config = config['platform']
        key_config = config['key']
except:
    print("配置文件错误，结束运行 | 配置文件：config.json")
    os._exit()
###########################################
class Xixunyun_record():
    def __init__(self,token,school_id):
        self.token = token
        self.school_id = school_id

    def get_record(self):
        current_date = datetime.now()
        formatted_date = current_date.strftime("%Y-%m").lstrip("0")
        # 如果月份部分以"0"开头，去掉这个"0"
        if formatted_date[5] == "0":
            formatted_date = formatted_date[:5] + formatted_date[6:]
        url = "https://api.xixunyun.com/signin40/SignInList"
        params = {
            "student_id": "",
            "month_date": formatted_date,
            "page_no": "1",
            "page_size": "300",
            "token": self.token,
            "from": from_config,
            "version": version_config,
            "platform": platform_config,
            "entrance_year": "0",
            "graduate_year": "0",
            "school_id": self.school_id
        }

        headers = {
            "Accept-Encoding": "gzip",
            "User-Agent": "okhttp/3.8.1"
        }

        try:  
            response = requests.get(url, params=params, headers=headers, timeout=10)
        except requests.exceptions.Timeout:
            return "请求超时，可能是网络问题"
        except requests.exceptions.RequestException as e:
            return "请求异常"
        
        try:
            response_json = response.json()
            # 计算正常上班次数
            sign_ins = sum(1 for record in response_json["data"]["list"] if record["remark_text"] == "上班")
            jiaqi_ins = sum(1 for record in response_json["data"]["list"] if record["remark_text"] == "假期")
            # 提取异常字段
            abnormal_records = [entry for entry in response_json['data']['list'] if entry['status_code'] != '0']
            abnormal_records_len = len(abnormal_records)
            #print(f"上班次数：{sign_ins}")
            #print(f"假期次数：{jiaqi_ins}")
            #print(f"异常字段：{abnormal_records}")
            #print(f"异常次数：{abnormal_records_len}")
            # Extracting the required fields for each abnormal record and printing
            for i, record in enumerate(abnormal_records, start=1):
                abnormal_data = {
                    'longitude': record['longitude'],
                    'latitude': record['latitude'],
                    'address': record['address'],
                    'address_name': record['address_name'],
                    'sign_time_text': record['sign_time_text']
                }
                print(f'【警告】本月异常字段[{i}]: {abnormal_data}')
            # 上班次数 假期次数 异常次数 
            return sign_ins,jiaqi_ins,abnormal_records_len
        except:
            return response_json

        