#!/usr/bin/env python3
"""Exercise the chat export verifier with real signed messages and moderation."""
import copy, importlib.util, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
def module(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result

fixture = module('chat_writer_fixture', 'official-chat-writer-check.py')
verifier = module('chat_export_verifier', 'verify-signed-chat-export.py')
case = fixture.Checks()
case.setUp()
try:
    case.writer.append(case.channel, case.genesis, case.record('first'), case.bind(), case.principal)
    state = case.registry.replayed_head(case.channel)['state']
    case.writer.append(case.channel, case.genesis,
                       case.record('second', sequence=2, previous=state['authors'][0]['last']),
                       case.bind(), case.principal)
    state = case.registry.replayed_head(case.channel)['state']
    fixture.mark_spam(case.registry, case.key, message=state['messages'][0]['id'])
    head = case.registry.replayed_head(case.channel)
    blocks = [json.loads(row[0]) for row in case.registry._db.execute(
        'SELECT wire FROM official_replayed_blocks WHERE channel=? ORDER BY height', (case.channel,))]
    record = {'version': 'codi-signed-chat/1', 'channel': case.channel,
              'genesisHash': case.genesis, 'policyWire': case.registry._db.execute(
                  'SELECT policy_wire FROM official_channels WHERE channel=?', (case.channel,)).fetchone()[0],
              'height': head['height'], 'head': head['head'], 'blocks': blocks}
    encode = lambda value: json.dumps(value, separators=(',', ':')).encode()
    result = verifier.verify(encode(record), case.channel)
    assert result['height'] == 3 and result['operations'] == 3
    for mutate in ('block', 'missing', 'head', 'channel'):
        broken = copy.deepcopy(record)
        if mutate == 'block': broken['blocks'][0]['header']['count'] += 1
        if mutate == 'missing': broken['blocks'].pop()
        if mutate == 'head': broken['head'] = case.genesis
        if mutate == 'channel': broken['channel'] = case.genesis
        try:
            verifier.verify(encode(broken), case.channel)
        except ValueError:
            continue
        raise AssertionError(mutate + ' was accepted')
    print('PASS real signed chat and spam marker; tampering, missing blocks and wrong channel rejected')
finally:
    case.tearDown()
