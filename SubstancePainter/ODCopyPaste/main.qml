import QtQuick 2.2
import Painter 1.0

PainterPlugin {
		// starts a timer that will trigger the 'onTick' callback at regular interval
		tickIntervalMS: -1 // -1 mean disabled (default value)

		// starts a JSON server on the given port:
		// you send javascript that will be evaluated and you get the result in JSON format
		jsonServerPort: -1 // -1 mean disabled (default value)

		Component.onCompleted: {
				// Called after the object has been instantiated.
				// This can be used to execute script code at startup,
				// once the full QML environment has been established.
				alg.log.info("Component.onCompleted")
			    //create a toolbar button
    			alg.ui.addToolBarWidget("paste.qml");
		}

		onTick: {
				// Do something at each tick, depending on tickIntervalMS value
				alg.log.info("onTick")
		}

		onConfigure: {
				// Do something when the user request the plugin configuration panel
				alg.log.info("onConfigure")
				alg.subprocess.check_call("\"" + alg.plugin_root_directory + "vertDataToObj.exe\"")
				alg.project.create("file:/" + alg.plugin_root_directory + "1.obj")
				//alg.log.info(alg.plugin_root_directory + "testingoliver")
		}

		onApplicationStarted: {
				// Called when the application is started
				alg.log.info("onApplicationStarted")
		}

		onNewProjectCreated: {
				// Called when a new project is created, before the onProjectOpened callback
				alg.log.info("onNewProjectCreated")
		}

		onProjectOpened: {
				// Called when the project is fully loaded
				alg.log.info("onProjectOpened")
		}

		onProjectAboutToClose: {
				// Called before project unload
				alg.log.info("onProjectAboutToClose")
		}

		onProjectAboutToSave: {
				// Called before a save, 'destination_url' parameter contains the save destination
				alg.log.info("onProjectAboutToSave: "+destination_url)
		}

		onProjectSaved: {
				// Called after the project was saved
				alg.log.info("onProjectSaved")
		}
}
