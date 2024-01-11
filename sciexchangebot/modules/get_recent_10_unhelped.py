""" sciexchangebot module get recent 10 unhelped url """
from sciexchangebot import config
from ..database import get_all_unhelped_msg_id

def get_recent_unhelped_url() -> str:
    recent_ten_unhelped_url = ''
    all_unhelped_msg_id_list = get_all_unhelped_msg_id()
    pre_url = f'https://t.me/{config["telegram"]["workgroupname"]}/'
    for i in range(0, 9):
        recent_ten_unhelped_url = (f'{recent_ten_unhelped_url}\n{pre_url}{all_unhelped_msg_id_list[i]}')
    return f'也请您关注一下其他未被找到的文献们\nPlease check this list to help others.\n{recent_ten_unhelped_url}'
