#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
File: xixunyun_cookie.py(习讯云打卡数据库)
Author: lanzeweie
Date: 2024/3/11 13:00
cron: 54 8 * * *
new Env('习讯云打卡数据库');
Update: 2024/10/29
"""

import json
import os
import re
import sys
from usr_token import Xixunyun_login
from usr_ua import Xixunyun_ua

####################################
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

# 加载通知服务
def load_send():
    cur_path = os.path.abspath(os.path.dirname(__file__))
    sys.path.append(cur_path)
    send_notify_path = os.path.join(cur_path, "sendNotify.py")
    if os.path.exists(send_notify_path):
        try:
            from sendNotify import send
            return send
        except Exception as e:
            print(f"加载通知服务失败：{e}")
            return None
    else:
        print("加载通知服务失败：sendNotify.py 不存在")
        return None

# 获取 Cookies
def get_cookies():
    cookie_env = os.getenv('XIXUNYUN_COOKIE')
    if cookie_env:
        if '&' in cookie_env:
            cookies = cookie_env.split('&')
        elif '\n' in cookie_env:
            cookies = cookie_env.split('\n')
        else:
            cookies = [cookie_env]
        cookies = list(set(filter(None, cookies)))
        return cookies
    else:
        # 仅用于本地测试
        env_json_path = os.path.join(weizhi, 'data', 'env.json')
        if os.path.exists(env_json_path):
            try:
                with open(env_json_path, 'r', encoding='utf-8') as f:
                    env_data = json.load(f)
                return [item['cookie'] for item in env_data.get('list', [])]
            except Exception as e:
                print(f"读取本地 env.json 失败：{e}")
                return []
        else:
            print("环境变量和本地 env.json 都不存在")
            return []

# 查找重复用户
def find_duplicates(users):
    seen = set()
    duplicates = []
    for user in users:
        identifier = (user.get('name'), user.get('account'))
        if identifier in seen:
            duplicates.append(user)
        else:
            seen.add(identifier)
    return duplicates

# 保存数据到 JSON 文件，确保原子性
def save_json_atomic(file_path, data):
    temp_file = f"{file_path}.tmp"
    try:
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.replace(temp_file, file_path)
    except Exception as e:
        print(f"保存数据失败：{e}")
        if os.path.exists(temp_file):
            os.remove(temp_file)

# 验证并更新用户信息
def validate_and_update_user(user, Env_cookies_value, data, file_name, bot_message, bot_message_sure, bot_message_error, from_config, version_config, platform_config):
    required_keys = [
        'school_id', 'name', 'account', 'model', 'time', 'phone', 'password', 'moth',
        'word_long', 'word_latit', 'word_name', 'word_name_guishu',
        'home_long', 'home_latit', 'home_name', 'home_name_guishu','mothxiu', 'mac'
    ]
    missing_keys = [key for key in required_keys if key not in Env_cookies_value]
    if missing_keys:
        print(f"{Env_cookies_value.get('name')} {Env_cookies_value.get('account')} 缺少以下键: {missing_keys}")
        bot_message += f"{Env_cookies_value.get('name')} {Env_cookies_value.get('account')} 【缺参数】\n"
        bot_message_error += 1
        return bot_message, bot_message_sure, bot_message_error

    # 检查用户是否存在
    existing_user = next((u for u in data['users'] if u.get('account') == Env_cookies_value['account'] and u.get('school_id') == str(Env_cookies_value['school_id'])), None)

    try:
        if existing_user:
            print(f"{Env_cookies_value['name']} 用户存在于数据库中，验证 Token")
            # 优先从 Env_cookies_value 获取 Token，否则从 existing_user 获取
            token = Env_cookies_value.get('token', existing_user.get('token'))
            if not token:
                print(f"{Env_cookies_value['name']} {Env_cookies_value['account']} 缺少 Token 信息")
                bot_message += f"{Env_cookies_value['name']} {Env_cookies_value['account']} 【缺少 Token】\n"
                bot_message_error += 1
                return bot_message, bot_message_sure, bot_message_error

            # 传递配置参数
            token_status = Xixunyun_ua(token, Env_cookies_value['school_id']).get_ua()
            #print(f"内容: {token_status}")  # 调试信息

            # 修改这里的类型检查，支持 list 和 tuple
            if (isinstance(token_status, list) or isinstance(token_status, tuple)) and len(token_status) == 3:
                # 成功获取地址信息
                print(f"用户初次签到地址为：{token_status[0]}, 经度：{token_status[1]}, 纬度：{token_status[2]}")
                existing_user['jiuxu'] = True
                bot_message_sure += 1
                bot_message += f"{Env_cookies_value['name']} {Env_cookies_value['account']} 【成功】\n"
            elif isinstance(token_status, dict) and token_status.get('code') == 20000:
                # Token 激活状态
                print("用户Token已是激活状态")
                existing_user['jiuxu'] = True
                bot_message_sure += 1
                bot_message += f"{Env_cookies_value['name']} {Env_cookies_value['account']} 【成功】\n"
            else:
                # 验证失败，尝试重新获取
                print("验证Token失败，尝试重新获取")
                new_token = Xixunyun_login(
                    Env_cookies_value['school_id'],
                    Env_cookies_value['password'],
                    Env_cookies_value['account'],
                    Env_cookies_value['model'],
                    Env_cookies_value['mac']
                ).get_token()
                # 检查 new_token 是否为列表或元组，并具有足够长度
                if (isinstance(new_token, list) or isinstance(new_token, tuple)) and len(new_token) > 7:
                    # 提取 token
                    token_value = new_token[2]
                    existing_user['token'] = token_value
                    save_json_atomic(file_name, data)
                    existing_user['jiuxu'] = True
                    print("用户Token信息更新成功")
                    bot_message_sure += 1
                    bot_message += f"{Env_cookies_value['name']} {Env_cookies_value['account']} 【成功】\n"
                else:
                    handle_token_error(new_token, existing_user, bot_message, bot_message_error)
        else:
            # 用户不存在，获取 Token 并添加到数据库
            new_token = Xixunyun_login(
                Env_cookies_value['school_id'],
                Env_cookies_value['password'],
                Env_cookies_value['account'],
                Env_cookies_value['model'],
                Env_cookies_value['mac']
            ).get_token()
            # 检查 new_token 是否为列表或元组，并具有足够长度
            if (isinstance(new_token, list) or isinstance(new_token, tuple)) and len(new_token) > 7:
                # 提取 token
                token_value = new_token[2]
                new_user_data = {
                    "name": Env_cookies_value['name'],
                    "school_id": str(Env_cookies_value['school_id']),
                    "token": token_value,
                    "account": Env_cookies_value['account'],
                    "password": Env_cookies_value['password'],
                    "phone": new_token[4],
                    "usr_id": str(new_token[5]),
                    "address": new_token[6],
                    "start_year": new_token[7],
                    "end_year": new_token[8],
                    "moth": Env_cookies_value['moth'],
                    "time": Env_cookies_value['time'],
                    "mothxiu": Env_cookies_value['mothxiu'],
                    "word_long": Env_cookies_value['word_long'],
                    "word_latit": Env_cookies_value['word_latit'],
                    "word_name": Env_cookies_value['word_name'],
                    "word_name_guishu": Env_cookies_value['word_name_guishu'],
                    "home_long": Env_cookies_value['home_long'],
                    "home_latit": Env_cookies_value['home_latit'],
                    "home_name": Env_cookies_value['home_name'],
                    "home_name_guishu": Env_cookies_value['home_name_guishu'],
                    "model": Env_cookies_value['model'],
                    "mac": Env_cookies_value['mac'],
                    "jiuxu": True
                }
                data["users"].append(new_user_data)
                save_json_atomic(file_name, data)
                print(f"{Env_cookies_value['name']} 用户数据验证成功")
                bot_message_sure += 1
                bot_message += f"【{Env_cookies_value['name']} {Env_cookies_value['account']} 成功】\n"
            else:
                handle_token_error(new_token, None, bot_message, bot_message_error)
    except Exception as e:
        print(f"处理用户 {Env_cookies_value.get('name')} 时出错：{e}")
        bot_message += f"{Env_cookies_value.get('name')} {Env_cookies_value.get('account')} 【失败】\n"
        bot_message_error += 1

    return bot_message, bot_message_sure, bot_message_error

# 处理 Token 错误
def handle_token_error(error, user, bot_message, bot_message_error):
    if error == "请求异常":
        print("请求异常")
        bot_message_error += 1
        bot_message += f"{user.get('name')} {user.get('account')} 【失败】\n"
        if user:
            user['jiuxu'] = False
    elif error == "请求超时，可能是网络问题":
        print("出现请求超时情况，终止所有任务")
        bot_message_error += 1
        bot_message += f"{user.get('name')} {user.get('account')} 【失败】\n"
        if user:
            user['jiuxu'] = False
        sys.exit()
    elif isinstance(error, dict):
        if error.get('code') == 99999:
            print(f"{user.get('name')} {user.get('account')} 密码错误：{error.get('message')}")
            bot_message_error += 1
            bot_message += f"{user.get('name')} {user.get('account')} 【密码错误】\n"
        elif error.get('code') == 42004:
            print(f"{user.get('name')} {user.get('account')} 登录失败，请微信搜索关注“企校云”微信公众号在线联系客服！ {error.get('message')}")
            bot_message_error += 1
            bot_message += f"{user.get('name')} {user.get('account')} 登录失败，请微信搜索关注“企校云”微信公众号 在线联系客服！\n"
        else:
            print(f"错误Token回复，用户Token更新失败：{error}")
            bot_message_error += 1
            bot_message += f"{user.get('name')} {user.get('account')} 【失败】\n"
            if user:
                user['jiuxu'] = False
    else:
        print(f"未知错误：{error}")
        bot_message_error += 1
        bot_message += f"{user.get('name')} {user.get('account')} 【失败】\n"
        if user:
            user['jiuxu'] = False

# 格式化并处理 Cookies
def Env_cookie_format(cookies, file_name, data, from_config, version_config, platform_config):
    bot_message = "数据库具体信息\n"
    bot_message_error = 0
    bot_message_sure = 0
    cookies_count = len(cookies)
    bot_message += f'总共【{cookies_count}】个 COOKIE\n'
    print(f"共有 {cookies_count} 个cookie")
    print("开始格式化cookie任务")

    for idx, cookie in enumerate(cookies, 1):
        print(f"—————————————第{idx}个———————————————\ncookie: {cookie}\n")
        cookie_pairs = [pair.split('=') for pair in cookie.split(',')]
        Env_cookies_value = {}
        try:
            Env_cookies_value = {pair[0]: pair[1] for pair in cookie_pairs if len(pair) == 2}
            if len(Env_cookies_value) != len(cookie_pairs):
                raise ValueError("Invalid cookie format")
        except ValueError:
            extracted = {
                'name': re.search(r'name=([^,]+)', cookie),
                'account': re.search(r'account=([^,]+)', cookie)
            }
            name_lose = extracted['name'].group(1).strip() if extracted['name'] else "未知"
            account_lose = extracted['account'].group(1).strip() if extracted['account'] else "未知"
            bot_message += f"{name_lose} {account_lose} 【格式化失败】\n"
            print(f"{name_lose} {account_lose} 【格式化失败】\n")
            bot_message_error += 1
            continue

        #print(f"解析后的 Env_cookies_value: {Env_cookies_value}")

        bot_message, bot_message_sure, bot_message_error = validate_and_update_user(
            None, Env_cookies_value, data, file_name, bot_message, bot_message_sure, bot_message_error,
            from_config, version_config, platform_config
        )
    
    huizong_message = (
        f"{bot_message}———————————— \n数据库数据总报告\n总共：{cookies_count}个\n成功：{bot_message_sure}个\n失败：{bot_message_error}个"
    )
    print(huizong_message)
    
    return {
        "huizong_message": huizong_message,
        "total": cookies_count,
        "success": bot_message_sure,
        "failure": bot_message_error
    }

if __name__ == "__main__":
    file_name = os.path.join(weizhi, 'data', 'user.json')
    
    # 读取 user.json 文件
    try:
        with open(file_name, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"读取用户数据库失败：{e}")
        sys.exit(1)

    # 重置所有用户的 'jiuxu' 状态为 False
    for user in data.get('users', []):
        user['jiuxu'] = False

    # 获取 Cookies
    cookies = get_cookies()
    if cookies:
        # 确保从配置文件中加载了这些配置
        try:
            with open(f'{weizhi}{os.sep}data{os.sep}config.json', 'r', encoding="utf-8") as file:
                config_data = json.load(file)
                config = config_data['config'][0]
                from_config = config['from']
                version_config = config['version']
                platform_config = config['platform']
        except Exception as e:
            print(f"读取配置文件失败：{e}")
            sys.exit(1)

        # 调用 Env_cookie_format 并获取统计数据
        stats = Env_cookie_format(cookies, file_name, data, from_config, version_config, platform_config)
        
        # 查找并打印重复用户
        duplicate_users = find_duplicates(data['users'])
        if duplicate_users:
            print("发现重复用户:")
            for user in duplicate_users:
                print(f"姓名: {user.get('name')}, 账号: {user.get('account')}")
        else:
            print("未发现重复用户.")
    
        # 移除 'jiuxu' 为 False 的用户
        removed_users = [user for user in data['users'] if not user.get('jiuxu', True)]
        removed_count = len(removed_users)
        print(f"移除的用户数：{removed_count}")
        data['users'] = [user for user in data['users'] if user.get('jiuxu', True)]
        save_json_atomic(file_name, data)
        
        users_len = len(data['users'])
        print(f"【二次检查】用户信息库总共有 {users_len} 个")
    
        # 构建完整的推送消息
        huizong_message = (
            f"{stats['huizong_message']}\n"
            f"移除的用户数：{removed_count}\n"
            f"【二次检查】用户信息库总共有 {users_len} 个"
        )
        print(huizong_message)
        
        # 发送推送通知
        send_notify = load_send()
        if send_notify:
            print("发现推送服务 | 正在推送")
            send_notify("习讯云助手", huizong_message)
    else:
        print("失败：无法获取 cookies")
        sys.exit(1)

