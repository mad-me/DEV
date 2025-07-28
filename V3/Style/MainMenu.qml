import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Window 2.15
import Style 1.0

ApplicationWindow {
    id: mainWindow
    visible: true
    width: 1100
    height: 700
    title: "Dashboard mit animierter Sidebar"
    color: Style.background
    visibility: Window.Maximized

    // Properties für Navigation
    property int activeIndex: -1
    property bool sidebarVisible: false
    property bool stackVisible: false
    property bool wizardVisible: false
    property string wizardFahrer: ""
    property string wizardFahrzeug: ""
    property string wizardKW: ""

    // StackView für die verschiedenen Seiten
    StackView {
        id: stackView
        anchors.fill: parent
        anchors.margins: Style.spacingHuge
        visible: stackVisible
        opacity: stackVisible ? 1.0 : 0.0

        Behavior on opacity {
            NumberAnimation { duration: Style.animationSlow }
        }

        // Initiale Seite
        initialItem: Rectangle {
            color: "transparent"
        }
    }

    // Start-Buttons Container
    Rectangle {
        id: startButtonsContainer
        anchors.fill: parent
        anchors.margins: Style.spacingHuge
        color: "transparent"
        visible: !stackVisible
        opacity: !stackVisible ? 1.0 : 0.0

        Behavior on opacity {
            NumberAnimation { duration: Style.animationNormal }
        }

        ColumnLayout {
            anchors.centerIn: parent
            spacing: Style.spacingExtra

            GridLayout {
                columns: 2
                rowSpacing: Style.spacingNormal
                columnSpacing: Style.spacingNormal
                Layout.alignment: Qt.AlignHCenter

                // Abrechnung Button
                Item {
                    width: 240; height: 240
                    MouseArea {
                        id: dashAbrechnung
                        anchors.fill: parent
                        hoverEnabled: true
                        onClicked: abrechnungsBackend.show_wizard_and_load_page()
                        cursorShape: Qt.PointingHandCursor
                    }
                    Image {
                        anchors.centerIn: parent
                        source: dashAbrechnung.pressed ? "assets/icons/dollar_gray.svg"
                            : dashAbrechnung.containsMouse ? "assets/icons/dollar_orange.svg" : "assets/icons/dollar_white.svg"
                        width: dashAbrechnung.pressed ? 96 : dashAbrechnung.containsMouse ? 128 : 96
                        height: width
                        fillMode: Image.PreserveAspectFit
                    }
                }
                // Daten Button
                Item {
                    width: 240; height: 240
                    MouseArea {
                        id: dashDaten
                        anchors.fill: parent
                        hoverEnabled: true
                        onClicked: showSidebar(1)
                        cursorShape: Qt.PointingHandCursor
                    }
                    Image {
                        anchors.centerIn: parent
                        source: dashDaten.pressed ? "assets/icons/data_gray.svg"
                            : dashDaten.containsMouse ? "assets/icons/data_orange.svg" : "assets/icons/data_white.svg"
                        width: dashDaten.pressed ? 96 : dashDaten.containsMouse ? 128 : 96
                        height: width
                        fillMode: Image.PreserveAspectFit
                    }
                }
                // Mitarbeiter Button
                Item {
                    width: 240; height: 240
                    MouseArea {
                        id: dashMitarbeiter
                        anchors.fill: parent
                        hoverEnabled: true
                        onClicked: showSidebar(2)
                        cursorShape: Qt.PointingHandCursor
                    }
                    Image {
                        anchors.centerIn: parent
                        source: dashMitarbeiter.pressed ? "assets/icons/driver_gray.svg"
                            : dashMitarbeiter.containsMouse ? "assets/icons/driver_orange.svg" : "assets/icons/driver_white.svg"
                        width: dashMitarbeiter.pressed ? 96 : dashMitarbeiter.containsMouse ? 128 : 96
                        height: width
                        fillMode: Image.PreserveAspectFit
                    }
                }
                // Fahrzeuge Button
                Item {
                    width: 240; height: 240
                    MouseArea {
                        id: dashFahrzeuge
                        anchors.fill: parent
                        hoverEnabled: true
                        onClicked: showSidebar(3)
                        cursorShape: Qt.PointingHandCursor
                    }
                    Image {
                        anchors.centerIn: parent
                        source: dashFahrzeuge.pressed ? "assets/icons/vehicle_gray.svg"
                            : dashFahrzeuge.containsMouse ? "assets/icons/vehicle_orange.svg" : "assets/icons/vehicle_white.svg"
                        width: dashFahrzeuge.pressed ? 96 : dashFahrzeuge.containsMouse ? 128 : 96
                        height: width
                        fillMode: Image.PreserveAspectFit
                    }
                }
            }
        }
    }

    // Overlay für den Wizard - temporär deaktiviert
    Rectangle {
        id: wizardCard
        visible: wizardVisible
        anchors.centerIn: parent
        width: 400
        height: 300
        color: Style.background
        radius: Style.radiusLarge
        border.color: Style.border
        border.width: 1

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: Style.spacingLarge
            spacing: Style.spacingNormal

            Text {
                text: "Wizard wird geladen..."
                font.pixelSize: Style.fontSizeTitle
                font.bold: true
                color: Style.text
                Layout.alignment: Qt.AlignHCenter
            }

            Text {
                text: "Diese Funktion wird noch implementiert."
                font.pixelSize: Style.fontSizeNormal
                color: Style.text
                Layout.alignment: Qt.AlignHCenter
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 40
                color: Style.primary
                radius: Style.radiusNormal

                MouseArea {
                    anchors.fill: parent
                    onClicked: wizardVisible = false
                }

                Text {
                    anchors.centerIn: parent
                    text: "Schließen"
                    font.pixelSize: Style.fontSizeNormal
                    color: Style.text
                }
            }
        }
    }

    // Funktionen
    function showSidebar(index) {
        activeIndex = index
        sidebarVisible = true
        stackVisible = true
        
        // Verzögerung für Animation mit Timer
        delayTimer.start()
    }

    // Timer für Verzögerung
    Timer {
        id: delayTimer
        interval: 300
        onTriggered: {
            updateActiveButton()
            loadPage(activeIndex)
        }
    }

    function updateActiveButton() {
        // Keine pressed-Properties mehr setzen, da MouseArea.pressed read-only ist.
        // Hier kann ggf. eine eigene State-Variable für aktive Buttons gepflegt werden, falls gewünscht.
    }

    function loadPage(index) {
        switch(index) {
            case 0:
                loadAbrechnungsseite()
                break
            case 1:
                loadDatenseite()
                break
            case 2:
                loadMitarbeiterSeite()
                break
            case 3:
                loadFahrzeugSeite()
                break
        }
    }

    function loadAbrechnungsseite() {
        stackView.replace("Abrechnungsseite.qml", {
            goHome: function() { goBack(); }
        })
    }

    function loadDatenseite() {
        stackView.replace("Datenseite.qml")
    }

    function loadMitarbeiterSeite() {
        stackView.replace("MitarbeiterSeite.qml")
    }

    function loadFahrzeugSeite() {
        stackView.replace("FahrzeugSeite.qml", {
            goHome: function() { stackVisible = false; }
        })
    }

    function goBack() {
        sidebarVisible = false
        stackVisible = false
        activeIndex = -1
    }

    Connections {
        target: abrechnungsBackend
        function onErgebnisseChanged() {
            showSidebar(0)
        }
    }
} 