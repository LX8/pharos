// SPDX-FileCopyrightText: 2026 The Pharos contributors
// SPDX-License-Identifier: GPL-3.0-or-later
const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const appDir = process.env.PHAROS_APP_DIR || path.resolve(__dirname, '../site/app');
const source = fs.readFileSync(path.join(appDir, 'app.js'), 'utf8').replace(/load\(\);\s*$/, '');
const html = fs.readFileSync(path.join(appDir, 'index.html'), 'utf8');

function harness() {
  class Element {
    constructor() { this.dataset = {}; this.children = []; this.attributes = {}; this.listeners = {}; this.textContent = ''; this.hidden = false; }
    append(...items) { this.children.push(...items); }
    replaceChildren(...items) { this.children = items; }
    setAttribute(key, value) { this.attributes[key] = String(value); }
    getAttribute(key) { return this.attributes[key] || null; }
    addEventListener(type, fn) { this.listeners[type] = fn; }
  }
  const elements = new Map([...html.matchAll(/id="([^"]+)"/g)].map(m => [m[1], new Element()]));
  for (const [id, element] of elements) element.id = id;
  const buttons = [elements.get('run-verification'), elements.get('run-simulations'), new Element()];
  ['verify', 'simulations', 'threshold_cascade'].forEach((kind, i) => { buttons[i].dataset.run = kind; });
  const timers = new Map(); let nextTimer = 1;
  const context = vm.createContext({
    AbortController, console, location: {hash: '#lab'}, window: {addEventListener() {}},
    document: {getElementById: id => elements.get(id), createElement: () => new Element(),
      querySelector: () => new Element(), querySelectorAll: selector => selector === '[data-run]' ? buttons : []},
    setTimeout(fn, delay) { const id = nextTimer++; timers.set(id, {fn, delay}); return id; },
    clearTimeout(id) { timers.delete(id); }, fetch: async () => {throw new Error('Unexpected request');},
  });
  vm.runInContext(source, context);
  vm.runInContext("state={run_token:'old',simulations:[{id:'threshold_cascade',name:'Threshold cascades'}]};", context);
  const run = code => vm.runInContext(code, context);
  const response = (data, status=200) => ({ok: status < 400, status, json: async () => data});
  return {context, elements, buttons, timers, run, response};
}
const running = {id:'synthetic-job', kind:'threshold_cascade', status:'running', started_utc:'test', exit_code:null, source_unchanged:null};

test('a failed status poll recovers and releases the run buttons after completion', async () => {
  const h = harness(); h.context.fetch = async () => h.response([running]);
  await h.context.refreshJobs();
  assert.ok(h.buttons.every(b => b.disabled));
  h.context.fetch = async () => {throw new Error('Connection lost');};
  await h.context.refreshJobs();
  assert.ok(h.timers.size, 'A failed poll must schedule recovery instead of freezing the controls');
  assert.match(h.elements.get('lab-run-message').textContent, /reconnect|retry/i);
  h.context.fetch = async () => h.response([{...running, status:'completed'}]);
  const retry = [...h.timers.values()][0]; h.timers.clear(); await retry.fn();
  assert.ok(h.buttons.every(b => !b.disabled));
  assert.match(h.elements.get('lab-run-message').textContent, /ready/i);
});

test('Lab shows why run buttons are disabled and links to the execution results', async () => {
  const h = harness(); h.context.fetch = async () => h.response([running]);
  await h.context.refreshJobs();
  assert.match(h.elements.get('lab-run-message').textContent, /Threshold cascades.*running/i);
  assert.equal(h.buttons[0].getAttribute('aria-describedby'), 'run-message');
  assert.ok(h.buttons.slice(1).every(b => b.getAttribute('aria-describedby')?.includes('lab-run-message')));
  assert.match(html, /id="lab"[\s\S]*?href="#verification"[\s\S]*?<\/section>/);
});

test('requests time out and clean up their timer instead of keeping controls locked', async () => {
  const h = harness();
  h.context.fetch = (_url, options) => new Promise((_resolve, reject) => {
    options?.signal?.addEventListener('abort', () => reject(Object.assign(new Error('aborted'), {name:'AbortError'})));
  });
  const pending = h.context.api('/api/jobs');
  assert.equal(h.timers.size, 1, 'Every API request needs a bounded wait');
  [...h.timers.values()][0].fn();
  await assert.rejects(pending, /timed out/i);
  assert.equal(h.timers.size, 0);
});

test('a restarted server refreshes a rejected token once before starting the requested run', async () => {
  const h = harness(); let posts = 0;
  h.context.fetch = async (url, options) => {
    if (options?.method === 'POST') {
      posts++;
      if (posts === 1) return h.response({error:'Run checks from the local Pharos app.'}, 403);
      assert.equal(options.headers['X-Pharos-Token'], 'new');
      return h.response(running, 202);
    }
    if (url === '/api/state') return h.response({run_token:'new'});
    return h.response(posts ? [running] : []);
  };
  await h.context.refreshJobs(); await h.context.startRun('threshold_cascade');
  assert.equal(posts, 2);
  assert.equal(h.context.location.hash, 'verification');
  assert.ok(h.buttons.every(b => b.disabled));
});

test('an ambiguous start failure never automatically resubmits the job', async () => {
  const h = harness(); let posts = 0;
  h.context.fetch = async (_url, options) => {
    if (options?.method === 'POST') {posts++; throw new Error('Connection lost');}
    return h.response(posts ? [running] : []);
  };
  await h.context.refreshJobs(); await h.context.startRun('threshold_cascade');
  assert.equal(posts, 1);
  assert.ok(h.buttons.every(b => b.disabled));
  assert.match(h.elements.get('lab-run-message').textContent, /running/i);
});

test('starting feedback is immediate and a repeated click cannot send a second request', async () => {
  const h = harness(); let resolvePost, posts = 0;
  h.context.fetch = async (_url, options) => {
    if (options?.method === 'POST') {posts++; return new Promise(resolve => {resolvePost = resolve;});}
    return h.response(posts ? [running] : []);
  };
  await h.context.refreshJobs(); const pending = h.context.startRun('threshold_cascade');
  assert.match(h.elements.get('lab-run-message').textContent, /starting.*Threshold cascades/i);
  await h.context.startRun('threshold_cascade'); assert.equal(posts, 1);
  resolvePost(h.response(running, 202)); await pending;
});

test('a stale in-flight poll cannot re-enable buttons during a newly started run', async () => {
  const h = harness(); h.context.fetch = async () => h.response([]);
  await h.context.refreshJobs(); let resolveOld;
  h.context.fetch = async () => new Promise(resolve => {resolveOld = resolve;});
  const stale = h.context.refreshJobs();
  h.context.fetch = async (_url, options) => h.response(options?.method === 'POST' ? running : [running]);
  await h.context.startRun('threshold_cascade');
  resolveOld(h.response([])); await stale;
  assert.ok(h.buttons.every(b => b.disabled));
  assert.match(h.elements.get('lab-run-message').textContent, /running/i);
});
