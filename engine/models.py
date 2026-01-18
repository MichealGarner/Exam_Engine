from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass(frozen=True)
class Question:
    id: int
    domain: str
    type: str
    question: str
    options: Dict[str,str]
    answer: str
    answer_text: str
    tags: List[str] = field(default_factory=list)
    difficulty: Optional[int] = None
    media: List[str] = field(default_factory=list)

@dataclass
class SessionConfig:
    num_questions:int=40
    time_limit_minutes:int=75
    reveal_mode:str='after'
    shuffle:bool=True
    shuffle_options:bool=False
    live_timer:bool=False
    beep_threshold_minutes:int=5
    adaptive:bool=False
    include_tags:List[str]=field(default_factory=list)
    exclude_tags:List[str]=field(default_factory=list)
    min_difficulty:Optional[int]=None
    max_difficulty:Optional[int]=None
    title:Optional[str]=None
    open_images:bool=False
    seed:Optional[int]=None

@dataclass
class AnswerRecord:
    question_id:int
    chosen:str
    correct:str
    is_correct:bool
    domain:str

@dataclass
class SessionResult:
    timestamp:str
    user:str
    total:int
    correct:int
    incorrect:int
    percentage:float
    per_domain:Dict[str,Dict[str,int]]
    wrong_question_ids:List[int]=field(default_factory=list)
    answers:List[AnswerRecord]=field(default_factory=list)
