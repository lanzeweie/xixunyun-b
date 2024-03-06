import json
#from loglog import XXYLogger
from usr_ua import Xixunyun_ua
from usr_token import Xixunyun_login
import os
####################################
#logger = XXYLogger('database', log_file='database.log')
weizhi = os.path.dirname(os.path.abspath(__file__))
'''
介绍：Xixunyun_cookie.py
简介：
将环境变量中的值给格式化，然后写入数据库中
具体介绍：
1.提取环境变量的值，格式化它
2.验证环境变量中的值是否在数据库中，没有则写入
3.第一次加入数据库的用户，会获得Token
4.如果环境变量存在数据库中，则对比缺失或者是不同的值（以环境变量为主），最后检查Token是否可用，不可用则重新获取

此脚本的意义就是创造与维护数据库，方便后续的签到任务

环境变量需求
school_id=学校代码,name=名字,phone=手机号,password=密码,moth=有效年月,word_long=工作地址经度,word_latit=工作地址纬度,word_name_guishu=工作地址的归属区,word_name=工作地址的名字,home_long=假期的经度,home_latit=假期的纬度,home_name_guishu=假期地址的归属区,home_name=假期的地址名字,mothxiu=月休几天
推送消息变量
bot_message
'''
# 青龙面板 首先通过环境变量获取cookie，如果没有则使用本地json文件
def Cookie():
    CookieJDs = []
    if 'XIXUNYUN_COOKIE' in os.environ:
        if '&' in os.environ['XIXUNYUN_COOKIE']:
            CookieJDs = os.environ['XIXUNYUN_COOKIE'].split('&')
        elif '\n' in os.environ['XIXUNYUN_COOKIE']:
            CookieJDs = os.environ['XIXUNYUN_COOKIE'].split('\n')
        else:
            CookieJDs = [os.environ['XIXUNYUN_COOKIE']]
    CookieJDs = list(set(filter(None, CookieJDs)))
    return CookieJDs

# 加载通知服务
def load_send():
    import sys
    cur_path = os.path.abspath(os.path.dirname(__file__))
    sys.path.append(cur_path)
    if os.path.exists(cur_path + "/sendNotify.py"):
        try:
            from sendNotify import send
            return send
        except Exception as e:
            #print(f"加载通知服务失败：{e}")
            return None
    else:
        print("加载通知服务失败")
        return None
####################################
#仅仅用于在windows本地的cooikie测试 ———— 使用的 json ，实际生产环境中使用的 环境变量
def Env_cookie():
    # 读取JSON文件
    with open(f'{weizhi}{os.sep}data{os.sep}env.json', 'r', encoding='utf-8') as f:
        Env_cookies_value = json.load(f)
    # 提取cookie的值
    Env_cookies = [item['cookie'] for item in Env_cookies_value['list']]
    # 输出cookie值列表
    return Env_cookies
#########################################################################

def Env_cookie_format(Env_cookies):
    # 分析有几个cookie
    bot_message = "数据库具体信息\n"
    bot_message_error = 0
    bot_message_sure = 0
    #logger.info('开始处理数据库')
    #logloglog_text = ""
    cookies = len(Env_cookies)
    #logloglog_text += f'("检测到环境变量中拥有【{cookies}】个cookie")\n'
    bot_message += f'总共【{cookies}】个 COOKIE\n'
    print("共有", cookies, "个cookie")
    # 格式化cookie
    #logloglog_text += "开始格式化cookie"
    #logger.info(#logloglog_text)
    
    print("开始格式化cookie任务")
    cookie_list = 0
    for Env_cookies_format in Env_cookies:
        #logloglog_text = ""
        cookie_list += 1
        print(f"—————————————第{cookie_list}个———————————————\ncookie: {Env_cookies_format}\n")
        #logloglog_text += (f"—————————————第{cookie_list}个———————————————\ncookie: {Env_cookies_format}\n")
        cookie_pairs = [pair.split('=') for pair in Env_cookies_format.split(',')]
        Env_cookies_value = {}
        try:
            # 尝试创建键值对字典
            Env_cookies_value = {key: value for key, value in cookie_pairs}
        except ValueError:
            # 如果无法格式化，跳出此cookie异常
            #logloglog_text += f"无法格式化此cookie:{Env_cookies_format}\n"
            print("无法格式化此cookie:", Env_cookies_format)
            bot_message_error += 1
            #logger.info(#logloglog_text)
            continue
        # 验证字典中是否缺少键
        required_keys = ['school_id', 'name', 'account', 'model', 'time', 'phone', 'password', 'moth', 'word_long', 'word_latit', 'word_name', 'word_name_guishu', 'home_long', 'home_latit', 'home_name', 'home_name_guishu', 'mothxiu', 'mac']
        missing_keys = [key for key in required_keys if key not in Env_cookies_value]
        if missing_keys:
            # 如果有缺少的键，跳出缺少此键的异常
            #logloglog_text += f"缺少以下键:{missing_keys}\n"
            print("缺少以下键:", missing_keys)
            bot_message_error += 1
            #logger.info(#logloglog_text+"\n")
            continue
        school_id = Env_cookies_value['school_id']
        name = Env_cookies_value['name']
        model = Env_cookies_value['model']
        phone = Env_cookies_value['phone']
        password = Env_cookies_value['password']
        moth = Env_cookies_value['moth']
        word_long = Env_cookies_value['word_long']
        word_latit = Env_cookies_value['word_latit']
        word_name = Env_cookies_value['word_name']
        word_name_guishu = Env_cookies_value['word_name_guishu']
        home_long = Env_cookies_value['home_long']
        home_latit = Env_cookies_value['home_latit']
        home_name = Env_cookies_value['home_name']
        home_name_guishu = Env_cookies_value['home_name_guishu']
        mothxiu = Env_cookies_value['mothxiu']
        mac = Env_cookies_value['mac']
        account = Env_cookies_value['account']
        time_user = Env_cookies_value['time']

        def user_exists(name, account, school_id):
            for user in data['users']:
                if (user['name'] == name and
                    user['account'] == str(account) and
                    user['school_id'] == str(school_id)):
                    return user
            return None
        #logloglog_text += "正在验证用户是否存在于数据库中\n"
        # Check if the user exists
        existing_user = user_exists(name, account, school_id)
        
        if existing_user is not None:
            #logloglog_text += f"{name} 用户存在于数据库中\n"
            print(f"{name} 用户存在于数据库中")
            #logloglog_text += "正在验证Token是否可用\n"
            print("正在|验证Token是否可用")
            Token = (existing_user.get('token'))
            usr_ua_insp = Xixunyun_ua(Token,school_id).get_ua()
            usr_ua_insp_len = len(usr_ua_insp)
            if usr_ua_insp_len <= 3:
                #logloglog_text += "用户Token已是激活状态\n"
                bot_message_sure += 1
                print("用户Token已是激活状态")
                bot_message += f"{name} {account} 【成功】\n"
                word_name_ua = usr_ua_insp[0]
                word_long_ua = usr_ua_insp[1]
                word_latit_ua = usr_ua_insp[2]
                #logloglog_text += f"用户初次签到地址为：{word_name_ua}, 纬度：{word_latit_ua} 经度：{word_long_ua}\n"
                print(f"用户初次签到地址为：{word_name_ua}, 经度：{word_long_ua}, 纬度：{word_latit_ua}")
            elif usr_ua_insp_len >3:
                usr_ua_errow = usr_ua_insp
                if usr_ua_errow == "请求异常":
                    print("请求异常")
                    #logloglog_text += "请求异常\n"
                    #logger.info(#logloglog_text)
                    bot_message_error += 1
                    continue
                elif usr_ua_errow == "请求超时，可能是网络问题":
                    print("----------------出现请求超时情况，终止所有任务---------------------")
                    #logloglog_text += "请求超时，可能是网络问题\n"
                    #logger.info(#logloglog_text)
                    bot_message_error += 1
                    break
                print("验证Token失败，可能是已经失效··········尝试重新获取")
                #logloglog_text += "验证Token失败，可能是已经失效··········尝试重新获取\n"
                #将新获得的token写入数据库中
                usr_token_insp = Xixunyun_login(school_id, password, account, model, mac).get_token()
                usr_token_insp_len = len(usr_token_insp)
                if usr_token_insp_len > 7:
                    user_name, school_id, token, user_number, bind_phone, user_id, class_name, entrance_year, graduation_year = usr_token_insp
                    existing_user['token'] = token
                    existing_user['jiuxu'] = True
                    with open(file_name, 'w', encoding='utf-8') as file:
                        json.dump(data, file, indent=2, ensure_ascii=False)
                    print("用户Token信息更新成功")
                    #logloglog_text += "用户Token信息更新成功\n"
                    bot_message_sure += 1
                    bot_message += f"{name} {account} 【成功】\n"
                else:
                    usr_token_errow = usr_token_insp
                    if usr_token_errow == "请求异常":
                        print("因为请求异常，用户Token更新失败")
                        #logloglog_text += "因为请求异常，用户Token更新失败\n"
                        existing_user['jiuxu'] = False
                        with open(file_name, 'w', encoding='utf-8') as file:
                            json.dump(data, file, indent=2, ensure_ascii=False)
                        #logger.info(#logloglog_text)
                        bot_message_error += 1
                        bot_message += f"{name} {account} 【失败】\n"
                        continue
                    elif usr_token_errow == "请求超时，可能是网络问题":
                        print("----------------出现请求超时情况，终止所有任务---------------------")
                        #logloglog_text += "请求超时，可能是网络问题\n"
                        existing_user['jiuxu'] = False
                        with open(file_name, 'w', encoding='utf-8') as file:
                            json.dump(data, file, indent=2, ensure_ascii=False)
                        #logger.info(#logloglog_text)
                        bot_message_error += 1
                        bot_message += f"{name} {account} 【失败】\n"
                        break
                    else:
                        print("错误Token回复，用户Token更新失败",usr_token_errow)
                        #logloglog_text += f"错误Token回复，用户Token更新失败{usr_token_errow}\n"
                        existing_user['jiuxu'] = False
                        with open(file_name, 'w', encoding='utf-8') as file:
                            json.dump(data, file, indent=2, ensure_ascii=False)
                        #logger.info(#logloglog_text)
                        bot_message_error += 1
                        bot_message += f"{name} {account} 【失败】\n"
                        continue
            
            # Check if other attributes match and update the database if necessary
            if all(existing_user.get(key) == value for key, value in {
                'model': model,
                'phone': phone,
                'password': password,
                'moth': moth,
                'time': time_user,
                'word_long': word_long,
                'word_latit': word_latit,
                'word_name': word_name,
                'word_name_guishu': word_name_guishu,
                'home_long': home_long,
                'home_latit': home_latit,
                'home_name': home_name,
                'home_name_guishu': home_name_guishu,
                'mothxiu': mothxiu,
                'mac': mac
            }.items()):
                print("用户基础数据已是最新")
                #logloglog_text += "用户基础数据已是最新\n"
                #logger.info(#logloglog_text)
            else:
                for key, value in {
                    'model': model,
                    'phone': phone,
                    'password': password,
                    'moth': moth,
                    'time': time_user,
                    'word_long': word_long,
                    'word_latit': word_latit,
                    'word_name': word_name,
                    'word_name_guishu': word_name_guishu,
                    'home_long': home_long,
                    'home_latit': home_latit,
                    'home_name': home_name,
                    'home_name_guishu': home_name_guishu,
                    'mothxiu': mothxiu,
                    'mac': mac
                }.items():
                    existing_user[key] = value
                print("用户信息基础数据与环境变量数据不一致，以环境变量数据为主······更新基础数据")
                #logloglog_text += "用户信息基础数据与环境变量数据不一致，以环境变量数据为主······更新基础数据\n"
                # Save the updated database back to the JSON file
                with open(file_name, 'w', encoding='utf-8') as file:
                    json.dump(data, file, indent=2, ensure_ascii=False)
                    print("用户信息基础数据更新成功")
                    #logloglog_text += "用户信息基础数据更新成功\n"
                #logger.info(#logloglog_text)
                continue
        else:
            usr_token_insp = Xixunyun_login(school_id, password, account, model, mac).get_token()
            usr_token_insp_len = len(usr_token_insp)
            if usr_token_insp_len > 7:
                user_name, school_id, token, user_number, bind_phone, user_id, class_name, entrance_year, graduation_year = usr_token_insp
                print(user_name, school_id, token, user_number, bind_phone, user_id, class_name, entrance_year, graduation_year)
            else:
                usr_token_errow = usr_token_insp
                if usr_token_errow == "请求异常":
                    print("请求异常")
                    #logloglog_text += "请求异常\n"
                    #logger.info(#logloglog_text)
                    bot_message_error += 1
                    continue
                elif usr_token_errow == "请求超时，可能是网络问题":
                    print("----------------出现请求超时情况，终止所有任务---------------------")
                    #logloglog_text += "请求超时，可能是网络问题\n"
                    #logger.info(#logloglog_text)
                    bot_message_error += 1
                    break
                else:
                    print("错误回复",usr_token_errow)
                    #logloglog_text += f"错误回复{usr_token_errow}\n"
                    #logger.info(#logloglog_text)
                    bot_message_error += 1
                    continue
            
            print("——————格式化成功！！移交数据库——————")
            #logloglog_text += "——————格式化成功！！移交数据库——————\n"
            with open(file_name, 'r', encoding='utf-8') as json_file:
                existing_data = json.load(json_file)
            new_user_data = {
                "name": user_name,
                "school_id": str(school_id),
                "token": token,
                "account": user_number,
                "password": password,
                "phone": bind_phone,
                "usr_id": str(user_id),
                "address": class_name,
                "start_year": entrance_year,
                "end_year": graduation_year,
                "moth": moth,
                "time": time_user,
                "mothxiu": mothxiu,
                "word_long": word_long,
                "word_latit": word_latit,
                "word_name": word_name,
                "word_name_guishu": word_name_guishu,
                "home_long": home_long,
                "home_latit": home_latit,
                "home_name": home_name,
                "home_name_guishu": home_name_guishu,
                "model": model,
                "mac": mac,
                "jiuxu": True
            }
            existing_data["users"].append(new_user_data)
            with open(file_name, 'w', encoding='utf-8') as json_file:
                json.dump(existing_data, json_file, indent=2, ensure_ascii=False)
            print(f"{name} 用户数据验证成功")
            #logloglog_text += f"{name} 用户数据验证成功\n"
            #logger.info(#logloglog_text+"\n")
            bot_message_sure += 1
            bot_message += f"【{name} {account} 成功】\n"
    huizong_message = (f"{bot_message}———————————— \n数据库数据总报告\n总共：{cookies}个\n成功：{bot_message_sure}个\n失败：{bot_message_error}个")
    #logloglog_text = f"数据库数据总报告\n总共：{cookies}个\n成功：{bot_message_sure}个\n失败：{bot_message_error}个\n"
    #logger.info(#logloglog_text)
    print(huizong_message)
    bot_message_tuisong = load_send()
    if bot_message_tuisong is not None:
        print("发现推送服务|正在推送")
        bot_message_tuisong("习讯云助手",huizong_message)

    
    

          
if __name__ == "__main__":
    file_name = f"{weizhi}{os.sep}data{os.sep}user.json"       
    # 读取user.json文件
    with open(f'{file_name}', 'r', encoding='utf-8') as file:
        data = json.load(file)

    def get_cookies():
        cookies = Cookie()
        if not cookies:  # 如果 cookies 列表为空
            cookies = Env_cookie()
        if not cookies:  # 如果 cookies 列表仍然为空
            print("失败：无法获取cookies")
            return None
        return cookies

    # 使用：
    cookies = get_cookies()
    if cookies is not None:
        Env_cookie_format(cookies)
    else:
        os._exit()

