<?php
/**
 * MyContentPilot.de — Pricing Page
 * Template: page-preise.php
 */
get_header(); ?>

<!-- ============================================================
     HERO — small, centered
     ============================================================ -->
<section class="section--dark" style="padding:var(--s-20) 0 var(--s-16);">
  <div class="container container--narrow" style="text-align:center;">
    <div class="t-eyebrow t-eyebrow--dark" style="display:inline-flex;margin-bottom:var(--s-4);">Preise</div>
    <h1 class="t-display" style="color:var(--c-white);font-size:var(--t-4xl);margin-bottom:var(--s-4);">
      Transparent. Fair. <span class="t-accent">Skalierbar.</span>
    </h1>
    <p class="t-lead" style="margin-bottom:var(--s-6);">
      Monatlich kündbar. Keine Einrichtungsgebühr. Keine versteckten Kosten.
    </p>
    <p style="font-size:var(--t-sm);color:var(--c-text-muted-dark);">
      Jährliche Zahlung? Sie sparen <strong style="color:var(--c-mint);">2 Monate</strong>.
    </p>
  </div>
</section>

<!-- ============================================================
     PRICING TOGGLE + CARDS
     Pure CSS radio button trick — zero JS
     ============================================================ -->
<section class="section section--off" style="padding-top:var(--s-12);">
  <div class="container">

    <!-- Radio inputs (hidden, drive the toggle) -->
    <input type="radio" name="billing" id="bill-monthly" class="billing-radio" checked>
    <input type="radio" name="billing" id="bill-annual"  class="billing-radio">

    <!-- Toggle UI -->
    <div class="billing-toggle" role="group" aria-label="Abrechnungszeitraum wählen">
      <label for="bill-monthly" class="billing-toggle__option">Monatlich</label>
      <label for="bill-annual"  class="billing-toggle__option">
        Jährlich
        <span class="billing-toggle__save">2 Monate gratis</span>
      </label>
    </div>

    <!-- Pricing cards -->
    <div class="grid-3 pricing-cards" style="margin-top:var(--s-10);align-items:start;">

      <!-- ── Starter ── -->
      <div class="card pricing-card">
        <p class="pricing-card__name">Starter</p>

        <div class="pricing-card__price pricing-card__price--monthly">
          <span class="pricing-card__amount">€49</span>
          <span class="pricing-card__period">/Monat</span>
        </div>
        <div class="pricing-card__price pricing-card__price--annual">
          <span class="pricing-card__amount">€490</span>
          <span class="pricing-card__period">/Jahr</span>
          <span class="pricing-card__saving">= €40,83/Monat</span>
        </div>

        <p class="pricing-card__desc">Ideal für Einzelpersonen, die ihren ersten Kanal automatisieren möchten.</p>

        <ul class="pricing-card__features">
          <li class="pricing-feature">1 Plattform</li>
          <li class="pricing-feature">1 KI-Modell wählbar</li>
          <li class="pricing-feature">Bis 30 Posts/Monat</li>
          <li class="pricing-feature">Cron-Scheduling</li>
          <li class="pricing-feature">Duplikat-Erkennung</li>
          <li class="pricing-feature">Setup-Anleitung inklusive</li>
          <li class="pricing-feature">E-Mail-Support</li>
        </ul>

        <a href="<?php echo esc_url( home_url('/kontakt') ); ?>?plan=starter" class="btn btn--ghost-dark" style="justify-content:center;width:100%;margin-top:auto;">
          Jetzt anfragen
        </a>
      </div>

      <!-- ── Pro (highlighted) ── -->
      <div class="card pricing-card pricing-card--featured">
        <div class="pricing-card__badge">⭐ Beliebteste Wahl</div>
        <p class="pricing-card__name">Pro</p>

        <div class="pricing-card__price pricing-card__price--monthly">
          <span class="pricing-card__amount">€99</span>
          <span class="pricing-card__period">/Monat</span>
        </div>
        <div class="pricing-card__price pricing-card__price--annual">
          <span class="pricing-card__amount">€990</span>
          <span class="pricing-card__period">/Jahr</span>
          <span class="pricing-card__saving">= €82,50/Monat</span>
        </div>

        <p class="pricing-card__desc">Für Selbstständige und kleine Teams mit mehreren Plattformen.</p>

        <ul class="pricing-card__features">
          <li class="pricing-feature">3 Plattformen</li>
          <li class="pricing-feature">Alle KI-Modelle</li>
          <li class="pricing-feature">Unbegrenzte Posts</li>
          <li class="pricing-feature">WordPress-Integration</li>
          <li class="pricing-feature">Cron-Scheduling</li>
          <li class="pricing-feature">Duplikat-Erkennung</li>
          <li class="pricing-feature">Fallback-KI konfigurierbar</li>
          <li class="pricing-feature">Prioritäts-Support</li>
        </ul>

        <a href="<?php echo esc_url( home_url('/kontakt') ); ?>?plan=pro" class="btn btn--primary" style="justify-content:center;width:100%;margin-top:auto;">
          Jetzt anfragen
        </a>
      </div>

      <!-- ── Agentur ── -->
      <div class="card pricing-card">
        <p class="pricing-card__name">Agentur</p>

        <div class="pricing-card__price pricing-card__price--monthly">
          <span class="pricing-card__amount">€199</span>
          <span class="pricing-card__period">/Monat</span>
        </div>
        <div class="pricing-card__price pricing-card__price--annual">
          <span class="pricing-card__amount">€1.990</span>
          <span class="pricing-card__period">/Jahr</span>
          <span class="pricing-card__saving">= €165,83/Monat</span>
        </div>

        <p class="pricing-card__desc">Für Agenturen mit mehreren Kunden, Accounts und Plattformen.</p>

        <ul class="pricing-card__features">
          <li class="pricing-feature">Unbegrenzte Plattformen</li>
          <li class="pricing-feature">Alle KI-Modelle</li>
          <li class="pricing-feature">Unbegrenzte Posts</li>
          <li class="pricing-feature">Multi-Account-Verwaltung</li>
          <li class="pricing-feature">WordPress-Integration</li>
          <li class="pricing-feature">Duplikat-Erkennung</li>
          <li class="pricing-feature">Fallback-KI konfigurierbar</li>
          <li class="pricing-feature">Onboarding-Call inklusive</li>
          <li class="pricing-feature">Dedizierter Support</li>
        </ul>

        <a href="<?php echo esc_url( home_url('/kontakt') ); ?>?plan=agentur" class="btn btn--ghost-dark" style="justify-content:center;width:100%;margin-top:auto;">
          Jetzt anfragen
        </a>
      </div>

    </div><!-- /.pricing-cards -->

    <p style="text-align:center;font-size:var(--t-xs);color:var(--c-text-muted);margin-top:var(--s-6);">
      Alle Preise zzgl. gesetzlicher MwSt. · Monatlich kündbar · Keine Einrichtungsgebühr
    </p>

  </div>
</section>

<!-- ============================================================
     FEATURE COMPARISON MATRIX
     ============================================================ -->
<section class="section">
  <div class="container">

    <div class="section__header">
      <div class="t-eyebrow">Vergleich</div>
      <h2 class="t-h2" style="margin-top:var(--s-4);">Was ist in jedem Plan enthalten?</h2>
    </div>

    <div class="compare-wrap">
      <table class="compare-table">
        <thead>
          <tr>
            <th class="compare-table__feature-col">Funktion</th>
            <th>Starter<br><span>€49/Monat</span></th>
            <th class="compare-table__featured">Pro<br><span>€99/Monat</span></th>
            <th>Agentur<br><span>€199/Monat</span></th>
          </tr>
        </thead>
        <tbody>
          <tr class="compare-table__group">
            <td colspan="4">Plattformen &amp; Publishing</td>
          </tr>
          <tr>
            <td>Anzahl Plattformen</td>
            <td>1</td>
            <td class="compare-table__featured">3</td>
            <td>Unbegrenzt</td>
          </tr>
          <tr>
            <td>Facebook</td>
            <td><span class="cmp-yes" aria-label="Ja">✓</span></td>
            <td class="compare-table__featured"><span class="cmp-yes" aria-label="Ja">✓</span></td>
            <td><span class="cmp-yes" aria-label="Ja">✓</span></td>
          </tr>
          <tr>
            <td>Instagram</td>
            <td><span class="cmp-yes" aria-label="Ja">✓</span></td>
            <td class="compare-table__featured"><span class="cmp-yes" aria-label="Ja">✓</span></td>
            <td><span class="cmp-yes" aria-label="Ja">✓</span></td>
          </tr>
          <tr>
            <td>WordPress</td>
            <td><span class="cmp-no" aria-label="Nein">—</span></td>
            <td class="compare-table__featured"><span class="cmp-yes" aria-label="Ja">✓</span></td>
            <td><span class="cmp-yes" aria-label="Ja">✓</span></td>
          </tr>
          <tr>
            <td>Multi-Account-Verwaltung</td>
            <td><span class="cmp-no" aria-label="Nein">—</span></td>
            <td class="compare-table__featured"><span class="cmp-no" aria-label="Nein">—</span></td>
            <td><span class="cmp-yes" aria-label="Ja">✓</span></td>
          </tr>

          <tr class="compare-table__group">
            <td colspan="4">Content-Generierung</td>
          </tr>
          <tr>
            <td>Posts pro Monat</td>
            <td>Bis 30</td>
            <td class="compare-table__featured">Unbegrenzt</td>
            <td>Unbegrenzt</td>
          </tr>
          <tr>
            <td>KI-Modelle</td>
            <td>1 wählbar</td>
            <td class="compare-table__featured">Alle</td>
            <td>Alle</td>
          </tr>
          <tr>
            <td>Fallback-KI konfigurierbar</td>
            <td><span class="cmp-no" aria-label="Nein">—</span></td>
            <td class="compare-table__featured"><span class="cmp-yes" aria-label="Ja">✓</span></td>
            <td><span class="cmp-yes" aria-label="Ja">✓</span></td>
          </tr>
          <tr>
            <td>Duplikat-Erkennung</td>
            <td><span class="cmp-yes" aria-label="Ja">✓</span></td>
            <td class="compare-table__featured"><span class="cmp-yes" aria-label="Ja">✓</span></td>
            <td><span class="cmp-yes" aria-label="Ja">✓</span></td>
          </tr>

          <tr class="compare-table__group">
            <td colspan="4">Infrastruktur</td>
          </tr>
          <tr>
            <td>Selbst-gehostet (eigener Server)</td>
            <td><span class="cmp-yes" aria-label="Ja">✓</span></td>
            <td class="compare-table__featured"><span class="cmp-yes" aria-label="Ja">✓</span></td>
            <td><span class="cmp-yes" aria-label="Ja">✓</span></td>
          </tr>
          <tr>
            <td>Docker-basiert</td>
            <td><span class="cmp-yes" aria-label="Ja">✓</span></td>
            <td class="compare-table__featured"><span class="cmp-yes" aria-label="Ja">✓</span></td>
            <td><span class="cmp-yes" aria-label="Ja">✓</span></td>
          </tr>
          <tr>
            <td>Cron-Scheduling</td>
            <td><span class="cmp-yes" aria-label="Ja">✓</span></td>
            <td class="compare-table__featured"><span class="cmp-yes" aria-label="Ja">✓</span></td>
            <td><span class="cmp-yes" aria-label="Ja">✓</span></td>
          </tr>

          <tr class="compare-table__group">
            <td colspan="4">Support &amp; Onboarding</td>
          </tr>
          <tr>
            <td>Setup-Anleitung</td>
            <td><span class="cmp-yes" aria-label="Ja">✓</span></td>
            <td class="compare-table__featured"><span class="cmp-yes" aria-label="Ja">✓</span></td>
            <td><span class="cmp-yes" aria-label="Ja">✓</span></td>
          </tr>
          <tr>
            <td>Onboarding-Call</td>
            <td><span class="cmp-no" aria-label="Nein">—</span></td>
            <td class="compare-table__featured"><span class="cmp-no" aria-label="Nein">—</span></td>
            <td><span class="cmp-yes" aria-label="Ja">✓</span></td>
          </tr>
          <tr>
            <td>Support-Kanal</td>
            <td>E-Mail</td>
            <td class="compare-table__featured">Priorität</td>
            <td>Dediziert</td>
          </tr>
        </tbody>
      </table>
    </div><!-- /.compare-wrap -->

  </div>
</section>

<!-- ============================================================
     BILLING FAQ
     ============================================================ -->
<section class="section section--off">
  <div class="container container--narrow">

    <div class="section__header">
      <div class="t-eyebrow">Fragen zur Abrechnung</div>
      <h2 class="t-h2" style="margin-top:var(--s-4);">Alles zur Zahlung &amp; Kündigung.</h2>
    </div>

    <div class="faq">

      <div class="faq__item">
        <input type="checkbox" id="bfaq1" class="faq__toggle">
        <label class="faq__question" for="bfaq1">
          Wie kann ich kündigen?
          <span class="faq__icon" aria-hidden="true"></span>
        </label>
        <div class="faq__answer">
          <p>Sie können jederzeit zum Ende des Abrechnungszeitraums kündigen — ohne Angabe von Gründen. Senden Sie einfach eine E-Mail an info@mycontentpilot.de mit Ihrer Kündigungsanfrage.</p>
        </div>
      </div>

      <div class="faq__item">
        <input type="checkbox" id="bfaq2" class="faq__toggle">
        <label class="faq__question" for="bfaq2">
          Wie erhalte ich meine Rechnung?
          <span class="faq__icon" aria-hidden="true"></span>
        </label>
        <div class="faq__answer">
          <p>Nach jeder Zahlung erhalten Sie eine Rechnung per E-Mail an die bei der Bestellung angegebene Adresse. Rechnungen sind DSGVO-konform und enthalten alle steuerlich relevanten Angaben.</p>
        </div>
      </div>

      <div class="faq__item">
        <input type="checkbox" id="bfaq3" class="faq__toggle">
        <label class="faq__question" for="bfaq3">
          Kann ich meinen Plan upgraden oder downgraden?
          <span class="faq__icon" aria-hidden="true"></span>
        </label>
        <div class="faq__answer">
          <p>Ja. Ein Upgrade ist jederzeit möglich und wird sofort wirksam. Ein Downgrade gilt ab dem nächsten Abrechnungszeitraum. Kontaktieren Sie uns einfach per E-Mail.</p>
        </div>
      </div>

      <div class="faq__item">
        <input type="checkbox" id="bfaq4" class="faq__toggle">
        <label class="faq__question" for="bfaq4">
          Gibt es eine Rückerstattung bei jährlicher Zahlung?
          <span class="faq__icon" aria-hidden="true"></span>
        </label>
        <div class="faq__answer">
          <p>Bei Kündigung eines Jahresplans erstatten wir die verbleibenden vollen Monate anteilig zurück. Angefangene Monate werden nicht erstattet. Die Rückerstattung erfolgt auf dem ursprünglichen Zahlungsweg.</p>
        </div>
      </div>

      <div class="faq__item">
        <input type="checkbox" id="bfaq5" class="faq__toggle">
        <label class="faq__question" for="bfaq5">
          Welche Zahlungsarten werden akzeptiert?
          <span class="faq__icon" aria-hidden="true"></span>
        </label>
        <div class="faq__answer">
          <p>Aktuell akzeptieren wir Zahlung per Überweisung (SEPA) und PayPal. Weitere Zahlungsarten folgen. Bei Fragen zur Abrechnung kontaktieren Sie uns direkt.</p>
        </div>
      </div>

    </div>
  </div>
</section>

<!-- ============================================================
     BOTTOM CTA
     ============================================================ -->
<section class="section" style="background:linear-gradient(135deg,#3A56D4 0%,#4F6EF7 50%,#6B8AFB 100%);">
  <div class="container container--narrow" style="text-align:center;">
    <h2 class="t-h2" style="color:#fff;margin-bottom:var(--s-4);">
      Noch unsicher? Kein Problem.
    </h2>
    <p style="font-size:var(--t-lg);color:rgba(255,255,255,0.82);margin-bottom:var(--s-8);line-height:1.6;">
      Vereinbaren Sie eine kostenlose Demo — wir zeigen Ihnen,<br>wie MyContentPilot für Ihren Anwendungsfall funktioniert.
    </p>
    <div style="display:flex;align-items:center;justify-content:center;gap:var(--s-4);flex-wrap:wrap;">
      <a href="<?php echo esc_url( home_url('/kontakt') ); ?>"
         class="btn btn--lg"
         style="background:#fff;color:var(--c-indigo);font-weight:700;box-shadow:0 4px 20px rgba(0,0,0,0.15);">
        Demo anfragen
      </a>
      <a href="<?php echo esc_url( home_url('/funktionen') ); ?>" class="btn btn--ghost btn--lg">
        Funktionen ansehen
      </a>
    </div>
  </div>
</section>

<?php get_footer(); ?>
