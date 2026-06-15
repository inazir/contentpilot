<?php
/**
 * MyContentPilot — index.php
 * WordPress fallback template.
 * All real pages are handled by dedicated template files
 * via the slug router in functions.php.
 */
get_header(); ?>

<section class="section">
  <div class="container container--narrow" style="text-align:center;padding-top:var(--s-20);">
    <div class="t-eyebrow" style="margin-bottom:var(--s-4);">404</div>
    <h1 class="t-h2" style="margin-bottom:var(--s-4);">Seite nicht gefunden.</h1>
    <p class="t-lead" style="margin-bottom:var(--s-8);">
      Die aufgerufene Seite existiert nicht oder wurde verschoben.
    </p>
    <a href="<?php echo esc_url( home_url('/') ); ?>" class="btn btn--primary btn--lg">
      Zur Startseite
    </a>
  </div>
</section>

<?php get_footer(); ?>
