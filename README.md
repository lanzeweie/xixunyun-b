<div align="center">

# -XiXunYun-

_✨ 超多用户实习打卡签到最终解决方案 ✨_

</div>

# 习讯云自动化数据库+习讯云自动化签到任务库
## 介绍
> 掌握用户的一些必要数据后就可以建立成数据库  
使用数据库让自动化签到任务库异步分发出所有签到任务   
支持`大规模数量用户` `不同用户不同时间签到` `真实随机提取签到` `支持随机休假`     
支持`消息推送汇总`   
~~支持 日志~~ (_日志打印支持，但是打包昨天日志的代码发生卡死，但是青龙面板支持日志保存，所有就没有管本地日志bug问题_)  

## 目录
- [-XiXunYun-](#-xixunyun-)
- [习讯云自动化数据库+习讯云自动化签到任务库](#习讯云自动化数据库习讯云自动化签到任务库)
  - [介绍](#介绍)
  - [目录](#目录)
    - [自动化数据库](#自动化数据库)
      - [**从COOKIE中解析用户的必要数据**](#从cookie中解析用户的必要数据)
      - [**数据库建立方式与逻辑**](#数据库建立方式与逻辑)
    - [自动化签到任务库](#自动化签到任务库)
  - [使用方式](#使用方式)
    - [目录结构](#目录结构)
    - [配置填写](#配置填写)
    - [本地运行](#本地运行)
    - [云端执行(青龙面板)](#云端执行青龙面板)
      - [定时任务](#定时任务)
      - [注意事项](#注意事项)
  - [日志、推送](#日志推送)
    - [打印](#打印)
    - [日志](#日志)
    - [推送](#推送)

### 自动化数据库  
#### **从COOKIE中解析用户的必要数据**   
`school_id` `name` `account` `model` `phone` `password` `time` `moth` `word_long` `word_latit` `word_name` `word_name_guishu` `home_latit` `home_long` `home_name` `home_name_guishu` `mothxiu` `mac`  


| 元素 | 值 | 例如 |
| ------- | ------- | ------- | 
| school_id | 学校代码 | 837 |
| name | 姓名 | 小明 |
| account | 学号 | 2132312 |
| model | 设备 | XiaoMi 15 |
| phone | 手机号 | 184818125 |
| password | 密码 | 123456 |
| time | 签到时间 | 9:00 |
| moth | 有效月份 | 2024-01:2024-06 |
| word_latit | 上班纬度 | 30.418515 |
| word_long | 上班经度 | 120.155115 |
| word_name | 上班完整地址 | 成都高新合作街道创新创业孵化基地 |
| word_name_guishu | 上班地址归属地 | 四川省成都市郫都区天骄路368号 |
| home_latit | 放假纬度 | 30.1181888 |
| home_long | 放假经度 | 120.1518545 |
| home_name | 放假完整地址 | 成都市金牛区欢乐谷售票处
| home_name_guishu | 放假地址归属地 | 四川省成都市金牛区西华大道41号 |
| mothxiu | 每月最大月休天数 | 5 |
| mac | 设备物理地址 | CA:DE:D9:FD:1E:F7 |

一个完整的地址 例如：
```
school_id=837,name=小明,account=2151511,model=XiaoMI 15,phone=1818151815,password=!321Zhoujinhan,time=9:00,moth=2024-01:2024-06,word_long=131,word_latit=232,word_name=四川省成都市郫都区三和街道,word_name_guishu=四川省成都市郫都区,home_latit=30.72243,home_long=104.0337,home_name=四川省成都市金牛区欢乐谷,home_name_guishu=四川省成都市金牛区西华大道16号,mothxiu=5,mac=CA:DE:D9:FD:1E:F7   
```

#### **数据库建立方式与逻辑**     
解析COOKIE，分析出用户的必要信息   
使用此信息访问`习讯云`的`api`获得Token，以此验证必要信息是否正确，最后通过验证的信息进行数据库建立  

### 自动化签到任务库
_需要依赖数据库运行_  
根据数据库将每一个用户都转为定时任务分发出去  
**重要依据**  
`token` `moth` `mothxiu`  
Token：用户身份  3.5
moth：检查用户是否在有限期内   
mothxiu：一个月的月休上限  
 
**逻辑**   
因为依据数据库，且相信数据库信息为最新，不再验证用户身份    
分析数据库 --> 验证当前用户是否在有效期 --> 概率判断今天类型签到/假期(每个月至少有90%概率休满最大月休息数,节假日强制放假) --> 使用`await`库分配任务[根据`time`定时] --> 达到定时的时间后执行签到


## 使用方式

本地运行与云端运行(青龙面板)区别在于COOKIE的获取方式  
因为是在本地上进行开发，COOKIE的方式设计的需要与云端一样。但是云端(青龙面包)可以使用相同的环境变量达到多个多用户的方式，而本地不行，为了通用性本地使用的json来完成多用户的模式。  

采用先建立数据库后执行任务库的顺序使用   
可以使用定时任务，每天检查一次数据库的信息   
在数据库检查完毕后在启动任务库  


### 目录结构
- data                   
  - `config.json`  习讯云配置文件
  - `user.json`   数据库任务程序存放用户的数据 
- log
  - `database.log`  数据库任务程序的日志(BUG：打包昨天的日志卡死)
  - `task.log`   任务程序的日志(BUG：打包昨天的日志卡死)
- `loglog.py`  调用的日志模块
- README.md
- requirements.txt
- `school-id.json` 学校代码
- `usr_qian.py` 签到模块
- `usr_record.py` 用户本月状况模块
- `usr_token.py` 通过账号密码获得用户token
- `usr_ua.py` 用户的数据
- `xixunyun_cookie.py` 数据库程序
- `xixunyun_sign.py` 打卡程序

### 配置填写
在`data\user.json` 填写习讯云的配置信息   
``version`` 习讯云版本号  
`from` 来源   
`platform` 系统  
`key` 习讯云打卡经纬度加密公钥，必须进行习讯云认证的公钥加密，否则打卡地址会被拒收。  
例如：
```
{
    "name":"习讯云配置文件",
    "config":[
        {
            "version": "4.9.7",
            "from":"app",
            "platform": "android",
            "key":""
        }
    ]
}
```   
### 本地运行 
```
pip install -r  requirements.txt
```
`env.json` 填写用户的COOKIE   


首先建立数据库  
```
python xixunyun_cookie.py
```
建立数据库后执行任务库  
```  
python xixunyun_sign.py
```  

### 云端执行(青龙面板)  
建立环境变量  `XIXUNYUN_COOKIE`  
填写 COOKIE 即可，多个用户重复建立即可 

#### 定时任务
强烈建议每日执行数据库 `xixunyun_cookie.py`   
强烈建议在数据库执行后执行任务库 `xixunyun_sign.py`

#### 注意事项  
一切都是为了模拟真实用户
_如果用户的签到时间**小于**任务库分配任务的时间则会立即执行_   
_定时时间有小概率事件发生随机提前【1-5分钟】_  
_有小概率发生不会休满一个月最大月休数_  

## 日志、推送
### 打印
控制台会默认输出消息  
### 日志  
`loglog.py` 日志程序  
`log\database.log` 数据库日志  
`log\task.log` 任务库日志  
日志自动会压缩昨天的日志成`zip`包(BUG未修复，压缩卡死)
### 推送  
变量 `bot_message` 存放推送的信息   
<img src="./README/1.jpg" alt="图片1" style="float: left; margin-right: 10px;" width="300">   
<img src="./README/2.jpg" alt="图片2" style="float: left; margin-right: 10px;" width="300">      

(青龙面板)      
直接配置青龙面板本身的机器人推送即可  

