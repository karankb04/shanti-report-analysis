/*************************************************************
 * SHANTI TRAVEL — RAPPORT SEO : moteur de données
 * Sheet hub : un onglet par source, une ligne par mois.
 *************************************************************/

const DATA_TABS = ['vercel', 'gsc', 'ahrefs', 'keywords', 'ai', 'analysis', 'deep_analysis'];

function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('📊 Rapport SEO')
    .addItem('Ouvrir le panneau', 'showSidebar')
    .addSeparator()
    .addItem('Initialiser les onglets', 'setupTabs')
    .addItem('🧹 Nettoyer les doublons index', 'deduplicateIndex')
    .addItem('🔧 Corriger toutes les clés de mois', 'fixAllMonthKeys')
    .addToUi();
}

function showSidebar() {
  const html = HtmlService.createHtmlOutputFromFile('Sidebar')
    .setTitle('Rapport SEO — Mise à jour')
    .setWidth(360);
  SpreadsheetApp.getUi().showSidebar(html);
}

function setupTabs() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let idx = ss.getSheetByName('index');
  if (!idx) idx = ss.insertSheet('index');
  if (idx.getLastRow() === 0)
    idx.getRange(1,1,1,2).setValues([['month','label']]).setFontWeight('bold');

  DATA_TABS.forEach(function(name) {
    let sh = ss.getSheetByName(name);
    if (!sh) sh = ss.insertSheet(name);
    if (sh.getLastRow() === 0) {
      sh.getRange(1,1,1,3).setValues([['month','label','json']]).setFontWeight('bold');
      sh.setColumnWidth(3, 600);
    }
  });

  let sh = ss.getSheetByName('shared');
  if (!sh) sh = ss.insertSheet('shared');
  if (sh.getLastRow() === 0) {
    sh.getRange(1,1).setValue('json').setFontWeight('bold');
    sh.setColumnWidth(1, 600);
  }

  deduplicateIndex();
  SpreadsheetApp.getUi().alert('✅ Onglets prêts et index nettoyé !');
}

/* ---- Deduplicate the index tab (keep last occurrence of each month key) ---- */
function deduplicateIndex() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const idx = ss.getSheetByName('index');
  if (!idx || idx.getLastRow() < 2) return;

  const data = idx.getDataRange().getValues();
  const header = data[0];
  const rows = data.slice(1);

  // Keep only unique month keys (last one wins)
  const seen = {};
  rows.forEach(function(r) {
    const key = String(r[0]).trim();
    if (key && key !== 'month') seen[key] = r[1]; // label
  });

  // Rebuild sorted
  const unique = Object.keys(seen).sort().map(function(k) { return [k, seen[k]]; });

  // Clear and rewrite
  idx.clearContents();
  idx.getRange(1,1,1,2).setValues([header]).setFontWeight('bold');
  if (unique.length > 0) {
    idx.getRange(2,1,unique.length,2).setValues(unique);
  }
}

/* ---- Upsert: write/overwrite a single month row in a data tab ---- */
function upsertRow(tabName, monthKey, label, jsonStr) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sh = ss.getSheetByName(tabName);
  if (!sh) {
    sh = ss.insertSheet(tabName);
    sh.getRange(1,1,1,3).setValues([['month','label','json']]).setFontWeight('bold');
    sh.setColumnWidth(3, 600);
  }
  const data = sh.getDataRange().getValues();
  let rowIdx = -1;
  for (let i = 1; i < data.length; i++) {
    if (String(data[i][0]).trim() === monthKey) { rowIdx = i + 1; break; }
  }
  if (rowIdx === -1) rowIdx = sh.getLastRow() + 1;
  sh.getRange(rowIdx,1,1,3).setValues([[monthKey, label, jsonStr]]);
  syncIndex(monthKey, label);
}

/* ---- Sync index: add month if missing, never duplicate ---- */
function syncIndex(monthKey, label) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const idx = ss.getSheetByName('index');
  if (!idx) return;
  const last = idx.getLastRow();
  if (last > 1) {
    const data = idx.getRange(2, 1, last - 1, 2).getValues();
    for (let i = 0; i < data.length; i++) {
      if (String(data[i][0]).trim() === monthKey) {
        if (label && data[i][1] !== label) idx.getRange(i + 2, 2).setValue(label);
        return; // already exists, stop
      }
    }
  }
  // Not found — append and re-sort
  idx.getRange(last + 1, 1, 1, 2).setValues([[monthKey, label || monthKey]]);
  const newLast = idx.getLastRow();
  if (newLast > 2) idx.getRange(2, 1, newLast - 1, 2).sort({column: 1, ascending: true});
}

/* ---- Functions called from the sidebar ---- */
function validateAndSave(tab, monthKey, label, jsonStr, skipParse) {
  if (!/^\d{4}-\d{2}$/.test(monthKey))
    return { ok:false, msg:'Format du mois attendu : AAAA-MM (ex. 2026-05).' };
  if (!skipParse) {
    try { JSON.parse(jsonStr); }
    catch(e) { return { ok:false, msg:'JSON invalide : ' + e.message }; }
  }
  upsertRow(tab, monthKey, label, jsonStr);
  return { ok:true, msg:'✅ ' + tab + ' enregistré pour ' + monthKey + '.' };
}

function saveVercel(monthKey, label, jsonStr)   { return validateAndSave('vercel',   monthKey, label, jsonStr); }
function saveGSC(monthKey, label, jsonStr)      { return validateAndSave('gsc',      monthKey, label, jsonStr); }
function saveAhrefs(monthKey, label, jsonStr)   { return validateAndSave('ahrefs',   monthKey, label, jsonStr); }
function saveKeywords(monthKey, label, jsonStr) { return validateAndSave('keywords', monthKey, label, jsonStr); }
function saveAI(monthKey, label, jsonStr)       { return validateAndSave('ai',       monthKey, label, jsonStr); }
function saveDeepAnalysis(monthKey, label, jsonStr) {
  return validateAndSave('deep_analysis', monthKey, label, jsonStr);
}

function updateDeepAnalysisStatus(monthKey, section, query, newStatus) {
  // Lightweight status update — finds the row for this month and patches the matching entry
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sh = ss.getSheetByName('deep_analysis');
  if (!sh || sh.getLastRow() < 2) return { ok:false, msg:'Onglet deep_analysis introuvable.' };

  const data = sh.getDataRange().getValues();
  for (let i = 1; i < data.length; i++) {
    if (String(data[i][0]).trim() === monthKey) {
      try {
        const obj = JSON.parse(data[i][2]);
        const arr = obj[section];
        if (!arr) return { ok:false, msg:'Section ' + section + ' introuvable.' };
        const item = arr.find(function(x){ return x.query === query || x.keyword === query; });
        if (!item) return { ok:false, msg:'Requête «' + query + '» introuvable dans ' + section + '.' };
        item.status = newStatus;
        sh.getRange(i+1, 3).setValue(JSON.stringify(obj));
        return { ok:true, msg:'✅ Statut mis à jour : «' + query + '» → ' + newStatus };
      } catch(e) { return { ok:false, msg:'Erreur JSON : ' + e.message }; }
    }
  }
  return { ok:false, msg:'Mois ' + monthKey + ' non trouvé.' };
}

function saveAnalysis(monthKey, label, text) {
  return validateAndSave('analysis', monthKey, label, JSON.stringify({text:text||''}), true);
}
function saveShared(jsonStr) {
  try { JSON.parse(jsonStr); }
  catch(e) { return { ok:false, msg:'JSON invalide : ' + e.message }; }
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  let sh = ss.getSheetByName('shared');
  if (!sh) { sh = ss.insertSheet('shared'); sh.getRange(1,1).setValue('json').setFontWeight('bold'); sh.setColumnWidth(1,600); }
  const last = sh.getLastRow();
  if (last < 2) sh.getRange(2,1).setValue(jsonStr);
  else sh.getRange(2,1).setValue(jsonStr); // always overwrite row 2
  return { ok:true, msg:'✅ Données partagées enregistrées.' };
}

function getExistingMonths() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const idx = ss.getSheetByName('index');
  if (!idx || idx.getLastRow() < 2) return [];
  return idx.getRange(2,1,idx.getLastRow()-1,2).getValues()
    .filter(function(r){ return r[0] && String(r[0]) !== 'month'; })
    .map(function(r){ return {key:String(r[0]).trim(), label:String(r[1])}; });
}

/*************************************************************
 * NETTOYAGE COMPLET — corrige les clés de mois incohérentes
 * Remplace 2025-04 → 2026-04 et 2025-05 → 2026-05 partout,
 * puis déduplique tous les onglets (garde la dernière ligne).
 * À lancer une seule fois depuis le menu.
 *************************************************************/
function fixAllMonthKeys() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const remap = { '2025-04':'2026-04', '2025-05':'2026-05' };
  const labelFix = { '2026-04':'Avril 2026', '2026-05':'Mai 2026' };

  const allTabs = DATA_TABS.concat(['index']);

  allTabs.forEach(function(tabName) {
    const sh = ss.getSheetByName(tabName);
    if (!sh || sh.getLastRow() < 2) return;

    const isIndex = (tabName === 'index');
    const numCols = isIndex ? 2 : 3;
    const data = sh.getRange(2, 1, sh.getLastRow() - 1, numCols).getValues();

    // Remap keys + dedupe (last wins)
    const seen = {};
    data.forEach(function(r) {
      let key = String(r[0]).trim();
      if (!key || key === 'month') return;
      if (remap[key]) key = remap[key];
      const label = labelFix[key] || r[1] || key;
      if (isIndex) seen[key] = [key, label];
      else seen[key] = [key, label, r[2]];
    });

    const rows = Object.keys(seen).sort().map(function(k){ return seen[k]; });

    // Clear data rows, keep header
    if (sh.getLastRow() > 1) {
      sh.getRange(2, 1, sh.getLastRow() - 1, sh.getMaxColumns()).clearContent();
    }
    if (rows.length) {
      sh.getRange(2, 1, rows.length, numCols).setValues(rows);
    }
  });

  SpreadsheetApp.getUi().alert('✅ Toutes les clés de mois corrigées (2026-04 / 2026-05) et doublons supprimés.');
}