#!/usr/bin/python3
# -*- coding: utf-8 -*-

import email.message
import smtplib

HOST = "smtp.qq.com"
PORT = 465


def send_qq_mail(sender, password, receiver_list, title, content, cc_list=None, bcc_list=None, debug=False):
    msg = email.message.EmailMessage()
    msg.set_content(content)
    msg["Subject"] = title
    msg["From"] = sender
    msg["To"] = ",".join(receiver_list)
    to_addrs = receiver_list
    if cc_list is not None:
        msg["Cc"] = ",".join(cc_list)
        to_addrs += cc_list
    if bcc_list is not None:
        to_addrs += bcc_list

    with smtplib.SMTP_SSL(HOST, PORT) as smtp:
        if debug:
            smtp.set_debuglevel(1)
        smtp.login(sender, password)
        smtp.sendmail(sender, to_addrs, msg.as_string())
