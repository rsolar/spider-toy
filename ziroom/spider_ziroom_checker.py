#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
import os
import traceback

import bs4
import requests
import requests.adapters

from utils.rotate_logger import init_logger
from utils.send_qq_mail import send_qq_mail

logger = init_logger(os.path.join(os.path.dirname(__file__), "..", "log", os.path.basename(__file__) + ".log"))

MAX_RETRIES = 5
TIMEOUT = 10
headers = {
    "User-Agent": "Chrome"
}


def get_room_info(url):
    s = requests.Session()
    s.mount("http://", requests.adapters.HTTPAdapter(max_retries=MAX_RETRIES))
    r = s.get(url, headers=headers, timeout=TIMEOUT)
    if r is None:
        return None
    soup = bs4.BeautifulSoup(r.content, "lxml")
    # logger.debug(soup.prettify())
    room = []

    hide_info = soup.find("div", class_="hide")
    room_id = hide_info.find("input", id="room_id")["value"]
    house_id = hide_info.find("input", id="house_id")["value"]
    room.append(("url", url))
    room.append(("room_id", room_id))
    room.append(("house_id", house_id))

    outer = soup.select("body > div.area.clearfix")
    if len(outer) != 1:
        return None
    outer = outer[0]

    right = outer.find("div", class_="room_detail_right")
    details = [detail.get_text(strip=True) for detail in right.find("ul", class_="detail_room").find_all("li")]
    details = [" ".join(detail.replace("\n", " ").split()) for detail in details]
    room.append(("名称", right.find("div", class_="room_name").h2.get_text(strip=True)))
    for detail in details:
        room.append(tuple(map(lambda x: x.strip(), detail.split("："))))

    detail_json_r = s.get("http://sz.ziroom.com/detail/info?id={}&house_id={}".format(room_id, house_id),
                          headers=headers, timeout=10)
    if detail_json_r is not None:
        detail_json = detail_json_r.json()
        room.append((detail_json["data"]["air_part"]["vanancy"]["promise"].strip(),
                     "{}，{}".format(detail_json["data"]["air_part"]["vanancy"]["vanancy_day"],
                                    detail_json["data"]["air_part"]["vanancy"]["status"])))
        room.append(tuple(
            map(lambda x: x.strip(), detail_json["data"]["air_part"]["air_quality"]["show_info"]["status"].split(":"))))

    logger.debug(room)
    return room


def gen_report_text(room):
    text = "\r\n".join("：".join(item) for item in room)
    logger.info(text)
    logger.info(len(text))
    return text


def spider_ziroom_checker():
    parser = argparse.ArgumentParser(description="检查指定租房房源（整租）URL状态")
    parser.add_argument("send_address", type=str, help="发件邮箱地址")
    parser.add_argument("password", type=str, help="发件邮箱密码")
    parser.add_argument("receive_address", type=str, help="收件邮箱地址，以\",\"分隔")
    parser.add_argument("url", nargs="+", type=str, help="待检查URL列表")
    args = parser.parse_args()

    sender = args.send_address
    password = args.password
    receiver_list = args.receive_address.split(",")
    urls = args.url
    title = "自如租房房源状态监控"
    for url in urls:
        room = get_room_info(url)
        if room is None:
            logger.error("{} check failed".format(url))
            continue
        content = gen_report_text(room)
        try:
            send_qq_mail(sender, password, receiver_list, title, content)
        except Exception:
            logger.error(traceback.format_exc())
        logger.info("{} check finished".format(url))


if __name__ == "__main__":
    spider_ziroom_checker()
