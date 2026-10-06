#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check a storyboard document. Does not verify image semantics or generated video."""
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def validate(board):
    errors = []
    def fail(message):
        errors.append(message)
    def nonempty(value):
        return isinstance(value, str) and bool(value.strip())
    def number(value):
        return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)
    if not isinstance(board, dict):
        return ['顶层必须是对象']
    if board.get('version') != 1:
        fail('version 必须为1')
    for key in ('story', 'aspect_ratio'):
        if not nonempty(board.get(key)):
            fail(f'{key} 必须是非空文字')
    catalog = json.loads((ROOT / 'references/styles.json').read_text())
    styles = {s['id'] for s in catalog['styles']}
    if board.get('style_id') not in styles:
        fail('style_id 必须是当前风格目录里的编号')
    duration = board.get('duration_seconds')
    if not number(duration) or duration <= 0:
        fail('duration_seconds 必须为正数')
    if board.get('camera_form') not in ('cut', 'one_take'):
        fail('camera_form 必须为 cut 或 one_take')
    indexes = {}
    for key, fields in [('characters', ('description',)), ('scenes', ('layout', 'light'))]:
        items = board.get(key)
        if not isinstance(items, list) or not items:
            fail(f'{key} 必须为非空数组')
            items = []
        ids = set()
        for item in items:
            if not isinstance(item, dict):
                fail(f'{key} 条目必须为对象')
                continue
            item_id = item.get('id')
            if not nonempty(item_id) or item_id in ids:
                fail(f'{key} 的 id 缺失或重复')
            elif isinstance(item_id, str):
                ids.add(item_id)
            for field in fields:
                if not nonempty(item.get(field)):
                    fail(f'{key} {item_id} 缺少 {field}')
        indexes[key] = ids
    shots = board.get('shots')
    if not isinstance(shots, list) or not shots:
        fail('shots 必须是非空数组')
        return errors
    count = board.get('panel_count')
    if not isinstance(count, int) or isinstance(count, bool) or count < 1 or count != len(shots):
        fail('panel_count 必须等于实际镜头数')
    previous_end = 0
    previous_state = None
    shot_ids = set()
    for i, shot in enumerate(shots):
        label = f'第{i + 1}镜'
        if not isinstance(shot, dict):
            fail(f'{label} 必须为对象')
            continue
        shot_id = shot.get('id')
        if not nonempty(shot_id) or shot_id in shot_ids:
            fail(f'{label} id 缺失或重复')
        else:
            shot_ids.add(shot_id)
        for key in ('decisive_frame', 'framing', 'camera', 'image_prompt', 'video_prompt'):
            if not nonempty(shot.get(key)):
                fail(f'{label} 缺少 {key}')
        if not isinstance(shot.get('audio'), (str, list, dict)):
            fail(f'{label} audio 必须为文字、数组或对象')
        if shot.get('scene_id') not in indexes['scenes']:
            fail(f'{label} 引用未知场景')
        characters = shot.get('character_ids')
        if not isinstance(characters, list) or any(not isinstance(c, str) or c not in indexes['characters'] for c in characters):
            fail(f'{label} character_ids 引用未知人物或不是数组')
        start, end = shot.get('start'), shot.get('end')
        if not number(start) or not number(end) or start < 0 or end <= start:
            fail(f'{label} 时间无效')
        else:
            if abs(start - previous_end) > 1e-6:
                fail(f'{label} 时间有空洞或重叠，必须从 {previous_end} 开始')
            previous_end = end
        before, after = shot.get('state_before'), shot.get('state_after')
        if not isinstance(before, dict) or not isinstance(after, dict):
            fail(f'{label} state_before/state_after 必须为对象')
            previous_state = None
            continue
        explanation = shot.get('explained_changes', {})
        if not isinstance(explanation, dict):
            fail(f'{label} explained_changes 必须为对象')
            explanation = {}
        if previous_state is not None:
            for key in set(previous_state) | set(before):
                changed = key not in previous_state or key not in before or previous_state[key] != before[key]
                if changed and not nonempty(explanation.get(key)):
                    fail(f'{label} 状态 {key} 未继承前镜，需解释变化')
        previous_state = after
    if number(duration) and abs(previous_end - duration) > 1e-6:
        fail('最后一镜结束时间与总时长不符')
    return errors

def main():
    if len(sys.argv) != 2:
        print('用法：python scripts/validate_board.py board.json', file=sys.stderr)
        return 2
    try:
        board = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
        errors = validate(board)
    except (OSError, ValueError, TypeError) as exc:
        print(f'FAIL: {exc}', file=sys.stderr)
        return 1
    if errors:
        print('\n'.join('FAIL: ' + error for error in errors), file=sys.stderr)
        return 1
    print(f'PASS: {len(board["shots"])}镜 / {board["duration_seconds"]}秒 / {board["style_id"]}；仅文档结构与状态交接通过')
    return 0

if __name__ == '__main__':
    sys.exit(main())
