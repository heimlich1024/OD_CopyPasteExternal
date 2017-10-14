import QtQuick 2.3
import QtQuick.Window 2.2
import QtQuick.Layouts 1.2
import QtQuick.Dialogs 1.0

Rectangle {
    id: saveButton
    width: 50
    height: 30
    border.color: "yellow"

    /*set color based on if mouse is in mouseArea using Conditional (ternary) Operator
    since MouseArea doesn't enble hover, the color changes on click of the button */
    color: buttonMouseArea.containsMouse ? "grey" : "black"

    Text {
        id: buttonLabel
        anchors.centerIn: parent
        text: "PExtUDIM"
        color: "white"
    }

    //signal - emitted when event occurs (onClicked:)
    signal buttonClick()

    //button click handler
    onButtonClick: {

        try{
            if (Qt.platform.os == "windows")  {
                alg.subprocess.check_call("\"" + alg.plugin_root_directory + "vertDataToObj.exe\"")
                alg.project.create("file:/" + alg.plugin_root_directory + "1.obj",[],[],{"splitMaterialsByUDIM":true})
            } else {
                alg.subprocess.check_call("\"" + alg.plugin_root_directory + "vertDataToObj\"")
                alg.project.create("file:/" + alg.plugin_root_directory + "1.obj",[],[],{"splitMaterialsByUDIM":true})
            }
        }catch (e){
            alg.log.error(e.message)
        }
    }

    MouseArea {
        id: buttonMouseArea
        //anchor all sides of the mouse area to the rectangle's anchors
        anchors.fill: parent

        //onClicked handles valid mouse button clicks
        onClicked: buttonClick()
    }

}
