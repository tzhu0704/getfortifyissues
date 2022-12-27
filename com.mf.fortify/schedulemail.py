#!/usr/bin/env python
#-*-coding:utf-8-*-

import smtplib
import os
import shutil
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import datetime
import configparser
import logging
import http.cookiejar
import requests

import json
import urllib3
import urllib.parse
import os
from requests.auth import HTTPBasicAuth
import codecs
import getFortifyData
import base64
# 获取Mail MIMITEXT
def get_mimetext(subject, body,mailfrom, mailto,unprocessedpath,processedpath):

    headers = {'Content-Type': 'application/x-www-form-urlencoded','accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'}


    hasFile = False
    try:
        # 创建一个带附件的实例
        msg = MIMEMultipart()
        msg["Subject"] = subject
        msg["From"] = mailfrom
        msg["To"] = ",".join(mailto)  # 区别与给一个人发，指定某个人用 msg["To"] = _to 多个人用.join
        # msg.add_header(headers);
        # msg.add_header('Content-Disposition', 'attachment',
        #                filename='=?utf-8?b?' + base64.b64encode(fileName.encode('UTF-8')) + '?=')

        msg.add_header('Content-Disposition', 'attachment', filename=filename.split("/")[-1])
        # msg.add_header('Content-Disposition', 'attachment',
        #                 filename='=?utf-8?b?' + base64.b64encode(filename.encode('UTF-8')) + '?=')

        # 邮件正文内容
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        print("===================="+unprocessedpath)
        items = os.listdir(unprocessedpath)
        for item in items:
            attachFile=os.path.join(unprocessedpath,item)
            if os.path.isfile(attachFile):
                att = MIMEText(open(attachFile, 'rb').read(), 'base64', 'utf-8')
                att['Content-Type'] = 'application/octet-stream'
                # item = base64.b64encode(item.encode('UTF-8'))
                # att.add_header('Content-Disposition', 'attachment', filename=('gbk', '', item))
                # att['Content-Disposition'] = 'attachment;filename="' + item + ''  # filename 填什么，邮件里边展示什么
                att.add_header("Content-Disposition", "attachment", filename=("utf-8", "", item))
                # att['Content-Disposition'] = 'attachment;filename="'+item+''  # filename 填什么，邮件里边展示什么
                hasFile=True


                print(item)
                msg.attach(att)
                now = datetime.datetime.now()
                timestamp = now.strftime("%Y-%m-%d-%H-%M-%S")
                shutil.move(os.path.join(unprocessedpath,item),os.path.join(processedpath,timestamp+"@"+item))
                logging.info(item+"  processed")


    except Exception  as e:
        print(e.code, ':', e.reason)
        logging.error("Failed----" +e.reason)
    if hasFile:
        return msg
    else:
        return None

# 获取JSON
def requests_json(opener, url, jsonStr,action):
    headers = {
        'User-Agent':
            'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }
    get_request = urllib.request.Request(url=url, data=json.dumps(jsonStr).encode('utf-8'), headers=headers,
                                         method=action)
    get_response = opener.open(get_request)
    output = get_response.read().decode()

    return output

# 发送Mail, 使用阿里邮箱
def sendMimeMail(smtphost,port,user, password,mailfrom, mailto,msg):

    try:

        s = smtplib.SMTP(smtphost, port)
        s.login(user,password)
        s.sendmail(mailfrom,mailto,msg.as_string())
        s.quit()
        print("Success!")
    except Exception as e:
        logging.error("Failed----" +e.reason)

def getConfigValue(cf,section, name):
    value = cf.get(section, name)
    return value

try:
    #  实例化configParser对象
    cf = configparser.ConfigParser()
    #  读取config.ini文件
    cf.read("config.ini")
    _smtphost = getConfigValue(cf, "mail", "smtphost")
    _port = getConfigValue(cf, "mail", "port")
    _user = getConfigValue(cf, "mail", "user")
    _pwd = getConfigValue(cf, "mail", "password")
    _mailfrom = getConfigValue(cf, "mail", "mailfrom")


    mailto = getConfigValue(cf,"report","receipent")
    _recer = mailto.split(";")
    _unprocessed = getConfigValue(cf,"report","unprocessedpath")
    _processed = getConfigValue(cf,"report","processedpath")


    logpath = getConfigValue(cf,"log","logpath")

    filename = time.strftime('%Y-%m-%d', time.localtime(time.time()))

    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s \tFile \"%(filename)s\"[line:%(lineno)d] %(levelname)s %(message)s',
                        # datefmt='%a, %d %b %Y %H:%M:%S',
                        filename=logpath + filename + ".log",
                        filemode='a')
    #单位是秒
    frequency= getConfigValue(cf,"report","pollingseconds")
    if frequency!=None:
        frequency= int(frequency)
    else:
        frequency = 300
    while True:
        now = datetime.datetime.now()
        timestamp=now.strftime("%Y-%m-%d %H:%M:%S")
        logging.info("----------start to sendmail to snow------------")
        subject = "Fortify vulnerability report generated@"+timestamp
        body="check attached spreadsheet for Fortify vulnerability data."
        msg=get_mimetext(subject, body,_user, _recer,_unprocessed,_processed)
        if msg!=None:
            sendMimeMail(_smtphost,_port,_user, _pwd, _mailfrom, _recer, msg)

            logging.info("mail Sent Success!"+" @"+timestamp)
        else:
            print("NO Report generated!"+" @"+timestamp)
        time.sleep(frequency)

except Exception as e:
    print("Failed,%s"%e)
    logging.error("Failed,%s"%e)