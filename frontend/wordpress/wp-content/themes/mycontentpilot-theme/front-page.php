<?php
/**
 * MyContentPilot.de — Homepage
 * Template: front-page.php
 */
get_header(); ?>

<!-- ============================================================
     SECTION 1 — HERO (dark)
     ============================================================ -->
<section class="hero section--dark" style="padding-top:var(--s-24);padding-bottom:var(--s-24);position:relative;overflow:hidden;">

  <!-- Ambient glow behind headline -->
  <div aria-hidden="true" style="position:absolute;top:0;left:50%;transform:translateX(-50%);width:700px;height:400px;background:radial-gradient(ellipse at center,rgba(79,110,247,0.18) 0%,transparent 70%);pointer-events:none;"></div>

  <div class="container" style="position:relative;text-align:center;">

    <div class="t-eyebrow t-eyebrow--dark" style="margin-bottom:var(--s-6);display:inline-flex;">
      KI-gestützte Content-Automatisierung
    </div>

    <h1 class="t-display" style="color:var(--c-white);margin-bottom:var(--s-6);max-width:780px;margin-left:auto;margin-right:auto;">
      Ihr Content-Workflow.<br>
      <span class="t-accent">Vollständig automatisiert.</span>
    </h1>

    <p class="t-lead" style="max-width:580px;margin:0 auto var(--s-8);">
      MyContentPilot generiert, plant und veröffentlicht Inhalte auf allen Plattformen —
      auf Ihrem eigenen Server, mit jedem KI-Modell.
    </p>

    <div style="display:flex;align-items:center;justify-content:center;gap:var(--s-4);flex-wrap:wrap;margin-bottom:var(--s-10);">
      <a href="https://calendly.com/mycontentpilot/30min" class="btn btn--primary btn--lg">
        Demo anfragen
      </a>
      <a href="<?php echo esc_url( home_url('/funktionen') ); ?>" class="btn btn--ghost btn--lg">
        Funktionen entdecken
      </a>
    </div>

    <!-- Platform trust row -->
    <div style="display:flex;align-items:center;justify-content:center;gap:var(--s-3);flex-wrap:wrap;">
      <span style="font-size:var(--t-xs);color:var(--c-text-muted-dark);margin-right:var(--s-1);">Verfügbar für:</span>
      <span class="badge badge--live">Facebook</span>
      <span class="badge badge--live">Instagram</span>
      <span class="badge badge--live">LinkedIn</span>
      <span class="badge badge--live">WordPress</span>
      <span style="font-size:var(--t-xs);color:var(--c-text-muted-dark);">+ weitere demnächst</span>
    </div>

  </div>
</section>

<!-- ============================================================
     SECTION 2 — FÜR WEN? (light bg)
     ============================================================ -->
<section class="section section--off">
  <div class="container">

    <div class="section__header">
      <div class="t-eyebrow">Für wen ist MyContentPilot?</div>
      <h2 class="t-h2" style="margin-top:var(--s-4);">Gebaut für alle, die Content<br>ernst nehmen.</h2>
    </div>

    <div class="grid-3">

      <div class="card">
        <div class="card__icon" style="font-size:24px;">🏢</div>
        <h3>Agenturen</h3>
        <p>Verwalten Sie mehrere Kundenaccounts und Plattformen zentral. Skalieren Sie ohne zusätzliches Personal.</p>
      </div>

      <div class="card">
        <div class="card__icon" style="font-size:24px;">👤</div>
        <h3>Selbstständige</h3>
        <p>Automatisieren Sie Ihren Content-Workflow ohne teures Team. Mehr Zeit für Ihr Kerngeschäft.</p>
      </div>

      <div class="card">
        <div class="card__icon" style="font-size:24px;">🏭</div>
        <h3>Unternehmen</h3>
        <p>Skalieren Sie Ihre Content-Produktion ohne Qualitätsverlust. DSGVO-konform auf Ihrer eigenen Infrastruktur.</p>
      </div>

    </div>
  </div>
</section>

<!-- ============================================================
     SECTION 3 — PROBLEM (dark bg)
     ============================================================ -->
<section class="section section--dark">
  <div class="container">

    <div class="section__header">
      <div class="t-eyebrow t-eyebrow--dark">Das Problem</div>
      <h2 class="t-h2" style="color:var(--c-white);margin-top:var(--s-4);">Content kostet Zeit.<br>Zeit kostet Geld.</h2>
      <p class="t-lead" style="margin-top:var(--s-4);max-width:520px;margin-left:auto;margin-right:auto;">
        Kennen Sie diese Probleme? Sie sind nicht allein.
      </p>
    </div>

    <div class="grid-3" style="margin-bottom:var(--s-6);">

      <div class="card card--dark">
        <div class="card__icon card__icon--dark" style="font-size:22px;">⏰</div>
        <h3 style="color:var(--c-text-on-dark);">Zu wenig Zeit</h3>
        <p>Täglich Content zu erstellen kostet Stunden, die Sie für Ihr Kerngeschäft brauchen.</p>
      </div>

      <div class="card card--dark">
        <div class="card__icon card__icon--dark" style="font-size:22px;">💸</div>
        <h3 style="color:var(--c-text-on-dark);">Teure Agenturen</h3>
        <p>Social-Media-Manager und Agenturen kosten hunderte Euro im Monat — ohne Erfolgsgarantie.</p>
      </div>

      <div class="card card--dark">
        <div class="card__icon card__icon--dark" style="font-size:22px;">🔄</div>
        <h3 style="color:var(--c-text-on-dark);">Fehlende Kontinuität</h3>
        <p>Unregelmäßige Posts schaden der Reichweite. Algorithmen belohnen nur konsistente Präsenz.</p>
      </div>

    </div>

    <div class="grid-2" style="max-width:740px;margin:0 auto var(--s-12);">

      <div class="card card--dark">
        <div class="card__icon card__icon--dark" style="font-size:22px;">💡</div>
        <h3 style="color:var(--c-text-on-dark);">Ideen gehen aus</h3>
        <p>Jeden Tag neue Themen zu finden ist erschöpfend und blockiert den gesamten Workflow.</p>
      </div>

      <div class="card card--dark">
        <div class="card__icon card__icon--dark" style="font-size:22px;">🔒</div>
        <h3 style="color:var(--c-text-on-dark);">Vendor Lock-in</h3>
        <p>SaaS-Tools speichern Ihre Daten auf fremden Servern — unkontrollierbar und dauerhaft teuer.</p>
      </div>

    </div>

    <div style="text-align:center;">
      <p style="font-size:var(--t-xl);font-weight:700;color:var(--c-white);">
        MyContentPilot löst all das —
        <span style="color:var(--c-indigo);">automatisch.</span>
      </p>
    </div>

  </div>
</section>

<!-- ============================================================
     SECTION 4 — HOW IT WORKS (light bg)
     ============================================================ -->
<section class="section section--off">
  <div class="container">

    <div class="section__header">
      <div class="t-eyebrow">So funktioniert es</div>
      <h2 class="t-h2" style="margin-top:var(--s-4);">Drei Schritte. Content fertig.</h2>
    </div>

    <!-- Steps -->
    <div class="hiw-steps">

      <div class="hiw-step">
        <div class="hiw-step__number" aria-hidden="true">1</div>
        <div class="hiw-step__connector" aria-hidden="true"></div>
        <div class="hiw-step__icon" aria-hidden="true">⚙️</div>
        <h3 class="hiw-step__title">Einmalig einrichten</h3>
        <p class="hiw-step__desc">Sie definieren Branche, Stil, KI-Modell und Zielplattformen. Einmal konfigurieren, dauerhaft profitieren.</p>
      </div>

      <div class="hiw-step">
        <div class="hiw-step__number" aria-hidden="true">2</div>
        <div class="hiw-step__connector" aria-hidden="true"></div>
        <div class="hiw-step__icon" aria-hidden="true">🤖</div>
        <h3 class="hiw-step__title">KI generiert den Content</h3>
        <p class="hiw-step__desc">MyContentPilot wählt das beste verfügbare KI-Modell und erstellt plattformgerechte Inhalte — vollautomatisch.</p>
      </div>

      <div class="hiw-step">
        <div class="hiw-step__number" aria-hidden="true">3</div>
        <div class="hiw-step__connector hiw-step__connector--last" aria-hidden="true"></div>
        <div class="hiw-step__icon" aria-hidden="true">🚀</div>
        <h3 class="hiw-step__title">Automatisch veröffentlicht</h3>
        <p class="hiw-step__desc">Ihr Inhalt erscheint pünktlich auf allen gewählten Plattformen — ohne Ihr Zutun.</p>
      </div>

    </div>
  </div>
</section>

<!-- ============================================================
     SECTION 5 — FEATURES GRID (white bg)
     ============================================================ -->
<section class="section">
  <div class="container">

    <div class="section__header">
      <div class="t-eyebrow">Funktionen</div>
      <h2 class="t-h2" style="margin-top:var(--s-4);">Alles was Sie brauchen.<br>Nichts was Sie nicht brauchen.</h2>
    </div>

    <div class="grid-3">

      <div class="card">
        <div class="card__icon" style="font-size:22px;">🤖</div>
        <h3>KI-Modell frei wählbar</h3>
        <p>Claude, GPT-4, DeepSeek, Gemini — Sie entscheiden, welches Modell verwendet wird. Jederzeit wechselbar.</p>
      </div>

      <div class="card">
        <div class="card__icon" style="font-size:22px;">📅</div>
        <h3>Vollautomatische Planung</h3>
        <p>Cron-basiertes Scheduling sorgt dafür, dass Inhalte zum richtigen Zeitpunkt veröffentlicht werden — ohne manuellen Aufwand.</p>
      </div>

      <div class="card">
        <div class="card__icon" style="font-size:22px;">🌐</div>
        <h3>Multi-Plattform-Publishing</h3>
        <p>Ein Workflow, viele Kanäle. Facebook, Instagram, WordPress — gleichzeitig und fehlertolerant.</p>
      </div>

      <div class="card">
        <div class="card__icon" style="font-size:22px;">🔁</div>
        <h3>Duplikat-Erkennung</h3>
        <p>MyContentPilot erkennt bereits veröffentlichte Inhalte automatisch. Kein Beitrag erscheint zweimal.</p>
      </div>

      <div class="card">
        <div class="card__icon" style="font-size:22px;">🏠</div>
        <h3>Ihr eigener Server</h3>
        <p>Alle Daten bleiben auf Ihrer Infrastruktur. Kein externer Anbieter hat Zugriff auf Ihre Inhalte oder Zugangsdaten.</p>
      </div>

      <div class="card">
        <div class="card__icon" style="font-size:22px;">🔌</div>
        <h3>Modular erweiterbar</h3>
        <p>Neue Plattformen und Inhaltsmodule auf Anfrage. MyContentPilot wächst mit Ihren Anforderungen.</p>
      </div>

    </div>
  </div>
</section>

<!-- ============================================================
     SECTION 6 — PLATFORMS (off-white bg)
     ============================================================ -->
<section class="section section--off" id="plattformen">
  <div class="container">

    <div class="section__header">
      <div class="t-eyebrow">Plattformen</div>
      <h2 class="t-h2" style="margin-top:var(--s-4);">Heute live. Morgen mehr.</h2>
      <p class="t-lead" style="margin-top:var(--s-4);">
        Jetzt verfügbar — und ständig wächst die Liste.
      </p>
    </div>

    <!-- Live platforms -->
    <div style="text-align:center;margin-bottom:var(--s-6);">
      <p style="font-size:var(--t-xs);font-weight:700;letter-spacing:0.08em;text-transform:uppercase;color:var(--c-text-muted);margin-bottom:var(--s-4);">
        Jetzt verfügbar
      </p>
      <div style="display:flex;align-items:center;justify-content:center;gap:var(--s-3);flex-wrap:wrap;">
        <div class="platform-pill platform-pill--live">
          <span class="platform-pill__dot"></span>
          Facebook
        </div>
        <div class="platform-pill platform-pill--live">
          <span class="platform-pill__dot"></span>
          Instagram
        </div>
        <div class="platform-pill platform-pill--live">
          <span class="platform-pill__dot"></span>
          LinkedIn
        </div>
        <div class="platform-pill platform-pill--live">
          <span class="platform-pill__dot"></span>
          WordPress
        </div>
      </div>
    </div>

    <p style="text-align:center;font-size:var(--t-sm);color:var(--c-text-secondary);">
      Weitere Plattformen auf Anfrage verfügbar. &nbsp;
      <a href="<?php echo esc_url( home_url('/kontakt') ); ?>" style="color:var(--c-indigo);font-weight:600;">Anfrage stellen →</a>
    </p>

  </div>
</section>

<!-- ============================================================
     SECTION 7 — AI MODELS (white bg)
     ============================================================ -->
<section class="section" id="ki-modelle">
  <div class="container container--narrow" style="text-align:center;">

    <div class="t-eyebrow" style="display:inline-flex;margin-bottom:var(--s-6);">KI-Modelle</div>
    <h2 class="t-h2" style="margin-bottom:var(--s-4);">
      Funktioniert mit jedem KI-Modell.
    </h2>
    <p class="t-lead" style="margin-bottom:var(--s-8);">
      MyContentPilot ist modell-agnostisch. Sie wählen — oder wechseln jederzeit ohne Aufwand.
    </p>

    <!-- Model pills -->
    <div style="display:flex;align-items:center;justify-content:center;gap:var(--s-3);flex-wrap:wrap;margin-bottom:var(--s-6);">
      <span class="model-pill">Claude</span>
      <span class="model-pill">GPT-4</span>
      <span class="model-pill">DeepSeek</span>
      <span class="model-pill">Gemini</span>
      <span class="model-pill model-pill--more">+ weitere</span>
    </div>

    <p style="font-size:var(--t-sm);color:var(--c-text-secondary);">
      Primär- und Fallback-Modell frei konfigurierbar. Automatischer Wechsel bei Ausfall des Primärmodells.
    </p>

  </div>
</section>

<!-- ============================================================
     SECTION 8 — PRICING PREVIEW (dark bg)
     ============================================================ -->
<section class="section section--dark">
  <div class="container">

    <div class="section__header">
      <div class="t-eyebrow t-eyebrow--dark">Preise</div>
      <h2 class="t-h2" style="color:var(--c-white);margin-top:var(--s-4);">Einfache Preise.<br>Keine versteckten Kosten.</h2>
    </div>

    <div class="grid-3" style="margin-bottom:var(--s-8);">

      <!-- Starter -->
      <div class="card card--dark" style="display:flex;flex-direction:column;">
        <div style="margin-bottom:var(--s-4);">
          <p style="font-size:var(--t-sm);font-weight:600;color:var(--c-text-muted-dark);margin-bottom:var(--s-2);">Starter</p>
          <div style="display:flex;align-items:baseline;gap:var(--s-1);">
            <span style="font-size:var(--t-4xl);font-weight:800;color:var(--c-white);">€49</span>
            <span style="font-size:var(--t-sm);color:var(--c-text-muted-dark);">/Monat</span>
          </div>
        </div>
        <ul style="display:flex;flex-direction:column;gap:var(--s-3);margin-bottom:var(--s-6);flex:1;">
          <li class="pricing-feature">1 Plattform</li>
          <li class="pricing-feature">1 KI-Modell</li>
          <li class="pricing-feature">Bis 30 Posts/Monat</li>
          <li class="pricing-feature">E-Mail-Support</li>
        </ul>
        <a href="<?php echo esc_url( home_url('/kontakt') ); ?>" class="btn btn--ghost" style="justify-content:center;">
          Jetzt anfragen
        </a>
      </div>

      <!-- Pro — highlighted -->
      <div class="card card--dark" style="border:2px solid var(--c-indigo);position:relative;display:flex;flex-direction:column;box-shadow:0 0 0 1px var(--c-indigo),0 8px 40px rgba(79,110,247,0.25);">
        <div style="position:absolute;top:-14px;left:50%;transform:translateX(-50%);">
          <span style="background:var(--c-indigo);color:#fff;font-size:var(--t-xs);font-weight:700;padding:4px 14px;border-radius:var(--radius-pill);white-space:nowrap;">⭐ Beliebteste Wahl</span>
        </div>
        <div style="margin-bottom:var(--s-4);margin-top:var(--s-2);">
          <p style="font-size:var(--t-sm);font-weight:600;color:var(--c-text-muted-dark);margin-bottom:var(--s-2);">Pro</p>
          <div style="display:flex;align-items:baseline;gap:var(--s-1);">
            <span style="font-size:var(--t-4xl);font-weight:800;color:var(--c-white);">€99</span>
            <span style="font-size:var(--t-sm);color:var(--c-text-muted-dark);">/Monat</span>
          </div>
        </div>
        <ul style="display:flex;flex-direction:column;gap:var(--s-3);margin-bottom:var(--s-6);flex:1;">
          <li class="pricing-feature">3 Plattformen</li>
          <li class="pricing-feature">Alle KI-Modelle</li>
          <li class="pricing-feature">Unbegrenzte Posts</li>
          <li class="pricing-feature">WordPress-Integration</li>
          <li class="pricing-feature">Prioritäts-Support</li>
        </ul>
        <a href="<?php echo esc_url( home_url('/kontakt') ); ?>" class="btn btn--primary" style="justify-content:center;">
          Jetzt anfragen
        </a>
      </div>

      <!-- Agentur -->
      <div class="card card--dark" style="display:flex;flex-direction:column;">
        <div style="margin-bottom:var(--s-4);">
          <p style="font-size:var(--t-sm);font-weight:600;color:var(--c-text-muted-dark);margin-bottom:var(--s-2);">Agentur</p>
          <div style="display:flex;align-items:baseline;gap:var(--s-1);">
            <span style="font-size:var(--t-4xl);font-weight:800;color:var(--c-white);">€199</span>
            <span style="font-size:var(--t-sm);color:var(--c-text-muted-dark);">/Monat</span>
          </div>
        </div>
        <ul style="display:flex;flex-direction:column;gap:var(--s-3);margin-bottom:var(--s-6);flex:1;">
          <li class="pricing-feature">Unbegrenzte Plattformen</li>
          <li class="pricing-feature">Multi-Account-Verwaltung</li>
          <li class="pricing-feature">Onboarding-Call inklusive</li>
          <li class="pricing-feature">Dedizierter Support</li>
        </ul>
        <a href="<?php echo esc_url( home_url('/kontakt') ); ?>" class="btn btn--ghost" style="justify-content:center;">
          Jetzt anfragen
        </a>
      </div>

    </div>

    <div style="text-align:center;">
      <a href="<?php echo esc_url( home_url('/preise') ); ?>" style="color:var(--c-indigo);font-weight:600;font-size:var(--t-sm);">
        Alle Preise &amp; Features im Vergleich →
      </a>
      <p style="color:var(--c-text-muted-dark);font-size:var(--t-xs);margin-top:var(--s-3);">
        Monatlich kündbar. Keine Einrichtungsgebühr.
      </p>
    </div>

  </div>
</section>

<!-- ============================================================
     SECTION 9 — FAQ (off-white bg)
     Pure CSS accordion — no JavaScript
     ============================================================ -->
<section class="section section--off">
  <div class="container container--narrow">

    <div class="section__header">
      <div class="t-eyebrow">FAQ</div>
      <h2 class="t-h2" style="margin-top:var(--s-4);">Häufige Fragen.</h2>
    </div>

    <div class="faq">

      <div class="faq__item">
        <input type="checkbox" id="faq1" class="faq__toggle">
        <label class="faq__question" for="faq1">
          Brauche ich technisches Wissen?
          <span class="faq__icon" aria-hidden="true"></span>
        </label>
        <div class="faq__answer">
          <p>Grundkenntnisse mit einem Linux-Server (SSH, Docker) sind hilfreich. Wir unterstützen Sie beim Onboarding und stellen eine Schritt-für-Schritt-Anleitung bereit.</p>
        </div>
      </div>

      <div class="faq__item">
        <input type="checkbox" id="faq2" class="faq__toggle">
        <label class="faq__question" for="faq2">
          Welches KI-Modell wird verwendet?
          <span class="faq__icon" aria-hidden="true"></span>
        </label>
        <div class="faq__answer">
          <p>Sie wählen das Modell selbst — Claude, GPT-4, DeepSeek, Gemini oder andere. Sie können jederzeit wechseln oder ein Fallback-Modell konfigurieren.</p>
        </div>
      </div>

      <div class="faq__item">
        <input type="checkbox" id="faq3" class="faq__toggle">
        <label class="faq__question" for="faq3">
          Wo werden meine Daten gespeichert?
          <span class="faq__icon" aria-hidden="true"></span>
        </label>
        <div class="faq__answer">
          <p>Ausschließlich auf Ihrem eigenen Server. Wir haben keinen Zugriff auf Ihre Inhalte, API-Keys oder Zugangsdaten. Das macht MyContentPilot von Grund auf DSGVO-freundlich.</p>
        </div>
      </div>

      <div class="faq__item">
        <input type="checkbox" id="faq4" class="faq__toggle">
        <label class="faq__question" for="faq4">
          Kann ich jederzeit kündigen?
          <span class="faq__icon" aria-hidden="true"></span>
        </label>
        <div class="faq__answer">
          <p>Ja — monatlich kündbar, keine Mindestlaufzeit. Bei jährlicher Zahlung erhalten Sie zwei Monate gratis.</p>
        </div>
      </div>

      <div class="faq__item">
        <input type="checkbox" id="faq5" class="faq__toggle">
        <label class="faq__question" for="faq5">
          Welche Plattformen werden unterstützt?
          <span class="faq__icon" aria-hidden="true"></span>
        </label>
        <div class="faq__answer">
          <p>Aktuell Facebook, Instagram, LinkedIn und WordPress. Weitere Plattformen sind auf Anfrage möglich.</p>
        </div>
      </div>

      <div class="faq__item">
        <input type="checkbox" id="faq6" class="faq__toggle">
        <label class="faq__question" for="faq6">
          Was kostet der Einstieg?
          <span class="faq__icon" aria-hidden="true"></span>
        </label>
        <div class="faq__answer">
          <p>Der Starter-Plan beginnt bei €49/Monat, inklusive Setup-Unterstützung per E-Mail. Keine versteckten Kosten, keine Einrichtungsgebühr.</p>
        </div>
      </div>

    </div><!-- /.faq -->
  </div>
</section>

<!-- ============================================================
     SECTION 10 — FINAL CTA (indigo gradient)
     ============================================================ -->
<section class="section" style="background:linear-gradient(135deg,#3A56D4 0%,#4F6EF7 50%,#6B8AFB 100%);">
  <div class="container container--narrow" style="text-align:center;">

    <h2 class="t-h2" style="color:#fff;margin-bottom:var(--s-4);">
      Bereit, Ihren Content zu automatisieren?
    </h2>
    <p style="font-size:var(--t-lg);color:rgba(255,255,255,0.82);margin-bottom:var(--s-8);line-height:1.6;">
      Vereinbaren Sie eine kostenlose Demo und sehen Sie<br>MyContentPilot live in Aktion.
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
