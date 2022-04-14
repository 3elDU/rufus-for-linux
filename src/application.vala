public class Application : Gtk.Application {
	
	public Application () {
		Object(
			application_id: "com.github.neagiry.rfl",
			flags: ApplicationFlags.HANDLES_OPEN
		);
	}
	
	protected override void activate () {
	
		var window = new Window (this);

		add_window (window);
	}

}
