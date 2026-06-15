<?php
/**
 * MyContentPilot.de — Allgemeine Geschäftsbedingungen
 * Template: page-agb.php
 * Standard German SaaS AGB
 */
get_header(); ?>

<section class="section" style="padding-top:var(--s-20);">
  <div class="container container--narrow">

    <div style="margin-bottom:var(--s-12);">
      <div class="t-eyebrow" style="margin-bottom:var(--s-4);">Rechtliches</div>
      <h1 class="t-display" style="font-size:var(--t-4xl);margin-bottom:var(--s-4);">
        Allgemeine Geschäftsbedingungen
      </h1>
      <p class="t-lead">
        Nutzungsbedingungen für das MyContentPilot-System und zugehörige Dienstleistungen.
      </p>
      <p style="font-size:var(--t-xs);color:var(--c-text-muted);margin-top:var(--s-3);">
        Stand: <?php echo date('F Y'); ?>
      </p>
    </div>

    <div class="legal-body">

      <!-- §1 Geltungsbereich -->
      <div class="legal-section">
        <h2>§1 Geltungsbereich</h2>
        <p>
          Diese Allgemeinen Geschäftsbedingungen (nachfolgend „AGB") gelten für alle
          Verträge zwischen
        </p>
        <address class="legal-address">
          <strong>Iqbal Nazir</strong><br>
          Anemonenstr. 5/1<br>
          70771 Leinfelden-Echterdingen<br>
          Deutschland<br>
          (nachfolgend „Anbieter")
        </address>
        <p style="margin-top:var(--s-4);">
          und Kunden (nachfolgend „Nutzer") über die entgeltliche Nutzung des
          MyContentPilot-Systems und zugehöriger Supportleistungen.
        </p>
        <p>
          Entgegenstehende oder von diesen AGB abweichende Bedingungen des Nutzers werden
          nicht anerkannt, es sei denn, der Anbieter stimmt ihrer Geltung ausdrücklich
          schriftlich zu. Diese AGB gelten auch dann, wenn der Anbieter in Kenntnis
          entgegenstehender Bedingungen des Nutzers die Leistung vorbehaltlos erbringt.
        </p>
        <p>
          Diese AGB gelten ausschließlich gegenüber Unternehmern im Sinne von §14 BGB.
          Ein Unternehmer ist eine natürliche oder juristische Person oder eine
          rechtsfähige Personengesellschaft, die bei Abschluss eines Rechtsgeschäfts
          in Ausübung ihrer gewerblichen oder selbständigen beruflichen Tätigkeit handelt.
        </p>
      </div>

      <!-- §2 Vertragsgegenstand -->
      <div class="legal-section">
        <h2>§2 Vertragsgegenstand</h2>

        <h3>2.1 Beschreibung des MyContentPilot-Systems</h3>
        <p>
          MyContentPilot ist eine modulare, Docker-basierte Software-Plattform zur
          Automatisierung von Content-Workflows. Das System ermöglicht die automatisierte
          Generierung, Planung und Veröffentlichung von Inhalten auf digitalen Plattformen
          (WordPress, Facebook, Instagram sowie zukünftig weiteren Plattformen).
        </p>
        <p>
          Das System besteht aus folgenden Kernkomponenten:
        </p>
        <ul>
          <li>Modulare Content-Pipelines (daily_news, article_publisher, deals_engine, social_tips, social_video)</li>
          <li>KI-Modell-Abstraktion zur Anbindung externer KI-Anbieter</li>
          <li>Automatisierte Publishing-Adapter für unterstützte Plattformen</li>
          <li>Cron-basiertes Scheduling-System</li>
          <li>Logging- und Monitoring-Infrastruktur</li>
        </ul>

        <h3>2.2 Art der Leistungserbringung</h3>
        <p>
          MyContentPilot ist eine <strong>selbst-gehostete Software</strong> (On-Premise).
          Der Anbieter stellt dem Nutzer das MyContentPilot-System zur Installation und
          zum Betrieb auf der eigenen Serverinfrastruktur des Nutzers bereit.
          Das System wird nicht als Software-as-a-Service (SaaS) auf Infrastruktur
          des Anbieters betrieben.
        </p>
        <p>
          Der Anbieter hat zu keinem Zeitpunkt Zugriff auf den Server des Nutzers,
          die dort gespeicherten Daten, API-Schlüssel, Zugangsdaten zu Social-Media-Plattformen
          oder generierten Inhalte, es sei denn, der Nutzer gewährt dem Anbieter
          ausdrücklich und temporär Zugang zum Zweck des technischen Supports.
        </p>

        <h3>2.3 Nicht im Leistungsumfang enthalten</h3>
        <p>Folgende Leistungen sind ausdrücklich nicht Bestandteil des Vertrages:</p>
        <ul>
          <li>Bereitstellung von Serverinfrastruktur (VPS, Dedicated Server, Cloud)</li>
          <li>API-Kosten externer KI-Anbieter (Anthropic, OpenAI, DeepSeek, Google u. a.)</li>
          <li>API-Kosten oder Werbebudgets für Social-Media-Plattformen</li>
          <li>WordPress-Hosting oder -Lizenzen</li>
          <li>Inhaltliche Qualitätsprüfung der generierten Inhalte</li>
          <li>Rechtliche Prüfung veröffentlichter Inhalte</li>
        </ul>
        <p>
          Der Nutzer trägt alle anfallenden Kosten für externe Dienste und Infrastruktur
          eigenverantwortlich.
        </p>
      </div>

      <!-- §3 Leistungsumfang je Tarif -->
      <div class="legal-section">
        <h2>§3 Leistungsumfang je Tarif</h2>

        <h3>3.1 Starter-Tarif (€49/Monat)</h3>
        <ul>
          <li>Nutzung von MyContentPilot auf 1 Plattform</li>
          <li>Anbindung von 1 KI-Modell-Anbieter</li>
          <li>Bis zu 30 automatisierte Veröffentlichungen pro Monat</li>
          <li>Setup-Dokumentation und Konfigurationsanleitung</li>
          <li>Support per E-Mail (Reaktionszeit: werktags innerhalb von 48 Stunden)</li>
        </ul>

        <h3>3.2 Pro-Tarif (€99/Monat)</h3>
        <ul>
          <li>Nutzung von MyContentPilot auf bis zu 3 Plattformen</li>
          <li>Anbindung aller unterstützten KI-Modell-Anbieter</li>
          <li>Konfiguration eines Fallback-KI-Modells</li>
          <li>Unbegrenzte automatisierte Veröffentlichungen</li>
          <li>WordPress-Publishing-Integration</li>
          <li>Setup-Dokumentation und Konfigurationsanleitung</li>
          <li>Prioritäts-Support per E-Mail (Reaktionszeit: werktags innerhalb von 24 Stunden)</li>
        </ul>

        <h3>3.3 Agentur-Tarif (€199/Monat)</h3>
        <ul>
          <li>Nutzung von MyContentPilot auf unbegrenzt vielen Plattformen</li>
          <li>Multi-Account-Verwaltung (mehrere Kundenaccounts)</li>
          <li>Alle Leistungen des Pro-Tarifs</li>
          <li>Onboarding-Call (einmalig, bis zu 45 Minuten)</li>
          <li>Dedizierter Support-Kanal mit priorisierter Bearbeitung</li>
        </ul>

        <h3>3.4 Individuelle Erweiterungen</h3>
        <p>
          Die Integration zusätzlicher Plattformen, Module oder kundenspezifischer
          Anpassungen kann auf Anfrage und gegen gesonderte Vereinbarung erbracht werden.
          Entsprechende Leistungen werden individuell vereinbart und sind nicht
          Bestandteil dieser AGB.
        </p>
      </div>

      <!-- §4 Vertragsschluss -->
      <div class="legal-section">
        <h2>§4 Vertragsschluss</h2>
        <p>
          Die Darstellung des MyContentPilot-Systems auf der Website mycontentpilot.de
          stellt kein rechtlich bindendes Angebot, sondern eine Aufforderung zur
          Abgabe eines Angebots (invitatio ad offerendum) dar.
        </p>
        <p>
          Der Vertragsschluss erfolgt wie folgt:
        </p>
        <ol>
          <li>Der Nutzer sendet eine Anfrage über das Kontaktformular oder per E-Mail.</li>
          <li>Der Anbieter unterbreitet daraufhin ein individuelles Angebot.</li>
          <li>Der Nutzer nimmt das Angebot schriftlich (per E-Mail) an.</li>
          <li>Der Vertrag kommt mit der Auftragsbestätigung des Anbieters zustande.</li>
        </ol>
        <p>
          Der Anbieter behält sich vor, Anfragen ohne Angabe von Gründen abzulehnen.
        </p>
      </div>

      <!-- §5 Preise & Zahlung -->
      <div class="legal-section">
        <h2>§5 Preise &amp; Zahlung</h2>

        <h3>5.1 Preise</h3>
        <p>
          Alle genannten Preise verstehen sich in Euro (EUR) zuzüglich der gesetzlichen
          Mehrwertsteuer. Die jeweils aktuellen Preise sind auf der Website unter
          mycontentpilot.de/preise einsehbar.
        </p>

        <h3>5.2 Zahlungsmodalitäten</h3>
        <p>
          Die Vergütung ist monatlich im Voraus fällig. Bei jährlicher Vorauszahlung
          gewährt der Anbieter einen Rabatt in Höhe von zwei Monatsbeträgen
          (d. h. 10 Monatsbeiträge anstelle von 12).
        </p>
        <p>Akzeptierte Zahlungsarten:</p>
        <ul>
          <li>SEPA-Überweisung</li>
          <li>PayPal</li>
        </ul>

        <h3>5.3 Verzug</h3>
        <p>
          Bei Zahlungsverzug ist der Anbieter berechtigt, die Leistungserbringung
          bis zum Ausgleich der ausstehenden Beträge auszusetzen und Verzugszinsen
          gemäß §288 BGB zu berechnen. Mahnkosten werden gemäß gesetzlicher Regelung
          in Rechnung gestellt.
        </p>

        <h3>5.4 Preisanpassungen</h3>
        <p>
          Der Anbieter behält sich vor, die Preise mit einer Ankündigungsfrist von
          30 Tagen zum Ende des laufenden Abrechnungszeitraums anzupassen.
          Der Nutzer hat in diesem Fall ein Sonderkündigungsrecht.
        </p>
      </div>

      <!-- §6 Laufzeit & Kündigung -->
      <div class="legal-section">
        <h2>§6 Laufzeit &amp; Kündigung</h2>

        <h3>6.1 Vertragslaufzeit</h3>
        <p>
          Der Vertrag wird auf unbestimmte Zeit geschlossen. Bei monatlicher Zahlung
          beträgt die Mindestlaufzeit einen Monat. Bei jährlicher Vorauszahlung
          beträgt die Mindestlaufzeit zwölf Monate.
        </p>

        <h3>6.2 Ordentliche Kündigung</h3>
        <p>
          Beide Vertragsparteien können den Vertrag mit einer Frist von 14 Tagen
          zum Ende des jeweiligen Abrechnungszeitraums ordentlich kündigen.
          Die Kündigung hat schriftlich per E-Mail an
          <a href="#" class="mcp-email" data-u="info" data-d="mycontentpilot.de">
            info [at] mycontentpilot.de
          </a>
          zu erfolgen.
        </p>

        <h3>6.3 Außerordentliche Kündigung</h3>
        <p>
          Das Recht zur außerordentlichen Kündigung aus wichtigem Grund bleibt
          unberührt. Ein wichtiger Grund liegt insbesondere vor, wenn der Nutzer
          gegen wesentliche Pflichten aus diesen AGB verstößt und trotz schriftlicher
          Abmahnung nicht innerhalb von 14 Tagen Abhilfe schafft.
        </p>

        <h3>6.4 Rückerstattung bei Jahreszahlung</h3>
        <p>
          Bei Kündigung eines Jahresvertrages vor Ablauf der Laufzeit erstattet der
          Anbieter die auf volle Monate entfallenden, noch nicht in Anspruch genommenen
          Vorauszahlungen anteilig zurück. Angefangene Monate werden nicht erstattet.
          Die Rückerstattung erfolgt auf dem ursprünglichen Zahlungsweg innerhalb von
          14 Werktagen nach Wirksamwerden der Kündigung.
        </p>

        <h3>6.5 Folgen der Kündigung</h3>
        <p>
          Nach Wirksamwerden der Kündigung erlischt das Nutzungsrecht des Nutzers
          an der MyContentPilot-Software. Der Nutzer ist verantwortlich für die
          Deinstallation des Systems von seinen Servern. Bereits veröffentlichte
          Inhalte auf Plattformen des Nutzers sind nicht betroffen.
        </p>
      </div>

      <!-- §7 Pflichten des Nutzers -->
      <div class="legal-section">
        <h2>§7 Pflichten des Nutzers</h2>

        <h3>7.1 Technische Voraussetzungen</h3>
        <p>Der Nutzer ist selbst verantwortlich für:</p>
        <ul>
          <li>Bereitstellung und Betrieb geeigneter Serverinfrastruktur (Linux-Server mit Docker-Unterstützung)</li>
          <li>Beschaffung und Verwaltung eigener API-Schlüssel für KI-Anbieter</li>
          <li>Zugangsdaten und Berechtigungen für Social-Media-Plattformen und WordPress</li>
          <li>Sicherheit und Absicherung der eigenen Serverinfrastruktur</li>
          <li>Regelmäßige Datensicherung der auf dem eigenen Server gespeicherten Daten</li>
        </ul>

        <h3>7.2 Zulässige Nutzung</h3>
        <p>Der Nutzer verpflichtet sich, MyContentPilot ausschließlich für legale Zwecke einzusetzen. Insbesondere ist es dem Nutzer untersagt:</p>
        <ul>
          <li>Inhalte zu generieren oder zu veröffentlichen, die gegen geltendes Recht verstoßen</li>
          <li>Urheberrechtlich geschützte Inhalte ohne entsprechende Berechtigung zu verwenden</li>
          <li>Irreführende, falsche oder diffamierende Inhalte zu veröffentlichen</li>
          <li>Spam oder unerwünschte Massenkommunikation zu versenden</li>
          <li>Die Nutzungsbedingungen der angebundenen Plattformen (Facebook, Instagram, WordPress u. a.) zu verletzen</li>
          <li>Das MyContentPilot-System an Dritte weiterzugeben, zu lizenzieren oder zu verkaufen</li>
        </ul>

        <h3>7.3 Verantwortung für KI-generierte Inhalte</h3>
        <p>
          Der Nutzer ist vollumfänglich verantwortlich für alle durch MyContentPilot
          generierten und veröffentlichten Inhalte. Die Qualität, Richtigkeit,
          Rechtmäßigkeit und Angemessenheit der durch KI-Modelle erzeugten Inhalte
          liegt in der Verantwortung des Nutzers. Der Nutzer ist verpflichtet,
          generierte Inhalte vor der Veröffentlichung zu prüfen oder geeignete
          Kontrollmechanismen einzurichten.
        </p>

        <h3>7.4 Meldepflicht bei Sicherheitsvorfällen</h3>
        <p>
          Der Nutzer ist verpflichtet, dem Anbieter unverzüglich zu melden,
          wenn er Kenntnis von Sicherheitslücken, Missbrauch oder unberechtigtem
          Zugriff auf das MyContentPilot-System erlangt.
        </p>
      </div>

      <!-- §8 Verfügbarkeit & Support -->
      <div class="legal-section">
        <h2>§8 Verfügbarkeit &amp; Support</h2>

        <h3>8.1 Softwarepflege</h3>
        <p>
          Der Anbieter stellt Updates, Bugfixes und Sicherheits-Patches für das
          MyContentPilot-System bereit. Ein Anspruch auf Bereitstellung bestimmter
          Features oder Plattform-Integrationen innerhalb bestimmter Fristen
          besteht nicht.
        </p>

        <h3>8.2 Supportleistungen</h3>
        <p>
          Support wird ausschließlich per E-Mail erbracht. Die im jeweiligen Tarif
          genannten Reaktionszeiten sind Richtwerte und stellen keine verbindlichen
          Fristen dar. Support gilt für Fragen zur Konfiguration und zum Betrieb
          des MyContentPilot-Systems gemäß der bereitgestellten Dokumentation.
        </p>
        <p>
          Nicht vom Support umfasst sind:
        </p>
        <ul>
          <li>Administration der Serverinfrastruktur des Nutzers</li>
          <li>Einrichtung oder Verwaltung von API-Zugängen externer Anbieter</li>
          <li>Inhaltliche Beratung zur Content-Strategie</li>
          <li>Leistungen der angebundenen Plattformen (WordPress, Social Media)</li>
        </ul>
      </div>

      <!-- §9 Haftungsbeschränkung -->
      <div class="legal-section">
        <h2>§9 Haftungsbeschränkung</h2>

        <h3>9.1 Grundsatz</h3>
        <p>
          Der Anbieter haftet unbeschränkt für Schäden aus der Verletzung des Lebens,
          des Körpers oder der Gesundheit, die auf einer vorsätzlichen oder fahrlässigen
          Pflichtverletzung des Anbieters, seiner gesetzlichen Vertreter oder
          Erfüllungsgehilfen beruhen, sowie für sonstige Schäden, die auf einer
          vorsätzlichen oder grob fahrlässigen Pflichtverletzung beruhen.
        </p>

        <h3>9.2 Beschränkung bei einfacher Fahrlässigkeit</h3>
        <p>
          Bei einfacher Fahrlässigkeit haftet der Anbieter nur bei Verletzung einer
          wesentlichen Vertragspflicht (Kardinalpflicht), d. h. einer Pflicht, deren
          Erfüllung die ordnungsgemäße Durchführung des Vertrages überhaupt erst
          ermöglicht und auf deren Einhaltung der Nutzer regelmäßig vertrauen darf.
          Die Haftung ist in diesem Fall auf den vorhersehbaren, typischerweise
          eintretenden Schaden begrenzt, höchstens jedoch auf die vom Nutzer
          im letzten Monat gezahlte Vergütung.
        </p>

        <h3>9.3 Ausschluss für KI-Ausgaben</h3>
        <p>
          Der Anbieter übernimmt keine Haftung für die inhaltliche Qualität,
          Richtigkeit, Vollständigkeit oder Rechtmäßigkeit der durch externe
          KI-Modelle generierten Inhalte. Die Verantwortung für veröffentlichte
          Inhalte liegt ausschließlich beim Nutzer (siehe §7.3).
        </p>

        <h3>9.4 Ausschluss für externe Dienste</h3>
        <p>
          Der Anbieter haftet nicht für Ausfälle, Änderungen oder Einschränkungen
          externer Dienste und Plattformen (KI-Anbieter, Social-Media-Plattformen,
          WordPress-Hosting, DNS-Dienste u. a.), die sich auf den Betrieb von
          MyContentPilot auswirken.
        </p>

        <h3>9.5 Höhere Gewalt</h3>
        <p>
          Der Anbieter haftet nicht für Leistungsstörungen, die auf Ereignisse
          höherer Gewalt zurückzuführen sind, die außerhalb seines Einflussbereichs
          liegen (z. B. Naturkatastrophen, Stromausfälle, Cyberangriffe auf
          Drittinfrastruktur).
        </p>
      </div>

      <!-- §10 Urheberrecht & Nutzungsrechte -->
      <div class="legal-section">
        <h2>§10 Urheberrecht &amp; Nutzungsrechte</h2>

        <h3>10.1 Rechte am MyContentPilot-System</h3>
        <p>
          Das MyContentPilot-System, einschließlich aller Quellcodes, Architekturen,
          Dokumentationen, Prompts und zugehörigen Materialien, ist urheberrechtlich
          geschütztes Eigentum des Anbieters. Mit Zahlung der vereinbarten Vergütung
          erhält der Nutzer ein nicht-exklusives, nicht-übertragbares Nutzungsrecht
          für die Dauer des Vertrages.
        </p>

        <h3>10.2 Verbot der Weitergabe</h3>
        <p>
          Der Nutzer ist nicht berechtigt, das MyContentPilot-System oder Teile davon
          zu kopieren, zu modifizieren, zu vertreiben, zu verkaufen oder Dritten
          zur Nutzung zu überlassen, es sei denn, der Anbieter stimmt dem
          ausdrücklich schriftlich zu.
        </p>

        <h3>10.3 Rechte an generierten Inhalten</h3>
        <p>
          Inhalte, die durch das MyContentPilot-System auf Weisung des Nutzers
          generiert werden, stehen dem Nutzer zu. Der Anbieter erhebt keinen
          Anspruch auf durch den Nutzer generierte Inhalte. Es obliegt dem Nutzer,
          die Nutzungsrechte an Inhalten gemäß den Bedingungen der jeweils
          eingesetzten KI-Anbieter zu prüfen.
        </p>
      </div>

      <!-- §11 Schlussbestimmungen -->
      <div class="legal-section">
        <h2>§11 Schlussbestimmungen</h2>

        <h3>11.1 Anwendbares Recht</h3>
        <p>
          Es gilt das Recht der Bundesrepublik Deutschland unter Ausschluss des
          UN-Kaufrechts (CISG).
        </p>

        <h3>11.2 Gerichtsstand</h3>
        <p>
          Gerichtsstand für alle Streitigkeiten aus oder im Zusammenhang mit diesen
          AGB ist Stuttgart, sofern der Nutzer Kaufmann, juristische Person des
          öffentlichen Rechts oder öffentlich-rechtliches Sondervermögen ist.
          Der Anbieter ist jedoch auch berechtigt, am allgemeinen Gerichtsstand
          des Nutzers Klage zu erheben.
        </p>

        <h3>11.3 Salvatorische Klausel</h3>
        <p>
          Sollten einzelne Bestimmungen dieser AGB ganz oder teilweise unwirksam
          oder undurchführbar sein oder werden, so berührt dies die Wirksamkeit
          der übrigen Bestimmungen nicht. Anstelle der unwirksamen oder
          undurchführbaren Bestimmung gilt eine wirksame und durchführbare
          Regelung als vereinbart, die dem wirtschaftlichen Zweck der unwirksamen
          Bestimmung am nächsten kommt.
        </p>

        <h3>11.4 Änderungen der AGB</h3>
        <p>
          Der Anbieter behält sich vor, diese AGB mit einer Ankündigungsfrist von
          30 Tagen zu ändern. Der Nutzer wird über Änderungen per E-Mail informiert.
          Widerspricht der Nutzer den geänderten AGB nicht innerhalb von 14 Tagen
          nach Zugang der Änderungsmitteilung, gelten die geänderten AGB als
          angenommen. Auf dieses Widerspruchsrecht und die Folgen des Schweigens
          wird der Anbieter in seiner Mitteilung ausdrücklich hinweisen.
        </p>

        <h3>11.5 Schriftformerfordernis</h3>
        <p>
          Änderungen und Ergänzungen dieser AGB sowie aller auf ihrer Grundlage
          geschlossenen Verträge bedürfen der Schriftform. Dies gilt auch für
          die Abbedingung dieser Schriftformklausel. E-Mail genügt der
          Schriftform im Sinne dieser Klausel.
        </p>
      </div>

      <!-- Back link -->
      <div style="margin-top:var(--s-12);padding-top:var(--s-8);border-top:1px solid var(--c-border-light);">
        <div style="display:flex;gap:var(--s-4);flex-wrap:wrap;">
          <a href="<?php echo esc_url( home_url('/') ); ?>" class="btn btn--ghost-dark">
            ← Zurück zur Startseite
          </a>
          <a href="<?php echo esc_url( home_url('/impressum') ); ?>" class="btn btn--ghost-dark">
            Impressum
          </a>
          <a href="<?php echo esc_url( home_url('/datenschutz') ); ?>" class="btn btn--ghost-dark">
            Datenschutz
          </a>
        </div>
      </div>

    </div><!-- /.legal-body -->
  </div>
</section>

<?php get_footer(); ?>
