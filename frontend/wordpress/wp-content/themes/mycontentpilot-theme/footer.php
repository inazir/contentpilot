</main><!-- /#main-content -->

<!-- ============================================================
     SITE FOOTER
     ============================================================ -->
<footer class="site-footer" role="contentinfo">
  <div class="container">
    <div class="site-footer__grid">

      <!-- Column 1: Brand -->
      <div class="footer-brand">
        <div class="footer-brand__logo">
          <div class="site-logo__mark" aria-hidden="true">
            <svg viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M3 9 L7 13 L15 5"/>
              <circle cx="9" cy="9" r="8" stroke-width="1.5"/>
            </svg>
          </div>
          <span>MyContent<span style="color:var(--c-indigo)">Pilot</span></span>
        </div>

        <p>
          Die Automatisierungsplattform für Ihren gesamten Content-Workflow —
          auf Ihrem eigenen Server, mit jedem KI-Modell, für jede Plattform.
        </p>

        <!-- Social Icons -->
        <div class="footer-social" aria-label="Social Media">
          <a href="https://linkedin.com" target="_blank" rel="noopener noreferrer" aria-label="LinkedIn">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
              <path d="M16 8a6 6 0 016 6v7h-4v-7a2 2 0 00-2-2 2 2 0 00-2 2v7h-4v-7a6 6 0 016-6zM2 9h4v12H2z"/>
              <circle cx="4" cy="4" r="2"/>
            </svg>
          </a>
          <a href="https://facebook.com" target="_blank" rel="noopener noreferrer" aria-label="Facebook">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
              <path d="M18 2h-3a5 5 0 00-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 011-1h3z"/>
            </svg>
          </a>
          <a href="https://instagram.com" target="_blank" rel="noopener noreferrer" aria-label="Instagram">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <rect x="2" y="2" width="20" height="20" rx="5" ry="5"/>
              <circle cx="12" cy="12" r="4"/>
              <circle cx="17.5" cy="6.5" r="1" fill="currentColor" stroke="none"/>
            </svg>
          </a>
        </div>

        <!-- Newsletter -->
        <div class="footer-newsletter">
          <p>Updates & neue Plattformen — kein Spam.</p>
          <div class="footer-newsletter__form">
            <label for="footer-email" class="sr-only">E-Mail-Adresse</label>
            <input
              type="email"
              id="footer-email"
              name="email"
              placeholder="ihre@email.de"
              autocomplete="email"
            >
            <button type="button" aria-label="Newsletter abonnieren">OK</button>
          </div>
        </div>
      </div><!-- /.footer-brand -->

      <!-- Column 2: Produkt -->
      <div class="footer-col">
        <h4>Produkt</h4>
        <ul>
          <li><a href="<?php echo esc_url( home_url('/funktionen') ); ?>">Funktionen</a></li>
          <li><a href="<?php echo esc_url( home_url('/preise') ); ?>">Preise</a></li>
          <li><a href="<?php echo esc_url( home_url('/kontakt') ); ?>">Demo anfragen</a></li>
          <li><a href="<?php echo esc_url( home_url('/funktionen') ); ?>#plattformen">Plattformen</a></li>
          <li><a href="<?php echo esc_url( home_url('/funktionen') ); ?>#ki-modelle">KI-Modelle</a></li>
        </ul>
      </div>

      <!-- Column 3: Rechtliches -->
      <div class="footer-col">
        <h4>Rechtliches</h4>
        <ul>
          <li><a href="<?php echo esc_url( home_url('/impressum') ); ?>">Impressum</a></li>
          <li><a href="<?php echo esc_url( home_url('/datenschutz') ); ?>">Datenschutz</a></li>
          <li><a href="<?php echo esc_url( home_url('/agb') ); ?>">AGB</a></li>
        </ul>
      </div>

      <!-- Column 4: Kontakt -->
      <div class="footer-col">
        <h4>Kontakt</h4>
        <ul>
          <li>
            <a href="#" class="mcp-email" data-u="info" data-d="mycontentpilot.de">
              <!-- obfuscated — filled by JS -->
              info [at] mycontentpilot.de
            </a>
          </li>
          <li>
            <a href="https://wa.me/4915254113795" target="_blank" rel="noopener noreferrer"
               style="color:var(--c-mint); font-size:var(--t-sm);">
              💬 Auf WhatsApp schreiben
            </a>
          </li>
        </ul>
      </div>

    </div><!-- /.site-footer__grid -->

    <!-- Bottom bar -->
    <div class="site-footer__bottom">
      <span>&copy; <?php echo date('Y'); ?> MyContentPilot. Alle Rechte vorbehalten.</span>
      <nav class="footer-legal" aria-label="Rechtliche Links">
        <a href="<?php echo esc_url( home_url('/impressum') ); ?>">Impressum</a>
        <a href="<?php echo esc_url( home_url('/datenschutz') ); ?>">Datenschutz</a>
        <a href="<?php echo esc_url( home_url('/agb') ); ?>">AGB</a>
      </nav>
    </div>

  </div><!-- /.container -->
</footer><!-- /.site-footer -->

<!-- ============================================================
     WHATSAPP FLOATING BUTTON
     ============================================================ -->
<a
  href="https://wa.me/4915254113795"
  target="_blank"
  rel="noopener noreferrer"
  class="whatsapp-float"
  aria-label="Auf WhatsApp kontaktieren"
>
  <!-- WhatsApp SVG logo -->
  <svg viewBox="0 0 24 24" aria-hidden="true">
    <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
  </svg>
  <span class="whatsapp-float__label">WhatsApp</span>
</a>

<!-- ============================================================
     FOOTER JS — email obfuscation
     ============================================================ -->
<script>
(function () {
  document.querySelectorAll('.mcp-email').forEach(function (el) {
    var u = el.getAttribute('data-u');
    var d = el.getAttribute('data-d');
    if (u && d) {
      var addr = u + '@' + d;
      el.href = 'mailto:' + addr;
      el.textContent = addr;
    }
  });
})();
</script>

<?php wp_footer(); ?>
</body>
</html>
