import requests
import re
import json
import os
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

class Xixunyun_qian():
    def __init__(self,token,school_id,province,city,address,address_name,latitude,longitude,remark):
        self.token = token
        self.school_id = school_id
        self.address = address
        self.address_name = address_name
        # 脑残习讯云的傻逼机制，TM的把 经纬度地址互换了
        self.latitude = longitude
        self.longitude = latitude
        ###############################################
        self.remark = remark
        self.province = province
        self.city = city

    def get_qiandao(self):
        from_shebei = from_config #来源
        shebei_version = version_config  #版本
        platform = platform_config  #设备类
        zhu_url = "https://api.xixunyun.com/signin_rsa"
        fujia_url = f'token={self.token}&from={from_shebei}&version={shebei_version}&platform={platform}&entrance_year=0&graduate_year=0&school_id={self.school_id}'
        url = f"{zhu_url}?{fujia_url}"

        headers = {
            "Host": "api.xixunyun.com",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept-Encoding": "gzip",
            "User-Agent": "okhttp/3.8.1"
        }

        params = {
            "token": self.token,
            "from": from_shebei,
            "version": shebei_version,
            "platform": platform,
            "entrance_year": "0",
            "graduate_year": "0",
            "school_id": self.school_id
        }

        data = {
            "address": self.address,
            "province": self.province,
            "city": self.city,
            "latitude": self.latitude,
            "remark": self.remark,
            "comment": "",
            "address_name": self.address_name,
            "change_sign_resource": "0",
            "longitude": self.longitude
        }

        try:  
            response = requests.post(url, headers=headers, params=params, data=data,timeout=10)
        except requests.exceptions.Timeout:
            return "error",'请求超时，可能是网络问题'
        except requests.exceptions.RequestException as e:
            return "error","请求异常"
        
        print(response.text)
        response_json = response.json()
        
        if response_json["code"] == 20000:
            days_signed = re.search(r'已签到(\d+)天', response_json['data']['message_string'])
            days_signed = int(days_signed.group(1)) if days_signed else 0
            return True, days_signed
        elif response_json["code"] == 64033:
            message = response_json["message"]
            return False, message
        elif response_json["code"] == 64032:
            message = response_json["message"]
            return False, message
        else:
            return False, "未知错误"
    
    

