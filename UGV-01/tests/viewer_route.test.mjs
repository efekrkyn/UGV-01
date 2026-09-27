// N6 (M3 review): the viewer's arm route stays on the swept pose graph when a pose button interrupts a move and
// after free sliders. Runs the route block of tools/viewer_template.html (between ROUTE-BEGIN and ROUTE-END).
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const root = new URL('../', import.meta.url);
const html = readFileSync(new URL('tools/viewer_template.html', root), 'utf8');
const block = html.split('ROUTE-BEGIN')[1]?.split('// ROUTE-END')[0];
assert.ok(block, 'route block markers missing in tools/viewer_template.html');
const { plan } = new Function(`${block.slice(block.indexOf('\n'))}; return { plan };`)();
const arm = JSON.parse(readFileSync(new URL('config/vehicle.json', root), 'utf8')).geometry.arm;
const edges = arm.pose_edges, P = arm.poses_deg;
const isEdge = (a, b) => edges.some(([u, v]) => (u === a && v === b) || (u === b && v === a));
const lerp = (a, b, k) => P[a].map((v, i) => v + (P[b][i] - v) * k);

function onGraph(start, legs) {  // every leg after the first is a graph edge from the previous node
  for (let i = 1; i < legs.length; i++) assert.ok(isEdge(legs[i - 1], legs[i]), `${legs[i - 1]} -> ${legs[i]}`);
  assert.ok(legs.length === 0 || start.includes(legs[0]), `first leg ${legs[0]} not an end of the current edge`);
}

test('a button pressed mid-edge finishes that edge or goes back along it, never across', () => {
  // The review's case: ready -> reach_low half done, then reach_center: it went straight to an off-graph joint mix.
  for (const k of [0.1, 0.5, 0.9]) {
    const p = plan(edges, 'ready', { to: 'reach_low', k }, 'reach_center');
    assert.equal(p.snap, null);
    onGraph(['ready', 'reach_low'], p.legs);
    assert.equal(p.legs.at(-1), 'reach_center');
    // The first leg runs from the interrupted point to an edge end: the same joint-space line as the edge.
    const q = lerp('ready', 'reach_low', k), end = P[p.legs[0]], other = p.legs[0] === 'ready' ? P.reach_low : P.ready;
    const t = end.map((v, i) => (v - q[i]) / (v - other[i] || 1)).filter((_, i) => end[i] !== other[i]);
    assert.ok(t.every(x => Math.abs(x - t[0]) < 1e-9), `leg leaves the edge line (${t})`);
  }
  assert.deepEqual(plan(edges, 'ready', { to: 'reach_low', k: 0.9 }, 'reach_low').legs, ['reach_low']);
  assert.deepEqual(plan(edges, 'ready', { to: 'reach_low', k: 0.2 }, 'ready').legs, ['ready']);
});

test('after free sliders the route snaps to park, then follows the graph', () => {
  const p = plan(edges, null, null, 'reach_low');
  assert.equal(p.snap, 'stow');
  onGraph(['stow', ...edges.filter(e => e.includes('stow')).flat()], p.legs);
  assert.equal(p.legs.at(-1), 'reach_low');
});

test('from a node the route is the shortest graph path', () => {
  const p = plan(edges, 'stow', null, 'reach_low');
  assert.deepEqual(p.legs, ['lift', 'up', 'ready', 'reach_low']);
  assert.deepEqual(plan(edges, 'ready', null, 'ready').legs, []);
});
