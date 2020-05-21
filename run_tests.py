# coding=utf-8
import os
import time
import logging
import pytest
import click
import yagmail
import zipfile
from conftest import REPORT_DIR
from conftest import cases_path, rerun, max_fail,user,password,sendto,host

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

'''
说明：
1、用例创建原则，测试文件名必须以“test”开头，测试函数必须以“test”开头。
2、运行方式：
  > python3 run_tests.py  (回归模式，生成HTML报告)
  > python3 run_tests.py -m debug  (调试模式)
'''


def init_env(now_time):
    """
    初始化测试报告目录
    """
    os.mkdir(REPORT_DIR + now_time)
    os.mkdir(REPORT_DIR + now_time + "/image")


def zip_ya(start_dir):
    '''
    压缩测试报告文件夹
    :param start_dir:
    :return:
    '''
    start_dir = start_dir  # 要压缩的文件夹路径
    file_news = start_dir + '.zip'  # 压缩后文件夹的名字

    z = zipfile.ZipFile(file_news, 'w', zipfile.ZIP_DEFLATED)
    for dir_path, dir_names, file_names in os.walk(start_dir):
        f_path = dir_path.replace(start_dir, '')  # 这一句很重要，不replace的话，就从根目录开始复制
        f_path = f_path and f_path + os.sep or ''  # 实现当前文件夹以及包含的所有文件的压缩
        for filename in file_names:
            z.write(os.path.join(dir_path, filename), f_path + filename)
    z.close()
    return file_news


def send_mail(report):
    '''
    :param report: 测试报告压缩包
    :return: 发送邮件
    '''
    now_time = time.strftime("%Y_%m_%d_%H_%M_%S")
    yag = yagmail.SMTP(user=user,
                       password=password,
                       host=host)

    subject = "测试报告_" + now_time
    contents = "详情请查看附件！"
    try:
        yag.send(sendto,subject,contents,report)
    except BaseException as msg:
        print(msg)
    else:
        print("运行结束，已发送邮件♥❤！")


@click.command()
@click.option('-m', default=None, help='输入运行模式：run 或 debug.')
def run(m):
    if m is None or m == "run":
        logger.info("回归模式，开始执行✈✈！")
        now_time = time.strftime("%Y_%m_%d_%H_%M_%S")
        init_env(now_time)
        html_report = os.path.join(REPORT_DIR, now_time, "report.html")
        xml_report = os.path.join(REPORT_DIR, now_time, "junit-xml.xml")
        pytest.main(["-s", "-v", cases_path,
                     "--html=" + html_report,
                     "--junit-xml=" + xml_report,
                     "--self-contained-html",
                     "--maxfail", max_fail,
                     "--reruns", rerun])
        logger.info("运行结束，生成测试报告♥❤！")
        #report = zip_ya(REPORT_DIR + now_time)#压缩文件夹
        #send_mail(report)#发送邮件
    elif m == "debug":
        print("debug模式，开始执行！")
        pytest.main(["-v", "-s", cases_path])
        print("运行结束！！")


if __name__ == '__main__':
    run()
