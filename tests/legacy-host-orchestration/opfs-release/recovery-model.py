"""Pure transition invariant model. No filesystem, services, or host actions."""
from dataclasses import dataclass

@dataclass(frozen=True)
class State:
    gated: bool = False
    floor_committed: bool = False
    candidate_exposed: bool = False

def gate(state):
    if state.candidate_exposed: raise ValueError('Cannot re-enter initial gate')
    return State(True,state.floor_committed,False)

def commit_floor(state, *, candidate_verified, baseline_verified):
    if not state.gated or state.floor_committed or not candidate_verified or not baseline_verified:
        raise ValueError('Gate and verified artifacts required')
    return State(True,True,False)

def expose_candidate(state, *, candidate_verified):
    if not state.gated or not state.floor_committed or not candidate_verified:
        raise ValueError('Durable floor and verified candidate required')
    return State(False,True,True)

def recover(state, *, candidate_verified, baseline_verified):
    # A floor must be recorded before any v2 response can be served. After it
    # exists, failure to verify the candidate means staying gated, not v1.
    if state.candidate_exposed and not state.floor_committed:
        raise ValueError('Impossible journal: v2 exposure without floor')
    if state.floor_committed:
        return 'forward-candidate' if candidate_verified else 'remain-gated'
    return 'restore-guarded-v1' if baseline_verified else 'remain-gated'
