from __future__ import annotations
import os, subprocess, sys
from pathlib import Path
from typing import List, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich.text import Text
from rich.markdown import Markdown
from .models import Question, SessionConfig, AnswerRecord, SessionResult
from .analytics import build_session_result

console=Console()

def _open_media(paths:List[str], data_dir:Path)->None:
    for p in paths:
        fp=(data_dir/p).resolve()
        if fp.exists():
            try:
                if os.name=='nt': os.startfile(str(fp))  # type: ignore
                elif sys.platform=='darwin': subprocess.run(['open', str(fp)], check=False)
                else: subprocess.run(['xdg-open', str(fp)], check=False)
            except Exception: pass

def render_question(q:Question, idx:int, total:int, remaining:int, *, title:Optional[str], beep_threshold_minutes:int, data_dir:Path, open_images:bool)->str:
    header=[title] if title else []
    header+= [f"Q {idx}/{total}", f"Domain: {q.domain}", f"Time left: {remaining//60}m {remaining%60}s"]
    console.rule(' • '.join(header))
    if remaining <= beep_threshold_minutes*60:
        try: print('', end='')
        except Exception: pass
    try: console.print(Panel.fit(Markdown(q.question), title=f"Q{q.id} [{q.type}]", border_style='cyan'))
    except Exception: console.print(Panel.fit(Text(q.question, style='bold'), title=f"Q{q.id} [{q.type}]", border_style='cyan'))
    if q.media:
        console.print(f"[blue]Media attached:[/blue] {', '.join(q.media)}");
        if open_images: _open_media(q.media, data_dir)
    table=Table(show_header=False, box=None)
    for l in ['A','B','C','D']: table.add_row(f"[bold]{l}[/]", q.options.get(l,''))
    console.print(table)
    console.print('(Enter A/B/C/D. Press P to pause & save state.)')
    while True:
        ans=Prompt.ask('Your answer (A/B/C/D or P)').strip().upper()
        if ans in {'A','B','C','D','P'}: return ans
        console.print('[red]Please enter A, B, C, D, or P.[/red]')

def render_feedback(correct:bool, q:Question)->None:
    console.print('[green]Correct![/green]' if correct else f"[red]Wrong.[/red] Correct: [bold]{q.answer}[/bold] — {q.answer_text}")

def render_final_review(cfg:SessionConfig, qs:List[Question], ans:List[AnswerRecord], user:str)->SessionResult:
    if cfg.reveal_mode=='end':
        console.rule('Final Review — Correct Answers'); qmap={q.id:q for q in qs}
        for a in ans:
            q=qmap[a.question_id]; status='✅' if a.is_correct else '❌'
            console.print(Panel.fit(f"Q{q.id} [{q.domain}] {status}
Correct: {q.answer} — {q.answer_text}", title=f"Your answer: {a.chosen}", border_style='magenta'))
    return build_session_result(ans, user=user)

def render_summary(res:SessionResult)->None:
    console.rule('Session Summary')
    console.print(f"Score: [bold]{res.correct}/{res.total}[/bold] ({res.percentage}%) • User: {res.user}")
    t=Table(title='Per-Domain Performance'); t.add_column('Domain'); t.add_column('Correct'); t.add_column('Total'); t.add_column('%')
    for d,st in sorted(res.per_domain.items()):
        c,tot=st['correct'],st['total']; pct=round((c/tot)*100,1) if tot else 0.0
        t.add_row(d,str(c),str(tot),f"{pct}%")
    console.print(t)
    if res.wrong_question_ids: console.print('[yellow]Questions to Review:[/yellow] '+', '.join(map(str,res.wrong_question_ids)))
