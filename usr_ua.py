import requests
from datetime import datetime
import json
import os
##################################################
weizhi = os.path.dirname(os.path.abspath(__file__))
##################导入配置文件#####################
# 直接运行可以获得 用户第一次打卡的地址与经纬度  需要在下方填写 Token 与 学校代码
##################################################
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
class Xixunyun_ua():
    def __init__(self,token,school_id):
        self.token = token
        self.school_id = school_id

    def get_ua(self):
        url = "https://api.xixunyun.com/signin40/homepage"
        current_date = datetime.now()
        formatted_date = current_date.strftime("%Y-%m").lstrip("0")
        # 如果月份部分以"0"开头，去掉这个"0"
        if formatted_date[5] == "0":
            formatted_date = formatted_date[:5] + formatted_date[6:]
        params = {
            "month_date": formatted_date,
            "token": self.token,
            "from": from_config,
            "version": version_config,
            "platform": platform_config,
            "entrance_year": "0",
            "graduate_year": "0",
            "school_id": self.school_id
        }

        headers = {
            "Host": "api.xixunyun.com",
            "accept-encoding": "gzip",
            "user-agent": "okhttp/3.8.1"
        }

        try:    
            response = requests.get(url, params=params, headers=headers, timeout=10)
        except requests.exceptions.Timeout:
            return "请求超时，可能是网络问题"
        except requests.exceptions.RequestException as e:
            return "请求异常"
        try:
            data = response.json()
            # Process the data as needed
            mid_sign_address = data['data']['sign_resources_info']['mid_sign_address']
            mid_sign_longitude = data['data']['sign_resources_info']['mid_sign_longitude']
            mid_sign_latitude = data['data']['sign_resources_info']['mid_sign_latitude']
            return mid_sign_address,mid_sign_longitude,mid_sign_latitude
        except:
            return data

if __name__ == "__main__":
    #Token
    Token = ''
    #学校代码
    school_id = 837
    usr_ua_insp = Xixunyun_ua(Token,school_id).get_ua()
    # 返回值  地址，经度，纬度
    print(usr_ua_insp)