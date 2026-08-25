/**
 * RUN THIS ONCE — fixes all month keys across every tab.
 * Handles: "Wed Apr 01 2026...", "2025-04", "2025-05", etc.
 * Converts everything to clean "2026-04" / "2026-05" strings.
 * Also deduplicates rows (keeps the one with JSON data if duplicate).
 */
function fixEverything() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const ALL_TABS = ['index', 'vercel', 'gsc', 'ahrefs', 'keywords', 'ai', 'analysis'];
  
  // Maps any messy key → clean key
  function cleanKey(raw) {
    const s = String(raw).trim();
    if (!s || s === 'month') return null;
    // Already correct
    if (/^\d{4}-\d{2}$/.test(s)) {
      // Fix wrong year
      if (s === '2025-04') return '2026-04';
      if (s === '2025-05') return '2026-05';
      return s;
    }
    // Date object serialized as string: "Wed Apr 01 2026 00:00:00..."
    const d = new Date(s);
    if (!isNaN(d.getTime())) {
      const y = d.getFullYear();
      const m = String(d.getMonth() + 1).padStart(2, '0');
      return y + '-' + m;
    }
    return null;
  }

  const LABELS = { '2026-04': 'Avril 2026', '2026-05': 'Mai 2026' };

  ALL_TABS.forEach(function(tabName) {
    const sh = ss.getSheetByName(tabName);
    if (!sh) return;
    const lastRow = sh.getLastRow();
    if (lastRow < 2) return;

    const isIndex = (tabName === 'index');
    const numCols = isIndex ? 2 : 3;
    const range = sh.getRange(2, 1, lastRow - 1, numCols);
    const data = range.getValues();

    // Dedupe: build map of key → best row (prefer row with most content in col 3)
    const seen = {};
    data.forEach(function(row) {
      const key = cleanKey(row[0]);
      if (!key) return;
      const label = LABELS[key] || String(row[1] || key);
      const content = isIndex ? null : String(row[2] || '');
      
      if (!seen[key]) {
        seen[key] = isIndex ? [key, label] : [key, label, content];
      } else if (!isIndex) {
        // Keep whichever row has more content in the JSON column
        const existing = String(seen[key][2] || '');
        if (content.length > existing.length) {
          seen[key] = [key, label, content];
        }
      }
    });

    // Write back sorted
    const rows = Object.keys(seen).sort().map(function(k) { return seen[k]; });

    // Clear old data rows
    range.clearContent();

    // Write clean rows
    if (rows.length > 0) {
      sh.getRange(2, 1, rows.length, numCols).setValues(rows);
    }
  });

  SpreadsheetApp.getUi().alert('✅ Tout est corrigé ! Clés normalisées, doublons supprimés.');
}