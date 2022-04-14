public class Window : Gtk.ApplicationWindow {

	public Window (Application Application) {
		Object (
			application:		Application,
			resizable:			false,
			title:				"Rufus For Linux",
			default_height:		600,
			default_width:		400,
			window_position:	Gtk.WindowPosition.CENTER
		);
	}

	construct {

		var DriveProperties = new Gtk.Label ("");

			DriveProperties.halign			=	START;
			DriveProperties.set_markup		("<big><b>Drive properties</b></big>");

		var DriveSeparator = new Gtk.Separator (HORIZONTAL);

			DriveSeparator.margin_top		=	10;

		var Devices = new Gtk.Label ("Devices");

			Devices.halign					=	START;
			Devices.margin_top				=	10;

		var DevicesBox = new Gtk.FileChooserButton ("Select Diskt",SELECT_FOLDER);

			DevicesBox.halign				=	FILL;

		var BootSelection = new Gtk.Label ("Boot selection");

			BootSelection.halign			=	START;

		var BootSelectionBox = new Gtk.FileChooserButton ("Select Diskt",OPEN);

			BootSelectionBox.halign			=	FILL;

		var PartitionScheme = new Gtk.Label ("Partition scheme");

			PartitionScheme.halign				=	START;

		var PartitionSchemeBox = new Gtk.ComboBoxText ();

			PartitionSchemeBox.halign			=	FILL;
			PartitionSchemeBox.append_text		("MBR");
			PartitionSchemeBox.append_text		("GPT");

		var TargetSystem = new Gtk.Label ("Target system");

			TargetSystem.halign				=	START;

		var TargetSystemBox = new Gtk.ComboBoxText ();

			TargetSystemBox.halign			=	FILL;
			TargetSystemBox.append_text		("BIOS or UEFI");

/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

		var FormatOption = new Gtk.Label ("");

			FormatOption.halign				=	START;
			FormatOption.margin_top			=	10;
			FormatOption.set_markup			("<big><b>Format option</b></big>");

		var FormatOptionSeparator = new Gtk.Separator (HORIZONTAL);

			FormatOptionSeparator.margin_top		=	20;

		var ValumeLabel = new Gtk.Label ("Valume label");

			ValumeLabel.halign				=	START;

		var ValumeEntry = new Gtk.Entry ();

			ValumeEntry.halign				=	FILL;

		var ClustterSize = new Gtk.Label ("Clustter size");

			ClustterSize.halign				=	START;

		var ClustterSizeBox = new Gtk.ComboBoxText ();

			ClustterSizeBox.halign			=	FILL;
			ClustterSizeBox.append_text		("4096 (Default)");

		var FileSystem = new Gtk.Label ("File system");

			FileSystem.halign				=	START;

		var FileSystemBox = new Gtk.ComboBoxText ();

			FileSystemBox.halign			=	FILL;
			FileSystemBox.append_text		("FAT32 (Default)");
			FileSystemBox.append_text		("NTFS (Uses WindowsOS)");

/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

		var Status = new Gtk.Label ("");

			Status.halign					=	START;
			Status.margin_top				=	10;
			Status.set_markup				("<big><b>Status</b></big>");

		var StatusSeparator = new Gtk.Separator (HORIZONTAL);

			StatusSeparator.margin_top		=	20;

		var StatusBar = new Gtk.ProgressBar ();

			StatusBar.halign				=	FILL;
			StatusBar.margin_top			=	60;

		var StartButton = new Gtk.Button.with_label ("Start");

			StartButton.halign				=	FILL;

		var CloseButton = new Gtk.Button.with_label ("Close");

			CloseButton.halign				=	FILL;

		var grid = new Gtk.Grid ();

			grid.margin							=	20;
			grid.column_spacing					=	20;
			grid.row_spacing					=	10;

			grid.attach			(DriveProperties,		0,	0,	1,	1);
			grid.attach_next_to (DriveSeparator,		DriveProperties,	Gtk.PositionType.RIGHT,		3,	1);
			grid.attach_next_to (Devices,				DriveProperties,	Gtk.PositionType.BOTTOM,	1,	1);
			grid.attach_next_to (DevicesBox,			Devices,			Gtk.PositionType.BOTTOM,	4,	1);
			grid.attach_next_to (BootSelection,			DevicesBox,			Gtk.PositionType.BOTTOM,	1,	1);
			grid.attach_next_to (BootSelectionBox,		BootSelection,		Gtk.PositionType.BOTTOM,	4,	1);
			grid.attach_next_to (PartitionScheme,		BootSelectionBox,	Gtk.PositionType.BOTTOM,	2,	1);
			grid.attach_next_to (PartitionSchemeBox,	PartitionScheme,	Gtk.PositionType.BOTTOM,	2,	1);
			grid.attach_next_to	(TargetSystem,			PartitionScheme,	Gtk.PositionType.RIGHT,		1,	1);
			grid.attach_next_to (TargetSystemBox,		PartitionSchemeBox,	Gtk.PositionType.RIGHT,		2,	1);
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
			grid.attach_next_to (FormatOption,			PartitionSchemeBox,	Gtk.PositionType.BOTTOM,	1,	1);
			grid.attach_next_to (FormatOptionSeparator,	FormatOption,		Gtk.PositionType.RIGHT,		3,	1);
			grid.attach_next_to (ValumeLabel,			FormatOption,		Gtk.PositionType.BOTTOM,	1,	1);
			grid.attach_next_to (ValumeEntry,			ValumeLabel,		Gtk.PositionType.BOTTOM,	4,	1);
			grid.attach_next_to (FileSystem,			ValumeEntry,		Gtk.PositionType.BOTTOM,	2,	1);
			grid.attach_next_to (FileSystemBox,			FileSystem,			Gtk.PositionType.BOTTOM,	2,	1);
			grid.attach_next_to (ClustterSize,			FileSystem,			Gtk.PositionType.RIGHT,		1,	1);
			grid.attach_next_to (ClustterSizeBox,		ClustterSize,		Gtk.PositionType.BOTTOM,	2,	1);
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
			grid.attach_next_to (Status,				FileSystemBox,		Gtk.PositionType.BOTTOM,	1,	1);
			grid.attach_next_to (StatusSeparator,		Status,				Gtk.PositionType.RIGHT,		3,	1);
			grid.attach_next_to (StatusBar,				Status,				Gtk.PositionType.BOTTOM,	4,	1);
			grid.attach_next_to (StartButton,			StatusBar,			Gtk.PositionType.BOTTOM,	2,	1);
			grid.attach_next_to (CloseButton,			StartButton,		Gtk.PositionType.RIGHT,		2,	1);

		child = grid;

		show_all ();

	}

}
