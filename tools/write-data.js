#!/usr/bin/env node
/**
 * write-data.js — écrit un fichier de données versionné et régénère data/index.json
 *
 * Usage :
 *   node tools/write-data.js <onglet> <AAAA-MM> <fichier-source.json>
 *   node tools/write-data.js --reindex          (régénère seulement le manifeste)
 *
 * Exemple :
 *   node tools/write-data.js ai 2026-07 paste_AI_GSC_JUILLET.json
 *
 * Le contenu du fichier source est fusionné PAR-DESSUS ce qui vient du Sheet :
 * seules les clés présentes dans le fichier sont remplacées côté dashboard.
 * Onglets valides : vercel, gsc, ahrefs, keywords, ai, deep_analysis, ga4, ga4ch
 *
 * ga4 / ga4ch (ajoutés sept. 2026, remplacement de Coupler) : le fichier doit
 * être {"rows":[...]} avec les MÊMES noms de colonnes que l'export Coupler.io
 * ("Dimension: Landing page", "Session: Session default channel group", …)
 * — voir ga4-report/pull_august.py qui génère directement ce format.
 * PAS de reshaping ni de build.py pour ces deux-là.
 */

const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const DATA_DIR = path.join(ROOT, 'data');
const TABS = ['vercel', 'gsc', 'ahrefs', 'keywords', 'ai', 'deep_analysis', 'ga4', 'ga4ch'];

function reindex() {
  const manifest = {};
  for (const tab of TABS) {
    const dir = path.join(DATA_DIR, tab);
    if (!fs.existsSync(dir)) continue;
    const months = fs.readdirSync(dir)
      .filter(f => /^\d{4}-\d{2}\.json$/.test(f))
      .map(f => f.replace(/\.json$/, ''))
      .sort();
    if (months.length) manifest[tab] = months;
  }
  fs.mkdirSync(DATA_DIR, { recursive: true });
  fs.writeFileSync(path.join(DATA_DIR, 'index.json'), JSON.stringify(manifest, null, 2) + '\n');
  return manifest;
}

function main() {
  const args = process.argv.slice(2);

  if (args[0] === '--reindex') {
    console.log('Manifeste régénéré :', JSON.stringify(reindex()));
    return;
  }

  const [tab, month, srcPath] = args;

  if (!tab || !month || !srcPath) {
    console.error('Usage : node tools/write-data.js <onglet> <AAAA-MM> <source.json>');
    process.exit(1);
  }
  if (!TABS.includes(tab)) {
    console.error(`Onglet invalide « ${tab} ». Attendu : ${TABS.join(', ')}`);
    process.exit(1);
  }
  if (!/^\d{4}-\d{2}$/.test(month)) {
    console.error(`Mois invalide « ${month} ». Format attendu : AAAA-MM (ex. 2026-07).`);
    process.exit(1);
  }

  const resolved = path.isAbsolute(srcPath) ? srcPath : path.join(ROOT, srcPath);
  if (!fs.existsSync(resolved)) {
    console.error(`Fichier source introuvable : ${resolved}`);
    process.exit(1);
  }

  let payload;
  try {
    payload = JSON.parse(fs.readFileSync(resolved, 'utf8'));
  } catch (err) {
    console.error('JSON source invalide :', err.message);
    process.exit(1);
  }

  const outDir = path.join(DATA_DIR, tab);
  fs.mkdirSync(outDir, { recursive: true });
  const outFile = path.join(outDir, `${month}.json`);
  fs.writeFileSync(outFile, JSON.stringify(payload));

  const manifest = reindex();
  console.log(`✅ Écrit : data/${tab}/${month}.json (${Object.keys(payload).join(', ')})`);
  console.log('   Manifeste :', JSON.stringify(manifest));
}

main();
