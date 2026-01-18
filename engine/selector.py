from __future__ import annotations
import random
from typing import Dict, List, Optional
from .models import Question

def filter_pool(qs:List[Question], include_tags:List[str], exclude_tags:List[str], mi:Optional[int], ma:Optional[int])->List[Question]:
    def ok(q:Question)->bool:
        if include_tags and not any(t.lower() in [x.lower() for x in q.tags] for t in include_tags): return False
        if exclude_tags and any(t.lower() in [x.lower() for x in q.tags] for t in exclude_tags): return False
        if mi is not None and (q.difficulty or 0) < mi: return False
        if ma is not None and (q.difficulty or 0) > ma: return False
        return True
    return [q for q in qs if ok(q)]

def select_questions(qs:List[Question], total:int, weights:Dict[str,float], shuffle:bool=True)->List[Question]:
    by={}
    for q in qs: by.setdefault(q.domain,[]).append(q)
    sel=[]
    for d,w in weights.items():
        need=round(total*float(w)); pool=by.get(d,[])
        if pool: sel+=random.sample(pool, min(need,len(pool)))
    if len(sel)<total:
        rem=[q for q in qs if q not in sel]
        short=total-len(sel)
        if rem: sel+=random.sample(rem, min(short,len(rem)))
    sel=sel[:total]
    if shuffle: random.shuffle(sel)
    return sel

def blueprint_select(qs:List[Question], bp:Dict[str,int], shuffle:bool=True)->List[Question]:
    by={}
    for q in qs: by.setdefault(q.domain,[]).append(q)
    pick=[]
    for d,c in bp.items():
        pool=by.get(d,[])
        if pool: pick+=random.sample(pool, min(c,len(pool)))
    if shuffle: random.shuffle(pick)
    return pick
