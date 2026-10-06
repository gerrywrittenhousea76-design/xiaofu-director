#!/usr/bin/env python3
"""Look up a Xiaofu Director style by ID, number or catalog name."""
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def main():
    if len(sys.argv)!=2:
        print('用法：python scripts/get_style.py S38',file=sys.stderr)
        return 2
    cards=json.loads((ROOT/'references/styles.json').read_text())['styles']
    query=sys.argv[1].strip().casefold()
    if query.isdecimal():
        query='s'+str(int(query)).zfill(2)
    matched=[c for c in cards if query in (c['id'].casefold(),c['name'].casefold())]
    if len(matched)!=1:
        print('未找到唯一风格；请用 '+cards[0]['id']+'–'+cards[-1]['id']+' 或完整名称。',file=sys.stderr)
        return 1
    result=dict(matched[0])
    image=(ROOT/result['image']).resolve()
    result['image_absolute_path']=str(image)
    result['image_exists']=image.is_file()
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0

if __name__=='__main__':
    sys.exit(main())
