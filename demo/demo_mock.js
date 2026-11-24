/* SimpleScheduler 4 – in-memory server for the standalone demo page.
 *
 * export_demo.py puts this script before simplescheduler.js and fills DEMO_DATA with a snapshot
 * of a running add-on. It replaces fetch() and EventSource, so the page works from a file with no
 * server: every api/... call is answered from memory, the same way simplescheduler.py does.
 * Nothing is saved: reloading the page starts again from the snapshot.
 */
'use strict';
(function(){
  const DATA = window.DEMO_DATA;
  const S = JSON.parse(JSON.stringify(DATA.state));
  S.status = { home_assistant:true, mqtt:S.status && S.status.mqtt || 'Disabled' };
  const schedulers = new Map(S.schedulers.map(s => [s.id, s]));
  let logLines = DATA.log.slice();

  const APP_VERSION = '4.0.6';
  const VALID_DOMAINS = ['light','scene','switch','button','script','camera','climate','cover','vacuum','fan',
                         'humidifier','valve','automation','input_boolean','input_button','media_player'];
  const HVAC_MODES = ['heat','cool','heat_cool','auto','dry','fan_only'];
  const THEMES = ['auto','light','dark'];

  /* ---------- helpers (same rules as simplescheduler.py) ---------- */
  const pad = n => String(n).padStart(2, '0');
  function log(level, message){
    const d = new Date();
    const ts = d.getFullYear() + '-' + pad(d.getMonth()+1) + '-' + pad(d.getDate()) + ' ' + pad(d.getHours()) + ':' + pad(d.getMinutes()) + ':' + pad(d.getSeconds());
    logLines.push('[' + ts + '] ' + level.padEnd(7) + ' ' + message);
  }
  function newId(){ let s = ''; for (let i = 0; i < 32; i++) s += Math.floor(Math.random()*16).toString(16); return s; }
  function parseTime(token){
    const t = String(token).trim().toLowerCase().replace(/ /g, '');
    let m = t.match(/^(sunrise|sunset)([+-]\d{1,3})?$/);
    if (m) return [m[1], Number(m[2] || 0)];
    m = t.match(/^([01]?\d|2[0-3])[:.]([0-5]\d)$/);
    return m ? ['clock', Number(m[1])*60 + Number(m[2])] : null;
  }
  function formatTime(kind, value){
    if (kind === 'clock') return pad(Math.floor(value/60)) + ':' + pad(value % 60);
    return kind + (value ? (value > 0 ? '+' : '') + value : '');
  }
  const cleanDays = v => [...new Set(String(v || '').split('').filter(c => '1234567'.includes(c)))].sort().join('');
  const isTrue = v => ['1','true','on','yes'].includes(String(v).trim().toLowerCase());
  const fail = message => { throw { status:400, message }; };

  function generateRecurring(rule){
    const start = parseTime(rule.from)[1], end = parseTime(rule.to)[1];
    const extra = rule.extra && typeof rule.extra === 'object' ? rule.extra : {};
    const ifc = rule.if_condition !== false, force = rule.force === true;
    const entries = [];
    for (let minute = start; minute <= end && entries.length < 600; minute += rule.every){
      if (rule.action === 'off'){
        entries.push({ action:'off', time:formatTime('clock', minute), weekdays:rule.weekdays, extra:{}, if_condition:ifc, force });
      } else {
        entries.push({ action:'on', time:formatTime('clock', minute), weekdays:rule.weekdays, extra:JSON.parse(JSON.stringify(extra)), if_condition:ifc, force });
        if (rule.action === 'pulse' && minute + rule.duration < 1440)
          entries.push({ action:'off', time:formatTime('clock', minute + rule.duration), weekdays:rule.weekdays, extra:{}, if_condition:ifc, force:false });
        if (rule.action === 'pulse_random'){
          const low = minute + rule.duration_min, high = Math.min(1439, minute + rule.duration_max);
          if (low < 1440){
            const middle = Math.floor((low + high) / 2);
            const off = { action:'off', time:formatTime('clock', middle), weekdays:rule.weekdays, extra:{}, if_condition:ifc, force:false };
            if (high > low) off.random_range = [middle - low, high - middle];
            entries.push(off);
          }
        }
      }
    }
    return entries;
  }

  function normalizeScheduler(raw){
    if (!raw || typeof raw !== 'object') fail('A scheduler must be a JSON object');
    const id = /^[0-9a-f]{32}$/.test(String(raw.id || '').toLowerCase()) ? String(raw.id).toLowerCase() : newId();
    const name = String(raw.name || '').trim().slice(0, 100);
    if (!name) fail('The scheduler needs a name');
    const type = raw.type || 'daily';
    if (!['daily','weekly','recurring'].includes(type)) fail("Unknown scheduler type '" + type + "'");
    const entities = [];
    for (let e of raw.entities || []){
      e = String(e).trim().toLowerCase();
      const m = e.match(/^([a-z_]+)\.[a-z0-9_]+$/);
      if (m && VALID_DOMAINS.includes(m[1]) && !entities.includes(e)) entities.push(e);
    }
    if (!entities.length) fail('Add at least one entity');

    let rule = null, source = raw.entries || [];
    if (type === 'recurring'){
      const r = raw.rule || {};
      const start = parseTime(r.from || ''), end = parseTime(r.to || '');
      if (!start || start[0] !== 'clock' || !end || end[0] !== 'clock') fail("Recurring: 'From' and 'To' must be times like 06:00");
      if (end[1] < start[1]) fail("Recurring: 'To' must be later than 'From'");
      const every = Math.max(1, Math.min(720, parseInt(r.every, 10) || 60));
      const duration = Math.max(1, Math.min(Math.max(1, every - 1), parseInt(r.duration, 10) || 1));
      const action = ['on','off','pulse','pulse_random'].includes(r.action) ? r.action : 'pulse';
      const weekdays = cleanDays(r.weekdays);
      if (!weekdays) fail('Recurring: choose at least one day');
      rule = { from:formatTime(...start), to:formatTime(...end), every, action, duration, weekdays,
               extra:action !== 'off' && r.extra && typeof r.extra === 'object' ? r.extra : {},
               if_condition:r.if_condition !== false, force:r.force === true };
      let longest = duration;
      if (action === 'pulse_random'){
        const high = Math.max(1, Math.min(Math.max(1, every - 1), parseInt(r.duration_max, 10) || every - 1));
        rule.duration_max = high;
        rule.duration_min = Math.max(1, Math.min(high, parseInt(r.duration_min, 10) || 1));
        longest = high;
      }
      if (action === 'pulse' || action === 'pulse_random'){
        const lastOn = start[1] + Math.floor((end[1] - start[1]) / every) * every;
        if (lastOn + longest > 1439) fail("Recurring: the last 'on' at " + formatTime('clock', lastOn) + ' could turn off after midnight. Keep the time on within ' + (1439 - lastOn) + ' minutes or end earlier');
      }
      source = generateRecurring(rule);
    }

    const entries = [];
    for (const item of source){
      if (!item || typeof item !== 'object') continue;
      if (!['on','off'].includes(item.action)) fail("Every event must be 'on' or 'off'");
      const time = parseTime(item.time || '');
      if (!time) fail("Invalid time '" + item.time + "': use hh:mm, sunrise±minutes or sunset±minutes");
      const weekdays = cleanDays(item.weekdays);
      if (!weekdays) fail('Every event needs at least one weekday');
      const extra = {}, src = item.extra && typeof item.extra === 'object' ? item.extra : {};
      if (item.action === 'on'){
        for (const [key, low, high, decimals] of [['brightness',1,100,0],['brightness_abs',1,255,0],['kelvin',1000,10000,0],
                                                  ['position',0,100,0],['fan',0,100,0],['temperature',5,40,1],
                                                  ['temperature_low',5,40,1],['temperature_high',5,40,1],['humidity',0,100,0]]){
          const v = src[key];
          if (v === undefined || v === null || v === '') continue;
          const n = Number(v);
          if (Number.isNaN(n)) fail("Invalid value '" + v + "' for " + key);
          const c = Math.max(low, Math.min(high, n));
          extra[key] = decimals ? Math.round(c*10)/10 : Math.round(c);
        }
        if ('brightness' in extra) delete extra.brightness_abs;
        const color = String(src.color || '').trim().replace(/^#/, '');
        if (color){
          if (!/^[0-9a-fA-F]{6}$/.test(color)) fail("Invalid color '" + color + "'");
          extra.color = '#' + color.toUpperCase();
          delete extra.kelvin;
        }
        if ('temperature_low' in extra || 'temperature_high' in extra){
          if (!('temperature_low' in extra) || !('temperature_high' in extra)) fail('A temperature range needs both the low and the high value');
          if (extra.temperature_low >= extra.temperature_high) fail('In a temperature range the low value must be lower than the high one');
          delete extra.temperature;
        }
        if (('temperature' in extra || 'temperature_low' in extra) && src.temperature_only) extra.temperature_only = true;
        const mode = String(src.hvac_mode || '').trim().toLowerCase();
        if (mode){
          if (!HVAC_MODES.includes(mode)) fail("Invalid climate mode '" + mode + "': use " + HVAC_MODES.join(', '));
          extra.hvac_mode = mode;
          delete extra.temperature_only;
        }
        let params = src.params;
        if (typeof params === 'string' && params.trim()){
          try { params = JSON.parse(params); } catch (err) { fail('Script parameters are not valid JSON'); }
        }
        if (params){
          if (typeof params !== 'object' || Array.isArray(params)) fail('Script parameters must be a JSON object');
          extra.params = params;
        }
      }
      const entry = { action:item.action, time:formatTime(...time), weekdays, extra,
                      if_condition:item.if_condition !== false, force:item.force === true };
      // random time (not in recurring schedulers), written only when used, as the server does
      const spread = type !== 'recurring' ? Math.round(Number(item.random) || 0) : 0;
      if (spread > 0) entry.random = Math.min(120, spread);
      if (type === 'recurring' && Array.isArray(item.random_range) && item.random_range.some(v => v > 0)) entry.random_range = item.random_range.slice(0, 2);
      if (type === 'weekly' && weekdays.length > 1){
        for (const day of weekdays) entries.push({ ...JSON.parse(JSON.stringify(entry)), weekdays:day });
      } else entries.push(entry);
    }
    if (!entries.length) fail('Add at least one event');

    const base = { clock:0, sunrise:360, sunset:1080 };
    const key = e => { const [k, v] = parseTime(e.time); return base[k] + v; };
    if (type !== 'recurring') entries.sort((a, b) => a.weekdays < b.weekdays ? -1 : a.weekdays > b.weekdays ? 1 : key(a) - key(b));
    const enabled = raw.enabled === undefined ? true : typeof raw.enabled === 'boolean' ? raw.enabled : isTrue(raw.enabled);
    const scheduler = { version:APP_VERSION, id, name, type, enabled, entities,
                        condition:String(raw.condition || '').trim(), retry:raw.retry !== false };
    if (rule){
      const firstOn = entries.find(e => e.action === 'on');
      rule.extra = firstOn ? JSON.parse(JSON.stringify(firstOn.extra)) : {};
      scheduler.rule = rule;
    }
    scheduler.entries = entries;
    return scheduler;
  }

  function normalizeLayout(layout){
    const srcGroups = layout && typeof layout.groups === 'object' && layout.groups ? layout.groups : {};
    const srcOrder = layout && Array.isArray(layout.order) ? layout.order : [];
    const placed = new Set(), groups = {};
    for (const [gid, g] of Object.entries(srcGroups)){
      if (!/^g[0-9a-z]{1,40}$/.test(gid) || !g || typeof g !== 'object') continue;
      const children = [];
      for (const sid of g.children || []) if (schedulers.has(sid) && !placed.has(sid)){ children.push(sid); placed.add(sid); }
      groups[gid] = { name:String(g.name || '').trim().slice(0, 60) || 'Group', collapsed:!!g.collapsed, children };
    }
    const order = [];
    for (const item of srcOrder){
      if (groups[item] && !order.includes(item)) order.push(item);
      else if (schedulers.has(item) && !placed.has(item)){ order.push(item); placed.add(item); }
    }
    for (const gid of Object.keys(groups)) if (!order.includes(gid)) order.push(gid);
    const missing = [...schedulers.keys()].filter(sid => !placed.has(sid))
      .sort((a, b) => schedulers.get(a).name.toLowerCase().localeCompare(schedulers.get(b).name.toLowerCase()));
    return { version:APP_VERSION, order:[...missing, ...order], groups };
  }

  function cleanOptions(src, base){
    const o = { ...base };
    if ('max_retry' in src){ const n = parseInt(src.max_retry, 10); if (!Number.isNaN(n)) o.max_retry = Math.max(0, Math.min(5, n)); }
    for (const k of ['details_uncovered','mqtt_enabled','debug']) if (k in src) o[k] = typeof src[k] === 'string' ? isTrue(src[k]) : !!src[k];
    if ('notifier' in src) o.notifier = String(src.notifier || '').toLowerCase().replace(/[^a-z0-9_]/g, '');
    if ('excluded_entities' in src) o.excluded_entities = String(src.excluded_entities || '').toLowerCase().split('\n')
      .filter(l => l.trim()).map(l => l.replace(/[^a-z0-9_*.]/g, '')).join('\n');
    if (THEMES.includes(src.theme)) o.theme = src.theme;
    return o;
  }

  function state(){
    S.schedulers = [...schedulers.values()];
    return JSON.parse(JSON.stringify(S));
  }
  const bump = () => { S.version += 1; };

  /* ---------- the API ---------- */
  function handle(method, path, body){
    let m;
    if (method === 'GET' && path === 'api/state') return state();
    if (method === 'GET' && path === 'api/version') return { version:S.version, home_assistant:true };
    if (method === 'GET' && path === 'api/entities'){
      const patterns = (S.options.excluded_entities || '').split('\n').filter(Boolean)
        .map(p => new RegExp('^' + p.replace(/[.+?^${}()|[\]\\]/g, '\\$&').replace(/\*/g, '.*') + '$'));
      return DATA.entities.filter(e => !patterns.some(r => r.test(e.id)));
    }
    if (method === 'GET' && path === 'api/notifiers') return DATA.notifiers;
    if (method === 'GET' && path === 'api/log') return { lines:logLines.slice(-2000) };
    if (method === 'POST' && path === 'api/log/clear'){ logLines = []; log('INFO', 'Log cleared from the interface'); return { ok:true }; }
    if (method === 'POST' && path === 'api/template') return { result:'True' };
    if (method === 'POST' && path === 'api/schedulers'){
      const payload = body || {};
      const isNew = !schedulers.has(payload.id);
      if (isNew) payload.id = newId(); else payload.type = schedulers.get(payload.id).type;
      const s = normalizeScheduler(payload);
      schedulers.set(s.id, s);
      S.layout = normalizeLayout(S.layout);
      bump();
      log('INFO', '[' + s.name + '] ' + (isNew ? 'created' : 'saved') + ' from the interface');
      return { id:s.id, state:state() };
    }
    if (method === 'DELETE' && (m = path.match(/^api\/schedulers\/([0-9a-f]{32})$/))){
      const s = schedulers.get(m[1]);
      if (s){ schedulers.delete(m[1]); S.layout = normalizeLayout(S.layout); bump(); log('INFO', '[' + s.name + '] deleted from the interface'); }
      return { state:state() };
    }
    if (method === 'POST' && (m = path.match(/^api\/schedulers\/([0-9a-f]{32})\/enabled$/))){
      const s = schedulers.get(m[1]), on = !!(body || {}).enabled;
      if (s && s.enabled !== on){ s.enabled = on; bump(); log('INFO', '[' + s.name + '] ' + (on ? 'enabled' : 'disabled') + ' from the interface'); }
      return { state:state() };
    }
    if (method === 'POST' && (m = path.match(/^api\/groups\/([^/]+)\/enabled$/))){
      const g = S.layout.groups[m[1]], on = !!(body || {}).enabled;
      if (g){ for (const sid of g.children) if (schedulers.has(sid)) schedulers.get(sid).enabled = on;
              bump(); log('INFO', "Group '" + g.name + "' " + (on ? 'enabled' : 'disabled') + ' from the interface'); }
      return { state:state() };
    }
    if (method === 'POST' && path === 'api/layout'){ S.layout = normalizeLayout(body || {}); bump(); return { state:state() }; }
    if (method === 'POST' && path === 'api/options'){
      const before = { ...S.options };
      S.options = cleanOptions(body || {}, S.options);
      for (const [k, v] of Object.entries(S.options))
        if (before[k] !== v && k !== 'excluded_entities') log('INFO', 'Option ' + k + ' changed to ' + (v !== '' ? v : '(none)'));
      if (S.options.mqtt_enabled !== before.mqtt_enabled) S.status.mqtt = S.options.mqtt_enabled ? 'Connected to demo broker' : 'Disabled';
      bump();
      return { state:state() };
    }
    throw { status:404, message:'Not available in the demo' };
  }

  window.fetch = async function(url, options){
    options = options || {};
    const path = String(url).replace(/^\.?\//, '').split('?')[0];
    const method = (options.method || 'GET').toUpperCase();
    let body = null;
    try { body = options.body ? JSON.parse(options.body) : null; } catch (err) { body = null; }
    let status = 200, data;
    try { data = handle(method, path, body); }
    catch (err) { status = err.status || 500; data = { error:err.message || String(err) }; }
    return new Response(JSON.stringify(data), { status, headers:{ 'Content-Type':'application/json' } });
  };
  // No server to push changes: the page only changes through its own calls
  window.EventSource = function(){ return { close(){}, addEventListener(){} }; };
})();
