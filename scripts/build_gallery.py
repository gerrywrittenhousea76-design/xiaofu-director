#!/usr/bin/env python3
"""Build the Xiaofu Director catalog from style data and actual image files."""
import argparse
import hashlib
import html
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]

PAGE = r'''<!doctype html>
<html lang="zh-CN">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>小夫导演 47种视觉方向</title>
<style>
:root{--paper:#f5f3ed;--ink:#252922;--muted:#647062;--line:#d8ded3;--green:#284b3b}*{box-sizing:border-box}body{margin:0;color:var(--ink);background:var(--paper);font:15px/1.7 system-ui,-apple-system,"PingFang SC",sans-serif}main{max-width:1440px;margin:auto;padding:44px 30px 60px}header{border-bottom:1px solid var(--line);padding-bottom:24px}header small{color:var(--green);letter-spacing:2px}h1{font-size:clamp(32px,4vw,58px);line-height:1.2;margin:16px 0}h2{margin:0 0 10px;font-size:22px}p{margin:10px 0}header p,footer,p.hint{color:var(--muted)}.workbench{margin:30px 0;padding:24px;border:1px solid var(--line);border-radius:16px;background:#fff}.settings,.filters{display:flex;gap:14px;flex-wrap:wrap;align-items:end}.filters{margin:28px 0 16px}label{display:flex;flex-direction:column;gap:5px;font-size:13px;color:var(--muted)}input,select,textarea,button{font:inherit;border:1px solid #bac6b8;border-radius:7px;padding:9px 12px;background:white;color:var(--ink)}textarea{width:100%;margin:10px 0;resize:vertical}input[type=number]{width:105px}#search{width:300px;max-width:100%}button{cursor:pointer}.primary{background:var(--green);color:white;border-color:var(--green)}#selected{font-weight:600;color:var(--green)}#instruction{background:#f4f7f2;font-size:13px}#feedback{font-size:13px;margin-left:12px}.gallery{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:18px}.card{background:white;border:1px solid var(--line);border-radius:12px;overflow:hidden}.card.chosen{outline:3px solid var(--green);outline-offset:2px}.card img{width:100%;aspect-ratio:16/9;object-fit:cover;display:block}.card-body{padding:16px}.card h3{margin:5px 0;font-size:20px}.card p{font-size:13px;color:var(--muted)}.card button{width:100%;margin-top:6px}.meta{display:flex;justify-content:space-between;font-size:12px;color:var(--green)}.pending{aspect-ratio:16/9;display:grid;place-items:center;background:#e6ebe1}.hint{font-size:12px}footer{border-top:1px solid var(--line);padding-top:20px;margin-top:32px;font-size:12px}@media(max-width:1050px){.gallery{grid-template-columns:repeat(3,minmax(0,1fr))}}@media(max-width:760px){.gallery{grid-template-columns:repeat(2,minmax(0,1fr))}main{padding:26px 18px}}@media(max-width:480px){.gallery{grid-template-columns:1fr}.workbench{padding:18px}}
</style></head>
<body><main>
<header><small>XIAOFU DIRECTOR / VISUAL CATALOG</small><h1>让故事成为镜头</h1><p>__TOTAL__种视觉方向。看颜色、光线和空间，选择适合你故事的一张卡。</p><p>__READY__张实际参考图 · S38–S47为新增情景剧方向</p></header>
<section class="workbench" aria-label="调用指令编辑器"><h2>先选风格，再写故事</h2><div id="selected" role="status">尚未选择风格</div>
<label for="story">故事</label><textarea id="story" rows="3" placeholder="谁正在做什么，发生什么变化，最后如何结束？"></textarea>
<div class="settings"><label for="count">分镜格数<input id="count" type="number" min="1" max="12" value="4"></label><label for="duration">总时长 秒<input id="duration" type="number" min="1" max="300" value="20"></label><label for="aspect">每格画幅<select id="aspect"><option>16:9</option><option>9:16</option><option>1:1</option></select></label><label for="form">镜头形式<select id="form"><option value="cut">剪辑分镜</option><option value="one_take">一镜到底关键帧</option></select></label></div>
<textarea id="instruction" rows="6" readonly aria-label="调用指令"></textarea><button class="primary" id="copy" type="button">复制调用指令</button><span id="feedback" role="status"></span><p class="hint">把指令粘贴到支持该 Skill 和图像工具的环境中继续生成。页面在本地整理文字，不上传剧情。</p></section>
<div class="filters"><label for="search">搜索编号 名称 用途<input id="search" type="search" placeholder="例如 S38、家庭、重逢"></label><label for="category">分类<select id="category"></select></label><span id="result-count" role="status"></span></div>
<section class="gallery" id="gallery" aria-label="视觉方向参考图"></section>
<footer>参考图用于比较视觉表达，用户故事中的人物、服装与场景由故事决定。既有37张图片本轮保留，新增10张独立生成。静态参考不表示动态视频已经完成。完整操作见使用教程。</footer>
</main><script>
const cards=__DATA__;
const byId=id=>document.getElementById(id);
const esc=value=>String(value).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let picked=null;
function compose(){
 if(!picked){byId('instruction').value='';return}
 const story=byId('story').value.trim()||'【填写故事】';
 const count=Number(byId('count').value),duration=Number(byId('duration').value);
 const form=byId('form').value==='one_take'?'一镜到底，分镜格为同一条镜头路线的连续关键帧。':'剪辑分镜。';
 byId('instruction').value=['使用 $xiaofu-director。','故事：'+story,'风格：'+picked.id+' '+picked.name+'。',duration+'秒，'+count+'格，每格'+byId('aspect').value+'，'+form,'生成分镜图，以及每镜独立的生图提示词和视频提示词。'].join('\n');
}
function render(){
 const query=byId('search').value.trim().toLocaleLowerCase(),category=byId('category').value;
 const shown=cards.filter(c=>(category==='全部'||c.category===category)&&[c.id,c.name,c.category,c.palette,...c.story_uses].join(' ').toLocaleLowerCase().includes(query));
 byId('result-count').textContent='显示 '+shown.length+' / '+cards.length;
 byId('gallery').innerHTML=shown.map(c=>'<article class="card'+(picked&&picked.id===c.id?' chosen':'')+'"><div>'+(c.image_status==='generated'?'<a href="'+esc(c.image)+'" target="_blank" rel="noopener"><img src="'+esc(c.image)+'" alt="'+esc(c.id+' '+c.name)+'参考图" loading="lazy"></a>':'<div class="pending">参考图尚未生成</div>')+'</div><div class="card-body"><div class="meta"><span>'+esc(c.id)+(c.number>=38?' · 新增':'')+'</span><span>'+esc(c.category)+'</span></div><h3>'+esc(c.name)+'</h3><p>'+esc(c.palette)+'</p><p>'+esc(c.story_uses.join(' / '))+'</p><button type="button" data-pick="'+esc(c.id)+'">'+(picked&&picked.id===c.id?'已选择':'选择 '+esc(c.id))+'</button></div></article>').join('');
}
byId('category').innerHTML=['全部',...new Set(cards.map(c=>c.category))].map(c=>'<option>'+esc(c)+'</option>').join('');
byId('gallery').addEventListener('click',event=>{
 const button=event.target.closest('[data-pick]');if(!button)return;
 picked=cards.find(c=>c.id===button.dataset.pick);
 byId('selected').textContent='已选 '+picked.id+' '+picked.name;byId('feedback').textContent='';compose();render();
});
['search','category'].forEach(id=>byId(id).addEventListener('input',render));
['story','count','duration','aspect','form'].forEach(id=>byId(id).addEventListener('input',compose));
byId('copy').addEventListener('click',async()=>{
 if(!picked){byId('feedback').textContent='请先选择风格';return}
 if(!byId('story').value.trim()){byId('feedback').textContent='请先写入故事';return}
 if(!byId('count').checkValidity()||!byId('duration').checkValidity()){byId('feedback').textContent='请检查格数和时长';return}
 compose();
 try{await navigator.clipboard.writeText(byId('instruction').value);byId('feedback').textContent='已复制，可以粘贴'}
 catch(error){byId('instruction').focus();byId('instruction').select();byId('feedback').textContent='指令已选中，按 ⌘C 或 Ctrl+C 复制'}
});
render();
</script></body></html>'''

def build(strict=False):
    path=ROOT/'references/styles.json'
    catalog=json.loads(path.read_text())
    cards=catalog['styles']
    count=catalog['count']
    if count!=len(cards) or [c['id'] for c in cards]!=[f'S{n:02d}' for n in range(1,count+1)]:
        raise ValueError('目录数量或编号顺序不一致')
    if len({c['name'] for c in cards})!=count or len({c['image'] for c in cards})!=count:
        raise ValueError('名称或图片路径重复')
    manifest=[]
    missing=[]
    for c in cards:
        image=(ROOT/c['image']).resolve()
        if not image.is_relative_to((ROOT/'assets/style-references').resolve()):
            raise ValueError('图片路径超出风格参考目录')
        item={k:c[k] for k in ('id','name','image','asset_origin','prompt_kind')}
        if image.is_file():
            with Image.open(image) as im:
                im.verify()
            with Image.open(image) as im:
                width,height=im.size
                if width<700 or height<400:
                    raise ValueError(c['id']+' 图片尺寸不足')
                item.update(width=width,height=height,format=im.format)
            item.update(bytes=image.stat().st_size,sha256=hashlib.sha256(image.read_bytes()).hexdigest(),status='generated')
            c['image_status']='generated'
        else:
            c['image_status']='pending'
            item['status']='pending'
            missing.append(c['id'])
        manifest.append(item)
    if strict and missing:
        raise ValueError('缺少实际图片：'+', '.join(missing))
    hashes=[m['sha256'] for m in manifest if m['status']=='generated']
    if len(set(hashes))!=len(hashes):
        raise ValueError('检测到重复图片')
    path.write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n')
    (ROOT/'assets/image-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    payload=json.dumps(cards,ensure_ascii=False).replace('</','<\\/')
    (ROOT/'风格选择册.html').write_text(PAGE.replace('__TOTAL__',str(count)).replace('__READY__',str(count-len(missing))).replace('__DATA__',payload))
    index=['# 视觉方向索引','','按故事用途推荐3项，查看实际参考图后再选择。编号优先；目录中的参考场景不是用户故事的默认场景。','','| 编号 | 名称 | 类别 | 色彩 | 适用故事 |','|---|---|---|---|---|']
    recipes=['# 47种视觉参考图配方','','S01–S37为本轮重写的复现建议，不是旧图原始输入的逐字日志；S38–S47为本轮实际生图输入。图片文件与状态见素材清单。']
    readme=['# 小夫导演 · Xiaofu Director','','给一句故事，选择视觉方向，生成分镜图，并拿到逐镜独立的生图和视频提示词。','','**47种视觉方向，47张实际参考图。** 本版重写全部风格卡与镜头指南，新增S38–S47十种情景剧方向。S01–S37图片保留，说明以实际画面重新编写。','','## 使用教程','','下载完整仓库，把文件夹命名为 xiaofu-director，放到支持 Skills 的环境中。保留图片、references 与 scripts。运行环境需要提供图像工具。安装与修改步骤见 [完整使用教程](使用教程.md)。','','~~~text','使用 $xiaofu-director。','故事：室友藏起最后一个饺子，听见门锁响，以为要被发现；来人放下一盒新买的饺子，她把藏着的饺子默默放回盘里。','风格：S38 家庭喜剧。','20秒，4格，每格16:9。','生成分镜图，以及每镜独立的生图提示词和视频提示词。','~~~','','没有风格方向，可以先要求推荐3种并展示参考图。已有风格和故事时可直接生成。一镜到底会按同一连续镜头的关键帧来设计。','','## 看图选择','','按S01–S47调用，点击图片打开原图。也可以打开 [离线风格选择册](风格选择册.html) 按分类和用途筛选、填写故事并复制指令。S08蓝色记忆与S26霓虹都市保留编号和名称。其余部分名称更新，以当前表为准。','','| 编号 | 风格 | 颜色与光线 | 参考图 |','|---|---|---|---|']
    for c in cards:
        index.append('| '+ ' | '.join([c['id'],c['name'],c['category'],c['palette'],'、'.join(c['story_uses'])])+' |')
        recipes.extend(['', '## '+c['id']+' '+c['name'], '', '配方类型：'+('本轮生图输入' if c['prompt_kind']=='generation_input' else '重写复现建议'), '', c['reference_prompt']])
        image=c['image']
        readme.append('| '+c['id']+' | '+c['name']+(' · 新增' if c['number']>=38 else '')+' | '+c['palette']+'；'+c['lighting']+' | [![参考图]('+image+') ]('+image+') |')
    readme.extend(['','## 输出与复核','','交付分镜图、镜头说明和每镜可独立复制的提示词。动作、机位、对白与声音写在视频指令中，静态图片只表示画面设计已完成。动态视频、口型和声音仍需后续工具实际生成和复看。','','单镜大图需要逐镜生成；裁切总览会标明是裁切。屏幕文字较小时，可以按交付文档里的准确台词单独排版。','','包内还提供风格查询、图册重建与镜头文档校验脚本。素材保留与新增的记录见 [素材说明](references/provenance.md)，结构化交接见 [文档格式](references/board-schema.md)。','','## 使用许可','','作者：[gerrywrittenhousea76-design](https://github.com/gerrywrittenhousea76-design)。当前为公开分享的受限许可项目，个人非商业使用按 [LICENSE.md](LICENSE.md) 进行；商用需联系作者取得书面授权。可通过 [商用授权申请](https://github.com/gerrywrittenhousea76-design/xiaofu-director/issues/new?template=commercial-license.yml) 联系。'])
    (ROOT/'references/style-index.md').write_text('\n'.join(index)+'\n')
    (ROOT/'风格参考图提示词.md').write_text('\n'.join(recipes)+'\n')
    (ROOT/'README.md').write_text('\n'.join(readme)+'\n')
    print(f'核验 {count-len(missing)}/{count} 张参考图，已重建首页、索引、图册、配方和素材清单')

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--strict',action='store_true',help='所有卡片都必须有实际图片')
    build(parser.parse_args().strict)
