"""Verify copied acceptance assertions/oracles were not changed for this run."""
from pathlib import Path
import hashlib
here=Path(__file__).resolve().parent
prior=here.parents[1]/'combined-alias-mechanical'
prefix='// Selected-profile r4 integration regression: only import/pin/source labels adapted.\n'
for name in ['bracket.test.mjs','typed-bracket.test.mjs','enclosure.test.mjs']:
 original=(prior/name).read_text()
 wanted=original.replace("from '../axis-symmetry/combined-alias/helpers.mjs'","from '../helpers.mjs'").replace('{requireReviewedPins,verifyRuntime}','{requiredPins as requireReviewedPins,verifyRuntime}').replace("from '../numeric-expressions/helpers.mjs'","from '../../numeric-expressions/helpers.mjs'").replace("desktopSource:'10910b2d6'","desktopSource:'478970d72'")
 assert (here/name).read_text()==prefix+wanted,name+' changed outside allowed import/pin/source labels'
 print('PASS unchanged acceptance assertions',name)
name='check-v2-3mf.py';assert (here/name).read_bytes()==(prior/name).read_bytes()
print('PASS unchanged independent checker',hashlib.sha256((here/name).read_bytes()).hexdigest())
