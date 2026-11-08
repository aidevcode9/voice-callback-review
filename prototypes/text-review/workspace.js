/* Browser-only design simulation. No inference, project data, or API access. */
(() => {
  const direction = document.body.className;
  const key = `vcr-prototype-${direction}-v1`;
  const model = 'qwen35-4b';
  const names = { callback_required: 'Callback required', no_callback: 'No callback', needs_review: 'Needs review' };
  const tones = { callback_required: '', no_callback: 'clear', needs_review: 'review' };
  const examples = [
    { id: 'DEMO-101', title: 'Appointment confirmation', text: 'Caller: I received the appointment details. That answers my question.\nRepresentative: Glad we could clear that up.\nCaller: Please still call me tomorrow to confirm the time with my sister.\nRepresentative: I have noted your request.\nCaller: Thank you. Goodbye.', label: 'callback_required', rule: 'CB-002', quote: 'Please still call me tomorrow to confirm the time with my sister.', reason: 'The appointment question is resolved, but a separate request for a callback remains outstanding.' },
    { id: 'DEMO-102', title: 'Directions clarified', text: 'Caller: I could not find your entrance.\nRepresentative: Use the east entrance, beside the pharmacy.\nCaller: I see it now. That solves it and I do not need any further help.\nRepresentative: See you shortly.', label: 'no_callback', rule: 'NC-003', quote: 'That solves it and I do not need any further help.', reason: 'The earlier issue is resolved before the conversation ends, with no outstanding follow-up.' },
    { id: 'DEMO-103', title: 'Call ends mid-request', text: 'Caller: I am calling about the forms you sent. I need to ask whether…\n[Conversation ends before the request is completed.]', label: 'needs_review', rule: 'NR-001', quote: '[Conversation ends before the request is completed.]', reason: 'The incomplete conversation does not establish resolution or a clear follow-up obligation.' }
  ];
  const seedRun = (c, index) => ({ id: `SIM-${index + 1}01`, version: 1, text: c.text, model, status: 'succeeded', label: c.label, rule: c.rule, quote: c.quote, reason: c.reason, at: 'Sample run', review: null });
  const fresh = () => ({ cases: examples.map((c, i) => ({ ...c, versions: [c.text], runs: [seedRun(c, i)] })), active: 'DEMO-101', serial: 1 });
  let state;
  try { state = JSON.parse(localStorage.getItem(key)) || fresh(); } catch { state = fresh(); }
  let outcomeFilter = 'all', statusFilter = 'all', selected = null, editing = false, scenario = 'success', busy = false, message = '';
  const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const active = () => state.cases.find(c => c.id === state.active);
  const currentText = () => active().versions.at(-1) || '';
  const currentRun = () => active().runs.find(r => r.id === selected) || active().runs.at(-1);
  const save = () => { try { localStorage.setItem(key, JSON.stringify(state)); } catch { message = 'Browser storage is unavailable. This session will not survive reload.'; } };
  const badge = (label, neutral = false) => `<span class="badge ${neutral ? 'neutral' : tones[label] || ''}">${esc(names[label] || label)}</span>`;
  function render() {
    const focusId = document.activeElement?.id;
    const c = active(), r = currentRun(), version = r?.version || c.versions.length;
    const visible = state.cases.filter(item => (outcomeFilter === 'all' || item.runs.at(-1)?.label === outcomeFilter) && (statusFilter === 'all' || (statusFilter === 'reviewed' ? item.runs.at(-1)?.review : !item.runs.at(-1)?.review)));
    document.getElementById('app').innerHTML = `
      <div class="prototype"><span>Interactive prototype · fictional cases & simulated processing</span><a href="index.html">Compare directions</a></div>
      <header class="brand"><strong>Voice Callback Review</strong><span>${direction === 'desk' ? 'Review desk' : 'Casebook'} · local workspace</span></header>
      <div class="shell"><nav aria-label="Development cases"><h2>Development cases</h2>
      <div class="filters"><label>Outcome<select id="outcome-filter"><option value="all">All outcomes</option>${Object.entries(names).map(([v,n])=>`<option value="${v}" ${v===outcomeFilter?'selected':''}>${n}</option>`).join('')}</select></label>
      <label>Human review<select id="status-filter"><option value="all">All reviews</option><option value="pending" ${statusFilter==='pending'?'selected':''}>Not reviewed</option><option value="reviewed" ${statusFilter==='reviewed'?'selected':''}>Reviewed</option></select></label></div>
      <div class="case-list">${visible.length ? visible.map(item=>`<button class="case-link" data-case="${esc(item.id)}" aria-current="${item.id===c.id}"><small>${esc(item.id)} · fictional</small><strong>${esc(item.title)}</strong>${badge(item.runs.at(-1)?.label || 'Not classified', !item.runs.at(-1)?.label)}</button>`).join('') : '<p class="help">No matching cases. Choose All outcomes and All reviews to see the samples.</p>'}</div>
      <div class="nav-actions"><button id="new-case" ${busy?'disabled':''}>Paste transcript</button><button id="load-case" ${busy?'disabled':''}>Load fictional case</button></div><p class="nav-footer">Development workspace only.<br>Held-out cases and answers are excluded.<br><br>Audio integration is planned for the final stage.</p></nav>
      <main class="content"><div class="case-header"><div><h1>${esc(c.title)}</h1><p>${esc(c.id)} · fictional development material · ${c.versions.length ? `transcript v${c.versions.length}` : 'unsaved transcript'}</p></div>${badge(!r ? 'No run to review' : r.status==='failed' ? 'Processing failed' : r?.review ? 'Human reviewed' : 'Awaiting human review', true)}</div>
      <div class="workspace"><section class="transcript" aria-labelledby="transcript-heading"><div class="section-head"><h2 id="transcript-heading">Transcript</h2><button id="edit-text" ${busy?'disabled':''}>${editing?'Read with evidence':'Edit transcript'}</button></div>
      <div class="transcript-meta">${editing ? `Editing a draft from v${c.versions.length}. Saving creates a new version.` : `Viewing ${r ? `${esc(r.id)} · v${version}` : (version ? `current v${version}` : 'Unsaved transcript')} · ${r?.status==='succeeded'?'highlighted quote supports this run':'no successful evidence for this view'}`}</div>
      ${editing ? `<div class="editor"><label for="transcript-input">Transcript text</label><textarea id="transcript-input" placeholder="Paste a fictional service-call transcript…">${esc(currentText())}</textarea><div class="actions"><button class="primary" id="save-text">Save new version</button><button id="cancel-edit">Discard draft</button></div><p class="help">12,000 UTF-8 bytes maximum. Earlier versions and results remain available.</p><p id="edit-error" class="help" role="alert"></p></div>` : currentText() ? `<div class="conversation">${conversation(r?.text || currentText(), r?.status==='succeeded' ? r.quote : '')}</div><p class="evidence-note">${r?.status==='succeeded' ? 'Highlighted text is an exact quote from this run’s transcript version.' : 'Save or select a transcript, then explicitly classify it.'}</p>` : '<div class="empty"><h2>Start with a conversation</h2><p>Paste a transcript or load a fictional development case. Then select an available model and request a classification.</p><button id="empty-load">Load fictional case</button></div>'}
      <div class="classification"><label>Classification model<select id="model" ${busy?'disabled':''}><option value="${model}" ${scenario==='unavailable'?'disabled':''}>Qwen3.5 · 4B · Q4_K_M</option><option disabled>Whisper · transcription · later</option></select></label><div class="actions"><button class="primary" id="classify" ${busy||editing||!currentText()||scenario==='unavailable'?'disabled':''}>${busy?'Classifying…':(c.versions.length ? `Classify transcript v${c.versions.length}` : 'Save a transcript first')}</button></div><p class="help">${scenario==='unavailable'?'Runtime unavailable. Restore local Ollama, then check availability.':'Explicit submission only. Selector changes do not run inference.'}</p></div></section>
      <aside class="decision-column" aria-label="Recommendation and human review"><section class="result" aria-live="polite"><h2>Model recommendation</h2>${processingStatus()}${result(r, c)}</section>${review(r)}</aside></div>
      ${message ? `<div class="notice" role="status">${esc(message)}</div>` : ''}
      <section class="history"><div class="history-head"><h2>Run history</h2><span class="help">${c.runs.length} preserved ${c.runs.length===1?'run':'runs'} · simulated</span></div><div class="runs">${c.runs.length ? [...c.runs].reverse().map(item=>`<button class="run" data-run="${esc(item.id)}" aria-pressed="${r?.id===item.id}"><strong>${esc(item.id)} · transcript v${item.version}</strong>${item.status==='succeeded' ? esc(names[item.label]) : esc(item.error)} · ${item.review?'human reviewed':'not reviewed'}<br>Qwen3.5 4B · ${esc(item.at)}</button>`).join('') : '<p class="help">No runs yet. An explicit classification will appear here.</p>'}</div>
      ${r ? `<details class="provenance"><summary>Inspect run provenance</summary><dl><dt>Run</dt><dd>${esc(r.id)} · simulated ${esc(r.status)}</dd><dt>Input</dt><dd>${esc(c.id)} / transcript v${r.version} · exact snapshot retained in this browser</dd><dt>Model</dt><dd>${esc(r.model)} / qwen3.5:4b-q4_K_M</dd><dt>Policy / prompt</dt><dd>v1.0 / callback-text-v2 (illustrative, no real request)</dd><dt>Identity</dt><dd>Production will expose source, transcript, request, policy and model hashes. No digest is fabricated here.</dd><dt>Settings</dt><dd>Context 8192 · output cap 768 · temperature 0 · seed 42 · thinking off (planned reuse of core)</dd><dt>Processing</dt><dd>Browser simulation only. No measured inference timing.</dd><dt>Human decision</dt><dd>${r.review?`${esc(names[r.review.label])} · ${esc(r.review.note || 'No note')} · separate from model output`:'Not recorded'}</dd></dl></details>`:''}</section>
      <footer class="lab"><p>Prototype controls<br>These simulate states; they do not configure the model.</p><label>Next simulated response<select id="scenario">${['success','loading','timeout','malformed','unavailable'].map(s=>`<option value="${s}" ${s===scenario?'selected':''}>${({success:'Valid sample output',loading:'Keep loading',timeout:'Timeout',malformed:'Malformed model output',unavailable:'Runtime unavailable'})[s]}</option>`).join('')}</select></label><button id="reset">Reset prototype</button></footer></main></div>`;
    if(direction==='casebook'){const work=document.querySelector('.workspace');work.prepend(document.querySelector('.decision-column'));}
    bind();
    if(focusId)document.getElementById(focusId)?.focus({preventScroll:true});
  }
  function conversation(text, quote) {
    return text.split('\n').map(line => {
      const colon = line.indexOf(':');
      const speaker = colon > 0 && colon < 20 ? line.slice(0, colon) : 'Note';
      let body = colon > 0 && colon < 20 ? line.slice(colon + 1).trim() : line;
      let safe = esc(body);
      if (quote && body.includes(quote)) safe = safe.replace(esc(quote), `<mark>${esc(quote)}</mark>`);
      return `<div class="utterance"><span class="speaker">${esc(speaker)}</span><p>${safe}</p></div>`;
    }).join('');
  }
  function processingStatus() {
    if(busy)return `<div class="notice"><strong>Classifying submitted transcript v${submitted.version}</strong>One simulated job is active for ${esc(submitted.caseId)}. No new result yet. Saved recommendations remain inspectable below.<div class="loading-bar"></div><button id="end-loading">Simulate timeout</button></div>`;
    if(scenario==='unavailable')return '<div class="notice error"><strong>Local runtime unavailable</strong>No new classification can start. Saved recommendations remain inspectable below. Start Ollama and check availability; no model is downloaded.</div><button id="check-runtime">Simulate restored runtime</button>';
    return '';
  }
  function result(r, c) {
    if (!r) return '<div class="notice"><strong>No classification yet</strong>Save a transcript, select the model, and choose Classify transcript.</div>';
    if (r.status === 'failed') return `<div class="notice error"><strong>${esc(r.error)}</strong>${r.error==='Inference timed out'?'The submitted job reached its deadline. No callback outcome was produced.':'The response failed validation. No callback outcome was produced.'} Prior successful runs remain in history. Explicitly submit again to retry.</div>`;
    return `${badge(r.label)}<h3 class="outcome ${tones[r.label]}">${esc(names[r.label])}</h3><p>${esc(r.reason)}</p><p class="rule">Policy v1.0 · ${esc(r.rule)}</p><p class="help">${esc(r.id)} · transcript v${r.version} · simulated output${r.version!==c.versions.length?' · newer text is saved; this run still uses its original version':''}</p><p class="quote">“${esc(r.quote)}”</p>`;
  }
  function review(r) {
    return `<form class="review-form" id="review-form"><h2>Human review</h2><p class="help">Your judgment is a separate record. It does not replace the model output or update gold.</p><label>Review decision<select id="review-choice" ${!r||r.status!=='succeeded'||busy?'disabled':''}><option value="">Choose a decision…</option>${Object.entries(names).map(([v,n])=>`<option value="${v}" ${r?.review?.label===v?'selected':''}>${n}</option>`).join('')}</select></label><label>Review note <span class="muted">(optional)</span><textarea id="review-note" placeholder="What did you find?" ${!r||r.status!=='succeeded'||busy?'disabled':''}>${esc(r?.review?.note || '')}</textarea></label><div class="actions"><button ${!r||r.status!=='succeeded'||busy?'disabled':''}>${r?.review?'Save another review decision':'Save human decision'}</button></div>${r?.review?`<p class="help">Saved separately for ${esc(r.id)}. Earlier review entries remain in the prototype record.</p>`:''}</form>`;
  }
  function on(id, event, handler) { document.getElementById(id)?.addEventListener(event, handler); }
  function bind() {
    document.querySelectorAll('[data-case]').forEach(el => el.onclick = () => { state.active=el.dataset.case; selected=null; editing=false; message=''; save(); render(); });
    document.querySelectorAll('[data-run]').forEach(el => el.onclick = () => { selected=el.dataset.run; editing=false; message='Earlier run selected. Its evidence still refers to its original transcript.'; render(); });
    on('outcome-filter','change',e=>{outcomeFilter=e.target.value;render();});
    on('status-filter','change',e=>{statusFilter=e.target.value;render();});
    on('scenario','change',e=>{scenario=e.target.value;render();});
    on('edit-text','click',()=>{editing=!editing;render();document.getElementById('transcript-input')?.focus();});
    on('cancel-edit','click',()=>{editing=false;render();});
    on('save-text','click',()=>{
      const value=document.getElementById('transcript-input').value;
      if(!value.trim()||new TextEncoder().encode(value).length>12000){document.getElementById('edit-error').textContent='Enter 1–12,000 UTF-8 bytes. Text is never truncated.';return;}
      active().versions.push(value); selected=null;editing=false;message=`Saved transcript v${active().versions.length}. Earlier results retain their original text. Classify explicitly to use the new version.`;save();render();
    });
    const load=()=>{state.active='DEMO-101';outcomeFilter='all';statusFilter='all';selected=null;editing=false;message='Loaded a fictional prototype case. No inference ran.';save();render();};
    on('load-case','click',load);on('empty-load','click',load);
    on('new-case','click',()=>{const id=`PASTED-${++state.serial}`;state.cases.push({id,title:'Pasted transcript',versions:[],runs:[]});state.active=id;selected=null;editing=true;message='';save();render();document.getElementById('transcript-input').focus();});
    on('classify','click',submit);
    on('end-loading','click',()=>{finish('timeout');});
    on('check-runtime','click',()=>{scenario='success';message='Simulated runtime restored. Submit explicitly to classify.';render();});
    on('review-form','submit',e=>{e.preventDefault();const r=currentRun(),label=document.getElementById('review-choice').value;if(!label){message='Choose a human decision before saving.';render();return;}const entry={label,note:document.getElementById('review-note').value};r.reviews=[...(r.reviews||[]),entry];r.review=entry;message=`Human decision saved separately for ${r.id}. Model output and frozen gold are unchanged.`;save();render();});
    on('reset','click',()=>{clearTimeout(timer);submitted=null;state=fresh();selected=null;editing=false;busy=false;scenario='success';outcomeFilter='all';statusFilter='all';message='Sample workspace restored.';save();render();});
  }
  let submitted=null, timer=null;
  function submit() {
    if(busy||editing||!currentText()||scenario==='unavailable')return;
    submitted={caseId:active().id,version:active().versions.length,text:currentText(),scenario};
    busy=true;message='';render();
    if(scenario!=='loading')timer=setTimeout(()=>finish(submitted.scenario),1100);
  }
  function finish(kind) {
    if(!submitted)return;
    clearTimeout(timer);
    const c=state.cases.find(item=>item.id===submitted.caseId);
    const sample=examples.find(item=>item.text===submitted.text);
    const r={id:`SIM-NEW-${++state.serial}`,version:submitted.version,text:submitted.text,model,status:kind==='success'?'succeeded':'failed',at:'Simulated just now',review:null};
    if(kind==='success')Object.assign(r,sample?{label:sample.label,rule:sample.rule,quote:sample.quote,reason:sample.reason}:{label:'needs_review',rule:'NR-001',quote:submitted.text.split('\n')[0].replace(/^[^:]{1,19}:\s*/, ''),reason:'Illustrative needs-review output for edited or pasted text. This is a browser simulation, not an assessment of the conversation.'});
    else r.error=kind==='timeout'?'Inference timed out':'Malformed model output';
    c.runs.push(r);busy=false;state.active=c.id;selected=r.id;submitted=null;message='Simulated run preserved. No real inference took place.';save();render();
  }
  render();
})();
