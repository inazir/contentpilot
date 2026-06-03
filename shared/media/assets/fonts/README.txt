# This directory contains bundled open-source fonts used by the
# ContentPilot branding engine (shared/media/branding.py).
#
# Bundled fonts:
#   Inter-Regular.ttf    — body text / website URLs
#   Inter-SemiBold.ttf   — CTA text / taglines
#   Inter-Bold.ttf       — brand name / headlines
#
# License: SIL Open Font License 1.1
# Source:  https://rsms.me/inter/
#
# These are bundled so the Docker image never depends on host system fonts.
# Pillow falls back to its built-in bitmap font if these files are missing.
