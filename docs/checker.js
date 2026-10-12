/* Browser port of contractcheck/checker.py (the Python code is the reference).
 * Rules, normaliser tables and the sentence splitter come from rules.js, which is generated from Python.
 * `node tests/test_checker.js` replays tests/vectors.json and requires identical reports.
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory(require("./rules.js"));
  else root.ContractCheck = factory(root.CONTRACT_RULES);
})(typeof self !== "undefined" ? self : this, function (R) {
  "use strict";

  var SEVERITY_ORDER = { low: 1, medium: 2, high: 3 };
  var TASHKEEL = new RegExp(R.tashkeel, "g");
  var INVISIBLE = new RegExp(R.invisible, "g");
  var WS = new RegExp(R.whitespace, "g");
  var SPLIT = new RegExp(R.split);

  function normalize(text) {
    text = String(text).replace(TASHKEEL, "").replace(INVISIBLE, "");
    var out = "";
    for (var ch of text) out += Object.prototype.hasOwnProperty.call(R.translate, ch) ? R.translate[ch] : ch;
    return out.toLowerCase().replace(WS, " ").trim();
  }

  var clauseRe = {}, riskRe = {};
  R.clauses.forEach(function (c) { clauseRe[c.id] = c.patterns.map(function (p) { return new RegExp(normalize(p)); }); });
  R.risks.forEach(function (r) { riskRe[r.id] = new RegExp(normalize(r.pattern)); });

  function sentences(text) {
    var out = [];
    text.split(SPLIT).forEach(function (raw) {
      raw = (raw || "").trim();
      if (raw) out.push([raw, normalize(raw)]);
    });
    return out;
  }

  function analyze(text, kind, maxExcerpts) {
    kind = kind || "sale";
    if (maxExcerpts === undefined) maxExcerpts = 3;
    if (kind !== "sale" && kind !== "lease") throw new Error("kind must be 'sale' or 'lease'");
    text = String(text).replace(/\ufeff/g, "");
    var normAll = normalize(text);
    var sents = sentences(text);
    var paras = [];
    text.split("\n").forEach(function (raw) { if (raw.trim()) paras.push([raw.trim(), normalize(raw)]); });
    var report = { contract_kind: kind, clauses_checked: 0, clauses_found: [], findings: [] };

    R.clauses.forEach(function (c) {
      if (c.kinds.indexOf(kind) < 0) return;
      report.clauses_checked++;
      if (clauseRe[c.id].some(function (rx) { return rx.test(normAll); })) report.clauses_found.push(c.id);
      else report.findings.push({ kind: "missing", id: c.id, severity: c.severity, title_en: c.en, title_ar: c.ar,
        tip_en: c.tip_en, tip_ar: c.tip_ar, count: 0, excerpts: [] });
    });

    R.risks.forEach(function (r) {
      if (r.kinds.indexOf(kind) < 0) return;
      var units = r.scope === "paragraph" ? paras : sents;
      var hits = units.filter(function (u) { return riskRe[r.id].test(u[1]); }).map(function (u) { return u[0]; });
      if (hits.length) report.findings.push({ kind: "risk", id: r.id, severity: r.severity, title_en: r.en, title_ar: r.ar,
        tip_en: r.tip_en, tip_ar: r.tip_ar, count: hits.length,
        excerpts: hits.slice(0, maxExcerpts).map(function (h) { return h.slice(0, 240); }) });
    });

    report.findings.sort(function (a, b) {
      var d = SEVERITY_ORDER[b.severity] - SEVERITY_ORDER[a.severity];
      if (d) return d;
      var ka = a.kind !== "risk", kb = b.kind !== "risk";
      if (ka !== kb) return ka ? 1 : -1;
      return a.id < b.id ? -1 : a.id > b.id ? 1 : 0;
    });
    report.disclaimer = R.disclaimer.en;
    return report;
  }

  /* Same key order as contractcheck.checker.to_dict */
  function toDict(r) {
    return { contract_kind: r.contract_kind, clauses_checked: r.clauses_checked, clauses_found: r.clauses_found,
      findings: r.findings, disclaimer: R.disclaimer.en };
  }

  function clauseTitles(kind, lang) {
    var out = {};
    R.clauses.forEach(function (c) { if (c.kinds.indexOf(kind) >= 0) out[c.id] = lang === "ar" ? c.ar : c.en; });
    return out;
  }

  return { analyze: analyze, normalize: normalize, toDict: toDict, clauseTitles: clauseTitles,
    disclaimer: R.disclaimer, severityOrder: SEVERITY_ORDER };
});
