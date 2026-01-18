from __future__ import annotations
import time
from typing import Callable, List, Dict
from .models import Question, SessionConfig, AnswerRecord
from .analytics import compute_domain_stats

class ExamSession:
    def __init__(self, questions:List[Question], config:SessionConfig)->None:
        self.original_pool=questions[:]
        self.questions=questions[:]
        self.config=config
        self.answers:List[AnswerRecord]=[]
        self.start_epoch=None; self.deadline_epoch=None
        self.current_index=0
    def start(self)->None:
        self.start_epoch=time.time(); self.deadline_epoch=self.start_epoch+(self.config.time_limit_minutes*60)
    def remaining_seconds(self)->int:
        if self.deadline_epoch is None: return self.config.time_limit_minutes*60
        return max(0,int(self.deadline_epoch-time.time()))
    def is_time_up(self)->bool: return self.remaining_seconds()<=0
    def _pick_next_adaptive(self)->Question|None:
        if not self.questions: return None
        st=compute_domain_stats(self.answers)
        dom_w={}
        for q in self.questions:
            d=st.get(q.domain,{"correct":0,"total":0}); acc=(d['correct']/d['total']) if d['total'] else 0.5
            dom_w[q.domain]=1.0-acc
        total=sum(dom_w.values()) or 1.0
        from random import choices
        by={};
        for q in self.questions: by.setdefault(q.domain,[]).append(q)
        doms=list(by.keys()); weights=[(dom_w[d]/total) for d in doms]
        chosen=choices(doms,weights,k=1)[0]
        for i,q in enumerate(self.questions):
            if q.domain==chosen: return self.questions.pop(i)
        return self.questions.pop(0)
    def _pick_next_linear(self)->Question|None:
        if self.current_index>=len(self.questions): return None
        q=self.questions[self.current_index]; self.current_index+=1; return q
    def run(self, ui_ask:Callable[[Question,int,int,int],str], ui_feedback:Callable[[bool,Question],None])->None:
        self.start(); total=len(self.questions); answered=0
        while not self.is_time_up():
            q=self._pick_next_adaptive() if self.config.adaptive else self._pick_next_linear()
            if q is None: break
            remaining=self.remaining_seconds(); choice=ui_ask(q, answered+1, total, remaining)
            if choice.upper()=='P':
                if not self.config.adaptive: self.current_index-=1
                continue
            correct=(choice.upper()==q.answer.upper())
            self.answers.append(AnswerRecord(q.id, choice.upper(), q.answer.upper(), correct, q.domain))
            answered+=1
            if self.config.reveal_mode=='after': ui_feedback(correct, q)
            if answered>=total: break
