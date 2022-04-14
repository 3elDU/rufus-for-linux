rufus_for_linux_sources = [
  'main.vala',
  'window.vala',
  'application.vala',
]

rufus_for_linux_deps = [
  dependency('libadwaita-1', version: '>= 1.0'),
]

gnome = import('gnome')

rufus_for_linux_sources += gnome.compile_resources('rufus_for_linux-resources',
  'rufus_for_linux.gresource.xml',
  c_name: 'rufus_for_linux'
)

executable('rufus-for-linux', rufus_for_linux_sources,
  vala_args: '--target-glib=2.50',  dependencies: rufus_for_linux_deps,
  install: true,
)
