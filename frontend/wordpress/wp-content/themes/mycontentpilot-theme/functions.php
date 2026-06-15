<?php
/**
 * MyContentPilot — functions.php
 *
 * Theme setup, asset enqueuing, menu registration,
 * template routing, and basic security hardening.
 */

defined('ABSPATH') || exit;

/* ============================================================
   1. THEME SETUP
   ============================================================ */

function mcp_setup(): void {
    // Allow WordPress to manage the document title
    add_theme_support('title-tag');

    // Featured images (used for og:image in future)
    add_theme_support('post-thumbnails');

    // Clean HTML5 markup for core elements
    add_theme_support('html5', [
        'search-form',
        'comment-form',
        'comment-list',
        'gallery',
        'caption',
        'style',
        'script',
    ]);

    // Wide/full alignment blocks (Gutenberg)
    add_theme_support('align-wide');

    // Custom logo support
    add_theme_support('custom-logo', [
        'height'      => 40,
        'width'       => 200,
        'flex-height' => true,
        'flex-width'  => true,
    ]);
}
add_action('after_setup_theme', 'mcp_setup');


/* ============================================================
   2. ENQUEUE STYLES & SCRIPTS
   ============================================================ */

function mcp_enqueue(): void {
    // Main stylesheet — versioned by file modification time for cache busting
    $css_path = get_template_directory() . '/css/style.css';
    $version  = file_exists($css_path)
        ? filemtime($css_path)
        : wp_get_theme()->get('Version');

    wp_enqueue_style(
        'mcp-style',
        get_template_directory_uri() . '/css/style.css',
        [],
        $version
    );

    // Dequeue block styles we don't need
    wp_dequeue_style('wp-block-library');
    wp_dequeue_style('wp-block-library-theme');
    wp_dequeue_style('classic-theme-styles');
}
add_action('wp_enqueue_scripts', 'mcp_enqueue');


/* ============================================================
   3. MENU REGISTRATION
   ============================================================ */

function mcp_register_menus(): void {
    register_nav_menus([
        'primary'   => __('Hauptnavigation', 'mycontentpilot'),
        'footer'    => __('Footer-Navigation', 'mycontentpilot'),
        'legal'     => __('Rechtliches', 'mycontentpilot'),
    ]);
}
add_action('after_setup_theme', 'mcp_register_menus');


/* ============================================================
   4. CUSTOM PAGE TEMPLATES
   Maps page slugs to template files automatically.
   No need to set template in WP Admin for each page.
   ============================================================ */

function mcp_page_template( string $template ): string {
    if ( ! is_page() ) {
        return $template;
    }

    $slug_map = [
        'funktionen' => 'page-funktionen.php',
        'preise'     => 'page-preise.php',
        'kontakt'    => 'page-kontakt.php',
        'impressum'  => 'page-impressum.php',
        'datenschutz'=> 'page-datenschutz.php',
        'agb'        => 'page-agb.php',
    ];

    $slug = get_post_field('post_name', get_queried_object_id());

    if ( isset($slug_map[$slug]) ) {
        $custom = get_template_directory() . '/' . $slug_map[$slug];
        if ( file_exists($custom) ) {
            return $custom;
        }
    }

    return $template;
}
add_filter('template_include', 'mcp_page_template');


/* ============================================================
   5. DOCUMENT TITLE SEPARATOR
   ============================================================ */

function mcp_document_title_separator(): string {
    return '–';
}
add_filter('document_title_separator', 'mcp_document_title_separator');


/* ============================================================
   6. EXCERPT LENGTH
   ============================================================ */

function mcp_excerpt_length(): int {
    return 24;
}
add_filter('excerpt_length', 'mcp_excerpt_length');


/* ============================================================
   7. SECURITY HARDENING
   ============================================================ */

// Remove WordPress version from all outputs
function mcp_remove_version(): string {
    return '';
}
add_filter('the_generator', 'mcp_remove_version');
remove_action('wp_head', 'wp_generator');

// Disable XML-RPC (not needed, reduces attack surface)
add_filter('xmlrpc_enabled', '__return_false');

// Remove unnecessary head items
remove_action('wp_head', 'wlwmanifest_link');
remove_action('wp_head', 'rsd_link');
remove_action('wp_head', 'wp_shortlink_wp_head');
remove_action('wp_head', 'adjacent_posts_rel_link_wp_head');

// Remove Emoji scripts (not needed)
remove_action('wp_head', 'print_emoji_detection_script', 7);
remove_action('wp_print_styles', 'print_emoji_styles');

// Disable REST API user enumeration
add_filter('rest_endpoints', function (array $endpoints): array {
    if ( ! is_user_logged_in() ) {
        unset($endpoints['/wp/v2/users']);
        unset($endpoints['/wp/v2/users/(?P<id>[\d]+)']);
    }
    return $endpoints;
});


/* ============================================================
   8. CONTACT FORM HANDLER (simple, no plugin needed)
   Handles POST from page-kontakt.php form.
   Uses wp_mail() — works with any SMTP plugin.
   ============================================================ */

function mcp_handle_contact_form(): void {
    if (
        ! isset($_POST['mcp_contact_nonce']) ||
        ! wp_verify_nonce(sanitize_text_field(wp_unslash($_POST['mcp_contact_nonce'])), 'mcp_contact_submit')
    ) {
        return;
    }

    if ( ! isset($_POST['mcp_contact']) ) {
        return;
    }

    $name    = sanitize_text_field(wp_unslash($_POST['name'] ?? ''));
    $email   = sanitize_email(wp_unslash($_POST['email'] ?? ''));
    $company = sanitize_text_field(wp_unslash($_POST['company'] ?? ''));
    $message = sanitize_textarea_field(wp_unslash($_POST['message'] ?? ''));
    $consent = isset($_POST['dsgvo']) ? true : false;

    // Basic validation
    $errors = [];
    if ( empty($name) )              $errors[] = 'name';
    if ( ! is_email($email) )        $errors[] = 'email';
    if ( empty($message) )           $errors[] = 'message';
    if ( ! $consent )                $errors[] = 'dsgvo';

    if ( ! empty($errors) ) {
        set_transient('mcp_form_errors_' . session_id(), $errors, 60);
        wp_safe_redirect(add_query_arg('status', 'error', wp_get_referer()));
        exit;
    }

    $to      = 'info@mycontentpilot.de';
    $subject = '[MyContentPilot] Neue Anfrage von ' . $name;
    $body    = "Name: {$name}\nE-Mail: {$email}\nUnternehmen: {$company}\n\nNachricht:\n{$message}";
    $headers = [
        'Content-Type: text/plain; charset=UTF-8',
        'Reply-To: ' . $name . ' <' . $email . '>',
    ];

    wp_mail($to, $subject, $body, $headers);

    wp_safe_redirect(add_query_arg('status', 'success', wp_get_referer()));
    exit;
}
add_action('init', 'mcp_handle_contact_form');


/* ============================================================
   9. HELPER: get current page section for active nav state
   ============================================================ */

function mcp_is_active_page( string $slug ): string {
    return is_page($slug) ? 'active" aria-current="page' : '';
}


/* ============================================================
   10. NEWSLETTER HANDLER (placeholder — connect to Mailchimp etc.)
   ============================================================ */

function mcp_handle_newsletter(): void {
    if (
        ! isset($_POST['mcp_newsletter_nonce']) ||
        ! wp_verify_nonce(sanitize_text_field(wp_unslash($_POST['mcp_newsletter_nonce'])), 'mcp_newsletter_submit')
    ) {
        return;
    }

    $email = sanitize_email(wp_unslash($_POST['email'] ?? ''));
    if ( ! is_email($email) ) {
        return;
    }

    // TODO: connect to Mailchimp / Brevo API here
    // For now: store in options as a simple list (fine for early stage)
    $subscribers = get_option('mcp_newsletter_subscribers', []);
    if ( ! in_array($email, $subscribers, true) ) {
        $subscribers[] = $email;
        update_option('mcp_newsletter_subscribers', $subscribers);
    }

    wp_safe_redirect(add_query_arg('newsletter', 'success', wp_get_referer()));
    exit;
}
add_action('init', 'mcp_handle_newsletter');
