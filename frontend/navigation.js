// Organize existing working tools into distinct views without destroying their event handlers.
const viewDefinitions = [
 ['explore','Area Explorer','Location, map and historical infrastructure'],
 ['satellite','Satellite Screening','Sentinel optical and radar observations'],
 ['analysis','Impact Assessment','Exposure, road access and terrain'],
 ['reports','Reports & Validation','Independent evaluation and downloadable documents'],
 ['assistant','Insight Assistant','Evidence-grounded questions'],
 ['demo','Demonstration','Clearly labelled synthetic example']
];
const workspace = document.querySelector('.workspace');
const viewNodes = Object.fromEntries(viewDefinitions.map(([key]) => [key, []]));
const selectorMap = {
 explore:['.page-head','.metrics','.map-card','.lower:last-of-type'],
 satellite:['#auto-optical-panel','#sar-panel'],
 analysis:['#unified-panel','#road-access-panel'],
 reports:['#advanced','.footer-panel'],
 assistant:['#assistant-panel'],
 demo:['#oneClickDemo']
};
// Capture complete top-level blocks and preserve nested control listeners.
const directChildren=Array.from(workspace.children);
const groupOf = node => {
 if(node.classList.contains('page-head')||node.classList.contains('metrics')||node.classList.contains('map-card'))return 'explore';
 if(node.id==='auto-optical-panel'||node.id==='sar-panel')return 'satellite';
 if(node.id==='unified-panel'||node.id==='road-access-panel'||node.querySelector?.('#analyzeGeo'))return 'analysis';
 if(node.id==='advanced'||node.classList.contains('footer-panel')||node.querySelector?.('#calculate'))return 'reports';
 if(node.id==='assistant-panel')return 'assistant';
 if(node.querySelector?.('#oneClickDemo'))return 'demo';
 if(node.classList.contains('lower')&&node.querySelector('#scenes'))return 'satellite';
 return 'explore';
};
const pages={};
viewDefinitions.forEach(([key,title,description])=>{let section=document.createElement('section');section.className='workspace-page';section.id='view-'+key;section.innerHTML='<div class="view-heading"><span class="view-eyebrow">FLOODSCOPE / '+title.toUpperCase()+'</span><h2>'+title+'</h2><p>'+description+'</p></div>';pages[key]=section;workspace.append(section)});
directChildren.forEach(node=>pages[groupOf(node)].append(node));
const nav=document.getElementById('workspaceNav');
viewDefinitions.forEach(([key,title])=>{const b=document.createElement('button');b.type='button';b.textContent=title;b.dataset.view=key;b.addEventListener('click',()=>showWorkspace(key));nav.append(b)});
const oldEnterPortal=window.enterPortal;
function showWorkspace(key){
 if(!pages[key])key='explore';
 document.getElementById('welcome').hidden=true;
 document.body.classList.add('portal-active');
 Object.entries(pages).forEach(([id,page])=>page.hidden=id!==key);
 nav.querySelectorAll('button').forEach(b=>b.classList.toggle('active',b.dataset.view===key));
 document.querySelector('.sidebar').hidden=!(key==='explore'||key==='satellite');
 document.querySelector('main').classList.toggle('full-workspace',!(key==='explore'||key==='satellite'));
 history.replaceState(null,'','#'+key);
 window.scrollTo({top:0,behavior:'instant'});
 if(window.map&&key==='explore')setTimeout(()=>map.invalidateSize(),60);
}
function enterPortal(mode){showWorkspace(mode==='analysis'?'analysis':mode);if(mode==='demo')setTimeout(()=>document.getElementById('oneClickDemo').click(),150)}
function goHome(){document.body.classList.remove('portal-active');document.getElementById('welcome').hidden=false;history.replaceState(null,'',location.pathname);window.scrollTo({top:0,behavior:'instant'})}
window.enterPortal=enterPortal;window.goHome=goHome;
// Additional cross-workspace shortcuts.
const quick=document.createElement('div');quick.className='quick-links';quick.innerHTML='<button type="button" data-target="analysis">Impact assessment →</button><button type="button" data-target="reports">Reports →</button>';
pages.explore.querySelector('.view-heading').append(quick);
quick.querySelectorAll('button').forEach(b=>b.addEventListener('click',()=>showWorkspace(b.dataset.target)));
const deep=location.hash.slice(1);if(pages[deep])showWorkspace(deep);else goHome();
