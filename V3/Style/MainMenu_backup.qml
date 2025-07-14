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

            Text {
                text: "🚀 Dashboard"
                font.pixelSize: Style.fontSizeHuge
                font.bold: true
                color: Style.text
                Layout.alignment: Qt.AlignHCenter
            }

            Text {
                text: "Wähle eine Seite aus"
                font.pixelSize: Style.fontSizeTitle
                color: Style.textMuted
                Layout.alignment: Qt.AlignHCenter
            }

            GridLayout {
                columns: 2
                rowSpacing: Style.spacingHuge
                columnSpacing: Style.spacingExtra
                Layout.alignment: Qt.AlignHCenter

                // Abrechnung Button
                Button {
                    text: "💰 Abrechnung"
                    Layout.preferredWidth: 200
                    Layout.preferredHeight: Style.buttonHeightHuge
                    font.pixelSize: Style.fontSizeTitle
                    font.bold: true
                    background: Rectangle {
                        color: parent.pressed ? Style.buttonPressed : 
                               parent.hovered ? Style.buttonHover : Style.buttonTransparent
                        radius: Style.radiusLarge
                        border.color: parent.hovered ? Style.buttonBorderHover : Style.buttonBorder
                        border.width: 1
                    }
                    contentItem: Text {
                        text: parent.text
                        color: Style.text
                        font: parent.font
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                    onClicked: {
                        abrechnungsBackend.show_wizard_and_load_page()
                    }
                }

                // Daten Button
                Button {
                    text: "📊 Daten"
                    Layout.preferredWidth: 200
                    Layout.preferredHeight: Style.buttonHeightHuge
                    font.pixelSize: Style.fontSizeTitle
                    font.bold: true
                    background: Rectangle {
                        color: parent.pressed ? Style.buttonPressed : 
                               parent.hovered ? Style.buttonHover : Style.buttonTransparent
                        radius: Style.radiusLarge
                        border.color: parent.hovered ? Style.buttonBorderHover : Style.buttonBorder
                        border.width: 1
                    }
                    contentItem: Text {
                        text: parent.text
                        color: Style.text
                        font: parent.font
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                    onClicked: showSidebar(1)
                }

                // Mitarbeiter Button
                Button {
                    text: "👥 Mitarbeiter"
                    Layout.preferredWidth: 200
                    Layout.preferredHeight: Style.buttonHeightHuge
                    font.pixelSize: Style.fontSizeTitle
                    font.bold: true
                    background: Rectangle {
                        color: parent.pressed ? Style.buttonPressed : 
                               parent.hovered ? Style.buttonHover : Style.buttonTransparent
                        radius: Style.radiusLarge
                        border.color: parent.hovered ? Style.buttonBorderHover : Style.buttonBorder
                        border.width: 1
                    }
                    contentItem: Text {
                        text: parent.text
                        color: Style.text
                        font: parent.font
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                    onClicked: showSidebar(2)
                }

                // Fahrzeuge Button
                Button {
                    text: "🚗 Fahrzeuge"
                    Layout.preferredWidth: 200
                    Layout.preferredHeight: Style.buttonHeightHuge
                    font.pixelSize: Style.fontSizeTitle
                    font.bold: true
                    background: Rectangle {
                        color: parent.pressed ? Style.buttonPressed : 
                               parent.hovered ? Style.buttonHover : Style.buttonTransparent
                        radius: Style.radiusLarge
                        border.color: parent.hovered ? Style.buttonBorderHover : Style.buttonBorder
                        border.width: 1
                    }
                    contentItem: Text {
                        text: parent.text
                        color: Style.text
                        font: parent.font
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }
                    onClicked: showSidebar(3)
                }
            }
        }
    }

    // Sidebar
    Rectangle {
        id: sidebar
        width: Style.sidebarWidth
        height: Style.sidebarHeight
        color: Style.surface
        radius: Style.radiusLarge
        visible: sidebarVisible
        anchors.right: parent.right
        anchors.verticalCenter: parent.verticalCenter
        anchors.rightMargin: sidebarVisible ? Style.spacingHuge : -width
        border.color: Style.border
        border.width: 1

        Behavior on anchors.rightMargin {
            NumberAnimation { duration: Style.animationNormal }
        }

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: Style.spacingNormal
            spacing: Style.spacingLarge

            // Abrechnung Button
            Button {
                id: btnAbrechnung
                Layout.fillWidth: true
                Layout.preferredHeight: 60
                text: "💰"
                font.pixelSize: 24
                background: Rectangle {
                    color: parent.pressed ? Style.buttonPressed : 
                           parent.hovered ? Style.buttonHover : Style.buttonTransparent
                    radius: Style.radiusNormal
                    border.color: parent.hovered ? Style.buttonBorderHover : Style.buttonBorder
                    border.width: 1
                }
                contentItem: Text {
                    text: parent.text
                    color: Style.text
                    font: parent.font
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
                onClicked: {
                    abrechnungsBackend.show_wizard_and_load_page()
                }
            }

            // Daten Button
            Button {
                id: btnDaten
                Layout.fillWidth: true
                Layout.preferredHeight: 60
                text: "📊"
                font.pixelSize: 24
                background: Rectangle {
                    color: parent.pressed ? Style.buttonPressed : 
                           parent.hovered ? Style.buttonHover : Style.buttonTransparent
                    radius: Style.radiusNormal
                    border.color: parent.hovered ? Style.buttonBorderHover : Style.buttonBorder
                    border.width: 1
                }
                contentItem: Text {
                    text: parent.text
                    color: Style.text
                    font: parent.font
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
                onClicked: {
                    activeIndex = 1
                    updateActiveButton()
                    loadDatenseite()
                }
            }

            // Mitarbeiter Button
            Button {
                id: btnMitarbeiter
                Layout.fillWidth: true
                Layout.preferredHeight: 60
                text: "👥"
                font.pixelSize: 24
                background: Rectangle {
                    color: parent.pressed ? Style.buttonPressed : 
                           parent.hovered ? Style.buttonHover : Style.buttonTransparent
                    radius: Style.radiusNormal
                    border.color: parent.hovered ? Style.buttonBorderHover : Style.buttonBorder
                    border.width: 1
                }
                contentItem: Text {
                    text: parent.text
                    color: Style.text
                    font: parent.font
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
                onClicked: {
                    activeIndex = 2
                    updateActiveButton()
                    loadMitarbeiterSeite()
                }
            }

            // Fahrzeuge Button
            Button {
                id: btnFahrzeuge
                Layout.fillWidth: true
                Layout.preferredHeight: 60
                text: "🚗"
                font.pixelSize: 24
                background: Rectangle {
                    color: parent.pressed ? Style.buttonPressed : 
                           parent.hovered ? Style.buttonHover : Style.buttonTransparent
                    radius: Style.radiusNormal
                    border.color: parent.hovered ? Style.buttonBorderHover : Style.buttonBorder
                    border.width: 1
                }
                contentItem: Text {
                    text: parent.text
                    color: Style.text
                    font: parent.font
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
                onClicked: {
                    activeIndex = 3
                    updateActiveButton()
                    loadFahrzeugSeite()
                }
            }

            // Zurück Button
            Button {
                Layout.fillWidth: true
                Layout.preferredHeight: 60
                text: "🏠"
                font.pixelSize: 24
                background: Rectangle {
                    color: parent.pressed ? Style.buttonPressed : 
                           parent.hovered ? Style.buttonHover : Style.buttonTransparent
                    radius: Style.radiusNormal
                    border.color: parent.hovered ? Style.buttonBorderHover : Style.buttonBorder
                    border.width: 1
                }
                contentItem: Text {
                    text: parent.text
                    color: Style.text
                    font: parent.font
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
                onClicked: {
                    goBack()
                }
            }
        }
    }

    // Overlay für den Wizard
    GenericWizardCard {
        id: wizardCard
        visible: wizardVisible
        anchors.centerIn: parent
        fahrerList: abrechnungsBackend.fahrer_list()
        fahrzeugList: abrechnungsBackend.fahrzeug_list()
        kwList: abrechnungsBackend.kw_list()
        onWizardFertig: {
            wizardVisible = false
            abrechnungsBackend.auswerten(fahrer, fahrzeug, kw)
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
        // Alle Buttons zurücksetzen
        btnAbrechnung.background.border.color = Style.buttonBorder
        btnDaten.background.border.color = Style.buttonBorder
        btnMitarbeiter.background.border.color = Style.buttonBorder
        btnFahrzeuge.background.border.color = Style.buttonBorder
        
        // Aktiven Button hervorheben
        switch(activeIndex) {
            case 0:
                btnAbrechnung.background.border.color = Style.primary
                break
            case 1:
                btnDaten.background.border.color = Style.success
                break
            case 2:
                btnMitarbeiter.background.border.color = Style.primary
                break
            case 3:
                btnFahrzeuge.background.border.color = Style.accent
                break
        }
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
        stackView.replace("Abrechnungsseite.qml")
    }

    function loadDatenseite() {
        stackView.replace("Datenseite.qml")
    }

    function loadMitarbeiterSeite() {
        stackView.replace("MitarbeiterSeite.qml")
    }

    function loadFahrzeugSeite() {
        stackView.replace("FahrzeugSeite.qml")
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