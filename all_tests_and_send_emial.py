#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@contact:    yufei@baixing.com
@desc:       邮件通知
"""
import argparse
import unittest
import os
import sys
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email import encoders
from report_info import HTMLTestRunner
import configparser



def send_mail(file_new,report_folder):
    # 发送报告需要在report目录内配置email相关信息
    print(report_folder)
    email_info = report_folder + 'email.ini'
    config = configparser.ConfigParser()
    config.read(email_info)
    mail_host = config.get('DEFAULT','mail_host')
    mail_from = config.get('DEFAULT','mail_from')
    mail_pass = config.get('DEFAULT','mail_pass')
    mail_port = config.getint('DEFAULT','mail_port')
    mail_to = eval(config.get('DEFAULT','mail_to'))

    msg = MIMEMultipart()
    # 构造附件1，传送当前目录下的 report
    f = open(file_new, 'rb')
    content = f.read()
    f.close()
    mail_body = MIMEText(content, _subtype='html', _charset='utf-8')
    msg.attach(mail_body)
    att1 = MIMEApplication('application','octet-stream')
    att1.set_payload(content)
    encoders.encode_base64(att1)
    att1.add_header('Content-Disposition', 'attachment; filename="Detail_Reprot.html"')
    msg.attach(att1)
    msg['Subject'] = u"自动化测试报告"
    # 定义发送时间（不定义的可能有的邮件客户端会不显示发送时间）
    msg['date'] = time.strftime('%a, %d %b %Y %H:%M:%S %z')

    try:
        smtp = smtplib.SMTP(mail_host, mail_port)
        smtp.starttls()
        # 发件人的用户名密码
        smtp.login(mail_from, mail_pass)
        smtp.sendmail(mail_from, mail_to, msg.as_string())
        smtp.quit()
        print("Email has been sent!")
    except smtplib.SMTPServerDisconnected:
        print("Error: Cannot send Email")


def send_report(report_folder):
    result_dir = report_folder
    lists = os.listdir(result_dir)
    lists.sort(key=lambda fn: os.path.getmtime(result_dir + "/" + fn))
    # 找到最新生成的文件
    file_new = os.path.join(result_dir, lists[-1])
    print(file_new)
    # 调用发邮件模块
    send_mail(file_new,report_folder)


def gen_test_suite(test_case_dir):
    # pattern用来匹配/test_case目录下哪些用例加入本次运行
    discover = unittest.defaultTestLoader.discover(test_case_dir, pattern='test_*.py',
                                                   top_level_dir=None)
    return discover

def main():
    # 将项目的目录加载到系统变量中
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", help="test_case directory")
    args = parser.parse_args()
    test_case_dir = args.d
    root = os.path.join(test_case_dir, '..')
    # 获取系统当前日期
    now = time.strftime("%Y-%m-%d %H_%M_%S")
    os.environ['WEBSERVICE_ITERATION_RUN_TIME'] = now

    report_folder = root + os.sep + 'report' + os.sep
    filename = report_folder + now + '_result.html'  # 测试报告的路径名
    fp = open(filename, 'wb+')

    runner = HTMLTestRunner.HTMLTestRunner(
        stream=fp,
        title=u'SmokeTest自动化测试报告',
        description=u'用例执行情况：',
        verbosity=2,
        )
    all_test_units = gen_test_suite(test_case_dir)
    # 获得报错数


    err_num = runner.run(all_test_units).__repr__()  #执行case



    failcasename = HTMLTestRunner.failcasename
    fp.close()  # 关闭生成的报告


    send_report(report_folder)  # 发送报告


    if err_num == 0:
        sys.exit(0)
    else:
        print("%s"%failcasename)
        sys.exit(1)


if __name__ == '__main__':
    main()
