#!/usr/bin/env python3

import os
import time
import threading

import wx
import wx.adv


import WoeUSB.core as core
import WoeUSB.list_devices as list_devices
import WoeUSB.miscellaneous as miscellaneous

data_directory = os.path.dirname(__file__) + "/data/"

app = wx.App()

_ = miscellaneous.i18n


class MainFrame(wx.Frame):
    __MainPanel = None

    def __init__(self, title, pos, size, style=wx.DEFAULT_FRAME_STYLE):
        super(MainFrame, self).__init__(None, -1, title, pos, size, style)

        self.SetIcon(wx.Icon(data_directory + "icon.ico"))


        main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.__MainPanel = MainPanel(self, wx.ID_ANY)
        main_sizer.Add(self.__MainPanel, 1, wx.EXPAND | wx.ALL, 4)

        self.SetSizer(main_sizer)

    def on_quit(self, __):
        self.Close(True)

    def on_about(self, __):
        my_dialog_about = DialogAbout(self, wx.ID_ANY)
        my_dialog_about.ShowModal()


class MainPanel(wx.Panel):
    __parent = None

    __usbStickList = wx.ListBox

    __dvdDriveDevList = []
    __usbStickDevList = []

    __isoFile = wx.FilePickerCtrl

    __parentFrame = None

    __btInstall = None
    __btRefresh = None

    __isoChoice = None
    __dvdChoice = None

    __progressStatus = None
    __progress = None

    def __init__(self, parent, ID, pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.TAB_TRAVERSAL):
        super(MainPanel, self).__init__(parent, ID, pos, size, style)

        self.__parent = parent

        # Controls
        main_sizer = wx.BoxSizer(wx.VERTICAL)


        # Iso
        self.__isoChoice = wx.StaticText(self, wx.ID_ANY, _("Ваш ISO:"))
        main_sizer.Add(self.__isoChoice, 0, wx.ALL, 3)

        tmp_sizer = wx.BoxSizer(wx.HORIZONTAL)
        tmp_sizer.AddSpacer(20)
        self.__isoFile = wx.FilePickerCtrl(self, wx.ID_ANY, "", _("Выбор ISO"),
                                           "Iso images (*.iso)|*.iso;*.ISO|All files|*")
        tmp_sizer.Add(self.__isoFile, 1, wx.LEFT | wx.RIGHT | wx.BOTTOM, 3)
        main_sizer.Add(tmp_sizer, 0, wx.EXPAND, 0)

        # Target
        main_sizer.AddSpacer(20)

        main_sizer.Add(wx.StaticText(self, wx.ID_ANY, _("Выберите устройство:")), 0, wx.ALL, 3)

        # List
        self.__usbStickList = wx.ListBox(self, wx.ID_ANY)
        main_sizer.Add(self.__usbStickList, 0.5, wx.EXPAND)

         #Progress
        main_sizer.AddSpacer(20)

        self.__progressStatus = wx.StaticText(self, wx.ID_ANY, _("Статус:"))
        main_sizer.Add(self.__progressStatus, 0, 0, 2)

        self.__progress = wx.Gauge(self, wx.ID_ANY, range = 100, style = wx.GA_HORIZONTAL)
        main_sizer.Add(self.__progress, 0, wx.EXPAND, 3)

        # Buttons
        main_sizer.AddSpacer(30)

        bt_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.__btRefresh = wx.Button(self, wx.ID_ANY, _("Обновить список устройств"))
        bt_sizer.Add(self.__btRefresh, 0, wx.ALL, 3)
        self.__btInstall = wx.Button(self, wx.ID_ANY, _("Записать"))
        bt_sizer.Add(self.__btInstall, 0, wx.ALL, 3)

        main_sizer.Add(bt_sizer, 0, wx.ALIGN_RIGHT, 0)

        # Finalization
        self.SetSizer(main_sizer)

        self.Bind(wx.EVT_LISTBOX, self.on_list_or_file_modified, self.__usbStickList)
        self.Bind(wx.EVT_FILEPICKER_CHANGED, self.on_list_or_file_modified, self.__isoFile)

        self.Bind(wx.EVT_BUTTON, self.on_install, self.__btInstall)
        self.Bind(wx.EVT_BUTTON, self.on_refresh, self.__btRefresh)

        self.Bind(wx.EVT_RADIOBUTTON, self.on_source_option_changed, self.__isoChoice)
        self.Bind(wx.EVT_RADIOBUTTON, self.on_source_option_changed, self.__dvdChoice)

        self.refresh_list_content()
        self.on_source_option_changed(wx.CommandEvent)
        self.__btInstall.Enable(self.is_install_ok())

    def refresh_list_content(self):
        # USB
        self.__usbStickDevList = []
        self.__usbStickList.Clear()

        show_all_checked = False

        device_list = list_devices.usb_drive(show_all_checked)

        for device in device_list:
            self.__usbStickDevList.append(device[0])
            self.__usbStickList.Append(device[1])

        # ISO
        self.__btInstall.Enable(self.is_install_ok())

    def on_source_option_changed(self, __):
        is_iso = True

        self.__isoFile.Enable(is_iso)

        self.__btInstall.Enable(self.is_install_ok())

    def is_install_ok(self):
        is_iso = True
        return ((is_iso and os.path.isfile(self.__isoFile.GetPath())) or (
                not is_iso)) and self.__usbStickList.GetSelection() != wx.NOT_FOUND

    def on_list_or_file_modified(self, event):
        if event.GetEventType() == wx.EVT_LISTBOX and not event.IsSelection():
            return

        self.__btInstall.Enable(self.is_install_ok())

    def on_refresh(self, __):
        self.refresh_list_content()

    def on_install(self, __):
        global woe
        if wx.MessageBox(
            _("Уверены? Все данные на выбранном носителе будут УНИЧТОЖЕНЫ! Возможно, без возможности восстановления."),
            _("Cancel"),
            wx.YES_NO | wx.ICON_QUESTION,
            self) == wx.NO:
            return
        if self.is_install_ok():
            is_iso = True

            device = self.__usbStickDevList[self.__usbStickList.GetSelection()]

            if is_iso:
                iso = self.__isoFile.GetPath()
        
            filesystem = "FAT"

            woe = WoeUSB_handler(iso, device, boot_flag=True, filesystem=filesystem)
            woe.start()

            dialog = wx.ProgressDialog(_("Запись..."), _("Подождите пожалуйста..."), 101, self.GetParent(),
                                       wx.PD_APP_MODAL | wx.PD_SMOOTH | wx.PD_CAN_ABORT)

            while woe.is_alive():
                if not woe.progress:
                    status = dialog.Pulse(woe.state)[0]
                    time.sleep(0.06)
                else:
                    status = dialog.Update(woe.progress, woe.state)[0]

                if not status:
                    if wx.MessageBox(_("Точно хотите отменить запись образа?"), _("Cancel"),
                                     wx.YES_NO | wx.ICON_QUESTION, self) == wx.NO:
                        dialog.Resume()
                    else:
                        woe.kill = True
                        break
            dialog.Destroy()

            if woe.error == "":
                wx.MessageBox(_("Запись завершена успешно!!"), _("Installation"), wx.OK | wx.ICON_INFORMATION, self)
            else:
                wx.MessageBox(_("Упс... Что-то сломалось. Записать образ не удалось!") + "\n" + str(woe.error), _("Installation"),
                              wx.OK | wx.ICON_ERROR,
                              self)

    def on_show_all_drive(self, __):
        self.refresh_list_content()


class DialogAbout(wx.Dialog):
    __bitmapIcone = None
    __staticTextTitre = None
    __staticTextVersion = None
    __NotebookAutorLicence = None
    __MyPanelNoteBookAutors = None
    __BtOk = None

    def __init__(self, parent, ID=wx.ID_ANY, title=_("About"), pos=wx.DefaultPosition, size=wx.Size(650, 590),
                 style=wx.DEFAULT_DIALOG_STYLE):
        super(DialogAbout, self).__init__(parent, ID, title, pos, size, style)

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        sizer_all = wx.BoxSizer(wx.VERTICAL)
        sizer_img = wx.BoxSizer(wx.HORIZONTAL)

        img = wx.Image(data_directory + "icon.ico", wx.BITMAP_TYPE_ICO).Scale(48, 48, wx.IMAGE_QUALITY_BILINEAR)
        self.__bitmapIcone = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap(img), wx.DefaultPosition, wx.Size(48, 48))
        sizer_img.Add(self.__bitmapIcone, 0, wx.ALL, 5)

        sizer_text = wx.BoxSizer(wx.VERTICAL)

        self.__staticTextTitre = wx.StaticText(self, wx.ID_ANY, "Rufus for Linux")
        self.__staticTextTitre.SetFont(wx.Font(16, 74, 90, 92, False, "Sans"))
        self.__staticTextTitre.SetForegroundColour(wx.Colour(0, 60, 118))
        sizer_text.Add(self.__staticTextTitre, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 5)

        self.__staticTextVersion = wx.StaticText(self, wx.ID_ANY, miscellaneous.__version__)
        self.__staticTextVersion.SetFont(wx.Font(10, 74, 90, 92, False, "Sans"))
        self.__staticTextVersion.SetForegroundColour(wx.Colour(69, 141, 196))
        sizer_text.Add(self.__staticTextVersion, 0, wx.LEFT, 5)
        sizer_img.Add(sizer_text, 0, 0, 5)
        sizer_all.Add(sizer_img, 0, wx.EXPAND, 5)

        self.__NotebookAutorLicence = wx.Notebook(self, wx.ID_ANY)

        self.__NotebookAutorLicence.AddPage(
            PanelNoteBookAutors(self.__NotebookAutorLicence, wx.ID_ANY, "slacka \nLin-Buo-Ren\nWaxyMocha", data_directory + "woeusb-logo.png",
                                "github.com/WoeUSB/WoeUSB-ng"), _("Authors"), True)
        self.__NotebookAutorLicence.AddPage(
            PanelNoteBookAutors(self.__NotebookAutorLicence, wx.ID_ANY, "Colin GILLE / Congelli501",
                                data_directory + "c501-logo.png", "www.congelli.eu"), _("Original WinUSB Developer"), False)

        licence_str = _('''
            This file is part of WoeUSB-ng.

            WoeUSB-ng is free software: you can redistribute it and/or modify
            it under the terms of the GNU General Public License as published by
            the Free Software Foundation, either version 3 of the License, or
            (at your option) any later version.

            WoeUSB-ng is distributed in the hope that it will be useful,
            but WITHOUT ANY WARRANTY; without even the implied warranty of
            MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
            GNU General Public License for more details.

            You should have received a copy of the GNU General Public License
            along with WoeUSB-ng.  If not, see <http://www.gnu.org/licenses/>.
        ''')

        licence_txt = wx.TextCtrl(self.__NotebookAutorLicence, wx.ID_ANY, licence_str, wx.DefaultPosition,
                                  wx.DefaultSize, wx.TE_MULTILINE | wx.TE_READONLY)

        self.__NotebookAutorLicence.AddPage(licence_txt, _("License"))

        sizer_all.Add(self.__NotebookAutorLicence, 1, wx.EXPAND | wx.ALL, 5)

        self.__BtOk = wx.Button(self, wx.ID_OK)
        sizer_all.Add(self.__BtOk, 0, wx.ALIGN_RIGHT | wx.BOTTOM | wx.RIGHT, 5)
        self.__BtOk.SetFocus()

        self.SetSizer(sizer_all)
        self.Layout()


class PanelNoteBookAutors(wx.Panel):
    def __init__(self, parent, ID=wx.ID_ANY, autherName="", imgName="", siteLink="", pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.TAB_TRAVERSAL):
        super(PanelNoteBookAutors, self).__init__(parent, ID, pos, size, style)

        sizer_note_book_autors = wx.BoxSizer(wx.VERTICAL)

        auteur_static_text = wx.StaticText(self, wx.ID_ANY, autherName)
        sizer_note_book_autors.Add(auteur_static_text, 0, wx.ALL, 5)

        if siteLink != "":
            autor_link = wx.adv.HyperlinkCtrl(self, wx.ID_ANY, siteLink, siteLink)
            sizer_note_book_autors.Add(autor_link, 0, wx.LEFT | wx.BOTTOM, 5)

        if imgName != "":
            img = wx.Image(imgName, wx.BITMAP_TYPE_PNG)
            img_autor_logo = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap(img))
            sizer_note_book_autors.Add(img_autor_logo, 0, wx.LEFT, 5)

        self.SetSizer(sizer_note_book_autors)


class WoeUSB_handler(threading.Thread):
    """
    Class for handling communication with woeusb.
    """
    progress = False
    state = ""
    error = ""
    kill = False

    def __init__(self, source, target, boot_flag, filesystem):
        threading.Thread.__init__(self)

        core.gui = self
        self.source = source
        self.target = target
        self.boot_flag = boot_flag
        self.filesystem = filesystem

    def run(self):
        source_fs_mountpoint, target_fs_mountpoint, temp_directory, target_media = core.init(
            from_cli=False,
            install_mode="device",
            source_media=self.source,
            target_media=self.target
        )
        try:
            core.main(source_fs_mountpoint, target_fs_mountpoint, self.source, self.target, "device", temp_directory,
                      self.filesystem, self.boot_flag)
        except SystemExit:
            pass

        core.cleanup(source_fs_mountpoint, target_fs_mountpoint, temp_directory, target_media)


def run():
    frameTitle = "Rufus for Linux"

    frame = MainFrame(frameTitle, wx.DefaultPosition, wx.Size(400, 300))
    frame.SetMinSize(wx.Size(400, 300))

    frame.Show(True)
    app.MainLoop()


if __name__ == "__main__":
    run()