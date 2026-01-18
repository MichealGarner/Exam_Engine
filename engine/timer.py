from __future__ import annotations
import threading, time
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
class TimerDisplay:
    def __init__(self, remaining_seconds_fn, refresh=1.0)->None:
        self.remaining_seconds_fn=remaining_seconds_fn; self.refresh=refresh
        self._stop=threading.Event(); self._th=threading.Thread(target=self._run, daemon=True)
    def start(self): self._th.start()
    def stop(self): self._stop.set(); self._th.join(timeout=2)
    def _fmt(self, s:int)->str:
        m,s=divmod(max(0,int(s)),60); h,m=divmod(m,60); return f"{h}h {m}m {s}s" if h else f"{m}m {s}s"
    def _run(self):
        with Live(auto_refresh=False, transient=False) as live:
            while not self._stop.is_set():
                secs=self.remaining_seconds_fn(); txt=Text(f"Time Remaining: {self._fmt(secs)}", style='bold white on blue')
                live.update(Panel(txt, border_style='blue')); live.refresh(); time.sleep(self.refresh)
