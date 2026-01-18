from __future__ import annotations
from typing import Dict, List
from .models import AnswerRecord, SessionResult

def compute_domain_stats(ans:List[AnswerRecord])->Dict[str,Dict[str,int]]:
    st={}
    for a in ans:
        d=st.setdefault(a.domain,{"correct":0,"total":0})
        d['total']+=1
        if a.is_correct: d['correct']+=1
    return st

def build_session_result(ans:List[AnswerRecord], user:str)->SessionResult:
    tot=len(ans); cor=sum(1 for a in ans if a.is_correct); inc=tot-cor
    pct=round((cor/tot)*100,2) if tot else 0.0
    per=compute_domain_stats(ans)
    wrong=[a.question_id for a in ans if not a.is_correct]
    from datetime import datetime, timezone
    ts=datetime.now(timezone.utc).isoformat()
    return SessionResult(ts,user,tot,cor,inc,pct,per,wrong,ans)
