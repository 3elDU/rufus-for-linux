rufus_for_linux_sources = [
  'main.vala',
  'window.vala',
]

rufus_for_linux_deps = [
  dependency('gio-2.0', version: '>= 2.50'),
  dependency('gtk+-3.0', version: '>= 3.22'),
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
