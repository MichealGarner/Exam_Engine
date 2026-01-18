from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, List
from .models import Question

def load_questions(p:Path)->List[Question]:
    if not p.exists():
        raise FileNotFoundError(p)
    out=[]
    with p.open('r',encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            obj=json.loads(line)
            q=Question(
                id=int(obj['id']), domain=obj['domain'], type=obj.get('type','mcq'),
                question=obj['question'], options=obj['options'], answer=str(obj['answer']).upper(),
                answer_text=obj.get('answer_text',''), tags=obj.get('tags',[]),
                difficulty=obj.get('difficulty'), media=obj.get('media',[])
            )
            if q.answer not in q.options: raise ValueError('bad answer')
            out.append(q)
    return out

def load_metadata(p:Path)->Dict:
    if not p.exists(): raise FileNotFoundError(p)
    return json.loads(p.read_text(encoding='utf-8'))
