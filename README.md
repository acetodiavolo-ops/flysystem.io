# flysystem.io · Fly System Srls

Sito vetrina di Fly System Srls (Riccione): **distributore ufficiale** di porte, serramenti e sistemi outdoor. Design "Catalogo Italiano": carta avorio, blu Fly System (dal logo), argento tecnico. HTML/CSS/JS puro, nessun framework, nessun processo di build, zero richieste esterne.

## Struttura

```
index.html            Home (hero con sigillo, Bolla anteprima, indice prodotti, chi siamo, professionisti, teaser cataloghi)
bolla.html            Bolla, prodotto di punta (placeholder progettato: specifiche e foto in arrivo)
cataloghi.html        Libreria: 11 cataloghi PDF con Sfoglia/Scarica
contatti.html         Recapiti, modulo di contatto, FAQ
404.html              Pagina non trovata
assets/
  css/style.css       Design system completo (@layer tokens/base/components/pages)
  js/main.js          Solo progressive enhancement (menu, reveal, form): il sito funziona senza JS
  fonts/              Zodiak + General Sans (woff2, self-hosted, licenza Fontshare)
  img/                Immagini ottimizzate AVIF/WebP/JPEG (480/960/1600) estratte dai cataloghi + logo
  pdf/                11 cataloghi ufficiali (fly-system-*.pdf)
tools/                Script di sviluppo (non pubblicare): estrazione PDF, encoder immagini, screenshot QA
```

## Brand

- Palette campionata dal logo ufficiale: blu primario `#304890`, navy `#141B2B`, blu chiaro `#9FB0DC`, argento `#84849C`, carta `#F5F2EC`. Tutto parte dai token in cima a `style.css`.
- Logo: estratto ad alta risoluzione dai cataloghi PDF (`assets/img/logo-300.png`, `logo-600.png`); nell'header usa `mix-blend-mode: multiply` per fondersi con la carta.
- Elementi distintivi: sigillo rotante "Distributore ufficiale" nella hero, trama millimetrata blueprint nelle sezioni tecniche, dorso e pagine impilate sulle copertine dei cataloghi, dissolvenza tra pagine (View Transitions), respiro della "bolla" nella hero di bolla.html.
- Regola tipografica fissa: mai em dash (né en dash). Separatori: punto mediano (·), due punti, virgole; trattino semplice per gli intervalli (REI 30-120).

## Anteprima locale

```
python -m http.server 8000
# oppure: npx serve .
```

## Da sapere

- **Modulo contatti**: `action` punta a `https://formsubmit.co/info@flysystemrn.it`. Al primo invio FormSubmit manda una mail di conferma da approvare. In alternativa sostituire l'endpoint (Formspree, PHP dell'hosting): è un solo attributo in `contatti.html`.
- **Bolla**: pagina strutturata per assorbire dati reali senza redesign. Sostituire i valori "n.d." nella scheda tecnica e riempire la gallery (Fig. 04-06 già riservate) quando arrivano foto e specifiche ufficiali.
- **Deploy**: caricare tutto tranne `tools/` su qualsiasi hosting statico. Configurare la pagina 404 nel pannello hosting.
- **Header/footer**: duplicati nelle 5 pagine, marcati `<!-- shared: ... keep in sync -->`. Modificarli ovunque insieme.
- **QA v2** (2026-07-19): Lighthouse mobile Perf 96-98 · A11y 100 · Best Practices 100 · SEO 100 su tutte le pagine; html-validate pulito; nessun overflow orizzontale a 360/390/768/1440.

## Dati in attesa di conferma (placeholder nel sito)

1. P.IVA per il footer legale
2. Orari di apertura / showroom (Contatti)
3. Numero mobile: il sito usa 380 897 2795 (catalogo 2026); il flyer 2025 riporta 327 4679241
4. Testo privacy/cookie (il sito non usa cookie)
5. Specifiche, listino e foto ufficiali Bolla
6. File vettoriale del logo, se disponibile (attuale: estrazione hi-res dai PDF)
