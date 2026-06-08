<?php
/**
 * Template Name: Sleek Landing Page
 * Template Post Type: page
 * Description: Custom code-first layout for MyContentPilot marketing page.
 */

if (isset($_SERVER['HTTP_X_FORWARDED_PROTO']) && $_SERVER['HTTP_X_FORWARDED_PROTO'] === 'https') {
    $_SERVER['HTTPS'] = 'on';
}
?>
<!DOCTYPE html>
<html <?php language_attributes(); ?> class="scroll-smooth">
<head>
    <meta charset="<?php bloginfo('charset'); ?>">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>MyContentPilot | AI Content Operations Platform</title>

    <meta name="description" content="Automate content creation, publishing, and social distribution with MyContentPilot. Built for businesses, agencies, publishers, and multi-brand operations.">

    <link rel="canonical" href="https://mycontentpilot.de">

    <meta property="og:title" content="MyContentPilot">
    <meta property="og:description" content="AI Content Operations Platform">
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://mycontentpilot.de">

    <meta name="twitter:card" content="summary_large_image">

    <script src="https://cdn.tailwindcss.com"></script>

    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        brandDark: '#0B0F19',
                        brandCard: '#151B2C',
                        brandAccent: '#3B82F6',
                        brandGreen: '#10B981'
                    }
                }
            }
        }
    </script>

    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": "MyContentPilot",
        "url": "https://mycontentpilot.de",
        "description": "AI Content Operations Platform that automates content creation, publishing, and social media distribution for businesses and multi-brand operations.",
        "applicationCategory": "BusinessApplication",
        "operatingSystem": "Cloud",
        "offers": {
            "@type": "Offer",
            "availability": "https://schema.org/PreOrder"
        }
    }
    </script>

    <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

        *, *::before, *::after { box-sizing: border-box; }

        :root {
            --dark: #0B0F19;
            --card: #151B2C;
            --card-2: #1A2235;
            --accent: #3B82F6;
            --green: #10B981;
            --border: rgba(255,255,255,0.07);
            --border-accent: rgba(59,130,246,0.3);
            --text-muted: #64748B;
            --text-dim: #94A3B8;
            --gradient-start: #3B82F6;
            --gradient-end: #8B5CF6;
        }

        html { scroll-behavior: smooth; }

        body {
            background-color: var(--dark);
            color: #E2E8F0;
            font-family: 'DM Sans', sans-serif;
            font-weight: 300;
            line-height: 1.7;
            overflow-x: hidden;
        }

        h1, h2, h3, h4, h5 {
            font-family: 'Syne', sans-serif;
            letter-spacing: -0.02em;
            line-height: 1.15;
        }

        .mono { font-family: 'DM Mono', monospace; }

        /* Grid background */
        .grid-bg {
            background-image:
                linear-gradient(rgba(59,130,246,0.04) 1px, transparent 1px),
                linear-gradient(90deg, rgba(59,130,246,0.04) 1px, transparent 1px);
            background-size: 48px 48px;
        }

        /* Glow effects */
        .glow-blue { box-shadow: 0 0 60px rgba(59,130,246,0.15), 0 0 120px rgba(59,130,246,0.06); }
        .glow-green { box-shadow: 0 0 40px rgba(16,185,129,0.12); }
        .text-glow { text-shadow: 0 0 40px rgba(59,130,246,0.4); }

        /* Gradient text */
        .gradient-text {
            background: linear-gradient(135deg, #60A5FA 0%, #A78BFA 50%, #34D399 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        /* Cards */
        .card {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 12px;
            transition: border-color 0.2s, transform 0.2s;
        }
        .card:hover {
            border-color: var(--border-accent);
            transform: translateY(-2px);
        }

        /* Noise overlay */
        .noise::before {
            content: '';
            position: absolute;
            inset: 0;
            background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.03'/%3E%3C/svg%3E");
            pointer-events: none;
            border-radius: inherit;
        }

        /* Animated pipeline connector */
        .pipe-line {
            width: 2px;
            background: linear-gradient(to bottom, transparent, var(--accent), transparent);
            margin: 0 auto;
            position: relative;
            overflow: hidden;
        }
        .pipe-line::after {
            content: '';
            position: absolute;
            top: -100%;
            width: 100%;
            height: 40%;
            background: linear-gradient(to bottom, transparent, #60A5FA, transparent);
            animation: flow 2s linear infinite;
        }
        @keyframes flow {
            to { top: 200%; }
        }

        /* Pulse dot */
        .pulse-dot {
            width: 8px; height: 8px;
            border-radius: 50%;
            background: var(--green);
            position: relative;
        }
        .pulse-dot::after {
            content: '';
            position: absolute;
            inset: -4px;
            border-radius: 50%;
            border: 1px solid var(--green);
            animation: pulse 2s ease-out infinite;
        }
        @keyframes pulse {
            0% { opacity: 1; transform: scale(1); }
            100% { opacity: 0; transform: scale(2.5); }
        }

        /* Badge */
        .badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 10px;
            border-radius: 999px;
            font-size: 11px;
            font-family: 'DM Mono', monospace;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            font-weight: 500;
        }
        .badge-blue { background: rgba(59,130,246,0.12); border: 1px solid rgba(59,130,246,0.25); color: #93C5FD; }
        .badge-green { background: rgba(16,185,129,0.12); border: 1px solid rgba(16,185,129,0.25); color: #6EE7B7; }
        .badge-purple { background: rgba(139,92,246,0.12); border: 1px solid rgba(139,92,246,0.25); color: #C4B5FD; }

        /* Buttons */
        .btn-primary {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 12px 24px;
            background: var(--accent);
            color: white;
            border: none;
            border-radius: 8px;
            font-family: 'DM Sans', sans-serif;
            font-weight: 500;
            font-size: 15px;
            cursor: pointer;
            transition: background 0.2s, transform 0.1s, box-shadow 0.2s;
            text-decoration: none;
        }
        .btn-primary:hover {
            background: #2563EB;
            box-shadow: 0 0 30px rgba(59,130,246,0.4);
            transform: translateY(-1px);
        }
        .btn-secondary {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 11px 22px;
            background: transparent;
            color: #CBD5E1;
            border: 1px solid var(--border);
            border-radius: 8px;
            font-family: 'DM Sans', sans-serif;
            font-weight: 400;
            font-size: 15px;
            cursor: pointer;
            transition: border-color 0.2s, color 0.2s;
            text-decoration: none;
        }
        .btn-secondary:hover {
            border-color: rgba(255,255,255,0.2);
            color: white;
        }

        /* Nav */
        #main-nav {
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            background: rgba(11,15,25,0.8);
            border-bottom: 1px solid var(--border);
            transition: all 0.3s;
        }

        /* FAQ accordion */
        .faq-content {
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease;
        }
        .faq-content.open { max-height: 300px; }
        .faq-icon { transition: transform 0.3s; }
        .faq-icon.open { transform: rotate(45deg); }

        /* Architecture flow node */
        .arch-node {
            position: relative;
            padding: 16px 20px;
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 10px;
            transition: border-color 0.2s;
        }
        .arch-node:hover { border-color: var(--border-accent); }
        .arch-node.active { border-color: rgba(59,130,246,0.5); background: rgba(59,130,246,0.05); }

        /* Modal */
        .modal-overlay {
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.8);
            backdrop-filter: blur(8px);
            z-index: 1000;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.25s;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .modal-overlay.open {
            opacity: 1;
            pointer-events: all;
        }
        .modal-box {
            background: #111827;
            border: 1px solid var(--border);
            border-radius: 16px;
            width: 100%;
            max-width: 640px;
            max-height: 80vh;
            overflow-y: auto;
            padding: 36px;
            transform: translateY(16px);
            transition: transform 0.25s;
        }
        .modal-overlay.open .modal-box { transform: translateY(0); }

        /* Scrollbar */
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: var(--dark); }
        ::-webkit-scrollbar-thumb { background: #1E293B; border-radius: 3px; }

        /* Stat counter */
        .stat-number {
            font-family: 'Syne', sans-serif;
            font-size: 2.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, #60A5FA, #A78BFA);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        /* Focus styles for accessibility */
        :focus-visible {
            outline: 2px solid var(--accent);
            outline-offset: 3px;
            border-radius: 4px;
        }

        /* Reduced motion */
        @media (prefers-reduced-motion: reduce) {
            *, *::before, *::after { animation-duration: 0.01ms !important; transition-duration: 0.01ms !important; }
        }

        /* Feature icon wrapper */
        .icon-wrap {
            width: 44px; height: 44px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
            font-size: 20px;
        }

        /* Pricing card highlight */
        .pricing-recommended {
            border-color: var(--accent) !important;
            background: linear-gradient(180deg, rgba(59,130,246,0.08) 0%, var(--card) 60%);
            position: relative;
        }

        /* Lang toggle */
        .lang-btn {
            padding: 4px 10px;
            border-radius: 6px;
            font-family: 'DM Mono', monospace;
            font-size: 12px;
            cursor: pointer;
            transition: background 0.15s, color 0.15s;
            border: none;
            background: transparent;
            color: var(--text-muted);
        }
        .lang-btn.active {
            background: rgba(59,130,246,0.15);
            color: #93C5FD;
        }
        .lang-btn:hover { color: white; }

        /* Section label */
        .section-label {
            font-family: 'DM Mono', monospace;
            font-size: 11px;
            letter-spacing: 0.15em;
            text-transform: uppercase;
            color: var(--text-muted);
        }
    </style>

    <?php wp_head(); ?>
</head>
<body class="bg-brandDark text-slate-100 font-sans antialiased">

<?php
/* ============================================================
   TRANSLATIONS
   ============================================================ */
function mcp_translations_json(): string {
    return json_encode([
        'de' => [
            'nav_features'      => 'Funktionen',
            'nav_platform'      => 'Plattform',
            'nav_pricing'       => 'Preise',
            'nav_faq'           => 'FAQ',
            'nav_cta'           => 'Frühzugang sichern',
            'badge_ops'         => 'AI Content Operations',
            'hero_h1'           => 'Automatisieren Sie Ihre Content-Produktion mit KI',
            'hero_sub'          => 'MyContentPilot überwacht RSS-Feeds, verarbeitet Artikel mit KI, generiert Mediendateien, veröffentlicht automatisch auf WordPress und verteilt Inhalte über alle Social-Media-Kanäle — vollständig automatisiert.',
            'hero_cta'          => 'Frühzugang sichern',
            'hero_cta2'         => 'Plattform-Architektur',
            'trust_1'           => 'Multi-Brand',
            'trust_2'           => 'WordPress Ready',
            'trust_3'           => 'Social Automation',
            'trust_4'           => 'KI-gesteuert',
            'form_notice'       => 'System-Hinweis: Bitte aktivieren Sie Fluent Forms und konfigurieren Sie Formular ID 6 im WordPress-Adminbereich.',
            'arch_title'        => 'Die Plattform-Architektur',
            'arch_sub'          => 'Von der Quelle bis zur Veröffentlichung — vollständig automatisiert.',
            'arch_node_1'       => 'RSS / Atom Quellen',
            'arch_node_1_d'     => 'Feeds überwachen & normalisieren',
            'arch_node_2'       => 'KI-Verarbeitungsschicht',
            'arch_node_2_d'     => 'Anthropic · DeepSeek · Routing',
            'arch_node_3'       => 'Brand Rules Engine',
            'arch_node_3_d'     => 'Multi-Brand Regeln & Deduplizierung',
            'arch_node_4'       => 'Medien-Generierung',
            'arch_node_4_d'     => 'DALL-E · Pexels · Social Formate',
            'arch_node_5'       => 'WordPress Publishing',
            'arch_node_5_d'     => 'REST API · Draft · Live',
            'arch_node_6'       => 'Social Distribution',
            'arch_node_6_d'     => 'Facebook · Instagram · Mehr',
            'feat_title'        => 'Alles was Sie brauchen',
            'feat_sub'          => 'Eine Plattform für den gesamten Content-Lifecycle.',
            'feat_1_t'          => 'RSS & Atom Ingestion',
            'feat_1_d'          => 'Überwachen Sie beliebig viele Feeds. Artikel werden normalisiert, dedupliziert und für die KI-Verarbeitung vorbereitet.',
            'feat_2_t'          => 'KI Content-Generierung',
            'feat_2_d'          => 'Anthropic und DeepSeek mit automatischem Fallback. Prompt-Logik bleibt vollständig extern und versionierbar.',
            'feat_3_t'          => 'Multi-Brand Management',
            'feat_3_d'          => 'Mehrere Marken, eigene Regeln, separate Targets. Vollständig isolierte Pipelines pro Marke.',
            'feat_4_t'          => 'Automatisiertes Publishing',
            'feat_4_d'          => 'WordPress-Integration über die REST API. Draft- und Live-Modus, Featured Images, Kategorien & Tags.',
            'feat_5_t'          => 'Social Media Distribution',
            'feat_5_d'          => 'Facebook-Seiten und Instagram-Konten. Erweiterbar auf LinkedIn, X, TikTok und YouTube Shorts.',
            'feat_6_t'          => 'Medien-Asset-Generierung',
            'feat_6_d'          => 'DALL-E 3 und Pexels. Alle Social-Formate automatisch: Facebook, Instagram, Stories.',
            'feat_7_t'          => 'Scheduling Engine',
            'feat_7_d'          => 'APScheduler mit SQLite WAL-Persistenz. Cron-basiert, idempotent und container-sicher.',
            'feat_8_t'          => 'Duplicate Detection',
            'feat_8_d'          => 'SHA-256-Fingerprinting auf Ingestion- und Publishing-Ebene. Kein Artikel wird doppelt verarbeitet oder veröffentlicht.',
            'feat_9_t'          => 'Brand-Aware Content Rules',
            'feat_9_d'          => 'Jede Marke erhält eigene KI-Provider, Modelle, Temperaturen und Formatierungsregeln.',
            'platform_title'    => 'Plattform-Architektur',
            'platform_sub'      => 'Produktionsreife Infrastruktur — gebaut für Zuverlässigkeit.',
            'platform_stable'   => 'Aktiv & Stabil',
            'platform_ready'    => 'Produktionsbereit',
            'waitlist_title'    => 'Early Access',
            'waitlist_sub'      => 'Bereits <strong>237+ Unternehmen</strong> haben ihr Interesse bekundet.',
            'waitlist_sub2'     => 'Sichern Sie sich Ihren Platz auf der Warteliste und erhalten Sie frühzeitigen Zugang.',
            'pricing_title'     => 'Preise',
            'pricing_sub'       => 'Transparent. Skalierbar. Für jede Unternehmensgröße.',
            'pricing_soon'      => 'Demnächst',
            'pricing_popular'   => 'Empfohlen',
            'pricing_starter'   => 'Starter',
            'pricing_pro'       => 'Professional',
            'pricing_ent'       => 'Enterprise',
            'pricing_starter_d' => 'Für Einzelpersonen und kleine Teams.',
            'pricing_pro_d'     => 'Für wachsende Unternehmen mit mehreren Marken.',
            'pricing_ent_d'     => 'Für Agenturen und große Publisher.',
            'faq_title'         => 'Häufig gestellte Fragen',
            'faq_sub'           => 'Alles Wichtige auf einen Blick.',
            'faq_1_q'           => 'Was ist MyContentPilot?',
            'faq_1_a'           => 'MyContentPilot ist eine KI-gestützte Content Operations Platform. Sie automatisiert den gesamten Content-Lifecycle: vom RSS-Monitoring über KI-Generierung und Medienerstellung bis zur automatischen Veröffentlichung auf WordPress und Social Media.',
            'faq_2_q'           => 'Wie funktioniert das automatisierte Publishing?',
            'faq_2_a'           => 'Die Plattform integriert sich direkt über die WordPress REST API. Sie unterstützt Draft- und Live-Publishing, Featured Images, Kategorien, Tags und benutzerdefinierte Felder. Alle Veröffentlichungen werden protokolliert und sind idempotent.',
            'faq_3_q'           => 'Welche KI-Provider werden unterstützt?',
            'faq_3_a'           => 'Aktuell unterstützt MyContentPilot Anthropic (Claude) und DeepSeek. Das System verfügt über eine Abstraktionsschicht, die automatischen Fallback zwischen Providern ermöglicht. Weitere Provider können einfach integriert werden.',
            'faq_4_q'           => 'Wie funktioniert die WordPress-Integration?',
            'faq_4_a'           => 'Die Integration erfolgt über Application Passwords und die WordPress REST API. Sie benötigen lediglich Ihre WordPress-URL, einen Benutzernamen und ein Application Password. Kein Plugin erforderlich.',
            'faq_5_q'           => 'Welche Social-Media-Plattformen werden unterstützt?',
            'faq_5_a'           => 'Aktuell werden Facebook-Seiten und Instagram unterstützt. Die Roadmap umfasst LinkedIn, X (Twitter), TikTok und YouTube Shorts. Die Architektur ist auf beliebige Plattformen erweiterbar.',
            'faq_6_q'           => 'Kann ich mehrere Marken verwalten?',
            'faq_6_a'           => 'Ja. Multi-Brand-Management ist ein Kernfeature von MyContentPilot. Jede Marke erhält eigene RSS-Feeds, KI-Regeln, Publishing-Targets und Scheduling-Konfigurationen — vollständig isoliert.',
            'faq_7_q'           => 'Wem gehören meine Daten?',
            'faq_7_a'           => 'Ihre Daten bleiben Ihnen. MyContentPilot verarbeitet Inhalte nach Ihren Regeln und speichert alles in Ihrer eigenen Infrastruktur. Es gibt keine Vendor-Lock-in-Abhängigkeiten.',
            'faq_8_q'           => 'Wann ist der Early Access verfügbar?',
            'faq_8_a'           => 'Der Early Access startet in Kürze. Tragen Sie sich in die Warteliste ein, um als einer der ersten informiert zu werden und exklusive Early-Access-Konditionen zu erhalten.',
            'faq_9_q'           => 'Kann ich eigene System-Prompts und Tonalitäten definieren?',
            'faq_9_a'           => 'Ja, absolut. Jede Marke kann mit individuellen System-Prompts, Formatierungsvorgaben (z.B. Du/Sie-Form) und Tonalitäten konfiguriert werden. Die Prompt-Logik bleibt sauber versionierbar außerhalb des Core-Codes.',
            'faq_10_q'          => 'Wo wird die Automatisierungs-Engine gehostet?',
            'faq_10_a'          => 'Da die Plattform vollständig Docker-basiert ist, läuft sie isoliert auf Ihrer eigenen Infrastruktur (z.B. einem Linux-VPS). Sie mieten kein undurchsichtiges Drittanbieter-Cloud-System, sondern behalten die volle Souveränität.',
            'faq_11_q'          => 'Wie wird die Qualität der KI-Inhalte sichergestellt?',
            'faq_11_a'          => 'Durch mehrstufige Prompt-Ketten, strukturiertes JSON-Parsing und automatische Validierungsschritte. Zudem können Artikel optional standardmäßig als "Draft" (Entwurf) in WordPress gespeichert werden, um eine manuelle Endkontrolle zu ermöglichen.',
            'faq_12_q'          => 'Benötige ich fortgeschrittene Programmierkenntnisse für das Setup?',
            'faq_12_a'          => 'Für die Nutzung der fertigen Weboberfläche nicht. Das initiale Deployment der Engine nutzt Docker Compose und ist mit wenigen CLI-Befehlen einsatzbereit. Einmal aufgesetzt, läuft das System vollautomatisch im Hintergrund.',
            'footer_product'    => 'Produkt',
            'footer_features'   => 'Funktionen',
            'footer_company'    => 'Unternehmen',
            'footer_legal'      => 'Rechtliches',
            'footer_copy'       => '© 2025 MyContentPilot. Alle Rechte vorbehalten.',
            'footer_tagline'    => 'KI Content Operations Platform',
            'imp_title'         => 'Impressum',
            'imp_link'          => 'Impressum',
            'dse_title'         => 'Datenschutzerklärung',
            'dse_link'          => 'Datenschutz',
            'close'             => 'Schließen',
            /* --- Impressum-specific keys (DE) --- */
            'imp_s1_heading'    => 'Impressum',
            'imp_s2_heading'    => 'Angaben gemäß § 5 TMG',
            'imp_s2_name_label' => 'Anbieter',
            'imp_s2_name'       => 'MyContentPilot',
            'imp_s2_owner'      => 'Iqbal Nazir',
            'imp_s2_street'     => 'Anemonenstr. 5/1',
            'imp_s2_city'       => '70771 Leinfelden-Echterdingen',
            'imp_s2_country'    => 'Deutschland',
            'imp_s3_heading'    => 'Kontakt',
            'imp_s3_email_label'=> 'E-Mail',
            'imp_s3_email'      => 'info@germanysupport.de',
            'imp_s4_heading'    => 'Umsatzsteuer',
            'imp_s4_body'       => 'Umsatzsteuer-Identifikationsnummer gemäß § 27a Umsatzsteuergesetz: DE342878499',
            'imp_s5_heading'    => 'Verantwortlich für den Inhalt nach § 18 Abs. 2 MStV',
            'imp_s5_name'       => 'Iqbal Nazir',
            'imp_s5_street'     => 'Anemonenstr. 5/1',
            'imp_s5_city'       => '70771 Leinfelden-Echterdingen',
            'imp_s5_country'    => 'Deutschland',
            'imp_s6_heading'    => 'Haftung für Inhalte',
            'imp_s6_body'       => 'Als Diensteanbieter sind wir gemäß § 7 Abs. 1 TMG für eigene Inhalte auf diesen Seiten nach den allgemeinen Gesetzen verantwortlich. Nach §§ 8 bis 10 TMG sind wir als Diensteanbieter jedoch nicht verpflichtet, übermittelte oder gespeicherte fremde Informationen zu überwachen oder nach Umständen zu forschen, die auf eine rechtswidrige Tätigkeit hinweisen. Verpflichtungen zur Entfernung oder Sperrung der Nutzung von Informationen nach den allgemeinen Gesetzen bleiben hiervon unberührt. Eine diesbezügliche Haftung ist jedoch erst ab dem Zeitpunkt der Kenntnis einer konkreten Rechtsverletzung möglich. Bei Bekanntwerden von entsprechenden Rechtsverletzungen werden wir diese Inhalte umgehend entfernen.',
            'imp_s7_heading'    => 'Haftung für Links',
            'imp_s7_body'       => 'Unser Angebot enthält Links zu externen Websites Dritter, auf deren Inhalte wir keinen Einfluss haben. Deshalb können wir für diese fremden Inhalte auch keine Gewähr übernehmen. Für die Inhalte der verlinkten Seiten ist stets der jeweilige Anbieter oder Betreiber der Seiten verantwortlich. Die verlinkten Seiten wurden zum Zeitpunkt der Verlinkung auf mögliche Rechtsverstöße überprüft. Rechtswidrige Inhalte waren zum Zeitpunkt der Verlinkung nicht erkennbar. Eine permanente inhaltliche Kontrolle der verlinkten Seiten ist jedoch ohne konkrete Anhaltspunkte einer Rechtsverletzung nicht zumutbar. Bei Bekanntwerden von Rechtsverletzungen werden wir derartige Links umgehend entfernen.',
            /* --- Datenschutz-specific keys (DE) --- */
            'dse_s1_heading'        => 'Verantwortliche Stelle',
            'dse_s1_label_name'     => 'Name',
            'dse_s1_name'           => 'MyContentPilot',
            'dse_s1_label_owner'    => 'Inhaber',
            'dse_s1_owner'          => 'Iqbal Nazir',
            'dse_s1_label_email'    => 'E-Mail',
            'dse_s1_email'          => 'contact@mycontentpilot.de',
            'dse_s1_body'           => 'Verantwortlicher im Sinne der Datenschutz-Grundverordnung (DSGVO) und anderer nationaler Datenschutzgesetze sowie sonstiger datenschutzrechtlicher Bestimmungen ist die oben genannte natürliche Person.',
            'dse_s2_heading'        => 'Server-Logdateien',
            'dse_s2_body'           => 'Der Hosting-Anbieter dieser Website erhebt und speichert automatisch Informationen in sogenannten Server-Logdateien, die Ihr Browser automatisch übermittelt. Dabei werden folgende Daten erfasst: IP-Adresse des anfragenden Rechners, Datum und Uhrzeit des Zugriffs, Name und URL der abgerufenen Datei, Website, von der aus der Zugriff erfolgt (Referrer-URL), verwendeter Browser und ggf. das Betriebssystem Ihres Rechners sowie der Name Ihres Access-Providers.',
            'dse_s2_purpose'        => 'Die Verarbeitung dieser Daten dient der Gewährleistung eines reibungslosen Verbindungsaufbaus, der systemseitigen Sicherheit sowie der technischen Stabilität der Website.',
            'dse_s2_legal_label'    => 'Rechtsgrundlage',
            'dse_s2_legal'          => 'Art. 6 Abs. 1 lit. f DSGVO (berechtigtes Interesse). Das berechtigte Interesse besteht in der sicheren und stabilen Bereitstellung des Dienstes.',
            'dse_s3_heading'        => 'Kontaktformular & Warteliste (Fluent Forms)',
            'dse_s3_body'           => 'Auf dieser Website wird ein Kontaktformular über das WordPress-Plugin Fluent Forms (Formular-ID 1) bereitgestellt. Wenn Sie das Formular zur Anmeldung für den Early Access von MyContentPilot nutzen, wird Ihre E-Mail-Adresse erhoben und gespeichert.',
            'dse_s3_purpose_label'  => 'Zweck der Verarbeitung',
            'dse_s3_purpose'        => 'Die erhobene E-Mail-Adresse wird ausschließlich dazu verwendet, Sie über die Verfügbarkeit des Early Access von MyContentPilot zu informieren sowie relevante Informationen zum Produkt zu übermitteln.',
            'dse_s3_legal_label'    => 'Rechtsgrundlage',
            'dse_s3_legal'          => 'Art. 6 Abs. 1 lit. a DSGVO (Einwilligung) und/oder Art. 6 Abs. 1 lit. f DSGVO (berechtigtes Interesse an der Direktkommunikation mit Interessenten).',
            'dse_s3_third_label'    => 'Weitergabe an Dritte',
            'dse_s3_third'          => 'Ihre Daten werden nicht an Dritte weitergegeben, verkauft oder für Werbezwecke Dritter genutzt.',
            'dse_s3_deletion_label' => 'Löschung',
            'dse_s3_deletion'       => 'Sie können die Löschung Ihrer Daten jederzeit formlos per E-Mail an contact@mycontentpilot.de verlangen. Die Daten werden unverzüglich gelöscht, sofern keine gesetzlichen Aufbewahrungspflichten entgegenstehen.',
            'dse_s4_heading'        => 'Ihre Rechte als betroffene Person',
            'dse_s4_intro'          => 'Ihnen stehen nach der DSGVO folgende Rechte zu. Zur Ausübung Ihrer Rechte wenden Sie sich bitte an: contact@mycontentpilot.de',
            'dse_s4_r1_label'       => 'Auskunftsrecht — Art. 15 DSGVO',
            'dse_s4_r1_body'        => 'Sie haben das Recht, eine Bestätigung darüber zu verlangen, ob Sie betreffende personenbezogene Daten verarbeitet werden, sowie Auskunft über diese Daten und weitere Informationen gemäß Art. 15 DSGVO zu erhalten.',
            'dse_s4_r2_label'       => 'Recht auf Berichtigung — Art. 16 DSGVO',
            'dse_s4_r2_body'        => 'Sie haben das Recht, unverzüglich die Berichtigung Sie betreffender unrichtiger personenbezogener Daten sowie die Vervollständigung unvollständiger Daten zu verlangen.',
            'dse_s4_r3_label'       => 'Recht auf Löschung — Art. 17 DSGVO',
            'dse_s4_r3_body'        => 'Sie haben das Recht, zu verlangen, dass Sie betreffende personenbezogene Daten unverzüglich gelöscht werden, sofern die gesetzlichen Voraussetzungen vorliegen.',
            'dse_s4_r4_label'       => 'Recht auf Einschränkung der Verarbeitung — Art. 18 DSGVO',
            'dse_s4_r4_body'        => 'Sie haben das Recht, die Einschränkung der Verarbeitung Ihrer personenbezogenen Daten zu verlangen, wenn eine der in Art. 18 DSGVO genannten Voraussetzungen erfüllt ist.',
            'dse_s4_r5_label'       => 'Recht auf Datenübertragbarkeit — Art. 20 DSGVO',
            'dse_s4_r5_body'        => 'Sie haben das Recht, die Sie betreffenden personenbezogenen Daten in einem strukturierten, gängigen und maschinenlesbaren Format zu erhalten und diese Daten einem anderen Verantwortlichen zu übermitteln.',
            'dse_s4_r6_label'       => 'Widerspruchsrecht — Art. 21 DSGVO',
            'dse_s4_r6_body'        => 'Sie haben das Recht, aus Gründen, die sich aus Ihrer besonderen Situation ergeben, jederzeit gegen die Verarbeitung Sie betreffender personenbezogener Daten, die aufgrund von Art. 6 Abs. 1 lit. e oder f DSGVO erfolgt, Widerspruch einzulegen.',
            'dse_s4_complaint'      => 'Unbeschadet anderer Rechtsbehelfe haben Sie das Recht auf Beschwerde bei einer Datenschutzaufsichtsbehörde, insbesondere in dem Mitgliedstaat Ihres gewöhnlichen Aufenthaltsorts, Ihres Arbeitsplatzes oder des Orts des mutmaßlichen Verstoßes, wenn Sie der Ansicht sind, dass die Verarbeitung der Sie betreffenden personenbezogenen Daten gegen die DSGVO verstößt.',
        ],
        'en' => [
            'nav_features'      => 'Features',
            'nav_platform'      => 'Platform',
            'nav_pricing'       => 'Pricing',
            'nav_faq'           => 'FAQ',
            'nav_cta'           => 'Get Early Access',
            'badge_ops'         => 'AI Content Operations',
            'hero_h1'           => 'Automate Your Content Operations with AI',
            'hero_sub'          => 'MyContentPilot monitors RSS feeds, processes articles with AI, generates media assets, publishes automatically to WordPress, and distributes content across all social media channels — fully automated.',
            'hero_cta'          => 'Get Early Access',
            'hero_cta2'         => 'Platform Architecture',
            'trust_1'           => 'Multi-Brand',
            'trust_2'           => 'WordPress Ready',
            'trust_3'           => 'Social Automation',
            'trust_4'           => 'AI Powered',
            'form_notice'       => 'System Notice: Please activate Fluent Forms and configure Form ID 6 in the WordPress admin panel.',
            'arch_title'        => 'The Platform Architecture',
            'arch_sub'          => 'From source to publication — fully automated.',
            'arch_node_1'       => 'RSS / Atom Sources',
            'arch_node_1_d'     => 'Monitor & normalize feeds',
            'arch_node_2'       => 'AI Processing Layer',
            'arch_node_2_d'     => 'Anthropic · DeepSeek · Routing',
            'arch_node_3'       => 'Brand Rules Engine',
            'arch_node_3_d'     => 'Multi-brand rules & deduplication',
            'arch_node_4'       => 'Media Generation',
            'arch_node_4_d'     => 'DALL-E · Pexels · Social formats',
            'arch_node_5'       => 'WordPress Publishing',
            'arch_node_5_d'     => 'REST API · Draft · Live',
            'arch_node_6'       => 'Social Distribution',
            'arch_node_6_d'     => 'Facebook · Instagram · More',
            'feat_title'        => 'Everything You Need',
            'feat_sub'          => 'One platform for the entire content lifecycle.',
            'feat_1_t'          => 'RSS & Atom Ingestion',
            'feat_1_d'          => 'Monitor any number of feeds. Articles are normalized, deduplicated, and prepared for AI processing.',
            'feat_2_t'          => 'AI Content Generation',
            'feat_2_d'          => 'Anthropic and DeepSeek with automatic fallback. Prompt logic stays fully external and versionable.',
            'feat_3_t'          => 'Multi-Brand Management',
            'feat_3_d'          => 'Multiple brands, separate rules, isolated targets. Fully isolated pipelines per brand.',
            'feat_4_t'          => 'Automated Publishing',
            'feat_4_d'          => 'WordPress integration via REST API. Draft and live mode, featured images, categories & tags.',
            'feat_5_t'          => 'Social Media Distribution',
            'feat_5_d'          => 'Facebook pages and Instagram accounts. Extendable to LinkedIn, X, TikTok and YouTube Shorts.',
            'feat_6_t'          => 'Media Asset Generation',
            'feat_6_d'          => 'DALL-E 3 and Pexels. All social formats automatically: Facebook, Instagram, Stories.',
            'feat_7_t'          => 'Scheduling Engine',
            'feat_7_d'          => 'APScheduler with SQLite WAL persistence. Cron-based, idempotent, and container-safe.',
            'feat_8_t'          => 'Duplicate Detection',
            'feat_8_d'          => 'SHA-256 fingerprinting at ingestion and publishing level. No article is processed or published twice.',
            'feat_9_t'          => 'Brand-Aware Content Rules',
            'feat_9_d'          => 'Each brand gets its own AI providers, models, temperatures, and formatting rules.',
            'platform_title'    => 'Platform Architecture',
            'platform_sub'      => 'Production-grade infrastructure — built for reliability.',
            'platform_stable'   => 'Active & Stable',
            'platform_ready'    => 'Production Ready',
            'waitlist_title'    => 'Early Access',
            'waitlist_sub'      => 'Already <strong>237+ businesses</strong> have registered their interest.',
            'waitlist_sub2'     => 'Secure your spot on the waitlist and get early access.',
            'pricing_title'     => 'Pricing',
            'pricing_sub'       => 'Transparent. Scalable. For every business size.',
            'pricing_soon'      => 'Coming Soon',
            'pricing_popular'   => 'Recommended',
            'pricing_starter'   => 'Starter',
            'pricing_pro'       => 'Professional',
            'pricing_ent'       => 'Enterprise',
            'pricing_starter_d' => 'For individuals and small teams.',
            'pricing_pro_d'     => 'For growing companies with multiple brands.',
            'pricing_ent_d'     => 'For agencies and large publishers.',
            'faq_title'         => 'Frequently Asked Questions',
            'faq_sub'           => 'Everything important at a glance.',
            'faq_1_q'           => 'What is MyContentPilot?',
            'faq_1_a'           => 'MyContentPilot is an AI-powered Content Operations Platform. It automates the entire content lifecycle: from RSS monitoring to AI generation and media creation, all the way to automatic publishing on WordPress and social media.',
            'faq_2_q'           => 'How does automated publishing work?',
            'faq_2_a'           => 'The platform integrates directly via the WordPress REST API. It supports draft and live publishing, featured images, categories, tags, and custom fields. All publications are logged and are idempotent.',
            'faq_3_q'           => 'Which AI providers are supported?',
            'faq_3_a'           => 'MyContentPilot currently supports Anthropic (Claude) and DeepSeek. The system has an abstraction layer that enables automatic fallback between providers. Additional providers can be integrated easily.',
            'faq_4_q'           => 'How does WordPress integration work?',
            'faq_4_a'           => 'Integration is done via Application Passwords and the WordPress REST API. You only need your WordPress URL, a username, and an Application Password. No plugin required.',
            'faq_5_q'           => 'Which social media platforms are supported?',
            'faq_5_a'           => 'Facebook pages and Instagram are currently supported. The roadmap includes LinkedIn, X (Twitter), TikTok and YouTube Shorts. The architecture is extensible to any platform.',
            'faq_6_q'           => 'Can I manage multiple brands?',
            'faq_6_a'           => 'Yes. Multi-brand management is a core feature of MyContentPilot. Each brand gets its own RSS feeds, AI rules, publishing targets, and scheduling configurations — fully isolated.',
            'faq_7_q'           => 'Who owns my data?',
            'faq_7_a'           => 'Your data stays yours. MyContentPilot processes content according to your rules and stores everything in your own infrastructure. There are no vendor lock-in dependencies.',
            'faq_8_q'           => 'When will Early Access be available?',
            'faq_8_a'           => 'Early access launches soon. Join the waitlist to be among the first to be notified and receive exclusive early access terms.',
            'faq_9_q'           => 'Can I define custom system prompts and brand voices?',
            'faq_9_a'           => 'Yes, absolutely. Each brand can be configured with its own system prompts, formatting criteria (e.g., formal vs. informal tone), and styling rules. Prompt logic stays cleanly versionable outside core code.',
            'faq_10_q'          => 'Where is the automation engine hosted?',
            'faq_10_a'          => 'Since the platform is fully containerized, it runs entirely on your own server infrastructure (like a standard Linux VPS) via Docker Compose. You retain 100% data privacy and control.',
            'faq_11_q'          => 'How do you guarantee high-quality content output?',
            'faq_11_a'          => 'We use sequential multi-stage prompting and automated schema validation. For safety, you can configure pipelines to drop generated posts directly into WordPress as "Drafts" for human review before going live.',
            'faq_12_q'          => 'Do I need deep programming knowledge to set it up?',
            'faq_12_a'          => 'Not to operate it. Initial deployment uses straightforward Docker Compose configs that initialize with a few basic terminal commands. Once deployed, all day-to-day operations run autonomously.',
            'footer_product'    => 'Product',
            'footer_features'   => 'Features',
            'footer_company'    => 'Company',
            'footer_legal'      => 'Legal',
            'footer_copy'       => '© 2025 MyContentPilot. All rights reserved.',
            'footer_tagline'    => 'AI Content Operations Platform',
            'imp_title'         => 'Legal Notice',
            'imp_link'          => 'Legal Notice',
            'dse_title'         => 'Privacy Policy',
            'dse_link'          => 'Privacy Policy',
            'close'             => 'Close',
            /* --- Impressum-specific keys (EN) --- */
            'imp_s1_heading'    => 'Legal Notice (Impressum)',
            'imp_s2_heading'    => 'Information pursuant to § 5 TMG',
            'imp_s2_name_label' => 'Provider',
            'imp_s2_name'       => 'MyContentPilot',
            'imp_s2_owner'      => 'Iqbal Nazir',
            'imp_s2_street'     => 'Anemonenstr. 5/1',
            'imp_s2_city'       => '70771 Leinfelden-Echterdingen',
            'imp_s2_country'    => 'Germany',
            'imp_s3_heading'    => 'Contact',
            'imp_s3_email_label'=> 'Email',
            'imp_s3_email'      => 'info@germanysupport.de',
            'imp_s4_heading'    => 'VAT Identification',
            'imp_s4_body'       => 'VAT identification number pursuant to § 27a of the German VAT Act (UStG): DE342878499',
            'imp_s5_heading'    => 'Responsible for content pursuant to § 18 para. 2 MStV',
            'imp_s5_name'       => 'Iqbal Nazir',
            'imp_s5_street'     => 'Anemonenstr. 5/1',
            'imp_s5_city'       => '70771 Leinfelden-Echterdingen',
            'imp_s5_country'    => 'Germany',
            'imp_s6_heading'    => 'Liability for Content',
            'imp_s6_body'       => 'As a service provider, we are responsible for our own content on these pages in accordance with § 7 para. 1 TMG and general law. However, pursuant to §§ 8 to 10 TMG, we are not obligated to monitor transmitted or stored third-party information or to investigate circumstances indicating unlawful activity. Obligations to remove or block the use of information under general law remain unaffected. Liability in this regard is only possible from the time of knowledge of a specific infringement. Upon becoming aware of such violations, we will remove the relevant content immediately.',
            'imp_s7_heading'    => 'Liability for Links',
            'imp_s7_body'       => 'Our offering contains links to external third-party websites over whose content we have no control. We therefore cannot accept any liability for such external content. The respective provider or operator of the linked pages is always responsible for their content. The linked pages were checked for possible legal violations at the time of linking. No illegal content was apparent at the time of linking. Permanent monitoring of the linked pages is not reasonable without concrete evidence of a legal violation. Upon becoming aware of legal violations, we will remove such links immediately.',
            /* --- Datenschutz-specific keys (EN) --- */
            'dse_s1_heading'        => 'Controller (Responsible Party)',
            'dse_s1_label_name'     => 'Name',
            'dse_s1_name'           => 'MyContentPilot',
            'dse_s1_label_owner'    => 'Owner',
            'dse_s1_owner'          => 'Iqbal Nazir',
            'dse_s1_label_email'    => 'Email',
            'dse_s1_email'          => 'contact@mycontentpilot.de',
            'dse_s1_body'           => 'The controller within the meaning of the General Data Protection Regulation (GDPR) and other national data protection laws, as well as other data protection regulations, is the natural person named above.',
            'dse_s2_heading'        => 'Server Log Files',
            'dse_s2_body'           => 'The hosting provider of this website automatically collects and stores information in server log files that your browser transmits automatically. The following data is recorded: IP address of the requesting device, date and time of access, name and URL of the retrieved file, website from which access is made (referrer URL), browser used and, if applicable, the operating system of your device and the name of your access provider.',
            'dse_s2_purpose'        => 'This data is processed to ensure a smooth connection, system-side security, and the technical stability of the website.',
            'dse_s2_legal_label'    => 'Legal basis',
            'dse_s2_legal'          => 'Art. 6(1)(f) GDPR (legitimate interest). The legitimate interest consists in the secure and stable provision of the service.',
            'dse_s3_heading'        => 'Contact Form & Waitlist (Fluent Forms)',
            'dse_s3_body'           => 'This website provides a contact form via the WordPress plugin Fluent Forms (Form ID 1). When you use the form to register for early access to MyContentPilot, your email address is collected and stored.',
            'dse_s3_purpose_label'  => 'Purpose of processing',
            'dse_s3_purpose'        => 'The collected email address is used solely to notify you about the availability of MyContentPilot early access and to send relevant product information.',
            'dse_s3_legal_label'    => 'Legal basis',
            'dse_s3_legal'          => 'Art. 6(1)(a) GDPR (consent) and/or Art. 6(1)(f) GDPR (legitimate interest in direct communication with prospective users).',
            'dse_s3_third_label'    => 'Disclosure to third parties',
            'dse_s3_third'          => 'Your data will not be shared with, sold to, or used for advertising purposes of any third party.',
            'dse_s3_deletion_label' => 'Deletion',
            'dse_s3_deletion'       => 'You may request deletion of your data at any time by sending an informal email to contact@mycontentpilot.de. Your data will be deleted promptly unless statutory retention obligations apply.',
            'dse_s4_heading'        => 'Your Rights as a Data Subject',
            'dse_s4_intro'          => 'Under the GDPR, you have the following rights. To exercise your rights, please contact: contact@mycontentpilot.de',
            'dse_s4_r1_label'       => 'Right of access — Art. 15 GDPR',
            'dse_s4_r1_body'        => 'You have the right to request confirmation as to whether personal data concerning you is being processed, and to obtain access to that data along with further information as specified in Art. 15 GDPR.',
            'dse_s4_r2_label'       => 'Right to rectification — Art. 16 GDPR',
            'dse_s4_r2_body'        => 'You have the right to demand the immediate correction of inaccurate personal data concerning you, as well as the completion of incomplete personal data.',
            'dse_s4_r3_label'       => 'Right to erasure — Art. 17 GDPR',
            'dse_s4_r3_body'        => 'You have the right to request the immediate deletion of personal data concerning you, provided the statutory conditions are met.',
            'dse_s4_r4_label'       => 'Right to restriction of processing — Art. 18 GDPR',
            'dse_s4_r4_body'        => 'You have the right to request the restriction of processing of your personal data if any of the conditions set out in Art. 18 GDPR are met.',
            'dse_s4_r5_label'       => 'Right to data portability — Art. 20 GDPR',
            'dse_s4_r5_body'        => 'You have the right to receive personal data concerning you in a structured, commonly used, and machine-readable format, and to transmit that data to another controller.',
            'dse_s4_r6_label'       => 'Right to object — Art. 21 GDPR',
            'dse_s4_r6_body'        => 'You have the right to object at any time, on grounds relating to your particular situation, to the processing of personal data concerning you which is carried out on the basis of Art. 6(1)(e) or (f) GDPR.',
            'dse_s4_complaint'      => 'Without prejudice to any other administrative or judicial remedy, you have the right to lodge a complaint with a supervisory authority, in particular in the Member State of your habitual residence, place of work or place of the alleged infringement, if you consider that the processing of personal data relating to you infringes the GDPR.',
        ]
    ]);
}
/* ============================================================
   RENDER FUNCTIONS
   ============================================================ */

function render_nav() { ?>
<nav id="main-nav" class="fixed top-0 left-0 right-0 z-50" role="navigation" aria-label="Main navigation">
    <div class="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <!-- Logo -->
        <a href="#" class="flex items-center gap-3 no-underline" aria-label="MyContentPilot Home">
            <div style="width:32px;height:32px;background:linear-gradient(135deg,#3B82F6,#8B5CF6);border-radius:8px;display:flex;align-items:center;justify-content:center;font-family:'DM Mono',monospace;font-size:13px;font-weight:500;color:white;">MCP</div>
            <span style="font-family:'Syne',sans-serif;font-weight:700;font-size:18px;color:white;">MyContentPilot</span>
            <span class="badge badge-blue hidden md:inline-flex" data-i18n="badge_ops">AI Content Operations</span>
        </a>

        <!-- Center nav (desktop) -->
        <div class="hidden md:flex items-center gap-8">
            <a href="#features" class="text-sm text-slate-400 hover:text-white transition-colors no-underline" data-i18n="nav_features">Funktionen</a>
            <a href="#platform" class="text-sm text-slate-400 hover:text-white transition-colors no-underline" data-i18n="nav_platform">Plattform</a>
            <a href="#pricing" class="text-sm text-slate-400 hover:text-white transition-colors no-underline" data-i18n="nav_pricing">Preise</a>
            <a href="#faq" class="text-sm text-slate-400 hover:text-white transition-colors no-underline" data-i18n="nav_faq">FAQ</a>
        </div>

        <!-- Right -->
        <div class="flex items-center gap-3">
            <!-- Lang switcher -->
            <div class="flex items-center gap-1 border border-white/10 rounded-lg p-1" role="group" aria-label="Language selector">
                <button class="lang-btn active" id="lang-de" onclick="setLang('de')" aria-pressed="true">DE</button>
                <button class="lang-btn" id="lang-en" onclick="setLang('en')" aria-pressed="false">EN</button>
            </div>
            <a href="#waitlist" class="btn-primary hidden sm:inline-flex" data-i18n="nav_cta">Frühzugang sichern</a>
        </div>
    </div>
</nav>
<?php }

function render_hero() { ?>
<section class="grid-bg relative min-h-screen flex items-center pt-20" id="hero">
    <!-- Ambient glow -->
    <div style="position:absolute;top:20%;left:50%;transform:translateX(-50%);width:600px;height:400px;background:radial-gradient(ellipse,rgba(59,130,246,0.12) 0%,transparent 70%);pointer-events:none;"></div>
    <div style="position:absolute;top:40%;right:5%;width:300px;height:300px;background:radial-gradient(ellipse,rgba(139,92,246,0.08) 0%,transparent 70%);pointer-events:none;"></div>

    <div class="max-w-7xl mx-auto px-6 py-24 w-full">
        <div class="max-w-4xl mx-auto text-center">

            <!-- Status badge -->
            <div class="flex items-center justify-center gap-2 mb-8">
                <div class="pulse-dot"></div>
                <span class="mono text-xs text-slate-500 tracking-widest uppercase">System Online — v2.0 Production</span>
            </div>

            <!-- Headline -->
            <h1 class="text-5xl md:text-6xl lg:text-7xl font-bold mb-6 text-glow" style="letter-spacing:-0.03em;" data-i18n="hero_h1">
                Automatisieren Sie Ihre Content-Produktion mit KI
            </h1>

            <!-- Sub -->
            <p class="text-lg md:text-xl text-slate-400 mb-10 max-w-2xl mx-auto leading-relaxed" data-i18n="hero_sub">
                MyContentPilot überwacht RSS-Feeds, verarbeitet Artikel mit KI, generiert Mediendateien, veröffentlicht automatisch auf WordPress und verteilt Inhalte über alle Social-Media-Kanäle — vollständig automatisiert.
            </p>

            <!-- CTAs -->
            <div class="flex flex-wrap items-center justify-center gap-4 mb-14">
                <a href="#waitlist" class="btn-primary" data-i18n="hero_cta">
                    Frühzugang sichern
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M3 8h10M9 4l4 4-4 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
                </a>
                <a href="#architecture" class="btn-secondary" data-i18n="hero_cta2">
                    Plattform-Architektur
                </a>
            </div>

            <!-- Trust row -->
            <div class="flex flex-wrap items-center justify-center gap-3">
                <?php
                $trust = [
                    ['trust_1','Multi-Brand','badge-blue'],
                    ['trust_2','WordPress Ready','badge-green'],
                    ['trust_3','Social Automation','badge-blue'],
                    ['trust_4','KI-gesteuert','badge-purple'],
                ];
                foreach ($trust as $t): ?>
                <span class="badge <?php echo $t[2]; ?>" data-i18n="<?php echo $t[0]; ?>"><?php echo $t[1]; ?></span>
                <?php endforeach; ?>
            </div>
        </div>

        <!-- Hero form card -->
        <div id="waitlist" class="mt-20 max-w-xl mx-auto">
            <div class="card p-8 glow-blue">
                <div class="text-center mb-6">
                    <h2 class="text-xl font-bold mb-1" data-i18n="waitlist_title">Früher Zugang</h2>
                    <p class="text-slate-400 text-sm" data-i18n-html="waitlist_sub">Bereits <strong>237+ Unternehmen</strong> haben Interesse registriert.</p>
                </div>
                <?php
                if (class_exists('FluentForm\App\Modules\Form\Form')) {
                    echo do_shortcode('[fluentform id="6"]');
                } else {
                    echo '<div class="p-4 bg-amber-950/40 border border-amber-500/30 rounded text-amber-200 text-sm" data-i18n="form_notice">System-Hinweis: Bitte aktivieren Sie Fluent Forms und konfigurieren Sie Formular ID 6 im WordPress-Adminbereich.</div>';
                }
                ?>
            </div>
        </div>
    </div>
</section>
<?php }

function render_architecture() { ?>
<section id="architecture" class="py-24 relative">
    <div style="position:absolute;inset:0;background:linear-gradient(180deg,transparent,rgba(59,130,246,0.03),transparent);pointer-events:none;"></div>
    <div class="max-w-7xl mx-auto px-6">
        <div class="text-center mb-16">
            <p class="section-label mb-4" data-i18n="arch_title">Die Plattform-Architektur</p>
            <h2 class="text-4xl md:text-5xl font-bold gradient-text mb-4" data-i18n="arch_title">Die Plattform-Architektur</h2>
            <p class="text-slate-400 max-w-xl mx-auto" data-i18n="arch_sub">Von der Quelle bis zur Veröffentlichung — vollständig automatisiert.</p>
        </div>

        <!-- Flow layout -->
        <div class="max-w-2xl mx-auto">
            <?php
            $nodes = [
                ['icon' => '📡', 'key' => '1', 'color' => 'blue'],
                ['icon' => '🤖', 'key' => '2', 'color' => 'purple'],
                ['icon' => '🏷️', 'key' => '3', 'color' => 'blue'],
                ['icon' => '🖼️', 'key' => '4', 'color' => 'green'],
                ['icon' => '🌐', 'key' => '5', 'color' => 'blue'],
                ['icon' => '📣', 'key' => '6', 'color' => 'green'],
            ];
            $colors = ['blue' => '#3B82F6', 'purple' => '#8B5CF6', 'green' => '#10B981'];
            foreach ($nodes as $i => $node):
                $c = $colors[$node['color']];
            ?>
            <div class="arch-node mb-2 flex items-center gap-4">
                <div style="width:44px;height:44px;border-radius:10px;background:<?php echo $c; ?>18;border:1px solid <?php echo $c; ?>30;display:flex;align-items:center;justify-content:center;font-size:20px;flex-shrink:0;" aria-hidden="true">
                    <?php echo $node['icon']; ?>
                </div>
                <div class="flex-1 min-w-0">
                    <div class="font-semibold text-white text-sm" data-i18n="arch_node_<?php echo $node['key']; ?>">—</div>
                    <div class="mono text-xs text-slate-500 mt-0.5" data-i18n="arch_node_<?php echo $node['key']; ?>_d">—</div>
                </div>
                <div class="badge" style="background:<?php echo $c; ?>12;border:1px solid <?php echo $c; ?>30;color:<?php echo $c; ?>;">
                    <span style="width:6px;height:6px;border-radius:50%;background:<?php echo $c; ?>;"></span>
                    <?php if ($i === 0 || $i === 1): ?>Active<?php else: ?>Ready<?php endif; ?>
                </div>
            </div>
            <?php if ($i < count($nodes) - 1): ?>
            <div class="pipe-line" style="height:32px;margin-bottom:2px;" aria-hidden="true"></div>
            <?php endif; ?>
            <?php endforeach; ?>
        </div>
    </div>
</section>
<?php }

function render_features() { ?>
<section id="features" class="py-24">
    <div class="max-w-7xl mx-auto px-6">
        <div class="text-center mb-16">
            <p class="section-label mb-3" data-i18n="feat_title">Features</p>
            <h2 class="text-4xl md:text-5xl font-bold mb-4" data-i18n="feat_title">Alles was Sie brauchen</h2>
            <p class="text-slate-400 max-w-xl mx-auto" data-i18n="feat_sub">Eine Plattform für den gesamten Content-Lifecycle.</p>
        </div>

        <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-5">
            <?php
            $features = [
                ['icon' => '📡', 'key' => '1', 'color' => '#3B82F6'],
                ['icon' => '🤖', 'key' => '2', 'color' => '#8B5CF6'],
                ['icon' => '🏷️', 'key' => '3', 'color' => '#06B6D4'],
                ['icon' => '🌐', 'key' => '4', 'color' => '#10B981'],
                ['icon' => '📣', 'key' => '5', 'color' => '#F59E0B'],
                ['icon' => '🖼️', 'key' => '6', 'color' => '#EC4899'],
                ['icon' => '⏰', 'key' => '7', 'color' => '#3B82F6'],
                ['icon' => '🔍', 'key' => '8', 'color' => '#8B5CF6'],
                ['icon' => '⚡', 'key' => '9', 'color' => '#10B981'],
            ];
            foreach ($features as $f): ?>
            <article class="card p-6">
                <div class="icon-wrap mb-4" style="background:<?php echo $f['color']; ?>15;border:1px solid <?php echo $f['color']; ?>25;" aria-hidden="true">
                    <span style="font-size:20px;"><?php echo $f['icon']; ?></span>
                </div>
                <h3 class="font-semibold text-white mb-2" data-i18n="feat_<?php echo $f['key']; ?>_t">—</h3>
                <p class="text-slate-400 text-sm leading-relaxed" data-i18n="feat_<?php echo $f['key']; ?>_d">—</p>
            </article>
            <?php endforeach; ?>
        </div>
    </div>
</section>
<?php }

function render_platform_state() { ?>
<section id="platform" class="py-24 relative">
    <div style="position:absolute;inset:0;background:linear-gradient(180deg,transparent,rgba(16,185,129,0.02),transparent);pointer-events:none;"></div>
    <div class="max-w-7xl mx-auto px-6">
        <div class="text-center mb-16">
            <p class="section-label mb-3">System Status</p>
            <h2 class="text-4xl md:text-5xl font-bold mb-4" data-i18n="platform_title">Plattform-Architektur</h2>
            <p class="text-slate-400 max-w-xl mx-auto" data-i18n="platform_sub">Produktionsreife Infrastruktur — gebaut für Zuverlässigkeit.</p>
        </div>

        <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-5">
            <?php
            $modules = [
                [
                    'title' => 'Core Scheduler Engine',
                    'status' => 'platform_stable',
                    'color' => '#10B981',
                    'items' => ['APScheduler', 'SQLite WAL', 'Persistent scheduling', 'Cron-based jobs'],
                    'icon' => '⚙️',
                ],
                [
                    'title' => 'AI Routing Layer',
                    'status' => 'platform_stable',
                    'color' => '#8B5CF6',
                    'items' => ['Anthropic / Claude', 'DeepSeek', 'Provider abstraction', 'Retry-aware execution'],
                    'icon' => '🧠',
                ],
                [
                    'title' => 'Ingestion Pipelines',
                    'status' => 'platform_stable',
                    'color' => '#3B82F6',
                    'items' => ['RSS & Atom', 'Feed normalization', 'Duplicate detection', 'Fingerprinting'],
                    'icon' => '📥',
                ],
                [
                    'title' => 'Asset Generation Engine',
                    'status' => 'platform_ready',
                    'color' => '#F59E0B',
                    'items' => ['DALL-E 3', 'Pexels integration', 'Brand templates', 'Social layouts'],
                    'icon' => '🎨',
                ],
                [
                    'title' => 'Distribution Nodes',
                    'status' => 'platform_stable',
                    'color' => '#06B6D4',
                    'items' => ['WordPress REST API', 'Facebook publishing', 'Instagram adapter', 'Multi-target routing'],
                    'icon' => '📤',
                ],
                [
                    'title' => 'Observability Layer',
                    'status' => 'platform_stable',
                    'color' => '#10B981',
                    'items' => ['Structured logging', 'SQLite persistence', 'Execution tracking', 'Failure notifications'],
                    'icon' => '📊',
                ],
            ];
            foreach ($modules as $m): ?>
            <div class="card p-6">
                <div class="flex items-start justify-between mb-4">
                    <div class="flex items-center gap-3">
                        <span style="font-size:22px;" aria-hidden="true"><?php echo $m['icon']; ?></span>
                        <h3 class="font-semibold text-white text-sm"><?php echo esc_html($m['title']); ?></h3>
                    </div>
                    <span class="badge" style="background:<?php echo $m['color']; ?>15;border:1px solid <?php echo $m['color']; ?>30;color:<?php echo $m['color']; ?>;font-size:10px;" data-i18n="<?php echo $m['status']; ?>">—</span>
                </div>
                <ul class="space-y-1.5" role="list">
                    <?php foreach ($m['items'] as $item): ?>
                    <li class="flex items-center gap-2 text-sm text-slate-400">
                        <svg width="12" height="12" viewBox="0 0 12 12" fill="none" aria-hidden="true"><path d="M2 6l3 3 5-5" stroke="<?php echo $m['color']; ?>" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
                        <?php echo esc_html($item); ?>
                    </li>
                    <?php endforeach; ?>
                </ul>
            </div>
            <?php endforeach; ?>
        </div>
    </div>
</section>
<?php }

function render_pricing() { ?>
<section id="pricing" class="py-24">
    <div class="max-w-7xl mx-auto px-6">
        <div class="text-center mb-16">
            <p class="section-label mb-3">Pricing</p>
            <h2 class="text-4xl md:text-5xl font-bold mb-4" data-i18n="pricing_title">Preise</h2>
            <p class="text-slate-400 max-w-xl mx-auto" data-i18n="pricing_sub">Transparent. Skalierbar. Für jede Unternehmensgröße.</p>
        </div>

        <div class="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
            <?php
            $plans = [
                ['key' => 'starter', 'popular' => false],
                ['key' => 'pro', 'popular' => true],
                ['key' => 'ent', 'popular' => false],
            ];
            foreach ($plans as $plan): ?>
            <div class="card p-8 flex flex-col <?php echo $plan['popular'] ? 'pricing-recommended' : ''; ?>">
                <?php if ($plan['popular']): ?>
                <div class="mb-4">
                    <span class="badge badge-blue" data-i18n="pricing_popular">Empfohlen</span>
                </div>
                <?php endif; ?>
                <h3 class="text-2xl font-bold mb-2" data-i18n="pricing_<?php echo $plan['key']; ?>">—</h3>
                <p class="text-slate-400 text-sm mb-6" data-i18n="pricing_<?php echo $plan['key']; ?>_d">—</p>
                <div class="flex-1 flex items-center justify-center py-8">
                    <div class="text-center">
                        <div style="font-family:'Syne',sans-serif;font-size:1.1rem;font-weight:700;color:#64748B;letter-spacing:0.05em;" data-i18n="pricing_soon">Demnächst verfügbar</div>
                        <div class="mono text-xs text-slate-600 mt-2">Early Access Preise folgen</div>
                    </div>
                </div>
                <a href="#waitlist" class="<?php echo $plan['popular'] ? 'btn-primary justify-center' : 'btn-secondary justify-center'; ?> mt-6 w-full" data-i18n="nav_cta" style="<?php echo $plan['popular'] ? '' : 'text-align:center;'; ?>">
                    Frühzugang sichern
                </a>
            </div>
            <?php endforeach; ?>
        </div>
    </div>
</section>
<?php }

function render_faq() { ?>
<section id="faq" class="py-24">
    <div class="max-w-3xl mx-auto px-6">
        <div class="text-center mb-16">
            <p class="section-label mb-3">FAQ</p>
            <h2 class="text-4xl font-bold mb-4" data-i18n="faq_title">Häufige Fragen</h2>
            <p class="text-slate-400" data-i18n="faq_sub">Alles Wichtige auf einen Blick.</p>
        </div>

        <div id="faq-list" class="space-y-2">
            <?php for ($i = 1; $i <= 12; $i++): ?>
            <div class="card">
                <button
                    class="w-full flex items-center justify-between p-5 text-left"
                    onclick="toggleFaq(this)"
                    aria-expanded="false"
                >
                    <span class="font-medium text-white pr-4" data-i18n="faq_<?php echo $i; ?>_q">—</span>
                    <span class="faq-icon text-slate-400 text-xl flex-shrink-0" aria-hidden="true">+</span>
                </button>
                <div class="faq-content" role="region">
                    <p class="px-5 pb-5 text-slate-400 text-sm leading-relaxed" data-i18n="faq_<?php echo $i; ?>_a">—</p>
                </div>
            </div>
            <?php endfor; ?>
        </div>
    </div>
</section>
<?php }

function render_footer() { ?>
<footer class="border-t border-white/5 py-16">
    <div class="max-w-7xl mx-auto px-6">
        <div class="grid grid-cols-2 md:grid-cols-5 gap-8 mb-12">
            <!-- Brand col -->
            <div class="col-span-2">
                <div class="flex items-center gap-2 mb-4">
                    <div style="width:28px;height:28px;background:linear-gradient(135deg,#3B82F6,#8B5CF6);border-radius:6px;display:flex;align-items:center;justify-content:center;font-family:'DM Mono',monospace;font-size:11px;color:white;">MCP</div>
                    <span style="font-family:'Syne',sans-serif;font-weight:700;font-size:16px;">MyContentPilot</span>
                </div>
                <p class="text-slate-500 text-sm" data-i18n="footer_tagline">KI Content Operations Platform</p>
            </div>

            <!-- Product -->
            <div>
                <h4 class="mono text-xs text-slate-500 uppercase tracking-widest mb-4" data-i18n="footer_product">Produkt</h4>
                <ul class="space-y-2" role="list">
                    <li><a href="#features" class="text-sm text-slate-400 hover:text-white transition-colors no-underline" data-i18n="nav_features">Funktionen</a></li>
                    <li><a href="#platform" class="text-sm text-slate-400 hover:text-white transition-colors no-underline" data-i18n="nav_platform">Plattform</a></li>
                    <li><a href="#pricing" class="text-sm text-slate-400 hover:text-white transition-colors no-underline" data-i18n="nav_pricing">Preise</a></li>
                </ul>
            </div>

            <!-- Features -->
            <div>
                <h4 class="mono text-xs text-slate-500 uppercase tracking-widest mb-4" data-i18n="footer_features">Funktionen</h4>
                <ul class="space-y-2" role="list">
                    <li><span class="text-sm text-slate-400">RSS Ingestion</span></li>
                    <li><span class="text-sm text-slate-400">AI Generation</span></li>
                    <li><span class="text-sm text-slate-400">WordPress API</span></li>
                    <li><span class="text-sm text-slate-400">Social Publishing</span></li>
                </ul>
            </div>

            <!-- Legal -->
            <div>
                <h4 class="mono text-xs text-slate-500 uppercase tracking-widest mb-4" data-i18n="footer_legal">Rechtliches</h4>
                <ul class="space-y-2" role="list">
                    <li>
                        <button onclick="openModal('modal-impressum')" class="text-sm text-slate-400 hover:text-white transition-colors bg-transparent border-0 cursor-pointer p-0" data-i18n="imp_link">Impressum</button>
                    </li>
                    <li>
                        <button onclick="openModal('modal-dse')" class="text-sm text-slate-400 hover:text-white transition-colors bg-transparent border-0 cursor-pointer p-0" data-i18n="dse_link">Datenschutz</button>
                    </li>
                </ul>
            </div>
        </div>

        <div class="border-t border-white/5 pt-8 flex flex-col md:flex-row items-center justify-between gap-4">
            <p class="text-slate-600 text-sm" data-i18n="footer_copy">© 2025 MyContentPilot. Alle Rechte vorbehalten.</p>
            <div class="flex items-center gap-2">
                <div class="pulse-dot" aria-hidden="true"></div>
                <span class="mono text-xs text-slate-600">All Systems Operational</span>
            </div>
        </div>
    </div>
</footer>
<?php }

function render_modals() { ?>
<!-- Impressum Modal -->
<div id="modal-impressum" class="modal-overlay" role="dialog" aria-modal="true" aria-labelledby="impressum-title">
    <div class="modal-box">

        <!-- Header -->
        <div class="flex items-center justify-between mb-8">
            <h2 id="impressum-title" class="text-2xl font-bold text-white" data-i18n="imp_s1_heading">Impressum</h2>
            <button
                onclick="closeModal('modal-impressum')"
                class="btn-secondary"
                style="padding:6px 14px;"
                data-i18n="close"
                aria-label="Close modal"
            >Schließen</button>
        </div>

        <div class="space-y-8 text-sm text-slate-300">

            <!-- § 5 TMG -->
            <section aria-labelledby="imp-sec2">
                <h3 id="imp-sec2" class="text-xs font-semibold uppercase tracking-widest text-slate-500 mb-3 font-mono" data-i18n="imp_s2_heading">Angaben gemäß § 5 TMG</h3>
                <div class="bg-white/[0.03] border border-white/[0.06] rounded-xl p-5 space-y-1 leading-relaxed">
                    <p class="font-semibold text-white" data-i18n="imp_s2_name">MyContentPilot</p>
                    <p data-i18n="imp_s2_owner">Iqbal Nazir</p>
                    <p data-i18n="imp_s2_street">Anemonenstr. 5/1</p>
                    <p data-i18n="imp_s2_city">70771 Leinfelden-Echterdingen</p>
                    <p data-i18n="imp_s2_country">Deutschland</p>
                </div>
            </section>

            <!-- Kontakt -->
            <section aria-labelledby="imp-sec3">
                <h3 id="imp-sec3" class="text-xs font-semibold uppercase tracking-widest text-slate-500 mb-3 font-mono" data-i18n="imp_s3_heading">Kontakt</h3>
                <div class="bg-white/[0.03] border border-white/[0.06] rounded-xl p-5">
                    <p class="text-sm text-slate-300">
                        <span data-i18n="imp_s3_email_label" class="text-slate-500"></span>
                        <a href="mailto:info@germanysupport.de"
                           class="text-blue-400 hover:text-blue-300 transition-colors">
                            <span data-i18n="imp_s3_email">info@germanysupport.de</span>
                        </a>
                    </p>
                </div>
            </section>

            <!-- Umsatzsteuer -->
            <section aria-labelledby="imp-sec4">
                <h3 id="imp-sec4" class="text-xs font-semibold uppercase tracking-widest text-slate-500 mb-3 font-mono" data-i18n="imp_s4_heading">Umsatzsteuer</h3>
                <div class="bg-white/[0.03] border border-white/[0.06] rounded-xl p-5">
                    <p data-i18n="imp_s4_body">Umsatzsteuer-Identifikationsnummer gemäß § 27a Umsatzsteuergesetz: DE342878499</p>
                </div>
            </section>

            <!-- § 18 Abs. 2 MStV -->
            <section aria-labelledby="imp-sec5">
                <h3 id="imp-sec5" class="text-xs font-semibold uppercase tracking-widest text-slate-500 mb-3 font-mono" data-i18n="imp_s5_heading">Verantwortlich für den Inhalt nach § 18 Abs. 2 MStV</h3>
                <div class="bg-white/[0.03] border border-white/[0.06] rounded-xl p-5 space-y-1 leading-relaxed">
                    <p class="font-semibold text-white" data-i18n="imp_s5_name">Iqbal Nazir</p>
                    <p data-i18n="imp_s5_street">Anemonenstr. 5/1</p>
                    <p data-i18n="imp_s5_city">70771 Leinfelden-Echterdingen</p>
                    <p data-i18n="imp_s5_country">Deutschland</p>
                </div>
            </section>

            <!-- Haftung für Inhalte -->
            <section aria-labelledby="imp-sec6">
                <h3 id="imp-sec6" class="text-xs font-semibold uppercase tracking-widest text-slate-500 mb-3 font-mono" data-i18n="imp_s6_heading">Haftung für Inhalte</h3>
                <div class="bg-white/[0.03] border border-white/[0.06] rounded-xl p-5">
                    <p class="leading-relaxed" data-i18n="imp_s6_body">Als Diensteanbieter sind wir gemäß § 7 Abs. 1 TMG für eigene Inhalte auf diesen Seiten nach den allgemeinen Gesetzen verantwortlich.</p>
                </div>
            </section>

            <!-- Haftung für Links -->
            <section aria-labelledby="imp-sec7">
                <h3 id="imp-sec7" class="text-xs font-semibold uppercase tracking-widest text-slate-500 mb-3 font-mono" data-i18n="imp_s7_heading">Haftung für Links</h3>
                <div class="bg-white/[0.03] border border-white/[0.06] rounded-xl p-5">
                    <p class="leading-relaxed" data-i18n="imp_s7_body">Unser Angebot enthält Links zu externen Websites Dritter, auf deren Inhalte wir keinen Einfluss haben.</p>
                </div>
            </section>

        </div>
    </div>
</div>

<!-- Datenschutz Modal -->
<div id="modal-dse" class="modal-overlay" role="dialog" aria-modal="true" aria-labelledby="dse-title">
    <div class="modal-box">
        <div class="flex items-center justify-between mb-6">
            <h2 id="dse-title" class="text-2xl font-bold" data-i18n="dse_title">Datenschutzerklärung</h2>
            <button onclick="closeModal('modal-dse')" class="btn-secondary" style="padding:6px 14px;" data-i18n="close" aria-label="Close modal">Schließen</button>
        </div>
        <div class="prose prose-invert text-slate-300 text-sm space-y-4">
            <h3 class="text-white font-semibold">1. Datenschutz auf einen Blick</h3>
            <p>Diese Datenschutzerklärung klärt Sie über die Art, den Umfang und Zweck der Verarbeitung von personenbezogenen Daten auf dieser Website auf.</p>

            <h3 class="text-white font-semibold">2. Datenerhebung</h3>
            <p>Wir erheben und verarbeiten personenbezogene Daten nur, wenn Sie uns diese freiwillig mitteilen (z. B. bei der Anmeldung zur Warteliste).</p>

            <h3 class="text-white font-semibold">3. Verwendung der Daten</h3>
            <p>Ihre Daten werden ausschließlich zur Kontaktaufnahme und Bereitstellung des Early Access verwendet. Eine Weitergabe an Dritte findet nicht statt.</p>

            <h3 class="text-white font-semibold">4. Ihre Rechte</h3>
            <p>Sie haben das Recht auf Auskunft, Berichtigung, Löschung und Einschränkung der Verarbeitung Ihrer Daten. Kontaktieren Sie uns unter: contact@mycontentpilot.de</p>

            <p class="text-slate-500 text-xs">Diese Datenschutzerklärung ist ein Entwurf. Bitte lassen Sie sie von einem Rechtsanwalt prüfen.</p>
        </div>
    </div>
</div>
<?php }

/* ============================================================
   RENDER PAGE
   ============================================================ */
render_nav();
render_hero();
render_architecture();
render_features();
render_platform_state();
render_pricing();
render_faq();
render_footer();
render_modals();
?>

<!-- ============================================================
     JAVASCRIPT
     ============================================================ -->
<script>
(function() {
    /* ---- Translation data ---- */
    const T = <?php echo mcp_translations_json(); ?>;

    let currentLang = localStorage.getItem('mcp_lang') || 'de';

    function applyTranslations(lang) {
        const t = T[lang];
        if (!t) return;

        // Text nodes
        document.querySelectorAll('[data-i18n]').forEach(el => {
            const key = el.getAttribute('data-i18n');
            if (t[key] !== undefined) el.textContent = t[key];
        });

        // HTML nodes (for bold etc.)
        document.querySelectorAll('[data-i18n-html]').forEach(el => {
            const key = el.getAttribute('data-i18n-html');
            if (t[key] !== undefined) el.innerHTML = t[key];
        });

        // Lang buttons
        document.getElementById('lang-de').classList.toggle('active', lang === 'de');
        document.getElementById('lang-de').setAttribute('aria-pressed', lang === 'de');
        document.getElementById('lang-en').classList.toggle('active', lang === 'en');
        document.getElementById('lang-en').setAttribute('aria-pressed', lang === 'en');
    }

    window.setLang = function(lang) {
        currentLang = lang;
        localStorage.setItem('mcp_lang', lang);
        applyTranslations(lang);
    };

    /* ---- FAQ accordion ---- */
    window.toggleFaq = function(btn) {
        const content = btn.nextElementSibling;
        const icon = btn.querySelector('.faq-icon');
        const isOpen = content.classList.contains('open');

        // Close all
        document.querySelectorAll('.faq-content').forEach(c => c.classList.remove('open'));
        document.querySelectorAll('.faq-icon').forEach(i => i.classList.remove('open'));
        document.querySelectorAll('#faq-list button').forEach(b => b.setAttribute('aria-expanded', 'false'));

        if (!isOpen) {
            content.classList.add('open');
            icon.classList.add('open');
            btn.setAttribute('aria-expanded', 'true');
        }
    };

    /* ---- Modals ---- */
    window.openModal = function(id) {
        const modal = document.getElementById(id);
        modal.classList.add('open');
        document.body.style.overflow = 'hidden';

        // Focus first focusable element
        const focusable = modal.querySelectorAll('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
        if (focusable.length) focusable[0].focus();

        // Trap focus
        modal._trapFn = function(e) {
            if (e.key === 'Escape') { window.closeModal(id); return; }
            if (e.key !== 'Tab') return;
            const els = Array.from(modal.querySelectorAll('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'));
            const first = els[0], last = els[els.length - 1];
            if (e.shiftKey ? document.activeElement === first : document.activeElement === last) {
                e.preventDefault();
                (e.shiftKey ? last : first).focus();
            }
        };
        modal.addEventListener('keydown', modal._trapFn);

        // Click outside to close
        modal._clickFn = function(e) { if (e.target === modal) window.closeModal(id); };
        modal.addEventListener('click', modal._clickFn);
    };

    window.closeModal = function(id) {
        const modal = document.getElementById(id);
        modal.classList.remove('open');
        document.body.style.overflow = '';
        if (modal._trapFn) modal.removeEventListener('keydown', modal._trapFn);
        if (modal._clickFn) modal.removeEventListener('click', modal._clickFn);
    };

    /* ---- Sticky nav shadow ---- */
    window.addEventListener('scroll', function() {
        const nav = document.getElementById('main-nav');
        if (window.scrollY > 20) {
            nav.style.boxShadow = '0 4px 40px rgba(0,0,0,0.4)';
        } else {
            nav.style.boxShadow = 'none';
        }
    }, { passive: true });

    /* ---- Init ---- */
    applyTranslations(currentLang);
})();
</script>

<?php wp_footer(); ?>
</body>
</html>