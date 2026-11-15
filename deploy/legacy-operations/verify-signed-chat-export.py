#!/usr/bin/env python3
"""Verify a complete public signed chat record using the existing replay verifier."""
import argparse, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'codiserver-server-v0.3.0')]
from codiauth import jose
from steward.official_chat_replay import ExperimentalChatReplay

LIMIT = 16 * 1024 * 1024

def verify(raw, expected_channel=None):
    if not isinstance(raw, bytes) or len(raw) > LIMIT:
        raise ValueError('Signed record exceeds the 16 MiB limit')
    try:
        record = jose.loads(raw.decode('utf-8'))
    except (UnicodeDecodeError, ValueError) as error:
        raise ValueError('Invalid UTF-8 JSON record') from error
    fields = {'version', 'channel', 'genesisHash', 'policyWire', 'height', 'head', 'blocks'}
    if not isinstance(record, dict) or set(record) != fields or record['version'] != 'codi-signed-chat/1':
        raise ValueError('Invalid signed chat record')
    if expected_channel is not None and record['channel'] != expected_channel:
        raise ValueError('Record does not match the expected channel')
    blocks, height = record['blocks'], record['height']
    if type(height) is not int or not 0 <= height <= 2048 or not isinstance(blocks, list) or len(blocks) != height:
        raise ValueError('Incomplete or invalid block count')
    replay = ExperimentalChatReplay(record['policyWire'], channel=record['channel'], genesis=record['genesisHash'])
    state = replay.snapshot()
    for offset in range(0, len(blocks), 64):
        state = replay.append(blocks[offset:offset + 64])
    if state['head'] != record['head'] or state['height'] != height:
        raise ValueError('Record does not match its claimed head')
    return {'status': 'verified', 'channel': record['channel'], 'height': height,
            'operations': state['state']['count'],
            'identityNote': 'Signatures verify against included public keys; establish channel ownership using a separately trusted channel ID.'}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('record', type=Path)
    parser.add_argument('--expected-channel')
    args = parser.parse_args()
    try:
        with args.record.open('rb') as file:
            raw = file.read(LIMIT + 1)
        print(json.dumps(verify(raw, args.expected_channel), indent=2))
    except (ValueError, OSError) as error:
        raise SystemExit('Verification failed: ' + str(error)) from None
