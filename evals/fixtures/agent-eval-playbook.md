# Building Reliable Evals for LLM Agents: A Practitioner's Playbook

*A synthetic technical guide used as an eval fixture for the youtube-to-wechat skill. It is intentionally long and dense, with eight concrete recommendations and a code example, to test that the skill localizes a long local document without compressing it into a summary.*

## Why most agent evals fail

Teams ship an agent, watch a few demos succeed, and assume it works. Then production traffic exposes the long tail: ambiguous instructions, tools that time out, multi-step plans that drift. The root problem is that the team never built an eval set that mirrors production. Demos are not evals. An eval is a fixed set of inputs, a way to run the agent against them repeatedly, and a grader that produces a comparable score each time.

## Recommendation 1: Start from real failures, not imagined ones

Pull the first 100 production traces and read every one by hand. The failure modes you find — wrong tool selected, hallucinated parameters, premature give-up — become your first eval cases. Inventing cases from intuition over-indexes on problems you already anticipate and misses the ones that actually bite.

## Recommendation 2: Separate capability evals from regression evals

Capability evals measure whether the agent can do something hard at all; they are allowed to have a low pass rate while you improve the system. Regression evals are cases the agent already passes, and they must stay green on every change. Mixing the two hides regressions inside an aggregate score that looks "good enough."

## Recommendation 3: Grade with assertions, not vibes

Every eval case needs at least one objectively checkable assertion: a file exists, a field equals a value, a forbidden string is absent. Reserve human judgment for the genuinely subjective dimensions (tone, helpfulness) and never let a subjective overall score substitute for the mechanical checks.

## Recommendation 4: Run each case multiple times

Agents are stochastic. A single run tells you almost nothing about reliability. Run each case at least three times and report the pass rate with its variance. A case that passes 2 of 3 runs is not "passing" — it is flaky, and flakiness in eval is a signal of flakiness in production.

## Recommendation 5: Keep a held-out set you never optimize against

If you tune the agent against your whole eval set, you overfit to it. Split off 30–40% as a held-out test set, evaluate on it only occasionally, and treat a gap between train and held-out scores as evidence of overfitting rather than progress.

## Recommendation 6: Instrument the trace, not just the output

A pass/fail on the final answer cannot tell you why the agent failed. Log every tool call, its arguments, and its result. When a case fails, the trace shows whether the model picked the wrong tool, passed bad arguments, or interpreted a correct result incorrectly — three failures that need three different fixes.

## Recommendation 7: Make the grader cheap enough to run on every commit

If grading takes an hour, nobody runs it. Push programmatic checks into a script that runs in CI on every commit, and reserve the expensive model-graded or human-graded passes for release candidates. Cheap-and-frequent beats thorough-and-never.

## Recommendation 8: Treat the eval set as a living artifact

Every new production failure becomes a new eval case. The set should grow with the product. A static eval set decays: the agent changes, the world changes, and last quarter's cases stop catching this quarter's bugs.

## A minimal grading harness

```python
import json
from pathlib import Path

def grade_case(output_dir: Path, assertions: list[dict]) -> dict:
    results = []
    for a in assertions:
        passed = check_assertion(output_dir, a)  # programmatic check
        results.append({"text": a["text"], "passed": passed})
    score = sum(r["passed"] for r in results) / len(results)
    return {"score": score, "results": results}

# Run each case 3x and average to surface flakiness.
def run_suite(cases, runs: int = 3):
    return {
        c["id"]: [grade_case(run_agent(c), c["assertions"]) for _ in range(runs)]
        for c in cases
    }
```

## Closing note

The discipline is not glamorous. It is reading traces, writing assertions, and running the suite until the numbers are trustworthy. But it is the difference between an agent that demos well and one that survives contact with real users.
