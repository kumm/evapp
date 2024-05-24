import json
from datetime import datetime, timedelta
from email.utils import formataddr

from commands.get_statements import get_statements
from ggle.MailClient import MailClient
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate

from wise.Account import Account


def mail_statements(gmail_client: MailClient, account: Account, to_addr, from_addr, year, month):
    statements = get_statements(account, year, month)
    msg = __build_mime_msg(
        send_to=to_addr,
        send_from=from_addr,
        subject=f'bankszámlakivonatok - {year}.{month:02d}.',
        statements=statements
    )
    labels = gmail_client.get_labels()['labels']
    label_map = {label['name']: label['id'] for label in labels}
    label_ids = [__get_or_create_label(gmail_client, label_map, name) for name in ['EvApp', 'Bankszámlakivonatok']]
    gmail_client.send(msg.as_bytes(), label_ids)


def __get_or_create_label(gmail_client: MailClient, label_map: dict, name: str):
    label_id = label_map.get(name)
    if label_id is None:
        return gmail_client.create_label(name)['id']
    else:
        return label_id


def __build_mime_msg(send_to, send_from, statements, subject):
    msg = MIMEMultipart()
    msg['From'] = formataddr(send_from)
    msg['To'] = formataddr(send_to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject
    msg.attach(MIMEText(""))
    for name in statements:
        part = MIMEApplication(statements[name], Name=name)
        part['Content-Disposition'] = f'attachment; filename="{name}"'
        msg.attach(part)
    return msg


# def mail_statements(send_to, send_from, subject, statements):
#     msg = build_mime_msg(send_to, send_from, statements, subject)
#
#     context = ssl.create_default_context()
#
#     with smtplib.SMTP_SSL(smtp_config.smtp_ssl_host, smtp_config.smtp_ssl_port, context=context) as server:
#         server.login(smtp_config.login, smtp_config.password)
#         server.send_message(msg)
#         server.close()
