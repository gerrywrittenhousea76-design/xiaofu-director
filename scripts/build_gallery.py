#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verify original style images and build an offline selection gallery."""
import argparse
import hashlib
import html
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]

def build(strict=False):
    catalog_path = ROOT / 'references/styles.json'
    catalog = json.loads(catalog_path.read_text(encoding='utf-8'))
    styles = catalog['styles']
    manifest, missing = [], []
    for style in styles:
        path = ROOT / style['image']
        item = {'id': style['id'], 'name': style['name'], 'image': style['image'], 'source_page': style['source_page'], 'generation_recipe': style['generation_prompt']}
        if path.is_file():
            with Image.open(path) as im:
                im.verify()
            with Image.open(path) as im:
                item.update(width=im.width, height=im.height, format=im.format)
                if im.width < 700 or im.height < 400:
                    raise ValueError(f'{style["id"]} 图片尺寸过小')
            item.update(bytes=path.stat().st_size, sha256=hashlib.sha256(path.read_bytes()).hexdigest(), status='generated')
            style['image_status'] = 'generated'
        else:
            missing.append(style['id'])
            style['image_status'] = 'pending'
            item['status'] = 'pending'
        manifest.append(item)
    if strict and (len(styles) != 37 or missing):
        raise ValueError('37张参考图未齐：' + ', '.join(missing))
    catalog_path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (ROOT / 'assets/image-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    payload = json.dumps(styles, ensure_ascii=False).replace('</', '<\\/')
    page = TEMPLATE.replace('__STYLES__', payload).replace('__COUNT__', str(len(styles) - len(missing)))
    (ROOT / '风格选择册.html').write_text(page, encoding='utf-8')
    prompt_text = ['# 37种风格参考图配方', '', '这些是本次独立AI生成参考图使用的视觉配方。共同母题用于比较风格，实际故事请保留用户人物、时代与剧情。', '']
    for style in styles:
        prompt_text += [f'## {style["id"]} {style["name"]}', '', style['generation_prompt'], '']
    (ROOT / '风格参考图提示词.md').write_text('\n'.join(prompt_text), encoding='utf-8')
    print(f'已核验 {len(styles) - len(missing)}/{len(styles)} 张图片，图册与SHA-256清单已重建。')
    if missing:
        print('待生成：' + ', '.join(missing))

TEMPLATE = '''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>One Shot · 电影风格选择册</title>
<style>
:root{color-scheme:dark;--ink:#eeeee6;--mute:#9a9d94;--line:#31372f;--accent:#d4f568}*{box-sizing:border-box}body{margin:0;background:#11150f;color:var(--ink);font:15px/1.65 system-ui,-apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif}main{max-width:1440px;margin:auto;padding:44px 36px 80px}header{display:grid;grid-template-columns:2fr 1fr;gap:35px;padding-bottom:32px;border-bottom:1px solid var(--line)}.eyebrow{color:var(--accent);font-size:12px;letter-spacing:2px}h1{font-size:clamp(32px,5vw,68px);line-height:1.1;letter-spacing:-2px;margin:18px 0}h2{margin:0 0 12px;font-size:22px}p{margin:12px 0;color:var(--mute)}.stats{align-self:end}.stats strong{font-size:46px;color:var(--accent);line-height:1}button,input,textarea,select{font:inherit;color:inherit;border:1px solid var(--line);background:#1b2118;border-radius:8px;padding:10px 14px}button{cursor:pointer}button:hover,button.active{border-color:var(--accent);color:var(--accent)}input{min-width:230px}textarea{width:100%;resize:vertical}label{display:block;color:var(--mute);font-size:13px;margin:8px 0 4px}.controls{display:flex;gap:10px;flex-wrap:wrap;margin:28px 0}.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:23px}.card{border:1px solid var(--line);border-radius:13px;overflow:hidden;background:#191e16}.card.chosen{outline:2px solid var(--accent)}.card img{display:block;width:100%;aspect-ratio:16/9;object-fit:cover}.placeholder{aspect-ratio:16/9;display:grid;place-items:center;background:#23291f;color:var(--mute)}.body{padding:19px}.meta{display:flex;justify-content:space-between;color:var(--accent);font-size:12px;gap:10px}.card h3{font-size:22px;margin:8px 0 4px}.alias{font-size:13px;min-height:22px}.detail{font-size:13px;margin:10px 0 16px;color:#b4b8ab;min-height:44px}.card button{width:100%}.composer{background:#1b2316;border:1px solid #3e502c;border-radius:15px;padding:26px;margin:32px 0}.settings{display:flex;gap:15px;flex-wrap:wrap}.settings input{min-width:80px;width:100px}.selected{color:var(--accent);margin-bottom:13px}.primary{background:var(--accent);color:#18210d;font-weight:700;border:0}.primary:hover{background:#e2ff8c;color:#18210d}.copyrow{display:flex;gap:15px;align-items:center;margin:12px 0}.notice{font-size:12px}.empty{display:none;color:var(--mute)}footer{border-top:1px solid var(--line);margin-top:35px;padding-top:20px;font-size:12px;color:var(--mute)}@media(max-width:900px){.grid{grid-template-columns:repeat(2,minmax(0,1fr))}header{grid-template-columns:1fr}.stats{display:none}}@media(max-width:560px){main{padding:24px 16px 50px}.grid{grid-template-columns:1fr}.controls input{width:100%}.composer{padding:18px}h1{letter-spacing:-1px}}
</style></head><body><main>
<header><div><div class="eyebrow">ONE SHOT / VISUAL DIRECTIONS</div><h1>故事先行。<br>选择它的电影质感。</h1><p>37种视觉方向。保留人物为什么行动、镜头看什么、前后怎么接；再决定光影、色彩与空间。</p></div><div class="stats"><strong>__COUNT__ / 37</strong><p>独立AI生成的风格参考图<br>同一“未寄出的信”母题，不代表跨图身份一致。</p></div></header>
<section class="composer"><h2>把选择交给 Skill</h2><div class="selected" id="selected">先在下面选择一个风格</div><label for="story">你的故事情节</label><textarea id="story" rows="3" placeholder="例如：女子准备把未寄出的信扔掉，听见身后有人叫她，最后把信交给来人。"></textarea><div class="settings"><div><label for="count">分镜格数</label><select id="count"><option>4</option><option>6</option><option>9</option></select></div><div><label for="duration">总时长 / 秒</label><input id="duration" type="number" min="4" max="180" value="16"></div><div><label for="form">镜头形式</label><select id="form"><option value="cut">剪辑分镜</option><option value="one_take">一镜到底关键帧</option></select></div></div><div class="copyrow"><button class="primary" id="copy">复制调用指令</button><span id="feedback" role="status"></span></div><textarea id="instruction" rows="4" readonly aria-label="调用指令"></textarea><p class="notice">这个离线页面负责选择与复制。将指令粘贴到支持该 Skill 和图像工具的代理里，才会实际生成分镜图。页面不会上传剧情。</p></section>
<nav class="controls" aria-label="筛选"><input id="search" placeholder="搜索风格、作品或关键词" aria-label="搜索风格"><div id="filters"></div></nav><div class="grid" id="grid"></div><p class="empty" id="empty">没有匹配的风格，换一个关键词试试。</p>
<footer>图片是原创AI参考，来源作品名称只帮助辨识视觉方向。真实人物、时代、服装和剧情始终以你的输入为准。完整风格卡、参考图配方和生成清单在本包 references 与 assets 中。</footer></main>
<script>
const styles=__STYLES__;let category='全部',selected=null;
const $=id=>document.getElementById(id),escapeHTML=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function updateInstruction(){if(!selected){$('instruction').value='';return}const story=$('story').value.trim();const seconds=$('duration').value;const form=$('form').value==='one_take'?'一镜到底，分镜格为同一条镜头路径上的关键帧':'采用剪辑分镜';$('instruction').value=`使用 $xiaofu-director。\\n故事：${story||'【填入你的故事】'}\\n风格：${selected.id} ${selected.name}。\\n${seconds||16}秒，${$('count').value}格，每格16:9，${form}。对白语言随故事语境。生成分镜总览、镜头说明和每镜独立可复制的生图与视频提示词。`;}
function render(){const query=$('search').value.trim().toLowerCase();const list=styles.filter(s=>(category==='全部'||s.category===category)&&JSON.stringify(s).toLowerCase().includes(query));$('grid').innerHTML=list.map(s=>`<article class="card ${selected?.id===s.id?'chosen':''}" id="card-${s.id}">${s.image_status==='generated'?`<a href="${escapeHTML(s.image)}" target="_blank"><img src="${escapeHTML(s.image)}" alt="${escapeHTML(s.name)}参考图" loading="lazy"></a>`:'<div class="placeholder">待生成</div>'}<div class="body"><div class="meta"><span>${s.id}</span><span>${escapeHTML(s.category)}</span></div><h3>${escapeHTML(s.name)}</h3><p class="alias">${escapeHTML(s.source_alias)}</p><p class="detail">${escapeHTML(s.palette)} · ${escapeHTML(s.lighting_texture)}</p><button data-id="${s.id}">${selected?.id===s.id?'已选择':'选择这个风格'}</button></div></article>`).join('');$('empty').style.display=list.length?'none':'block';document.querySelectorAll('[data-id]').forEach(b=>b.onclick=()=>{selected=styles.find(s=>s.id===b.dataset.id);$('selected').textContent=`已选 ${selected.id} · ${selected.name}`;updateInstruction();render()});}
function renderFilters(){const categories=['全部',...new Set(styles.map(s=>s.category))];$('filters').innerHTML=categories.map(c=>`<button data-category="${escapeHTML(c)}" class="${c===category?'active':''}" style="margin:0 6px 6px 0">${escapeHTML(c)}</button>`).join('');document.querySelectorAll('[data-category]').forEach(b=>b.onclick=()=>{category=b.dataset.category;renderFilters();render()});}
['story','duration','count','form'].forEach(id=>$(id).addEventListener('input',updateInstruction));$('search').addEventListener('input',render);$('copy').onclick=async()=>{if(!selected){$('feedback').textContent='请先选择风格';return}if(!$('story').value.trim()){$('feedback').textContent='请先填入故事';return}updateInstruction();try{await navigator.clipboard.writeText($('instruction').value);$('feedback').textContent='已复制，粘贴到代理中使用'}catch(e){$('instruction').focus();$('instruction').select();$('feedback').textContent='已选中指令，请按 ⌘C / Ctrl+C 复制'}};renderFilters();render();
</script></body></html>'''

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--strict', action='store_true', help='require all 37 original images')
    args = parser.parse_args()
    build(args.strict)
