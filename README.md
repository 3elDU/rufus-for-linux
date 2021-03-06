<h1 align="center">
  <br>
  <a href="https://osel.pp.ua/"><img src="https://github.com/OSeL-Team/rufus-for-linux/blob/main/visual/rfl-logo.svg" alt="RFL logo" width="180"></a>
  <br>
  Rufus for Linux
  <br>
</h1>

<h3 align="center">Linux version of the <a href="https://rufus.ie/en/" target="_blank">Rufus</a> utility
</h3>

<p align="center">
  <a href="https://t.me/crazy_linux_chat"><img src="https://github.com/OSeL-Team/rufus-for-linux/blob/main/visual/chat-telegram.svg" alt="telegram">
  </a>
  <a href="https://www.gnu.org/licenses/gpl-3.0.html">
    <img src="https://github.com/OSeL-Team/rufus-for-linux/blob/main/visual/license-gpl.svg" alt="license">
  </a>
</p>

<p align="center">
  <a href="#key-features">Key Features</a> •
  <a href="#download">Download</a> •
  <a href="#technology-stack">Technology stack</a> •
  <a href="#license">License</a> • 
  <a href="#contact-us">Contact us</a> 
</p>

<p align="center">
  <a href="#"><img src="https://github.com/OSeL-Team/rufus-for-linux/blob/main/visual/screenshot.png" alt="screenshot">
</p>

## Key Features
+ Support for ntfs and fat32 file systems
+ Support for the original authors of Rufus
+ Lightweight program
+ Portability utility (when using AppImage)
+ Sharpening the program to work on Linux
+ Open source code, the ability to participate in the development of the utility

## Download
You can [download](https://github.com/OSeL-Team/rufus-for-linux/releases) the latest version of this program on any Linux distribution using deb package, [AUR](https://aur.archlinux.org/packages/rufus-for-linux), [flatpak](https://www.flathub.org/home) and [AppImage](https://www.appimagehub.com/)

## Install requirements
We recommend you to create [virtual environment](https://docs.python.org/3/tutorial/venv.html), because installing packages globally is generally a bad practice.
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
The second command above may fail when using fish shell. If you use fish, instead run `source venv/bin/activate.fish`

## Technology stack
This software uses the following open source packages:

+ [Python](https://www.python.org/)
+ [Vala](https://wiki.gnome.org/Projects/Vala)
+ [GTK](https://www.gtk.org/)
+ [Meson](https://mesonbuild.com/)
+ [Flatpak](https://flatpak.org/)

## Rufus for Linux analogs

- [balenaEtcher](https://www.balena.io/etcher/), program for burning ISO on NodeJS
- [dd](https://wiki.archlinux.org/title/Dd), UNIX program for both copying and converting files

## License
Distributed under the GPL-3.0 License

## Contact us
If you are actively coding on 
[Python](https://www.python.org/), [Vala](https://www.gtk.org/docs/language-bindings/vala/) and [GTK](https://www.gtk.org/) then write us an [e-mail](mailto:ketronix2@gmail.com)


