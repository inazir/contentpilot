<?php
/**
 * MyContentPilot.de — Contact Page
 * Template: page-kontakt.php
 */

// Read URL params for pre-selection and status
$selected_plan   = isset($_GET['plan'])       ? sanitize_text_field($_GET['plan'])   : '';
$form_status     = isset($_GET['status'])     ? sanitize_text_field($_GET['status']) : '';

get_header(); ?>

<!-- ============================================================
     HERO — compact, dark
     ============================================================ -->
<section class="section--dark" style="padding:var(--s-20) 0 var(--s-16);text-align:center;">
  <div class="container container--narrow">
    <div class="t-eyebrow t-eyebrow--dark" style="display:inline-flex;margin-bottom:var(--s-4);">Kontakt</div>
    <h1 class="t-display" style="color:var(--c-white);font-size:var(--t-4xl);margin-bottom:var(--s-4);">
      Sprechen wir über<br>
      <span class="t-accent">Ihren Anwendungsfall.</span>
    </h1>
    <p class="t-lead">
      Demo anfragen, Fragen stellen oder direkt loslegen —
      wir antworten innerhalb von 24 Stunden.
    </p>
  </div>
</section>

<!-- ============================================================
     FORM + CONTACT INFO — two column layout
     ============================================================ -->
<section class="section">
  <div class="container">
    <div class="contact-layout">

      <!-- ── LEFT: Contact form ── -->
      <div class="contact-form-col">

        <?php if ( $form_status === 'success' ) : ?>
          <div class="form-notice form-notice--success" role="alert">
            <span class="form-notice__icon" aria-hidden="true">✓</span>
            <div>
              <strong>Nachricht erhalten.</strong>
              Wir melden uns innerhalb von 24 Stunden bei Ihnen.
            </div>
          </div>
        <?php elseif ( $form_status === 'error' ) : ?>
          <div class="form-notice form-notice--error" role="alert">
            <span class="form-notice__icon" aria-hidden="true">!</span>
            <div>
              <strong>Bitte überprüfen Sie Ihre Eingaben.</strong>
              Alle Pflichtfelder müssen ausgefüllt sein.
            </div>
          </div>
        <?php endif; ?>

        <form
          method="POST"
          action="<?php echo esc_url( home_url('/') ); ?>"
          class="contact-form"
          novalidate
        >
          <?php wp_nonce_field( 'mcp_contact_submit', 'mcp_contact_nonce' ); ?>
          <input type="hidden" name="mcp_contact" value="1">

          <!-- Honeypot — leave empty -->
          <div style="display:none;" aria-hidden="true">
            <input type="text" name="website" tabindex="-1" autocomplete="off">
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="contact-name">
                Name <span class="form-required" aria-label="Pflichtfeld">*</span>
              </label>
              <input
                type="text"
                id="contact-name"
                name="name"
                placeholder="Max Mustermann"
                required
                autocomplete="name"
                value="<?php echo esc_attr( $_POST['name'] ?? '' ); ?>"
              >
            </div>
            <div class="form-group">
              <label for="contact-email">
                E-Mail <span class="form-required" aria-label="Pflichtfeld">*</span>
              </label>
              <input
                type="email"
                id="contact-email"
                name="email"
                placeholder="max@unternehmen.de"
                required
                autocomplete="email"
                value="<?php echo esc_attr( $_POST['email'] ?? '' ); ?>"
              >
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="contact-company">Unternehmen <span style="color:var(--c-text-muted);font-weight:400;">(optional)</span></label>
              <input
                type="text"
                id="contact-company"
                name="company"
                placeholder="Muster GmbH"
                autocomplete="organization"
                value="<?php echo esc_attr( $_POST['company'] ?? '' ); ?>"
              >
            </div>
            <div class="form-group">
              <label for="contact-plan">Interessiert an</label>
              <select id="contact-plan" name="plan">
                <option value="" <?php selected( $selected_plan, '' ); ?>>Bitte wählen…</option>
                <option value="starter"  <?php selected( $selected_plan, 'starter'  ); ?>>Starter — €49/Monat</option>
                <option value="pro"      <?php selected( $selected_plan, 'pro'      ); ?>>Pro — €99/Monat</option>
                <option value="agentur"  <?php selected( $selected_plan, 'agentur'  ); ?>>Agentur — €199/Monat</option>
                <option value="demo"     <?php selected( $selected_plan, 'demo'     ); ?>>Erst eine Demo</option>
                <option value="custom"   <?php selected( $selected_plan, 'custom'   ); ?>>Individuelle Lösung</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label for="contact-message">
              Nachricht <span class="form-required" aria-label="Pflichtfeld">*</span>
            </label>
            <textarea
              id="contact-message"
              name="message"
              placeholder="Beschreiben Sie kurz Ihren Anwendungsfall — welche Plattformen, wie viele Accounts, welche Inhalte…"
              required
              rows="6"
            ><?php echo esc_textarea( $_POST['message'] ?? '' ); ?></textarea>
          </div>

          <div class="form-check">
            <input type="checkbox" id="contact-dsgvo" name="dsgvo" required>
            <label for="contact-dsgvo">
              Ich habe die
              <a href="<?php echo esc_url( home_url('/datenschutz') ); ?>" target="_blank" style="color:var(--c-indigo);">Datenschutzerklärung</a>
              gelesen und stimme der Verarbeitung meiner Daten zur Bearbeitung meiner Anfrage zu.
              <span class="form-required" aria-label="Pflichtfeld">*</span>
            </label>
          </div>

          <button type="submit" class="btn btn--primary btn--lg" style="width:100%;justify-content:center;margin-top:var(--s-2);">
            Nachricht senden
          </button>

          <p style="font-size:var(--t-xs);color:var(--c-text-muted);margin-top:var(--s-3);text-align:center;">
            * Pflichtfelder. Ihre Daten werden ausschließlich zur Bearbeitung Ihrer Anfrage verwendet.
          </p>

        </form>
      </div><!-- /.contact-form-col -->

      <!-- ── RIGHT: Contact info ── -->
      <div class="contact-info-col">

        <!-- Response time -->
        <div class="contact-info-card">
          <div class="contact-info-card__icon" aria-hidden="true">⏱️</div>
          <div>
            <h3>Antwortzeit</h3>
            <p>Wir antworten auf alle Anfragen <strong>innerhalb von 24 Stunden</strong> — werktags meist deutlich schneller.</p>
          </div>
        </div>

        <!-- Email -->
        <div class="contact-info-card">
          <div class="contact-info-card__icon" aria-hidden="true">✉️</div>
          <div>
            <h3>E-Mail</h3>
            <p>
              <a href="#" class="mcp-email contact-email-link" data-u="info" data-d="mycontentpilot.de">
                info [at] mycontentpilot.de
              </a>
            </p>
          </div>
        </div>

        <!-- WhatsApp -->
        <div class="contact-info-card">
          <div class="contact-info-card__icon" aria-hidden="true">💬</div>
          <div>
            <h3>WhatsApp</h3>
            <p>Für schnelle Fragen direkt per WhatsApp erreichbar.</p>
            <a
              href="https://wa.me/4915254113795"
              target="_blank"
              rel="noopener noreferrer"
              class="btn btn--ghost-dark"
              style="margin-top:var(--s-3);display:inline-flex;"
            >
              Auf WhatsApp schreiben
            </a>
          </div>
        </div>

        <!-- Address -->
        <div class="contact-info-card">
          <div class="contact-info-card__icon" aria-hidden="true">📍</div>
          <div>
            <h3>Adresse</h3>
            <address style="font-style:normal;font-size:var(--t-sm);color:var(--c-text-secondary);line-height:1.8;">
              Iqbal Nazir<br>
              Anemonenstr. 5/1<br>
              70771 Leinfelden-Echterdingen<br>
              Deutschland
            </address>
          </div>
        </div>

      </div><!-- /.contact-info-col -->

    </div><!-- /.contact-layout -->
  </div>
</section>

<!-- ============================================================
     CALENDLY CTA BLOCK
     ============================================================ -->
<section class="section section--off">
  <div class="container container--narrow">
    <div class="calendly-cta">
      <div class="calendly-cta__icon" aria-hidden="true">📅</div>
      <div class="calendly-cta__body">
        <h2 class="t-h2" style="font-size:var(--t-2xl);">Lieber direkt einen Termin buchen?</h2>
        <p style="color:var(--c-text-secondary);margin-top:var(--s-2);">
          30-minütige Demo — kostenlos, unverbindlich, individuell auf Ihren Anwendungsfall abgestimmt.
        </p>
      </div>
      <a
        href="https://calendly.com/mycontentpilot/30min"
        target="_blank"
        rel="noopener noreferrer"
        class="btn btn--primary btn--lg"
        style="flex-shrink:0;"
      >
        Termin wählen
      </a>
    </div>
  </div>
</section>

<?php get_footer(); ?>
