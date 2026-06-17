<?php
/**
 * MyContentPilot.de — Features / Demo Page
 * Template: page-funktionen.php
 */
get_header(); ?>

<!-- ============================================================
     HERO — compact, dark
     ============================================================ -->
<section class="section--dark" style="padding:var(--s-20) 0 var(--s-16);text-align:center;">
  <div class="container container--narrow">
    <div class="t-eyebrow t-eyebrow--dark" style="display:inline-flex;margin-bottom:var(--s-4);">Funktionen</div>
    <h1 class="t-display" style="color:var(--c-white);font-size:var(--t-4xl);margin-bottom:var(--s-4);">
      Eine Plattform.<br>
      <span class="t-accent">Der gesamte Workflow.</span>
    </h1>
    <p class="t-lead" style="margin-bottom:var(--s-8);">
      MyContentPilot ist kein Content-Tool — es ist eine vollständige
      Automatisierungsinfrastruktur, die auf Ihrem eigenen Server läuft.
    </p>
    <div style="display:flex;align-items:center;justify-content:center;gap:var(--s-4);flex-wrap:wrap;">
      <a href="https://calendly.com/mycontentpilot/30min" class="btn btn--primary btn--lg">Demo anfragen</a>
      <a href="<?php echo esc_url( home_url('/preise') ); ?>" class="btn btn--ghost btn--lg">Preise ansehen</a>
    </div>
  </div>
</section>

<!-- ============================================================
     VIDEO EMBED PLACEHOLDER
     ============================================================ -->
<section class="section section--off" style="padding-top:var(--s-16);padding-bottom:var(--s-16);">
  <div class="container container--narrow">
    <div class="section__header">
      <div class="t-eyebrow">Demo-Video</div>
      <h2 class="t-h2" style="margin-top:var(--s-4);">Sehen Sie MyContentPilot in Aktion.</h2>
      <p class="t-lead" style="margin-top:var(--s-4);">
        2 Minuten. Vom Thema zum fertigen Post — vollautomatisch.
      </p>
    </div>

    <div class="video-embed-wrap">
      <!-- Replace this block with your Loom embed code -->
      <div class="video-placeholder" aria-label="Demo-Video Platzhalter">
        <div class="video-placeholder__inner">
          <div class="video-placeholder__icon" aria-hidden="true">▶</div>
          <p class="video-placeholder__text">Demo-Video folgt in Kürze</p>
          <p style="font-size:var(--t-xs);color:var(--c-text-muted);margin-top:var(--s-2);">
            [LOOM-EMBED] — Loom-Einbettungscode hier einfügen
          </p>
        </div>
      </div>
      <!-- End placeholder -->
    </div>

    <p style="text-align:center;margin-top:var(--s-6);font-size:var(--t-sm);color:var(--c-text-secondary);">
      Lieber live ansehen?
      <a href="https://calendly.com/mycontentpilot/30min" style="color:var(--c-indigo);font-weight:600;">Demo-Termin vereinbaren →</a>
    </p>
  </div>
</section>

<!-- ============================================================
     PIPELINE ARCHITECTURE — how the engine works
     ============================================================ -->
<section class="section section--dark">
  <div class="container">
    <div class="section__header">
      <div class="t-eyebrow t-eyebrow--dark">Architektur</div>
      <h2 class="t-h2" style="color:var(--c-white);margin-top:var(--s-4);">
        Jeder Inhalt durchläuft<br>eine geprüfte Pipeline.
      </h2>
      <p class="t-lead" style="margin-top:var(--s-4);max-width:560px;margin-left:auto;margin-right:auto;">
        MyContentPilot arbeitet nicht nach dem Zufallsprinzip.
        Jeder Schritt ist deterministisch, wiederholbar und vollständig protokolliert.
      </p>
    </div>

    <!-- Pipeline stages -->
    <div class="pipeline">
      <div class="pipeline__stage">
        <div class="pipeline__num" aria-hidden="true">01</div>
        <div class="pipeline__icon" aria-hidden="true">🔍</div>
        <h3 class="pipeline__title">Collect</h3>
        <p class="pipeline__desc">Themen, Nachrichten und Rohdaten werden aus konfigurierten Quellen gesammelt.</p>
      </div>
      <div class="pipeline__arrow" aria-hidden="true">→</div>

      <div class="pipeline__stage">
        <div class="pipeline__num" aria-hidden="true">02</div>
        <div class="pipeline__icon" aria-hidden="true">✅</div>
        <h3 class="pipeline__title">Validate</h3>
        <p class="pipeline__desc">Duplikate werden erkannt. Qualität und Relevanz werden geprüft.</p>
      </div>
      <div class="pipeline__arrow" aria-hidden="true">→</div>

      <div class="pipeline__stage">
        <div class="pipeline__num" aria-hidden="true">03</div>
        <div class="pipeline__icon" aria-hidden="true">🤖</div>
        <h3 class="pipeline__title">Generate</h3>
        <p class="pipeline__desc">Das gewählte KI-Modell erstellt plattformgerechten Content.</p>
      </div>
      <div class="pipeline__arrow" aria-hidden="true">→</div>

      <div class="pipeline__stage">
        <div class="pipeline__num" aria-hidden="true">04</div>
        <div class="pipeline__icon" aria-hidden="true">✨</div>
        <h3 class="pipeline__title">Enrich</h3>
        <p class="pipeline__desc">Hashtags, Bilder und Metadaten werden automatisch ergänzt.</p>
      </div>
      <div class="pipeline__arrow" aria-hidden="true">→</div>

      <div class="pipeline__stage">
        <div class="pipeline__num" aria-hidden="true">05</div>
        <div class="pipeline__icon" aria-hidden="true">📤</div>
        <h3 class="pipeline__title">Publish</h3>
        <p class="pipeline__desc">Der fertige Inhalt wird pünktlich auf allen Plattformen veröffentlicht.</p>
      </div>
    </div><!-- /.pipeline -->

    <p style="text-align:center;margin-top:var(--s-8);font-size:var(--t-sm);color:var(--c-text-muted-dark);">
      Jeder Schritt ist unabhängig testbar, protokolliert und bei Fehler automatisch wiederholbar.
    </p>
  </div>
</section>

<!-- ============================================================
     MODULES — the 5 content engines
     ============================================================ -->
<section class="section" id="module">
  <div class="container">
    <div class="section__header">
      <div class="t-eyebrow">Module</div>
      <h2 class="t-h2" style="margin-top:var(--s-4);">Fünf spezialisierte Content-Engines.</h2>
      <p class="t-lead" style="margin-top:var(--s-4);">
        Jedes Modul ist ein eigenständiger Service — unabhängig konfigurierbar,
        betreibbar und erweiterbar.
      </p>
    </div>

    <div class="module-list">

      <!-- daily_news -->
      <div class="module-card">
        <div class="module-card__header">
          <div class="module-card__icon" aria-hidden="true">📰</div>
          <div>
            <div class="module-card__tag">daily_news</div>
            <h3 class="module-card__title">Tages-Nachrichten</h3>
          </div>
        </div>
        <p class="module-card__desc">
          Aggregiert täglich aktuelle Nachrichten aus konfigurierten Quellen,
          bewertet Relevanz, generiert redaktionell aufbereitete Artikel
          und veröffentlicht sie vollautomatisch auf WordPress und Social Media.
        </p>
        <ul class="module-card__features">
          <li>Automatische Quellaggregation</li>
          <li>KI-basierte Relevanzbewertung</li>
          <li>WordPress + Social Publishing</li>
          <li>Duplikat-Erkennung über alle Kanäle</li>
        </ul>
      </div>

      <!-- article_publisher -->
      <div class="module-card">
        <div class="module-card__header">
          <div class="module-card__icon" aria-hidden="true">✍️</div>
          <div>
            <div class="module-card__tag">article_publisher</div>
            <h3 class="module-card__title">Artikel-Publisher</h3>
          </div>
        </div>
        <p class="module-card__desc">
          Generiert vollständige Blog-Artikel auf Basis von Themen oder Keywords,
          optimiert für SEO und Lesbarkeit, und veröffentlicht direkt in WordPress
          inklusive Kategorien, Tags und Featured Image.
        </p>
        <ul class="module-card__features">
          <li>Vollständige Artikel-Generierung</li>
          <li>SEO-optimierte Struktur</li>
          <li>WordPress Direct Publishing</li>
          <li>Kategorien & Tags automatisch</li>
        </ul>
      </div>

      <!-- deals_engine -->
      <div class="module-card">
        <div class="module-card__header">
          <div class="module-card__icon" aria-hidden="true">🏷️</div>
          <div>
            <div class="module-card__tag">deals_engine</div>
            <h3 class="module-card__title">Deals &amp; Affiliate</h3>
          </div>
        </div>
        <p class="module-card__desc">
          Erstellt automatisiert Angebots- und Affiliate-Content aus Produktdaten.
          Generiert überzeugende Beschreibungen, formatiert Posts plattformgerecht
          und veröffentlicht zum optimalen Zeitpunkt.
        </p>
        <ul class="module-card__features">
          <li>Produktdaten-Verarbeitung</li>
          <li>Überzeugende KI-Texte</li>
          <li>Zeitgesteuertes Publishing</li>
          <li>Multi-Plattform-Format</li>
        </ul>
      </div>

      <!-- social_tips -->
      <div class="module-card">
        <div class="module-card__header">
          <div class="module-card__icon" aria-hidden="true">💡</div>
          <div>
            <div class="module-card__tag">social_tips</div>
            <h3 class="module-card__title">Social Tips &amp; Tipps</h3>
          </div>
        </div>
        <p class="module-card__desc">
          Erzeugt regelmäßige Tipps, How-tos und Ratgeber-Content für Social Media.
          Ideal für Branchenexperten, die kontinuierlich Mehrwert für ihre Community
          schaffen möchten — ohne Aufwand.
        </p>
        <ul class="module-card__features">
          <li>Themen-basierte Generierung</li>
          <li>Facebook & Instagram optimiert</li>
          <li>Hashtag-Automatisierung</li>
          <li>Konsistenter Posting-Rhythmus</li>
        </ul>
      </div>

      <!-- social_video -->
      <div class="module-card">
        <div class="module-card__header">
          <div class="module-card__icon" aria-hidden="true">🎬</div>
          <div>
            <div class="module-card__tag">social_video</div>
            <h3 class="module-card__title">Video-Skripte</h3>
          </div>
        </div>
        <p class="module-card__desc">
          Generiert strukturierte Skripte und Beschreibungen für Kurzvideos.
          Liefert Hook, Inhalt und Call-to-Action — fertig zum Aufnehmen
          oder für zukünftige vollautomatische Video-Produktion.
        </p>
        <ul class="module-card__features">
          <li>Hook + Inhalt + CTA Struktur</li>
          <li>Plattformgerechte Länge</li>
          <li>Beschreibungen & Tags</li>
          <li>Vorbereitet für TikTok & YouTube</li>
        </ul>
      </div>

    </div><!-- /.module-list -->
  </div>
</section>

<!-- ============================================================
     INFRASTRUCTURE HIGHLIGHTS — self-hosted advantages
     ============================================================ -->
<section class="section section--off">
  <div class="container">
    <div class="section__header">
      <div class="t-eyebrow">Infrastruktur</div>
      <h2 class="t-h2" style="margin-top:var(--s-4);">
        Ihr Server. Ihre Daten.<br>Ihre Kontrolle.
      </h2>
      <p class="t-lead" style="margin-top:var(--s-4);">
        MyContentPilot läuft vollständig auf Ihrer eigenen Infrastruktur —
        Docker-basiert, produktionsreif, DSGVO-konform by design.
      </p>
    </div>

    <div class="grid-3">
      <div class="card">
        <div class="card__icon" style="font-size:22px;">🐳</div>
        <h3>Docker-First</h3>
        <p>Jedes Modul läuft in einem eigenen Container. Kein Setup-Chaos, keine Abhängigkeitskonflikte — einfach deployen.</p>
      </div>
      <div class="card">
        <div class="card__icon" style="font-size:22px;">🔐</div>
        <h3>Zero Data Sharing</h3>
        <p>Ihre API-Keys, Inhalte und Zugangsdaten verlassen Ihren Server nie. Kein externer Anbieter hat Einblick.</p>
      </div>
      <div class="card">
        <div class="card__icon" style="font-size:22px;">📋</div>
        <h3>Vollständiges Logging</h3>
        <p>Jeder Pipeline-Schritt wird mit Zeitstempel, Status und Metadaten protokolliert. Vollständige Nachvollziehbarkeit.</p>
      </div>
      <div class="card">
        <div class="card__icon" style="font-size:22px;">🔄</div>
        <h3>Retry-Safe Pipelines</h3>
        <p>Fehler werden automatisch erkannt und mit Backoff wiederholt. Kein manuelles Eingreifen erforderlich.</p>
      </div>
      <div class="card">
        <div class="card__icon" style="font-size:22px;">⏱️</div>
        <h3>Cron-Scheduling</h3>
        <p>Jobs laufen nach Zeitplan — vollautomatisch. Konfigurierbar pro Modul, pro Plattform, pro Uhrzeit.</p>
      </div>
      <div class="card">
        <div class="card__icon" style="font-size:22px;">📦</div>
        <h3>Modular erweiterbar</h3>
        <p>Neue Module, Plattformen und KI-Modelle lassen sich ohne Änderungen am Kernsystem integrieren.</p>
      </div>
    </div>
  </div>
</section>

<!-- ============================================================
     PLATFORMS — live + roadmap
     ============================================================ -->
<section class="section" id="plattformen">
  <div class="container">
    <div class="section__header">
      <div class="t-eyebrow">Plattformen</div>
      <h2 class="t-h2" style="margin-top:var(--s-4);">Wo MyContentPilot veröffentlicht.</h2>
    </div>

    <div class="platforms-grid">

      <div class="platform-card platform-card--live">
        <div class="platform-card__status"><span class="badge badge--live">Live</span></div>
        <div class="platform-card__icon" aria-hidden="true">📘</div>
        <h3 class="platform-card__name">Facebook</h3>
        <p class="platform-card__desc">Posts, Bilder, Links — vollautomatisch auf Ihrer Facebook-Seite.</p>
      </div>

      <div class="platform-card platform-card--live">
        <div class="platform-card__status"><span class="badge badge--live">Live</span></div>
        <div class="platform-card__icon" aria-hidden="true">📸</div>
        <h3 class="platform-card__name">Instagram</h3>
        <p class="platform-card__desc">Beiträge mit Bild und Caption — direkt in Ihren Instagram-Account.</p>
      </div>

      <div class="platform-card platform-card--live">
        <div class="platform-card__status"><span class="badge badge--live">Live</span></div>
        <div class="platform-card__icon" aria-hidden="true">📸</div>
        <h3 class="platform-card__name">LinkedIn</h3>
        <p class="platform-card__desc">Professioneller Content für Ihr Unternehmensprofil und Ihre Seite.</p>
      </div>

      <div class="platform-card platform-card--live">
        <div class="platform-card__status"><span class="badge badge--live">Live</span></div>
        <div class="platform-card__icon" aria-hidden="true">🌐</div>
        <h3 class="platform-card__name">WordPress</h3>
        <p class="platform-card__desc">Artikel, Kategorien, Tags — direkt in Ihre WordPress-Installation.</p>
      </div>

      <div class="platform-card platform-card--request">
        <div class="platform-card__status"><span style="font-size:var(--t-xs);font-weight:600;color:var(--c-text-muted);">Auf Anfrage</span></div>
        <div class="platform-card__icon" aria-hidden="true">➕</div>
        <h3 class="platform-card__name">Weitere Plattformen</h3>
        <p class="platform-card__desc">Benötigen Sie eine andere Plattform? Wir integrieren auf Anfrage.</p>
        <a href="<?php echo esc_url( home_url('/kontakt') ); ?>" style="font-size:var(--t-sm);font-weight:600;color:var(--c-indigo);margin-top:var(--s-2);display:inline-block;">Anfrage stellen →</a>
      </div>

    </div><!-- /.platforms-grid -->
  </div>
</section>

<!-- ============================================================
     AI MODELS — agnostic section
     ============================================================ -->
<section class="section section--dark" id="ki-modelle">
  <div class="container container--narrow" style="text-align:center;">
    <div class="t-eyebrow t-eyebrow--dark" style="display:inline-flex;margin-bottom:var(--s-6);">KI-Modelle</div>
    <h2 class="t-h2" style="color:var(--c-white);margin-bottom:var(--s-4);">
      Das KI-Modell wählen Sie.
    </h2>
    <p class="t-lead" style="margin-bottom:var(--s-8);">
      MyContentPilot ist vollständig modell-agnostisch.
      Alle KI-Aufrufe laufen durch eine einheitliche Abstraktionsschicht —
      das Modell ist austauschbar, ohne dass Module angepasst werden müssen.
    </p>

    <div style="display:flex;align-items:center;justify-content:center;gap:var(--s-3);flex-wrap:wrap;margin-bottom:var(--s-8);">
      <span class="model-pill">Claude</span>
      <span class="model-pill">GPT-4</span>
      <span class="model-pill">DeepSeek</span>
      <span class="model-pill">Gemini</span>
      <span class="model-pill model-pill--more">+ weitere</span>
    </div>

    <div class="grid-3" style="text-align:left;">
      <div class="card card--dark">
        <div class="card__icon card__icon--dark" style="font-size:20px;">🔀</div>
        <h3 style="color:var(--c-text-on-dark);">Modell frei wählbar</h3>
        <p>Sie konfigurieren einmalig, welches KI-Modell verwendet wird. Jederzeit wechselbar.</p>
      </div>
      <div class="card card--dark">
        <div class="card__icon card__icon--dark" style="font-size:20px;">⚡</div>
        <h3 style="color:var(--c-text-on-dark);">Fallback-Modell</h3>
        <p>Fällt das Primärmodell aus, wechselt das System automatisch auf ein konfiguriertes Fallback.</p>
      </div>
      <div class="card card--dark">
        <div class="card__icon card__icon--dark" style="font-size:20px;">🔭</div>
        <h3 style="color:var(--c-text-on-dark);">Zukunftssicher</h3>
        <p>Neue KI-Modelle werden als Provider integriert — ohne Änderungen an Ihren Pipelines.</p>
      </div>
    </div>
  </div>
</section>

<!-- ============================================================
     FINAL CTA
     ============================================================ -->
<section class="section" style="background:linear-gradient(135deg,#3A56D4 0%,#4F6EF7 50%,#6B8AFB 100%);">
  <div class="container container--narrow" style="text-align:center;">
    <h2 class="t-h2" style="color:#fff;margin-bottom:var(--s-4);">
      Bereit für Ihre eigene Content-Automatisierung?
    </h2>
    <p style="font-size:var(--t-lg);color:rgba(255,255,255,0.82);margin-bottom:var(--s-8);line-height:1.6;">
      Vereinbaren Sie eine kostenlose Demo — individuell, live, ohne Verpflichtung.
    </p>
    <div style="display:flex;align-items:center;justify-content:center;gap:var(--s-4);flex-wrap:wrap;">
      <a href="https://calendly.com/mycontentpilot/30min"
         class="btn btn--lg"
         style="background:#fff;color:var(--c-indigo);font-weight:700;box-shadow:0 4px 20px rgba(0,0,0,0.15);">
        Demo anfragen
      </a>
      <a href="<?php echo esc_url( home_url('/preise') ); ?>" class="btn btn--ghost btn--lg">
        Preise ansehen
      </a>
    </div>
  </div>
</section>

<?php get_footer(); ?>
