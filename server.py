from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Literal

import json
import tempfile

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field


ROOT = Path(__file__).resolve().parent
POLLS_PATH = ROOT / "polls.json"
polls_lock = Lock()

app = FastAPI(title="Not Some AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


class VoteRequest(BaseModel):
    choice: Literal["yes", "no"]
    previous_choice: Literal["yes", "no"] | None = None
    note: str = Field(default="", max_length=1000)


def read_polls() -> dict:
    with POLLS_PATH.open(encoding="utf-8") as file:
        return json.load(file)


def write_polls(data: dict) -> None:
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        delete=False,
        dir=ROOT,
        newline="\n",
    ) as file:
        json.dump(data, file, indent=2, ensure_ascii=False)
        file.write("\n")
        temp_path = Path(file.name)
    temp_path.replace(POLLS_PATH)


def find_poll(data: dict, poll_id: str) -> dict | None:
    return next((poll for poll in data.get("polls", []) if poll.get("id") == poll_id), None)


@app.get("/api/polls")
def get_polls() -> dict:
    return read_polls()


@app.post("/api/polls/{poll_id}/vote")
def submit_vote(poll_id: str, vote: VoteRequest) -> dict:
    with polls_lock:
        data = read_polls()
        poll = find_poll(data, poll_id)
        if poll is None:
            raise HTTPException(status_code=404, detail="Poll not found")

        votes = poll.setdefault("votes", {"yes": 0, "no": 0})
        previous_choice = vote.previous_choice
        if previous_choice and previous_choice != vote.choice:
            votes[previous_choice] = max(0, int(votes.get(previous_choice, 0)) - 1)

        if previous_choice != vote.choice:
            votes[vote.choice] = int(votes.get(vote.choice, 0)) + 1

        total = int(votes.get("yes", 0)) + int(votes.get("no", 0))
        yes_pct = round((int(votes.get("yes", 0)) / total) * 100) if total else 0
        no_pct = 100 - yes_pct if total else 0
        poll.setdefault("history", []).append(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "yes": yes_pct,
                "no": no_pct,
                "total": total,
            }
        )

        note = vote.note.strip()
        if note:
            poll.setdefault("comments", []).append(
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "choice": vote.choice,
                    "note": note,
                }
            )

        write_polls(data)
        return {"poll": poll}


app.mount("/", StaticFiles(directory=ROOT, html=True), name="static")
