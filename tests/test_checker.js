// Parity check: the browser checker must produce the same reports as the Python reference.
const assert = require("assert");
const fs = require("fs");
const path = require("path");
const C = require("../docs/checker.js");

const v = JSON.parse(fs.readFileSync(path.join(__dirname, "vectors.json"), "utf8"));
for (const [src, want] of v.normalize) assert.strictEqual(C.normalize(src), want, "normalize " + JSON.stringify(src));
for (const c of v.reports) {
  const got = JSON.parse(JSON.stringify(C.toDict(C.analyze(c.text, c.kind))));
  assert.deepStrictEqual(got, c.expected, c.name);
}
assert.throws(() => C.analyze("x", "mortgage"), /kind must be/);
console.log(`ok - ${v.normalize.length} normalisation + ${v.reports.length} report vectors`);
