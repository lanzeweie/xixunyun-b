import requests
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
        key_config = r"{}".format(config['key'])
except:
    print("配置文件错误，结束运行 | 配置文件：config.json")
    os._exit()
###########################################
class Xixunyun_login:
    def __init__(self, school_id, password, account, model,mac):
        self.from_shebei = from_config #来源
        self.shebei_version = version_config  #版本
        self.platform = platform_config  #设备类
        self.school_id = school_id #学校代码 
        self.password = password #密码
        self.account = account #学号
        self.model = model #设备型号
        self.mac = mac

    def get_token(self):
        zhu_url = "https://api.xixunyun.com/login/api"
        fujia_url = f'from={self.from_shebei}&version={self.shebei_version}&platform={self.platform}&entrance_year=0&graduate_year=0&school_id={self.school_id}'

        url = f"{zhu_url}?{fujia_url}"
        headers = {
            'Host': 'api.xixunyun.com',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept-Encoding': 'gzip',
            'User-Agent': 'okhttp/3.8.1'
        }

        data = {
            'app_version': self.shebei_version,
            'registration_id': '',
            'uuid': '',
            'request_source': '3',
            'platform': '2',
            'mac': self.mac,
            'password': self.password,
            'system': '9',
            'school_id': self.school_id,
            'model': self.model,
            'app_id': 'cn.vanber.xixunyun.saas',
            'account': self.account,
            'key': ''
        }

        print(f"发送请求：{data}")
        try:    
            response = requests.post(url, headers=headers, data=data, timeout=6)
        except requests.exceptions.Timeout:
            print("请求超时，可能是网络问题")
            return "请求超时，可能是网络问题"
        except requests.exceptions.RequestException as e:
            print("请求异常",e)
            return "请求异常"
        data = response.json()
        try:
            user_name = data['data']['user_name']
            school_id = data['data']['school_id']
            token = data['data']['token']
            user_number = data['data']['user_number']
            bind_phone = data['data']['bind_phone']
            user_id = data['data']['user_id']
            class_name = data['data']['class_name']
            entrance_year = data['data']['entrance_year']
            graduation_year = data['data']['graduation_year']
        except:
            return data
        return user_name, school_id, token, user_number, bind_phone, user_id, class_name, entrance_year, graduation_year

'''
print("用户名：", user_name)
print("学校ID：", school_id)
print("Token：", token)
print("用户编号：", user_number)
print("绑定手机号：", bind_phone)
print("用户ID：", user_id)
print("班级名称：", class_name)
print("入学年份：", entrance_year)
print("毕业年份：", graduation_year)
'''