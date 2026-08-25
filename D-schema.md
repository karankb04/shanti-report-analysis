# Structure JSON — `__DATA_PLACEHOLDER__`
## Rapport SEO Shanti Travel · Référence Apps Script

Le template HTML contient exactement **une** occurrence de `__DATA_PLACEHOLDER__` (dans la ligne `var D = __DATA_PLACEHOLDER__;`).  
Apps Script doit remplacer ce token par le JSON sérialisé de l'objet `D` décrit ci-dessous.

```javascript
// Dans Apps Script (HtmlService)
var html = HtmlService.createTemplateFromFile('rapport-seo-template');
// OU avec string replace sur le fichier lu depuis Drive :
var content = DriveApp.getFileById(TEMPLATE_FILE_ID).getBlob().getDataAsString();
content = content.replace('__DATA_PLACEHOLDER__', JSON.stringify(buildD()));
```

---

## Schéma complet de `D`

```json
{
  "shared": { ... },
  "months": {
    "YYYY-MM": { ... },
    "YYYY-MM": { ... }
  }
}
```

---

## `D.shared` — données statiques (communes à tous les mois)

```json
{
  "shared": {
    "generated": "12 juin 2026",          // string — date de génération du rapport
    "ahrefsTrend": [                       // array — 3 derniers mois pour le sparkline
      { "m": "Mars",  "v": 19540 },       // m = label court, v = trafic organique Ahrefs
      { "m": "Avril", "v": 17537 },
      { "m": "Mai",   "v": 16491 }
    ],
    "competitors": [                       // array — liste fixe de concurrents
      {
        "d": "shantitravel.com",           // domain
        "self": true,                      // boolean — marquer votre propre domaine
        "dr": 52,                          // Domain Rating Ahrefs
        "traffic": 10070,                  // trafic organique FR estimé (Ahrefs batch-analysis)
        "kw": 1916,                        // mots-clés FR top 100
        "rd": 1130                         // referring domains
      },
      {
        "d": "japaventura.fr",
        "self": false,
        "dr": 26,
        "traffic": 6735,
        "kw": 1236,
        "rd": 507
      }
      // ... autres concurrents (même structure)
    ],
    "refdomains": [                        // array — top 25 domaines référents (Ahrefs live)
      {
        "d": "wikipedia.org",             // domain
        "dr": 97,                          // Domain Rating
        "df": 0,                           // liens dofollow vers shantitravel.com
        "l": 3                             // liens totaux (dofollow + nofollow)
      }
      // ... (même structure)
    ]
  }
}
```

### Sources Apps Script pour `D.shared`

| Champ | Source | Outil Ahrefs API |
|-------|--------|-----------------|
| `generated` | `Utilities.formatDate(new Date(), ...)` | — |
| `ahrefsTrend` | Boucle sur 3 mois | `site-explorer-metrics-history` (monthly, select: `date,org_traffic`) |
| `competitors` | Liste fixe dans le script | `batch-analysis` (select: `url,domain_rating,org_traffic,org_keywords,refdomains`, country: `fr`) |
| `refdomains` | Live | `site-explorer-referring-domains` (select: `domain,domain_rating,dofollow_links,links_to_target`, order: `domain_rating:desc`, limit: 25) |

---

## `D.months[key]` — données mensuelles

La clé est une string libre (ex: `"mai-2026"`, `"mai"`) — elle doit correspondre au sélecteur de mois affiché.

```json
{
  "months": {
    "mai-2026": {
      "label": "Mai 2026",               // string — affiché dans le sélecteur de mois
      "prevLabel": "avril",              // string — affiché dans les flèches MoM ("vs avril")

      "stamps": {                        // fraîcheur par source (affichée dans Vue d'ensemble)
        "vercel": "export du 01/06/2026",
        "gsc":    "01–31 mai (live MCP)",
        "ahrefs": "snapshot 31/05/2026",
        "ga4":    null                   // null = "non connecté"
      },

      "vercel": { ... },                 // voir section Vercel ci-dessous
      "gsc":    { ... },                 // voir section GSC ci-dessous
      "ahrefs": { ... },                 // voir section Ahrefs ci-dessous
      "kw":     null | { ... }           // null = page "Données non disponibles"
    }
  }
}
```

---

## `vercel` — source : Google Sheet (export manuel)

```json
{
  "kpi": {
    "visitors":   45962,     // int — visiteurs uniques (onglet vercel_overview)
    "pageviews":  86946,     // int — pages vues
    "bounce":     70,        // int — taux de rebond %
    "pps":        1.89,      // float — pages / session
    "mobile":     61,        // int — part mobile %
    "topCountry": "France"   // string
  },
  "prev": null | {           // null si pas d'export mois précédent dans le Sheet
    "visitors":  46939,
    "pageviews": 85898,
    "bounce":    72,
    "pps":       1.83,
    "mobile":    58
  },
  "devices": [               // onglet vercel_devices
    { "l": "Mobile",   "v": 61 },   // l = label, v = % (int)
    { "l": "Desktop",  "v": 37 },
    { "l": "Tablette", "v": 2  }
  ],
  "referrers": [             // onglet vercel_referrers — array de [label, visiteurs]
    ["google.com", 27000],
    ["bing.com", 911]
    // ...
  ],
  "pages": [                 // onglet vercel_top_pages — array de [path, visitors, pageviews]
    ["/fr", 3500, 4800],
    ["/fr/voyage-japon", 2700, 3800]
    // ...
  ],
  "countries": [             // onglet vercel_countries — array de [name, visitors, pct]
    ["France", 29000, 62],
    ["Belgique", 2300, 5]
    // ...
  ]
}
```

### Lecture Sheet (onglets)

| Champ | Onglet Sheet | Colonnes à lire |
|-------|-------------|-----------------|
| `kpi` | `vercel_overview` | Ligne correspondant au mois |
| `devices` | `vercel_devices` | Device, % |
| `referrers` | `vercel_referrers` | Referrer, Visitors |
| `pages` | `vercel_top_pages` | Path, Visitors, Pageviews |
| `countries` | `vercel_countries` | Country, Visitors, % |

---

## `gsc` — source : GSC API

```json
{
  "kpi": {
    "clicks":      17796,    // int
    "impressions": 2076270,  // int
    "ctr":         0.86,     // float — en % (ex: 0.86 = 0,86 %)
    "position":    10.2      // float
  },
  "prev": null | {           // mois précédent pour les flèches MoM
    "clicks":      16760,
    "impressions": 2419703,
    "ctr":         0.69,
    "position":    8.7
  },
  "branded": {
    "brand":    { "clicks": 1423, "impr": 5295, "share": 8  },   // share = % (int)
    "nonbrand": { "clicks": 16373,"impr": 1774305,"share": 92 },
    "prev": null | { "brand": 1513, "nonbrand": 15247 }           // clics mois précédent
  },
  "devices": [               // GSC dimension=device
    { "l": "Mobile",  "clicks": 11390, "impr": 1196587, "ctr": 0.95, "pos": 8.8  },
    { "l": "Desktop", "clicks": 5987,  "impr": 849512,  "ctr": 0.70, "pos": 13.6 },
    { "l": "Tablette","clicks": 419,   "impr": 30171,   "ctr": 1.39, "pos": 7.3  }
  ],
  "locales": [               // GSC filtré par /en/ et /de/ — FR = reste
    { "l": "FR", "clicks": 15868, "impr": 1353714, "ctr": 1.17, "pos": null },
    { "l": "EN", "clicks": 1425,  "impr": 597015,  "ctr": 0.24, "pos": 11.0 },
    { "l": "DE", "clicks": 503,   "impr": 125541,  "ctr": 0.40, "pos": 14.1 }
  ],
  "queries": [               // GSC top 50 requêtes — array de [query, clicks, impr, ctr%, pos, "M"|"H"]
    ["shanti travel", 1053, 1672, 62.98, 1.9, "M"],
    ["sri lanka",       72, 28396, 0.25, 11.4, "H"]
    // "M" = marque (contient "shanti"), "H" = hors-marque
  ],
  "pages": [                 // GSC top 50 pages — array de [path, locale, clicks, impr, ctr%, pos]
    ["/fr", "FR", 847, 7503, 11.29, 16.8],
    ["/en", "EN", 465, 5244, 8.87,  6.0 ]
  ],
  "countries": [             // GSC dimension=country, top 20
    ["France",    9608, 707839, 1.36, 11.7],   // [pays, clics, impr, ctr%, pos]
    ["Inde",      1282, 355926, 0.36, 9.3 ]
  ],
  "opportunities": [         // calculé par Apps Script : impr > 5000 ET ctr < 2%
                             // array de [path, locale, clicks, impr, ctr%, pos, gainEstimé]
    ["/en/blog/10-facts...", "EN", 328, 174391, 0.19, 10.0, 3156]
    // gainEstimé = Math.round(impr * 0.02) - clicks
  ]
}
```

### Appels GSC API

```javascript
// Totaux du mois
searchconsole.searchanalytics.query({
  siteUrl: 'https://www.shantitravel.com/',
  requestBody: { startDate, endDate, dimensions: [] }
})

// Par device
{ dimensions: ['device'] }

// Locale EN (filtrer pages /en/)
{ dimensions: ['device'], dimensionFilterGroups: [{ filters: [{ dimension: 'page', operator: 'contains', expression: '/en/' }] }] }

// Top requêtes
{ dimensions: ['query'], rowLimit: 50, orderBy: 'clicks desc' }

// Top pages
{ dimensions: ['page'], rowLimit: 50, orderBy: 'clicks desc' }

// Top pays
{ dimensions: ['country'], rowLimit: 20, orderBy: 'clicks desc' }
```

---

## `ahrefs` — source : Ahrefs API

```json
{
  "kpi": {
    "traffic":     16491,   // int — trafic organique estimé (site-explorer-metrics-history)
    "trafficPrev": 17537,   // int — mois précédent (pour flèche MoM)
    "dr":          52,      // float — Domain Rating (site-explorer-domain-rating-history)
    "drPrev":      53,      // float | null
    "rd":          1114,    // int — referring domains actifs (site-explorer-backlinks-stats)
    "rdPrev":      884,     // int | null
    "bl":          12959,   // int — backlinks actifs
    "blPrev":      11394,   // int | null
    "cost":        1983     // int — valeur estimée trafic en $ (org_cost / 100)
  },
  "buckets": {
    "top3": 582,   "mid": 1464,  "low": 440,   // mois sélectionné (site-explorer-keywords-history)
    "prev": { "top3": 406, "mid": 1358, "low": 892 }  // null si pas de mois précédent
  },
  "movers": {
    "up": [                // array — mots-clés gagnants [keyword, volume, posBefore, posAfter]
      ["nourriture vietnamienne", 900, 47, 4]
    ],
    "down": [              // array — mots-clés perdants [keyword, volume, posBefore, posAfter]
      ["circuit egypte 10 jours", 1000, 21, 50]
    ],
    "flat": []
  }
}
```

### Appels Ahrefs API

| Champ | Outil Ahrefs | Paramètres clés |
|-------|-------------|-----------------|
| `kpi.traffic` | `site-explorer-metrics-history` | `date_from=YYYY-MM-01`, `history_grouping=monthly`, `select=date,org_traffic,org_cost` |
| `kpi.dr` | `site-explorer-domain-rating-history` | `date_from`, `history_grouping=monthly` |
| `kpi.rd` / `kpi.bl` | `site-explorer-backlinks-stats` | `date=YYYY-MM-30` |
| `buckets` | `site-explorer-keywords-history` | `country=fr`, `select=date,top3,top4_10,top11_plus` |
| `movers.up/down` | `site-explorer-organic-keywords` | `country=fr`, `date=fin_mois`, `date_compared=fin_mois_prev`, `order_by=best_position_diff:asc` (gains) ou `:desc` (pertes), `where={volume≥500, best_position≤30}` |

---

## `kw` — mots-clés détaillés (null = "Données non disponibles")

```json
{
  "byTraffic": [             // array — top mots-clés par trafic estimé
    ["shanti travel", 900, 843, 1, 1],    // [keyword, volume, traffic, position, positionPrev|null]
    ["philippines religion", 1400, 634, 1, 1]
  ],
  "byVolume": [              // array — top mots-clés par volume, position ≤ 30
    ["sri lanka", 118000, 77, 15, 15],
    ["philippines", 70000, 51, 13, 29]
  ]
}
```

Mettre `kw: null` si les données de mots-clés ne sont pas disponibles pour le mois.

### Appels Ahrefs API

```javascript
// byTraffic : top 38 par trafic estimé
site-explorer-organic-keywords({
  target: 'shantitravel.com', country: 'fr', mode: 'subdomains',
  date: 'YYYY-MM-31', date_compared: 'YYYY-MM-30',
  select: 'keyword,volume,sum_traffic,best_position,best_position_prev',
  order_by: 'sum_traffic_merged:desc', limit: 38
})

// byVolume : top 25 par volume avec position ≤ 30
// même appel + order_by: 'volume_merged:desc'
// + where: { best_position: { lte: 30 } }
```

---

## Template Apps Script (squelette)

```javascript
function buildD() {
  const today = new Date();
  const monthKey = Utilities.formatDate(today, 'Europe/Paris', 'MMMM yyyy'); // ex: "mai 2026"
  const prevMonthKey = /* mois précédent */;

  return {
    shared: {
      generated: Utilities.formatDate(today, 'Europe/Paris', 'd MMMM yyyy'),
      ahrefsTrend: fetchAhrefsTrend(),      // 3 derniers mois
      competitors:  fetchAhrefsCompetitors(), // batch-analysis
      refdomains:   fetchAhrefsRefdomains()   // top 25
    },
    months: {
      [monthKey]: {
        label:     monthKey.charAt(0).toUpperCase() + monthKey.slice(1),
        prevLabel: prevMonthKey,
        stamps:    buildStamps(),
        vercel:    readVercelFromSheet(),    // SpreadsheetApp.openById(SHEET_ID)
        gsc:       fetchGSCData(monthKey, prevMonthKey),
        ahrefs:    fetchAhrefsData(monthKey, prevMonthKey),
        kw:        fetchAhrefsKeywords(monthKey, prevMonthKey)
      }
      // Ajouter le mois précédent si disponible dans le Sheet
    }
  };
}

function generateReport() {
  const template = DriveApp.getFileById(TEMPLATE_FILE_ID).getBlob().getDataAsString();
  const filled = template.replace(/__DATA_PLACEHOLDER__/g, JSON.stringify(buildD()));
  // Sauvegarder ou servir via HtmlService / doGet
  const output = DriveApp.getFolderById(OUTPUT_FOLDER_ID)
    .createFile('rapport-seo-' + Utilities.formatDate(new Date(),'Europe/Paris','yyyy-MM') + '.html',
                filled, MimeType.HTML);
  Logger.log('Rapport généré : ' + output.getUrl());
}
```

---

## Résumé des remplacements entre l'objet original et le schéma `D`

| Ancien | Nouveau |
|--------|---------|
| `const SHARED` | `D.shared` |
| `const DATA` | `D.months` |
| `DATA[current]` | `D.months[current]` |
| `SHARED.generated` | `D.shared.generated` |
| `SHARED.ahrefsTrend` | `D.shared.ahrefsTrend` |
| `SHARED.competitors` | `D.shared.competitors` |
| `SHARED.refdomains` | `D.shared.refdomains` |
| `const MONTHS = [...]` | `const MONTHS = Object.keys(D.months)` |
