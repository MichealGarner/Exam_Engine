from __future__ import annotations
import argparse, json, random
from pathlib import Path
from typing import Dict
from rich.console import Console
from .loader import load_questions, load_metadata
from .selector import select_questions, blueprint_select, filter_pool
from .models import SessionConfig
from .exam import ExamSession
from .renderer import render_question, render_feedback, render_final_review, render_summary
from .storage import append_history, export_csv, export_html, export_anki_wrong
from .timer import TimerDisplay

console=Console()

def parse_args()->argparse.Namespace:
    p=argparse.ArgumentParser(description='Exam Simulator (CLI)')
    p.add_argument('--data-dir', type=str, default=str(Path(__file__).resolve().parents[1]/'data'))
    p.add_argument('--questions-file', type=str, default='questions.jsonl')
    p.add_argument('--metadata-file', type=str, default='metadata.json')
    p.add_argument('--blueprint', type=str, default='')
    p.add_argument('--num-questions', type=int, default=40)
    p.add_argument('--time-limit', type=int, default=75)
    p.add_argument('--reveal', choices=['after','end'], default='after')
    p.add_argument('--shuffle', action='store_true')
    p.add_argument('--shuffle-options', action='store_true')
    p.add_argument('--seed', type=int, default=None)
    p.add_argument('--weights', type=str, default='')
    p.add_argument('--history', type=str, default='')
    p.add_argument('--user', type=str, default='default')
    p.add_argument('--live-timer', action='store_true')
    p.add_argument('--beep-threshold', type=int, default=5)
    p.add_argument('--include-tags', type=str, default='')
    p.add_argument('--exclude-tags', type=str, default='')
    p.add_argument('--min-difficulty', type=int, default=None)
    p.add_argument('--max-difficulty', type=int, default=None)
    p.add_argument('--open-images', action='store_true')
    p.add_argument('--adaptive', action='store_true')
    p.add_argument('--save-state', type=str, default='')
    p.add_argument('--resume', type=str, default='')
    p.add_argument('--export-anki-wrong', nargs='?', const='', default=None,
                   help='Write an Anki CSV of WRONG answers; optional path. If omitted, saves to results/<ts>_anki_wrong.csv')
    return p.parse_args()

def parse_weights(spec:str, default:Dict[str,float])->Dict[str,float]:
    if not spec: return default
    out={}
    for part in spec.split(','):
        if not part.strip(): continue
        name,val=part.split(':',1); out[name.strip()]=float(val)
    tot=sum(out.values());
    if tot>0: out={k:v/tot for k,v in out.items()}
    return out

def maybe_shuffle_options(sel):
    for q in sel:
        letters=['A','B','C','D']; items=[(k,q.options[k]) for k in letters]
        random.shuffle(items)
        newopts={letters[i]:items[i][1] for i in range(4)}
        correct=None
        for i,(k,_) in enumerate(items):
            if k==q.answer: correct=letters[i]
        q.options=newopts; q.answer=correct

def main()->None:
    args=parse_args()
    if args.seed is not None: random.seed(args.seed)
    data_dir=Path(args.data_dir)
    q_path=data_dir/args.questions_file; m_path=data_dir/args.metadata_file
    console.print(f"[cyan]Loading questions from[/cyan] {q_path}")
    questions=load_questions(q_path)
    console.print(f"[cyan]Loading metadata from[/cyan] {m_path}")
    meta=load_metadata(m_path); default_weights=meta.get('domains',{}); title=meta.get('title')
    include_tags=[t.strip() for t in args.include_tags.split(',') if t.strip()]
    exclude_tags=[t.strip() for t in args.exclude_tags.split(',') if t.strip()]
    filtered=filter_pool(questions, include_tags, exclude_tags, args.min_difficulty, args.max_difficulty)
    if not filtered:
        console.print('[red]No questions after applying filters.[/red]'); return
    if args.blueprint:
        bp=json.loads(Path(args.blueprint).read_text(encoding='utf-8'))
        selection=blueprint_select(filtered, bp, shuffle=args.shuffle)
    else:
        weights=parse_weights(args.weights, default_weights)
        if not weights:
            ds=sorted({q.domain for q in filtered}); eq=1.0/len(ds) if ds else 1.0
            weights={d:eq for d in ds}; console.print('[yellow]Using equal weights across domains:[/yellow] '+', '.join(f'{d}:{eq:.2f}' for d in ds))
        selection=select_questions(filtered, total=args.num_questions, weights=weights, shuffle=args.shuffle)
    if args.shuffle_options: maybe_shuffle_options(selection)
    cfg=SessionConfig(num_questions=len(selection), time_limit_minutes=args.time_limit, reveal_mode=args.reveal, shuffle=args.shuffle, shuffle_options=args.shuffle_options, live_timer=args.live_timer, beep_threshold_minutes=args.beep_threshold, adaptive=args.adaptive, include_tags=include_tags, exclude_tags=exclude_tags, min_difficulty=args.min_difficulty, max_difficulty=args.max_difficulty, title=title, open_images=args.open_images, seed=args.seed)
    hist_path=Path(args.history) if args.history else (Path(__file__).resolve().parents[1]/'results'/f'history_{args.user}.json')
    sess=ExamSession(selection[:], cfg)
    timer=None
    if cfg.live_timer:
        timer=TimerDisplay(sess.remaining_seconds); timer.start()
    if args.resume:
        saved=json.loads(Path(args.resume).read_text(encoding='utf-8'))
        from .models import AnswerRecord
        sess.answers=[AnswerRecord(**a) for a in saved.get('answers',[])]
        sess.current_index=saved.get('index',0)
    def ui_ask(q,i,total,rem):
        return render_question(q,i,total,rem,title=cfg.title,beep_threshold_minutes=cfg.beep_threshold_minutes,data_dir=data_dir,open_images=cfg.open_images)
    def ui_feedback(ok,q): return render_feedback(ok,q)
    try: sess.run(ui_ask, ui_feedback)
    finally:
        if timer: timer.stop()
    result=render_final_review(cfg, selection, sess.answers, user=args.user)
    render_summary(result)
    hist_path.parent.mkdir(parents=True, exist_ok=True); append_history(result, hist_path)
    from datetime import datetime, timezone
    ts=datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
    csv_path=Path(__file__).resolve().parents[1]/'results'/f'{ts}_summary.csv'
    html_path=Path(__file__).resolve().parents[1]/'results'/f'{ts}_summary.html'
    export_csv(result, csv_path); export_html(result, html_path)
    console.print(f"[green]Saved history to[/green] {hist_path}")
    console.print(f"[green]Saved CSV report to[/green] {csv_path}")
    console.print(f"[green]Saved HTML report to[/green] {html_path}")
    # anki export
    if args.export_anki_wrong is not None:
        qmap={q.id:{'question':q.question,'options':q.options,'answer_text':q.answer_text} for q in selection}
        if args.export_anki_wrong!='': anki_path=Path(args.export_anki_wrong)
        else: anki_path=Path(__file__).resolve().parents[1]/'results'/f'{ts}_anki_wrong.csv'
        export_anki_wrong(result, anki_path, qmap)
        console.print(f"[green]Saved Anki WRONG CSV to[/green] {anki_path}")

if __name__=='__main__': main()
