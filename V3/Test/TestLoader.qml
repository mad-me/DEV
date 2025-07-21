import QtQuick 2.15
import QtQuick.Controls 2.15

ApplicationWindow {
    visible: true
    width: 1200
    height: 800
    title: "Loader QML Test"

    LoaderWithTerminal {
        id: loader
        anchors.centerIn: parent
        showTerminal: true
        statusText: "Import läuft..."
        visible: true
    }
} 