from __future__ import annotations
import csv, json
from pathlib import Path
from typing import Any, Dict
from .models import SessionResult

def append_history(res:SessionResult, path:Path)->None:
    hist=[]
    if path.exists():
        try: hist=json.loads(path.read_text(encoding='utf-8') or '[]')
        except json.JSONDecodeError:
            path.with_suffix('.bak.json').write_text(path.read_text(encoding='utf-8'), encoding='utf-8')
            hist=[]
    rec={'timestamp':res.timestamp,'user':res.user,'total':res.total,'correct':res.correct,'incorrect':res.incorrect,'percentage':res.percentage,'per_domain':res.per_domain,'wrong_question_ids':res.wrong_question_ids,'answers':[a.__dict__ for a in res.answers]}
    hist.append(rec)
    path.write_text(json.dumps(hist, indent=2), encoding='utf-8')

def export_csv(res:SessionResult, p:Path)->None:
    with p.open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f)
        w.writerow(['timestamp','user','total','correct','incorrect','percentage'])
        w.writerow([res.timestamp,res.user,res.total,res.correct,res.incorrect,res.percentage])
        w.writerow([]); w.writerow(['Domain','Correct','Total','%'])
        for d,st in sorted(res.per_domain.items()):
            c,t=st['correct'],st['total']; pct=round((c/t)*100,2) if t else 0.0
            w.writerow([d,c,t,pct])

def export_html(res:SessionResult, p:Path)->None:
    rows=''.join([f"<tr><td>{d}</td><td>{st['correct']}</td><td>{st['total']}</td><td>{round((st['correct']/st['total'])*100,2) if st['total'] else 0}%</td></tr>" for d,st in sorted(res.per_domain.items())])
    html=f"""<!doctype html><html><head><meta charset='utf-8'><title>Exam Summary</title><style>table,td,th{{border:1px solid #999;border-collapse:collapse;padding:6px;}}</style></head><body><h2>Exam Summary</h2><p><b>Timestamp:</b> {res.timestamp} &nbsp; <b>User:</b> {res.user}</p><p><b>Score:</b> {res.correct}/{res.total} ({res.percentage}%)</p><h3>Per-Domain Performance</h3><table><tr><th>Domain</th><th>Correct</th><th>Total</th><th>%</th></tr>{rows}</table></body></html>"""
    p.write_text(html, encoding='utf-8')

def export_anki_wrong(res:SessionResult, p:Path, qmap:Dict[int,Dict[str,Any]])->None:
    with p.open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f); w.writerow(['Front','Back','Tags'])
        wrong=set(res.wrong_question_ids)
        for a in res.answers:
            if a.question_id not in wrong: continue
            q=qmap.get(a.question_id); 
            if not q: continue
            front=q.get('question','')+'<br>'+ '<br>'.join([f"{k}. {q.get('options',{}).get(k,'')}" for k in ['A','B','C','D']])
            back=f"Correct: {a.correct} — {q.get('answer_text','')}"; tag=a.domain.replace(' ','_').replace('&','and')
            w.writerow([front, back, tag])
