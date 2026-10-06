#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read one style card without loading the entire catalog into the agent context."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main():
    if len(sys.argv) != 2:
        print('用法：python scripts/get_style.py S26', file=sys.stderr)
        return 2
    query = sys.argv[1].strip().casefold()
    if query.isdigit():
        query = f's{int(query):02d}'
    styles = json.loads((ROOT / 'references/styles.json').read_text(encoding='utf-8'))['styles']
    matches = [s for s in styles if query in {s['id'].casefold(), s['name'].casefold(), s['source_alias'].casefold()}]
    if len(matches) != 1:
        print('未找到唯一风格，请使用 S01–S37 或完整中文风格名。', file=sys.stderr)
        return 1
    card = dict(matches[0])
    image = ROOT / card['image']
    card['image_absolute_path'] = str(image)
    card['image_exists'] = image.is_file()
    print(json.dumps(card, ensure_ascii=False, indent=2))
    return 0

if __name__ == '__main__':
    sys.exit(main())
