FORESIGHT Nexus Brand Assets

- foresight_nexus_logo.svg: primary dark-background wordmark. Used for the
  primary dark-UI presentation (Command Center hero, ui/components.py
  render_hero()).
- foresight_nexus_logo_light.svg: light-background wordmark. Not currently
  wired into the app (the UI theme is dark-only) — reserved for any future
  light-theme surface or exported document/README use.
- foresight_nexus_mark.svg: primary app/favicon mark. Used for compact
  branding: the sidebar (ui/branding.py render_sidebar_mark()) and the
  browser favicon (ui/branding.py get_favicon()).
- foresight_nexus_mark_monochrome.svg: monochrome variant. Not currently
  wired into the app — reserved for contexts where the gradient mark
  wouldn't render well (plain-text badges, print export).

Note: assets/icons/ does not exist in this repository — the application
uses Streamlit's built-in Material icon set for navigation and inline SVG
for the hero visual, so a custom icon folder has no current use.
