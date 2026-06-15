<!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
  <meta charset="<?php bloginfo('charset'); ?>">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="theme-color" content="#0D1117">
  <?php wp_head(); ?>
</head>
<body <?php body_class(); ?>>
<?php wp_body_open(); ?>

<!-- ============================================================
     SITE HEADER
     ============================================================ -->
<header class="site-header" id="site-header" role="banner">
  <div class="container">
    <div class="site-header__inner">

      <!-- Logo -->
      <a href="<?php echo esc_url( home_url('/') ); ?>" class="site-logo" aria-label="MyContentPilot – Startseite">
        <div class="site-logo__mark" aria-hidden="true">
          <svg viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M3 9 L7 13 L15 5"/>
            <circle cx="9" cy="9" r="8" stroke-width="1.5"/>
          </svg>
        </div>
        <span class="site-logo__text">MyContent<span>Pilot</span></span>
      </a>

      <!-- Desktop Navigation -->
      <nav class="site-nav" role="navigation" aria-label="Hauptnavigation">
        <a href="<?php echo esc_url( home_url('/funktionen') ); ?>"
           <?php if ( is_page('funktionen') ) echo 'class="active" aria-current="page"'; ?>>
          Funktionen
        </a>
        <a href="<?php echo esc_url( home_url('/preise') ); ?>"
           <?php if ( is_page('preise') ) echo 'class="active" aria-current="page"'; ?>>
          Preise
        </a>
        <a href="<?php echo esc_url( home_url('/kontakt') ); ?>"
           <?php if ( is_page('kontakt') ) echo 'class="active" aria-current="page"'; ?>>
          Kontakt
        </a>
      </nav>

      <!-- Desktop CTAs -->
      <div class="site-header__cta">
        <a href="<?php echo esc_url( home_url('/kontakt') ); ?>" class="btn btn--ghost-dark">
          Demo anfragen
        </a>
        <a href="<?php echo esc_url( home_url('/preise') ); ?>" class="btn btn--primary">
          Jetzt starten
        </a>
      </div>

      <!-- Mobile Hamburger -->
      <button class="nav-toggle" id="nav-toggle" aria-controls="mobile-nav" aria-expanded="false" aria-label="Menü öffnen">
        <span></span>
        <span></span>
        <span></span>
      </button>

    </div><!-- /.site-header__inner -->
  </div><!-- /.container -->
</header><!-- /.site-header -->

<!-- Mobile Navigation Drawer -->
<div class="mobile-nav" id="mobile-nav" role="navigation" aria-label="Mobile Navigation" aria-hidden="true">
  <a href="<?php echo esc_url( home_url('/funktionen') ); ?>">Funktionen</a>
  <a href="<?php echo esc_url( home_url('/preise') ); ?>">Preise</a>
  <a href="<?php echo esc_url( home_url('/kontakt') ); ?>">Kontakt</a>
  <div class="mobile-nav__cta">
    <a href="<?php echo esc_url( home_url('/kontakt') ); ?>" class="btn btn--ghost-dark" style="justify-content:center;">Demo anfragen</a>
    <a href="<?php echo esc_url( home_url('/preise') ); ?>" class="btn btn--primary" style="justify-content:center;">Jetzt starten</a>
  </div>
</div>

<!-- ============================================================
     INLINE JS — Header scroll state + mobile nav toggle
     No dependencies, no library, ~30 lines
     ============================================================ -->
<script>
(function () {
  'use strict';

  var header  = document.getElementById('site-header');
  var toggle  = document.getElementById('nav-toggle');
  var mobileNav = document.getElementById('mobile-nav');

  /* Scroll shadow on header */
  function onScroll() {
    if (window.scrollY > 8) {
      header.classList.add('scrolled');
    } else {
      header.classList.remove('scrolled');
    }
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* Hamburger toggle */
  function toggleNav(open) {
    toggle.classList.toggle('open', open);
    mobileNav.classList.toggle('open', open);
    toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    mobileNav.setAttribute('aria-hidden', open ? 'false' : 'true');
    document.body.style.overflow = open ? 'hidden' : '';
  }

  toggle.addEventListener('click', function () {
    var isOpen = mobileNav.classList.contains('open');
    toggleNav(!isOpen);
  });

  /* Close on outside click */
  document.addEventListener('click', function (e) {
    if (
      mobileNav.classList.contains('open') &&
      !mobileNav.contains(e.target) &&
      !toggle.contains(e.target)
    ) {
      toggleNav(false);
    }
  });

  /* Close on Escape */
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && mobileNav.classList.contains('open')) {
      toggleNav(false);
      toggle.focus();
    }
  });

  /* Close nav when a link is clicked (SPA-like navigation) */
  mobileNav.querySelectorAll('a').forEach(function (link) {
    link.addEventListener('click', function () { toggleNav(false); });
  });
})();
</script>

<!-- Page content begins -->
<main id="main-content" tabindex="-1">
