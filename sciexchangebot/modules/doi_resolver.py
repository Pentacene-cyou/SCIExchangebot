# -*- coding: utf-8 -*-

import aiohttp
import re
from bs4 import BeautifulSoup


WHITELIST_DOMAINS = []

def is_legal_url(msg: str) -> bool:
    if msg.startswith("https://"):
        return True
    elif msg.startswith("http://"):
        return True
    elif msg.startswith("doi.org"):
        return True
    else:
        return False

def is_doi(msg: str) -> bool:
    doi = re.findall(r'(?:https{,1}://doi.org/(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?!["&\'<>])\S)+))', msg, flags=re.IGNORECASE)
    if doi:
        return True
    else:
        msg = f'https://{msg}'
        doi = re.findall(r'(?:https{,1}://doi.org/(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?!["&\'<>])\S)+))', msg, flags=re.IGNORECASE)
        if doi:
            return True
        return False

async def resolve_doi(url):
    doi = re.findall(r'(?:https{,1}://doi.org/(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?!["&\'<>])\S)+))', url, flags=re.IGNORECASE)
    if doi:
        return doi[0]
    
    if re.findall('^(https{,1}://science.sciencemag.org/\S+)$', url):
        return await resolve_doi_science(url)
    
    async with aiohttp.request('GET', url) as resp:
        assert resp.status == 200
        content = await resp.text()
    if isinstance(content, str):
        content = content.encode('utf-8')
    soup = BeautifulSoup(content, 'html.parser')
    page_text_tokens = str(soup.html).split()
    for token in page_text_tokens:
        doi = re.findall(r'(?:https{,1}://doi.org/(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?!["&\'<>])\S)+))', token)
        if doi:
            return doi[0]
    return None


async def resolve_doi_science(url):
    async with aiohttp.request('GET', url) as resp:
        assert resp.status == 200
        content = await resp.text()
    if isinstance(content, str):
        content = content.encode('utf-8')
    soup = BeautifulSoup(content, 'html.parser')
    meta = soup.find_all(class_='meta-line')
    if not meta: return None
    meta = meta[0].text
    doi = re.findall(r'(?:DOI:\s*(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?!["&\'<>])\S)+)', meta)
    if doi:
        return doi[0]
    return None