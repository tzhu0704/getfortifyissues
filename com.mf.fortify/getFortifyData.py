#!/usr/bin/env python
#-*-coding:utf-8-*-

import smtplib
import os
import shutil
from flask import Flask, request, jsonify
from flask_restful import Resource, Api, reqparse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import datetime
import configparser
import logging

import json

import urllib.parse
import os

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


def get_withheaders( token,url):
    headers = {
        'User-Agent':
            'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }

    headers["Authorization"]=token;
    req = urllib.request.Request(url, headers=headers)
    response = urllib.request.urlopen(req)
    output = response.read().decode()
    # print("output----" +output)
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

def matchArray(array, name):
    result=False
    for item in array:
        if(item==name):
            result=True
            break
    return result

def getConfigValue(cf,section, name):
    value = cf.get(section, name)
    return value

def getIssueData(project_id,scandate,friority,primaryTag):
    list = []

    # 测试获取数据
    serverurl = getConfigValue(cf, "server", "serverurl")
    token = getConfigValue(cf, "server", "token")
    token = "FortifyToken " + token;

    if(primaryTag==""):
        primaryTag = getConfigValue(cf, "server", "primaryTag")
    tags = primaryTag.split('#')

    if (friority == ""):
        friority = getConfigValue(cf, "server", "friority")
    friorities = friority.split('#')

    try:
        if(not isinstance(now, datetime.datetime) or scandate==None):
            scandate=datetime.datetime(2000, 1, 1)



        severity = getConfigValue(cf, "server", "severity")
        print("severity--" + severity)

        logging.info("----------project_id-----" + project_id)
        logging.info("----------scandate-----" +scandate.strftime('%Y-%m-%d %H:%M:%S'))
        logging.info("----------friority-----"+friority)
        logging.info("----------primaryTag-----"+primaryTag)


        projecturl = serverurl + "/ssc/api/v1/projectVersions"
        jsonStr = get_withheaders(token, projecturl)

        # 将 JSON 对象转换为 Python 字典
        projects = json.loads(jsonStr)
        items = projects['data']
        for item in items:

            if(project_id!="" and project_id!= str(item["id"])):
                continue
            projectissuesUrl = serverurl + "/ssc/api/v1/projectVersions/" + str(item["id"]) + "/issues"+"?start=0&limit=3000"
            # print(projectissuesUrl)
            jsonStr = get_withheaders(token, projectissuesUrl)
            projectissues = json.loads(jsonStr)
            issueitems = projectissues['data']

            projectname = item["project"].get("name")
            projectid = item["project"].get("id")
            print("---prejectname-----" + item["project"].get("name")+"--issueitems--"+str(len(issueitems)))
            logging.info("---prejectname-----" + item["project"].get("name") + "--issueitems--" + str(len(issueitems)))
            for issueitem in issueitems:
                try:
                    if (str(issueitem["issueStatus"]) == "Reviewed"):
                        tag0 = str(issueitem["primaryTag"])
                        friority0 = str(issueitem["friority"])
                        severity0 = issueitem["severity"]
                        scandate0 = issueitem["foundDate"]
                        scandate0 = scandate0.replace(".000+0000","")
                        scandate0 = scandate0.replace("T", " ")
                        # print("---------------scandate0-------------" + scandate0)
                        scandate0 = datetime.datetime.strptime(scandate0, '%Y-%m-%d %H:%M:%S')

                        # print("----------scandate------------------" + scandate)

                        if (matchArray(tags, tag0) and matchArray(friorities, friority0) and  scandate0 >scandate and severity0 > float(severity)):
                            issueDetailsUrl = serverurl + "/ssc/api/v1/issueDetails/" + str(issueitem["id"])
                            # print(issueDetailsUrl)
                            jsonStr = get_withheaders(token, issueDetailsUrl)
                            issueDetail = json.loads(jsonStr)
                            issueitem = issueDetail['data']

                            issue = {}

                            issue["projectid"] = projectid
                            issue["projectname"] = projectname
                            issue["issueid"] = issueitem["id"]
                            issue["issueName"] = issueitem["issueName"]
                            issue["lineNumber"] = issueitem["lineNumber"]
                            print("sourceFile0-----------------------------------------" )
                            if ("sourceFile" in issueitem):
                                print("sourceFile1-----------------"+issue["sourceFile"])
                            else:
                                print("sourceFile2-----------------")
                            if(issueitem.get("sourceFile")!=None):
                              issue["sourceFile"] = issueitem["sourceFile"]
                            else:
                              issue["sourceFile"] = ""

                            print("sourceFile3-----------------"+issue["sourceFile"])

                            issue["fullFileName"] = issueitem["fullFileName"]
                            issue["sourceLine"] = issueitem["sourceLine"]
                            if (issueitem.get("source") != None):
                              issue["source"] = issueitem["source"]
                            else:
                              issue["source"] = ""

                            if (issueitem.get("sourceContext") != None):
                              issue["sourceContext"] = issueitem["sourceContext"]
                            else:
                              issue["sourceContext"] = ""

                            if (issueitem.get("className") != None):
                              issue["className"] = issueitem["className"]
                            else:
                              issue["className"] = ""

                            if (issueitem.get("impact") != None):
                                issue["impact"] = issueitem["impact"]
                            else:
                                issue["impact"] = ""

                            if (issueitem.get("friority") != None):
                                issue["friority"] = issueitem["friority"]
                            else:
                                issue["friority"] = ""

                            if (issueitem.get("severity") != None):
                                issue["severity"] = issueitem["severity"]
                            else:
                                issue["severity"] = ""

                            if (issueitem.get("detail") != None):
                                issue["detail"] = issueitem["detail"]
                            else:
                                issue["detail"] = ""

                            if (issueitem.get("recommendation") != None):
                                issue["recommendation"] = issueitem["recommendation"]
                            else:
                                issue["recommendation"] = ""


                            issue["foundDate"] = issueitem["foundDate"]

                            list.append(issue)
                except Exception as e:
                    print("Failed,%s" % e)
                    logging.error("Failed,%s" % e)
    except Exception as e:
        print("Failed,%s" % e)
        logging.error("Failed,%s" % e)
    print("Total issues-------------"+str(len(list)))
    logging.info("----------Total issus-----"+str(len(list)))


    retStr=json.dumps(list, ensure_ascii=False)
    logging.info( retStr)
    return retStr



# 正式开始运行。。。

try:
    #  实例化configParser对象
    cf = configparser.ConfigParser()
    #  读取config.ini文件
    cf.read("config.ini")
    # print("----------start to achieve Fortify Data to snow------------")

    logpath = getConfigValue(cf,"log","logpath")

    filename = time.strftime('%Y-%m-%d', time.localtime(time.time()))

    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s \tFile \"%(filename)s\"[line:%(lineno)d] %(levelname)s %(message)s',
                        # datefmt='%a, %d %b %Y %H:%M:%S',
                        filename=logpath + filename + ".log",
                        filemode='a')
    #单位是秒

    now = datetime.datetime.now()
    timestamp=now.strftime("%Y-%m-%d %H:%M:%S")
    logging.info("----------start to achieve Fortify Data to SMAX------------")
   

    # 启动监听

    host = '0.0.0.0'
    port = getConfigValue(cf,"server","listenport")
    app = Flask(__name__)
    api = Api(app)

    @app.route('/getFortifyData', methods=['post'])
    def get_FortifyData():
        # data = self.parser.parse_args()
        if not request.data:  # 检测是否有数据
            return ('fail')

        vue = request.data.decode('utf-8')
        # 获取到POST过来的数据，因为我这里传过来的数据需要转换一下编码。根据晶具体情况而定
        data = json.loads(vue)
        projectid = data.get("projectid")
        scandate = data.get("scandate")
        friority = data.get("friority")
        primaryTag = data.get("primaryTag")

        issuedata = getIssueData(projectid, scandate, friority, primaryTag);
        return issuedata
        # 返回JSON数据。


    if __name__ == '__main__':
        app.run(host=host, port=port, debug=True)

except Exception as e:
    print("Failed,%s"%e)
    logging.error("Failed,%s"%e)