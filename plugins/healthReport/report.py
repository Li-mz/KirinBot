import nonebot

import requests
from bs4 import BeautifulSoup

from time import sleep
from random import random
from datetime import datetime, timedelta

from .config import username, password, report_qq, province_code, city_code, is_inschool
from config import self_id


def get_token_from_response(response: requests.Response):
    soup = BeautifulSoup(response.content)
    return soup.find('input', attrs={'name': '_token'})['value']


async def login(session, username, password):
    loginurl = r'https://passport.ustc.edu.cn/login?service=https%3A%2F%2Fweixine.ustc.edu.cn%2F2020%2Fcaslogin'
    formdata = {'model': 'uplogin.jsp', 'service': r'https://weixine.ustc.edu.cn/2020/caslogin',
                'username': username, 'password': password, 
                'warn': '', 'showCode': '', 'button': ''}
    return session.post(loginurl, data=formdata)


async def daily_report(session, token):
    form_data = dict(
        _token=token,
        now_address=1, gps_now_address='', now_province=province_code, gps_province='', now_city=city_code, gps_city='',
        now_detail='', is_inschool=is_inschool, body_condition=1, body_condition_detail='', now_status=2, now_status_detail='',
        has_fever=0,
        last_touch_sars=0, last_touch_sars_date='', last_touch_sars_detail='',
        other_detail=''
    )
    header = {
        'user-agent': r'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
        'accept': r'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cache-control': 'max-age=0',
        'content-length': '480',
        'content-type': r'application/x-www-form-urlencoded',
        'origin': r'https://weixine.ustc.edu.cn',
        'referer': r'https://weixine.ustc.edu.cn/2020/home',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1'
    }
    return session.post(r'https://weixine.ustc.edu.cn/2020/daliy_report', data=form_data, headers=header)


async def weekly_report(session, token):
    form_data = dict(
        _token=token,
        start_date=datetime.now().strftime('%Y-%m-%d'),
        end_date=(datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
    )
    header = {
        'user-agent': r'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
        'accept': r'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cache-control': 'max-age=0',
        'content-length': '480',
        'content-type': r'application/x-www-form-urlencoded',
        'origin': r'https://weixine.ustc.edu.cn',
        'referer': r'https://weixine.ustc.edu.cn/2020/apply/daliy',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1'
    }
    return session.post(r'https://weixine.ustc.edu.cn/2020/apply/daliy/post', data=form_data, headers=header)


@nonebot.scheduler.scheduled_job('cron', id='healthReport', hour=0)
async def healthReport():
    sleep(random() * 600)  # randomly sleep 0-10 minutes

    session = requests.session()
    r = await login(session, username, password)
    token = get_token_from_response(r)
    await daily_report(session, token)

    if report_qq:
        bot = nonebot.get_bot()
        await bot.send_private_msg(user_id=report_qq, message='今日已健康打卡', self_id=self_id)


@nonebot.scheduler.scheduled_job('cron', id='healthReportWeekly', day_of_week=0, hour=1)
async def healthReportWeekly():
    session = requests.session()
    await login(session, username, password)

    r = session.get('https://weixine.ustc.edu.cn/2020/')
    token = get_token_from_response(r)
    await weekly_report(session, token)

    if report_qq:
        bot = nonebot.get_bot()
        await bot.send_private_msg(user_id=report_qq, message='已报备', self_id=self_id)
