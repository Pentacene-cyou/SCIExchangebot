""" sciexchangebot module get recent 10 unhelped url """
from sciexchangebot import config
from ..database import get_all_unhelped_msg_id

CHANNEL_NAME = config['telegram']['channel_name']

def get_recent_unhelped_url() -> str:
    recent_ten_unhelped_url = ''
    all_unhelped_msg_id_list = get_all_unhelped_msg_id()
    pre_url = f'https://t.me/{CHANNEL_NAME}/'
    for i in range(0, 9):
        recent_ten_unhelped_url = (f'{recent_ten_unhelped_url}\n{pre_url}{all_unhelped_msg_id_list[i]}')
    return f'Please also pay attention to the other literature that has not been found.\n{recent_ten_unhelped_url}'
