# -*- coding: utf-8 -*-
import re

def is_doi(msg: str) -> bool:
    doi = re.findall(r'\b10\.\d{4,9}/[-.;()/:\w]+', msg, flags=re.IGNORECASE)
    if len(doi) > 0:
        return True
    else:
        return False

def resolve_doi(msg: str) -> str:
    doi = re.findall(r'\b10\.\d{4,9}/[-.;()/:\w]+', msg, flags=re.IGNORECASE)
    if len(doi) > 0:
        return doi[0]
    else:
        return ''
