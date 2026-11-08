// SPDX-FileCopyrightText: 2026 The Pharos contributors
// SPDX-License-Identifier: GPL-3.0-or-later
'use strict';
const $ = id => document.getElementById(id);
const views = ['overview', 'evidence', 'signals', 'forecast', 'lab', 'verification'];
const docNames = {brief:'The plain-language brief',report:'The historical watch report',study:'The founding study',grading:'How evidence is graded','threat-model':'Data boundaries & threat model','forecast-method':'Forecast protocol',testing:'What the tests establish','local-app':'Using this observatory'};
const instrumentNames = {wgi_va:'World Bank · Voice & Accountability',vdem_foe:'V-Dem · Freedom of Expression',fh:'Freedom House · Civil Liberties'};
let state, pollTimer, jobs = [], starting = false, readerRequest = 0, jobSignature = '';
let jobsKnown = false, statusError = '', runError = '', pollVersion = 0, statusFailures = 0;
function node(tag, text, className) { const n=document.createElement(tag); if(text!==undefined)n.textContent=text; if(className)n.className=className; return n; }
function fill(id, children) { $(id).replaceChildren(...children); }
function number(n, digits=3) { return n===null || n===undefined ? 'Unavailable' : Number(n).toLocaleString('en', {maximumFractionDigits:digits}); }
function percent(n) { return n===null || n===undefined ? 'Unavailable' : `${number(n*100,1)}%`; }
async function api(path, options = {}) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 15000);
  try {
    const response = await fetch(path, {...options, signal: controller.signal});
    const data = await response.json();
    if (!response.ok) {
      const error = new Error(data.error || `Request failed (${response.status})`);
      error.status = response.status;
      throw error;
    }
    return data;
  } catch (error) {
    if (error.name === 'AbortError') throw new Error('The local server request timed out.');
    throw error;
  } finally { clearTimeout(timeout); }
}
function showError(error) { $('error-message').textContent=error.message || 'Could not load Pharos.'; $('error').hidden=false; }
function route(focus=false) { let view=location.hash.slice(1) || 'overview'; if(!views.includes(view)){view='overview';history.replaceState(null,'','#overview');} for(const v of views)$(v).hidden=v!==view; document.querySelectorAll('[data-view]').forEach(a=>{if(a.dataset.view===view)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current');}); document.title='Pharos — '+({overview:'Research observatory',evidence:'Evidence ledger',signals:'Institutional signals',forecast:'Forecast evaluation',lab:'Mechanism lab',verification:'Verification'})[view]; if(focus)$('main').focus(); }
function stat(label, value, note) { const div=node('div',undefined,'stat'); div.append(node('div',label,'small-label'),node('strong',value),node('span',note)); return div; }
function openReader(title) { readerRequest++; $('reader-title').textContent=title; fill('reader-body',[node('p','Loading source…')]); if(!$('reader').open)$('reader').showModal(); return readerRequest; }
function sourceLinks(text) { const urls=[...new Set(text.match(/https:\/\/[^\s<>"\]]+/g)||[])]; if(!urls.length)return null; const details=node('details'); details.append(node('summary','Open cited source links')); const list=node('ul'); for(let url of urls){url=url.replace(/[.,;]+$/,''); const a=node('a',url);a.href=url;a.target='_blank';a.rel='noopener noreferrer';const li=node('li');li.append(a);list.append(li);} details.append(list);return details; }
async function readDocument(key) { const request=openReader(docNames[key]); try {const d=await api('/api/document/'+key); if(request!==readerRequest)return; fill('reader-body',[node('pre',d.text)]);} catch(e){if(request===readerRequest)fill('reader-body',[node('p',e.message)]);} }
async function readEntry(entry) { const request=openReader(`${entry.id} · ${entry.title}`); try {const d=await api('/api/entry/'+entry.id); if(request!==readerRequest)return; const content=[node('pre',d.text)];const links=sourceLinks(d.text);if(links)content.unshift(links);fill('reader-body',content);} catch(e){if(request===readerRequest)fill('reader-body',[node('p',e.message)]);} }
async function viewExport(url, filename) {
  const request=openReader('Export: '+filename);
  try {
    const response=await fetch(url);
    if(!response.ok)throw new Error('Could not load this export. Please try again.');
    const text=await response.text();
    if(request!==readerRequest)return;
    const intro=node('p','Download the source file, copy its contents, or select the text below.');
    const contents=node('textarea');contents.value=text;contents.readOnly=true;contents.className='export-contents';contents.setAttribute('aria-label','Export contents');
    const actions=node('div',undefined,'export-actions'),download=node('a','Download file ↓','download');download.href=url;download.download=filename;
    const status=node('p','');status.setAttribute('role','status');
    const copy=node('button','Copy contents');copy.addEventListener('click',async()=>{try{await navigator.clipboard.writeText(text);status.textContent='Copied the complete export.';}catch(_error){status.textContent='Clipboard access is unavailable. Select all, then use your usual copy shortcut.';}});
    const select=node('button','Select all','secondary');select.addEventListener('click',()=>{contents.focus();contents.select();status.textContent='Complete export selected. Use your usual copy shortcut.';});
    actions.append(download,copy,select);fill('reader-body',[intro,actions,status,contents]);
  } catch(error) {if(request===readerRequest)fill('reader-body',[node('p',error.message)]);}
}
function overview() {
  const g=state.governance, o=g.overall;
  $('snapshot').textContent=`Historical window ${g.baseline_year}–${g.latest_year} · Source snapshot fetched ${g.fetched_utc.slice(0,10)} · Review status checked ${state.as_of}`;
  fill('stats',[stat('EVIDENCE ENTRIES',state.ledger.length,'Every claim keeps its grade'),stat('INSTRUMENTS',Object.keys(state.divergence.sources).length,'Distinct measures, shown separately'),stat('COUNTRIES / TERRITORIES',state.divergence.countries.length,'Historical comparison coverage'),stat('MECHANISM MODELS',state.simulations.length,'Runnable local demonstrations')]);
  $('noise-description').textContent=`${percent(o.within_noise/o.dimension_country_cells)} of ${number(o.dimension_country_cells)} country × dimension changes do not clear the WGI 90% significance bar. This is a measurement limit, not evidence of no change.`;
  fill('noise-figures',[['Within noise',o.within_noise],['Declines',o.meaningful_declines],['Improvements',o.meaningful_improvements]].map(([label,n])=>{const d=node('div');d.append(node('strong',number(n)),node('span',label));return d;}));
  $('overview-verdict').textContent=`Across ${number(state.forecast.result.n_forecasts)} pre-registered forecasts, the model suite ${state.forecast.verdict}.`;
  fill('documents',state.documents.map(key=>{const b=node('button',docNames[key]+' ↗');b.addEventListener('click',()=>readDocument(key));return b;}));
}
function evidence() {
  const q=$('evidence-search').value.trim().toLowerCase(),grade=$('grade-filter').value,review=$('review-filter').value;
  const list=state.ledger.filter(e=>(!grade||e.grade===grade)&&(!q||`${e.id} ${e.title} ${e.domain}`.toLowerCase().includes(q))&&(!review||(review==='stale'?e.review.stale:e.review.stale||e.review.days_left<=90)));
  $('evidence-count').textContent=`${list.length} of ${state.ledger.length} entries`;
  fill('evidence-list',list.length?list.map(e=>{const card=node('article',undefined,'evidence-card'),top=node('div',undefined,'entry-top'); top.append(node('span',e.id),node('span',e.grade,`badge ${e.grade.toLowerCase()}`),node('span',e.domain));card.append(top,node('h2',e.title));const trigger=node('p');trigger.append(node('strong','What would change this conclusion: '),document.createTextNode(e.falsification_trigger||'Read the entry for its stated conditions.'));card.append(trigger);const r=e.review;card.append(node('p',`Last reviewed: ${r.reviewed||'not recorded'} · ${r.stale?'OVERDUE':`${r.days_left} days until review due`}`,'review-text'));const b=node('button','Read entry & sources','secondary');b.addEventListener('click',()=>readEntry(e));card.append(b);return card;}):[node('p','No evidence matches these filters. Try another search or clear the filters.','empty')]);
}
function countryDetails(c) {
  openReader(c.country_name+' · '+c.agreement.label);
  const elements=[node('p',`Historical window ${state.divergence.window.join('–')}. ${c.agreement.n_available} instruments available; ${c.agreement.n_sig} flagged by their respective rules.`)];
  for(const [key,i] of Object.entries(c.instruments)){elements.push(node('h3',instrumentNames[key])); if(!i.available){elements.push(node('p','Unavailable — this snapshot has insufficient observations.'));continue;}elements.push(node('p',`${number(i.v_start,4)} → ${number(i.v_end,4)}; change ${number(i.delta,4)} (${i.unit}). Flag: ${i.flag}; rule: ${i.flag_basis}${i.z!==undefined?`; z = ${number(i.z)}`:''}${i.threshold!==undefined?`; threshold = ${i.threshold}`:''}.`));}
  if(c.agreement.dissenting.length)elements.push(node('p','Dissenting instrument(s): '+c.agreement.dissenting.map(k=>instrumentNames[k]).join(', ')));
  elements.push(node('p','These measures have different scales and uncertainty models. They are not averaged into a score.'));
  fill('reader-body',elements);
}
function signals() {
  const q=$('country-search').value.trim().toLowerCase(),filter=$('agreement-filter').value;
  const countries=state.divergence.countries.filter(c=>(!q||`${c.country_name} ${c.country}`.toLowerCase().includes(q))&&(!filter||c.agreement.label===filter)).sort((a,b)=>a.country_name.localeCompare(b.country_name));
  $('country-count').textContent=`${countries.length} of ${state.divergence.countries.length} countries / territories`;
  const rows=countries.map(c=>{const tr=node('tr');tr.append(node('td',c.country_name));for(const key of Object.keys(instrumentNames)){const i=c.instruments[key],td=node('td',i.available?number(i.delta,4):'Unavailable');td.append(node('small',i.available?`${i.flag} · ${i.flag_basis}`:'No value imputed'));tr.append(td);}tr.append(node('td',c.agreement.label));const td=node('td'),b=node('button','Inspect','secondary');b.setAttribute('aria-label','Inspect '+c.country_name);b.addEventListener('click',()=>countryDetails(c));td.append(b);tr.append(td);return tr;});
  if(!rows.length){const tr=node('tr'),td=node('td','No countries match. Clear filters to see the full comparison.');td.colSpan=6;tr.append(td);rows.push(tr);}fill('country-rows',rows);
}
function initSignals() {
  const d=state.divergence;
  $('signals-window').textContent=`Historical comparison: ${d.window.join('–')}. Snapshot data, not a live situation monitor.`;
  fill('agreement-counts',Object.entries(d.counts).map(([k,v])=>node('span',`${k} · ${v}`)));
  const select=$('agreement-filter');select.replaceChildren(new Option('All categories',''));for(const k of Object.keys(d.counts))select.add(new Option(k,k));
  const children=[node('p',state.governance.method),node('p',`All-three-significant concur-decline subset: ${d.headline_concur_decline_n_sig_3.length}. CONCUR categories require at least two flags and must not be confused with this stricter subset.`)];
  for(const [k,s] of Object.entries(d.sources)){const p=node('p'),a=node('a',s.name);a.href=s.url||state.governance.source_url;a.target='_blank';a.rel='noopener noreferrer';p.append(a,document.createTextNode(` · Scale ${s.scale}. ${s.license||'World Bank WGI; cite the source.'} Snapshot: ${d.input_provenance[k].fetched_utc}.`));children.push(p);}fill('signal-sources',children);signals();
}
function forecastData() { return $('forecast-window').value==='holdout'?state.holdout:state.forecast.result; }
function forecast() {
  const holdout=$('forecast-window').value==='holdout',d=forecastData();
  $('forecast-verdict').textContent=holdout?state.holdout.verdict.reason:state.forecast.verdict;
  $('forecast-bar').textContent='Pre-registered success bar: '+state.forecast.pre_registered.success_bar+'.';
  $('forecast-note').textContent=holdout?`${number(d.n_forecasts)} forecasts · Origins ${state.holdout.holdout_origins.join(', ')} · Recorded run ${state.holdout.run_date}. ${state.holdout.note}`:`${number(d.n_forecasts)} forecasts · ${state.forecast.pre_registered.horizon_years}-year horizon · Origins ${state.forecast.pre_registered.origins.join('–')} · Pinned data fetched ${state.forecast.input_provenance.fetched_utc.slice(0,10)}.`;
  fill('forecast-rows',Object.entries(d.per_model).map(([name,m])=>{const tr=node('tr');[name.replaceAll('_',' '),number(m.crps,5),number(m.brier,5),percent(m.crps_skill),percent(m.brier_skill),name==='no_change'?'Reference baseline':m.crps_skill>0&&m.brier_skill>0?'Yes; inspect calibration':'No'].forEach(t=>tr.append(node('td',t)));return tr;}));
  const select=$('calibration-model'),previous=select.value;select.replaceChildren();for(const name of Object.keys(d.per_model))select.add(new Option(name.replaceAll('_',' '),name));if(d.per_model[previous])select.value=previous;calibration();
}
function calibration() { const m=forecastData().per_model[$('calibration-model').value];fill('calibration-rows',m.reliability.map(([lo,hi,n,p,o])=>{const tr=node('tr');[`${percent(lo)}–${percent(hi)}`,number(n),percent(p),percent(o)].forEach(t=>tr.append(node('td',t)));return tr;})); }
function lab() {fill('simulation-cards',state.simulations.map(s=>{const card=node('article',undefined,'panel');card.append(node('h2',s.name),node('p',s.reference,'reference'),node('p',s.description));const b=node('button','Run demonstration','secondary');b.dataset.run=s.id;b.disabled=true;b.setAttribute('aria-label','Run '+s.name);b.addEventListener('click',()=>startRun(s.id));card.append(b);return card;}));}
function runName(kind) {return kind==='verify'?'Complete offline verification':kind==='simulations'?'All seven demonstrations':state.simulations.find(s=>s.id===kind)?.name||kind;}
const statusNames={running:'Running',passed:'Passed — software checks',completed:'Completed — demonstration execution',failed:'Failed',timed_out:'Timed out',source_changed:'Source changed during run — result needs review',error:'Could not complete'};
function renderRuns() {
  const active = jobs.find(j => j.status === 'running');
  const busy = Boolean(starting || !jobsKnown || active);
  const message = starting ? `Starting ${runName(starting)}…`
    : !jobsKnown ? statusError || 'Checking whether a local run is already active…'
    : active ? `${runName(active.kind)} is running. Other runs are paused until it finishes. View progress in Verification.`
    : runError || (jobs.length ? 'Ready for another run. Results and execution receipts are in Verification.' : 'Ready. Choose a demonstration or run verification.');
  document.querySelectorAll('[data-run]').forEach(button => {
    button.disabled = busy;
    button.setAttribute('aria-describedby', button.id === 'run-verification' ? 'run-message' : 'lab-run-message');
  });
  $('run-message').textContent = message;
  $('lab-run-message').textContent = message;
  const signature=JSON.stringify(jobs);if(signature===jobSignature)return;jobSignature=signature;
  fill('runs',jobs.map(j=>{const card=node('article',undefined,'run-card');card.append(node('span',statusNames[j.status]||j.status,'badge'),node('h2',runName(j.kind)));const dl=node('dl');for(const [key,value] of [['Started',j.started_utc],['Finished',j.finished_utc||'Still running'],['Exit code',j.exit_code===null?'Not available':String(j.exit_code)],['Source files',j.source_unchanged===null?'Checking…':j.source_unchanged?'Unchanged during this run':'Changed — inspect before relying on this result'],['Input fingerprint',j.inputs?.sha256||'Pending']]){dl.append(node('dt',key),node('dd',value));}card.append(dl);if(j.status!=='running'){const a=node('a','Export execution receipt ↓','download');a.href='/api/jobs/'+j.id;a.download=`pharos-${j.kind}-${j.id}.json`;a.addEventListener('click',event=>{event.preventDefault();viewExport(a.getAttribute('href'),a.download);});card.append(a);}if(j.receipt_warning)card.append(node('p',j.receipt_warning));if(j.output){const details=node('details');details.append(node('summary',j.output_truncated?'Execution output (last 200 KB)':'Execution output'),node('pre',j.output));card.append(details);}return card;}));
}
async function refreshJobs() {
  clearTimeout(pollTimer);
  const request = ++pollVersion;
  try {
    const latest = await api('/api/jobs');
    if (request !== pollVersion) return;
    if (!Array.isArray(latest) || latest.some(job => !job || !Object.hasOwn(statusNames, job.status)))
      throw new Error('The server returned an unreadable run status.');
    jobs = latest; jobsKnown = true; statusError = ''; statusFailures = 0;
    renderRuns();
    if (jobs.some(job => job.status === 'running')) pollTimer = setTimeout(refreshJobs, 1000);
  } catch (error) {
    if (request !== pollVersion) return;
    jobsKnown = false;
    statusError = `${error.message} Reconnecting automatically. A run may still be active; no new run has been sent.`;
    renderRuns();
    statusFailures++;
    pollTimer = setTimeout(refreshJobs, Math.min(30000, 1000 * 2 ** Math.min(statusFailures, 5)));
  }
}
async function startRun(kind) {
  if (starting || !jobsKnown || jobs.some(job => job.status === 'running')) return;
  starting = kind; runError = ''; ++pollVersion; clearTimeout(pollTimer); renderRuns();
  const submit = () => api('/api/jobs', {method:'POST', headers:{'Content-Type':'application/json', 'X-Pharos-Token':state.run_token}, body:JSON.stringify({kind})});
  try {
    let job;
    try { job = await submit(); }
    catch (error) {
      // A 403 means the server rejected the request before executing it.
      // Refresh a token invalidated by a server restart, once. Never resubmit
      // after a timeout or lost response: the original job may have started.
      if (error.status !== 403) throw error;
      const fresh = await api('/api/state');
      if (!fresh.run_token) throw error;
      state.run_token = fresh.run_token;
      job = await submit();
    }
    jobs = [job, ...jobs.filter(previous => previous.id !== job.id)];
    location.hash = 'verification';
  } catch (error) {
    runError = `Could not confirm the run: ${error.message} Check recent results before trying again.`;
  } finally {
    starting = false; jobsKnown = false; renderRuns(); await refreshJobs();
  }
}
async function load() {$('loading').hidden=false;$('error').hidden=true;try{state=await api('/api/state');overview();evidence();initSignals();forecast();lab();route();$('app').hidden=false;await refreshJobs();}catch(e){$('app').hidden=true;showError(e);}finally{$('loading').hidden=true;} }
$('reader-close').addEventListener('click',()=>$('reader').close());$('reader').addEventListener('close',()=>readerRequest++);
document.querySelectorAll('a[download]').forEach(link=>link.addEventListener('click',event=>{event.preventDefault();viewExport(link.getAttribute('href'),link.getAttribute('href').split('/').pop());}));
document.querySelector('.skip').addEventListener('click',event=>{event.preventDefault();$('main').focus();});
$('retry').addEventListener('click',load);window.addEventListener('hashchange',()=>route(true));
for(const id of ['evidence-search','grade-filter','review-filter'])$(id).addEventListener(id.endsWith('search')?'input':'change',()=>state&&evidence());
$('evidence-reset').addEventListener('click',()=>{for(const id of ['evidence-search','grade-filter','review-filter'])$(id).value='';evidence();});
$('country-search').addEventListener('input',()=>state&&signals());$('agreement-filter').addEventListener('change',()=>state&&signals());$('country-reset').addEventListener('click',()=>{$('country-search').value='';$('agreement-filter').value='';signals();});
$('forecast-window').addEventListener('change',forecast);$('calibration-model').addEventListener('change',calibration);
for(const id of ['run-verification','run-simulations'])$(id).addEventListener('click',()=>startRun($(id).dataset.run));
load();
