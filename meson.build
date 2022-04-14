project('com.github.neagiry.rfl', 'vala', 'c')

executable(
    meson.project_name(),

    'src/main.vala',
    'src/application.vala',
    'src/window.vala',

    dependencies: [
        dependency('gee-0.8'),
        dependency('gio-2.0'),
        dependency('glib-2.0'),
        dependency('gobject-2.0'),
        dependency('gtk+-3.0'),
        dependency('granite', version: '>=6.0.0'),
    ],

    install: true
)
