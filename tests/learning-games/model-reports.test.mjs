import assert from "node:assert/strict";
import test from "node:test";
import {FractionFarmSession} from "@webos/fraction-farm";
import {MarketMathSession} from "@webos/market-math";
import {MathPathSession} from "@webos/math-path";
import {PocketConquestSession} from "@webos/pocket-conquest";
import {RuleDetectiveSession} from "@webos/rule-detective";
import {TileIslandsSession} from "@webos/tile-islands";
import {WordWeaverSession} from "@webos/word-weaver";
import {validateLearningReport} from "@webos/learning-game-core/experience";

test("every core session exposes a valid learning report", () => {
  const sessions = [
    new MathPathSession("report-math", 3),
    new FractionFarmSession("report-fraction", 4),
    new MarketMathSession("report-market"),
    new PocketConquestSession("report-conquest", 3, 2),
    new RuleDetectiveSession("report-rule", 2),
    new TileIslandsSession("report-tiles", 3, 2),
    new WordWeaverSession("report-word"),
  ];
  for (const session of sessions) {
    const report = session.report;
    assert.equal(validateLearningReport(report), true);
    const before = session.state;
    report.details.skills = "mutated";
    assert.notEqual(session.state.details?.skills, "mutated");
    assert.deepEqual(session.state, before);
  }
});
