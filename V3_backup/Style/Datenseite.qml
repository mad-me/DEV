import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Window 2.15
import QtCharts 2.15

Rectangle {
    id: root
    color: Style.background

    // Properties für die Daten
    property var chartData: []
    property var filteredData: []
    property string selectedTimeRange: "week"
    property string selectedDriver: "all"
    property string selectedPlatform: "all"
    property bool isLoading: false
    property bool showDataView: false
    property string currentView: "icons" // "icons", "import", "charts", "wizard"
    property bool wizardVisible: false
    property string selectedImportType: "umsaetze"
    
    // Import-Status Properties (von datenBackend)
    property bool isImporting: datenBackend.isImporting
    property int importProgress: datenBackend.importProgress
    property int importTotalFiles: datenBackend.importTotalFiles
    property int importCurrentFile: datenBackend.importCurrentFile

    // Funktionen für dynamische Texte
    function getImportTypeText() {
        switch(selectedImportType) {
            case "umsaetze": return "Umsätze"
            case "gehalt": return "Gehalt"
            case "funk": return "Funk"
            default: return "Unbekannt"
        }
    }

    function getImportDescription() {
        switch(selectedImportType) {
            case "umsaetze": return "Umsatzdaten von verschiedenen Plattformen"
            case "gehalt": return "Gehaltsdaten und Lohnabrechnungen"
            case "funk": return "Funkdaten und Kommunikationsprotokolle"
            default: return "Daten"
        }
    }

    function getOption1Icon() {
        switch(selectedImportType) {
            case "umsaetze": return "🚗"
            case "gehalt": return "💰"
            case "funk": return "📻"
            default: return "📁"
        }
    }

    function getOption1Text() {
        switch(selectedImportType) {
            case "umsaetze": return "Uber"
            case "gehalt": return "Monatlich"
            case "funk": return "Digital"
            default: return "Option 1"
        }
    }

    function getOption2Icon() {
        switch(selectedImportType) {
            case "umsaetze": return "⚡"
            case "gehalt": return "💳"
            case "funk": return "📡"
            default: return "📁"
        }
    }

    function getOption2Text() {
        switch(selectedImportType) {
            case "umsaetze": return "Bolt"
            case "gehalt": return "Wöchentlich"
            case "funk": return "Analog"
            default: return "Option 2"
        }
    }

    function getOption3Icon() {
        switch(selectedImportType) {
            case "umsaetze": return "📞"
            case "gehalt": return "🏦"
            case "funk": return "📶"
            default: return "📁"
        }
    }

    function getOption3Text() {
        switch(selectedImportType) {
            case "umsaetze": return "40100"
            case "gehalt": return "Jährlich"
            case "funk": return "Hybrid"
            default: return "Option 3"
        }
    }

    // Hauptinhalt - Icons View (wie Startseite)
    Rectangle {
        id: iconsView
        anchors.fill: parent
        anchors.margins: Style.spacingHuge
        color: "transparent"
        visible: currentView === "icons"

        ColumnLayout {
            anchors.centerIn: parent
            spacing: Style.spacingExtra

            GridLayout {
                columns: 2
                rowSpacing: Style.spacingNormal
                columnSpacing: Style.spacingNormal
                Layout.alignment: Qt.AlignHCenter

                // Import Button
                Item {
                    width: 240; height: 240
                    MouseArea {
                        id: dashImport
                        anchors.fill: parent
                        hoverEnabled: true
                        onClicked: {
                            datenBackend.show_import_wizard()
                        }
                        cursorShape: Qt.PointingHandCursor
                    }
                    Image {
                        anchors.centerIn: parent
                        source: dashImport.pressed ? "assets/icons/import_gray.svg"
                            : dashImport.containsMouse ? "assets/icons/import_orange.svg" : "assets/icons/import_white.svg"
                        width: dashImport.pressed ? 96 : dashImport.containsMouse ? 128 : 96
                        height: width
                        fillMode: Image.PreserveAspectFit
                    }
                }

                // Charts Button (größer)
                Item {
                    width: 280; height: 280
                    MouseArea {
                        id: dashCharts
                        anchors.fill: parent
                        hoverEnabled: true
                        onClicked: {
                            datenBackend.show_generic_wizard()
                        }
                        cursorShape: Qt.PointingHandCursor
                    }
                    Image {
                        anchors.centerIn: parent
                        source: dashCharts.pressed ? "assets/icons/charts_gray.svg"
                            : dashCharts.containsMouse ? "assets/icons/charts_orange.svg" : "assets/icons/charts_white.svg"
                        width: dashCharts.pressed ? 112 : dashCharts.containsMouse ? 150 : 112
                        height: width
                        fillMode: Image.PreserveAspectFit
                    }
                }
            }
        }
    }

    // Import View
    Rectangle {
        id: importView
        anchors.fill: parent
        anchors.margins: Style.spacingHuge
        color: "transparent"
        visible: currentView === "import"

        ColumnLayout {
            anchors.fill: parent
            spacing: Style.spacingLarge

            // Import-Karte
            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                color: Style.border
                radius: Style.radiusLarge
                border.color: Style.border
                border.width: 1

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: Style.spacingLarge
                    spacing: Style.spacingNormal

                    Text {
                        id: importTitle
                        text: "📥 Daten Import - " + getImportTypeText()
                        font.pixelSize: Style.fontSizeTitle
                        font.bold: true
                        color: Style.text
                    }

                    Text {
                        id: importDescription
                        text: "Importieren Sie Ihre " + getImportDescription()
                        font.pixelSize: Style.fontSizeNormal
                        color: Style.text
                        wrapMode: Text.WordWrap
                        horizontalAlignment: Text.AlignHCenter
                    }

                    // Import-Buttons basierend auf ausgewähltem Typ
                    GridLayout {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        columns: 3
                        rowSpacing: Style.spacingLarge
                        columnSpacing: Style.spacingLarge

                        // Erste Option
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            color: Style.primary
                            radius: Style.radiusNormal

                            MouseArea {
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: importOption1()
                            }

                            ColumnLayout {
                                anchors.centerIn: parent
                                spacing: Style.spacingSmall

                                Text {
                                    id: option1Icon
                                    text: getOption1Icon()
                                    font.pixelSize: 40
                                }

                                Text {
                                    id: option1Text
                                    text: getOption1Text()
                                    font.pixelSize: Style.fontSizeTitle
                                    font.bold: true
                                    color: Style.text
                                }
                            }
                        }

                        // Zweite Option
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            color: Style.primary
                            radius: Style.radiusNormal

                            MouseArea {
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: importOption2()
                            }

                            ColumnLayout {
                                anchors.centerIn: parent
                                spacing: Style.spacingSmall

                                Text {
                                    id: option2Icon
                                    text: getOption2Icon()
                                    font.pixelSize: 40
                                }

                                Text {
                                    id: option2Text
                                    text: getOption2Text()
                                    font.pixelSize: Style.fontSizeTitle
                                    font.bold: true
                                    color: Style.text
                                }
                            }
                        }

                        // Dritte Option
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            color: Style.primary
                            radius: Style.radiusNormal

                            MouseArea {
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: importOption3()
                            }

                            ColumnLayout {
                                anchors.centerIn: parent
                                spacing: Style.spacingSmall

                                Text {
                                    id: option3Icon
                                    text: getOption3Icon()
                                    font.pixelSize: 40
                                }

                                Text {
                                    id: option3Text
                                    text: getOption3Text()
                                    font.pixelSize: Style.fontSizeTitle
                                    font.bold: true
                                    color: Style.text
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    // Charts View (bestehende Datenansicht)
    Rectangle {
        id: chartsView
        anchors.fill: parent
        anchors.margins: Style.spacingHuge
        color: "transparent"
        visible: currentView === "charts"

        // Hauptinhalt - Grid Layout für bessere Verteilung
        GridLayout {
            anchors.fill: parent
            columns: 3
            rowSpacing: Style.spacingLarge
            columnSpacing: Style.spacingLarge

            // Linke Spalte - Filter und Statistik
            ColumnLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.columnSpan: 1
                spacing: Style.spacingLarge

                // Filter-Karte
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 200
                    color: Style.border
                    radius: Style.radiusLarge
                    border.color: Style.border
                    border.width: 1

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: Style.spacingLarge
                        spacing: Style.spacingNormal

                        Text {
                            text: "🔍 Filter & Einstellungen"
                            font.pixelSize: Style.fontSizeTitle
                            font.bold: true
                            color: Style.text
                        }

                        // Zeitraum-Filter
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: Style.spacingSmall

                            Text {
                                text: "Zeitraum:"
                                font.pixelSize: Style.fontSizeNormal
                                color: Style.text
                            }

                            ComboBox {
                                id: timeRangeCombo
                                Layout.fillWidth: true
                                model: [
                                    { text: "Letzte Woche", value: "week" },
                                    { text: "Letzter Monat", value: "month" },
                                    { text: "Letztes Quartal", value: "quarter" },
                                    { text: "Letztes Jahr", value: "year" }
                                ]
                                textRole: "text"
                                valueRole: "value"
                                currentIndex: 0
                                background: Rectangle {
                                    color: Style.background
                                    radius: Style.radiusNormal
                                    border.color: Style.border
                                    border.width: 1
                                }
                                onCurrentValueChanged: {
                                    selectedTimeRange = currentValue
                                    loadData()
                                }
                            }
                        }

                        // Fahrer-Filter
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: Style.spacingSmall

                            Text {
                                text: "Fahrer:"
                                font.pixelSize: Style.fontSizeNormal
                                color: Style.text
                            }

                            ComboBox {
                                id: driverFilterCombo
                                Layout.fillWidth: true
                                model: [
                                    { text: "Alle Fahrer", value: "all" },
                                    { text: "Max Mustermann", value: "max" },
                                    { text: "Anna Schmidt", value: "anna" }
                                ]
                                textRole: "text"
                                valueRole: "value"
                                currentIndex: 0
                                background: Rectangle {
                                    color: Style.background
                                    radius: Style.radiusNormal
                                    border.color: Style.border
                                    border.width: 1
                                }
                                onCurrentValueChanged: {
                                    selectedDriver = currentValue
                                    loadData()
                                }
                            }
                        }

                        // Platform-Filter
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: Style.spacingSmall

                            Text {
                                text: "Platform:"
                                font.pixelSize: Style.fontSizeNormal
                                color: Style.text
                            }

                            ComboBox {
                                id: platformFilterCombo
                                Layout.fillWidth: true
                                model: [
                                    { text: "Alle Platforms", value: "all" },
                                    { text: "Uber", value: "uber" },
                                    { text: "Bolt", value: "bolt" },
                                    { text: "40100", value: "40100" }
                                ]
                                textRole: "text"
                                valueRole: "value"
                                currentIndex: 0
                                background: Rectangle {
                                    color: Style.background
                                    radius: Style.radiusNormal
                                    border.color: Style.border
                                    border.width: 1
                                }
                                onCurrentValueChanged: {
                                    selectedPlatform = currentValue
                                    loadData()
                                }
                            }
                        }
                    }
                }

                // Kompakte Statistik-Card
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 150
                    color: Style.border
                    radius: Style.radiusLarge
                    border.color: Style.border
                    border.width: 1

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: Style.spacingLarge
                        spacing: Style.spacingNormal

                        Text {
                            text: "📊 Übersicht"
                            font.pixelSize: Style.fontSizeTitle
                            font.bold: true
                            color: Style.text
                        }

                        // 2x2 Grid für die 4 Werte
                        GridLayout {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            columns: 2
                            rowSpacing: Style.spacingNormal
                            columnSpacing: Style.spacingLarge

                            // Umsatz
                            RowLayout {
                                Layout.fillWidth: true
                                spacing: Style.spacingSmall

                                Text {
                                    text: "💰"
                                    font.pixelSize: 20
                                }

                                ColumnLayout {
                                    Layout.fillWidth: true
                                    spacing: Style.spacingSmall

                                    Text {
                                        text: "Umsatz"
                                        font.pixelSize: Style.fontSizeSmall
                                        color: Style.text
                                    }

                                    Text {
                                        text: "€ 2,847.50"
                                        font.pixelSize: Style.fontSizeNormal
                                        font.bold: true
                                        color: Style.text
                                    }
                                }
                            }

                            // Fahrten
                            RowLayout {
                                Layout.fillWidth: true
                                spacing: Style.spacingSmall

                                Text {
                                    text: "🚗"
                                    font.pixelSize: 20
                                }

                                ColumnLayout {
                                    Layout.fillWidth: true
                                    spacing: Style.spacingSmall

                                    Text {
                                        text: "Fahrten"
                                        font.pixelSize: Style.fontSizeSmall
                                        color: Style.text
                                    }

                                    Text {
                                        text: "127"
                                        font.pixelSize: Style.fontSizeNormal
                                        font.bold: true
                                        color: Style.text
                                    }
                                }
                            }

                            // Stunden
                            RowLayout {
                                Layout.fillWidth: true
                                spacing: Style.spacingSmall

                                Text {
                                    text: "⏰"
                                    font.pixelSize: 20
                                }

                                ColumnLayout {
                                    Layout.fillWidth: true
                                    spacing: Style.spacingSmall

                                    Text {
                                        text: "Stunden"
                                        font.pixelSize: Style.fontSizeSmall
                                        color: Style.text
                                    }

                                    Text {
                                        text: "42.5h"
                                        font.pixelSize: Style.fontSizeNormal
                                        font.bold: true
                                        color: Style.text
                                    }
                                }
                            }

                            // Durchschnitt
                            RowLayout {
                                Layout.fillWidth: true
                                spacing: Style.spacingSmall

                                Text {
                                    text: "📈"
                                    font.pixelSize: 20
                                }

                                ColumnLayout {
                                    Layout.fillWidth: true
                                    spacing: Style.spacingSmall

                                    Text {
                                        text: "Ø/Stunde"
                                        font.pixelSize: Style.fontSizeSmall
                                        color: Style.text
                                    }

                                    Text {
                                        text: "€ 22.40"
                                        font.pixelSize: Style.fontSizeNormal
                                        font.bold: true
                                        color: Style.text
                                    }
                                }
                            }
                        }
                    }
                }

                // NEU: WizardCard für Datenbank-Navigation (unten links)
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 140
                    color: Style.border
                    radius: Style.radiusLarge
                    border.color: Style.border
                    border.width: 1

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: Style.spacingLarge
                        spacing: Style.spacingNormal

                        Text {
                            text: "🗄️ Datenbank-Navigation"
                            font.pixelSize: Style.fontSizeTitle
                            font.bold: true
                            color: Style.text
                        }
                        // Platzhalter für verkleinerte GenericWizardCard
                        Rectangle {
                            width: 80; height: 40
                            color: "#222"
                            border.color: "#f79009"
                            border.width: 1
                            radius: 8
                            Text {
                                anchors.centerIn: parent
                                text: "Wizard (Mini)"
                                color: "#fff"
                                font.pixelSize: 12
                            }
                        }
                        // Dummy-ComboBox für Datenbanken
                        ComboBox {
                            id: dbCombo
                            Layout.fillWidth: true
                            model: ["Datenbank1", "Datenbank2", "Datenbank3"]
                            currentIndex: 0
                        }
                        // Dummy-ComboBox für Tabellen (sichtbar nach Auswahl)
                        ComboBox {
                            id: tableCombo
                            Layout.fillWidth: true
                            model: dbCombo.currentIndex === 0 ? ["TabelleA", "TabelleB"] : dbCombo.currentIndex === 1 ? ["TabelleC", "TabelleD"] : ["TabelleE"]
                            visible: dbCombo.currentIndex >= 0
                        }
                    }
                }
            }

            // Mittlere Spalte - Charts
            ColumnLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.columnSpan: 1
                spacing: Style.spacingLarge

                // Umsatz-Chart
                Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    color: Style.border
                    radius: Style.radiusLarge
                    border.color: Style.border
                    border.width: 1

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: Style.spacingLarge
                        spacing: Style.spacingNormal

                        Text {
                            text: "📊 Umsatz-Entwicklung"
                            font.pixelSize: Style.fontSizeTitle
                            font.bold: true
                            color: Style.text
                        }

                        // Platzhalter für Chart
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            color: Style.background
                            radius: Style.radiusNormal

                            Text {
                                anchors.centerIn: parent
                                text: "📈 Chart wird geladen..."
                                font.pixelSize: Style.fontSizeNormal
                                color: Style.text
                                opacity: 0.6
                            }
                        }
                    }
                }

                // Platform-Verteilung
                Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    color: Style.border
                    radius: Style.radiusLarge
                    border.color: Style.border
                    border.width: 1

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: Style.spacingLarge
                        spacing: Style.spacingNormal

                        Text {
                            text: "🍕 Platform-Verteilung"
                            font.pixelSize: Style.fontSizeTitle
                            font.bold: true
                            color: Style.text
                        }

                        // Platzhalter für Pie Chart
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            color: Style.background
                            radius: Style.radiusNormal

                            Text {
                                anchors.centerIn: parent
                                text: "🥧 Pie Chart wird geladen..."
                                font.pixelSize: Style.fontSizeNormal
                                color: Style.text
                                opacity: 0.6
                            }
                        }
                    }
                }
            }

            // Rechte Spalte - Detaillierte Tabelle
            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.columnSpan: 1
                color: Style.border
                radius: Style.radiusLarge
                border.color: Style.border
                border.width: 1

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: Style.spacingLarge
                    spacing: Style.spacingNormal

                    Text {
                        text: "📋 Detaillierte Fahrten"
                        font.pixelSize: Style.fontSizeTitle
                        font.bold: true
                        color: Style.text
                    }

                    // Tabellen-Header
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 40
                        color: Style.background
                        radius: Style.radiusNormal

                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: Style.spacingNormal
                            spacing: Style.spacingNormal

                            Text {
                                text: "Datum"
                                font.pixelSize: Style.fontSizeSmall
                                font.bold: true
                                color: Style.text
                                Layout.preferredWidth: 80
                            }

                            Text {
                                text: "Platform"
                                font.pixelSize: Style.fontSizeSmall
                                font.bold: true
                                color: Style.text
                                Layout.preferredWidth: 60
                            }

                            Text {
                                text: "Fahrer"
                                font.pixelSize: Style.fontSizeSmall
                                font.bold: true
                                color: Style.text
                                Layout.preferredWidth: 80
                            }

                            Text {
                                text: "Umsatz"
                                font.pixelSize: Style.fontSizeSmall
                                font.bold: true
                                color: Style.text
                                Layout.preferredWidth: 60
                            }

                            Text {
                                text: "Status"
                                font.pixelSize: Style.fontSizeSmall
                                font.bold: true
                                color: Style.text
                                Layout.fillWidth: true
                            }
                        }
                    }

                    // Tabellen-Inhalt (ScrollView)
                    ScrollView {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        clip: true

                        ListView {
                            model: ListModel {
                                ListElement { datum: "2024-01-15"; platform: "Uber"; fahrer: "Max M."; umsatz: "€ 45.20"; status: "Abgeschlossen" }
                                ListElement { datum: "2024-01-15"; platform: "Bolt"; fahrer: "Anna S."; umsatz: "€ 38.50"; status: "Abgeschlossen" }
                                ListElement { datum: "2024-01-14"; platform: "40100"; fahrer: "Max M."; umsatz: "€ 52.80"; status: "Abgeschlossen" }
                                ListElement { datum: "2024-01-14"; platform: "Uber"; fahrer: "Anna S."; umsatz: "€ 41.30"; status: "Abgeschlossen" }
                                ListElement { datum: "2024-01-13"; platform: "Bolt"; fahrer: "Max M."; umsatz: "€ 47.90"; status: "Abgeschlossen" }
                                ListElement { datum: "2024-01-13"; platform: "Uber"; fahrer: "Anna S."; umsatz: "€ 39.20"; status: "Abgeschlossen" }
                                ListElement { datum: "2024-01-12"; platform: "40100"; fahrer: "Max M."; umsatz: "€ 48.60"; status: "Abgeschlossen" }
                                ListElement { datum: "2024-01-12"; platform: "Bolt"; fahrer: "Anna S."; umsatz: "€ 35.80"; status: "Abgeschlossen" }
                            }

                            delegate: Rectangle {
                                width: parent.width
                                height: 35
                                color: index % 2 === 0 ? Style.background : Style.border

                                RowLayout {
                                    anchors.fill: parent
                                    anchors.margins: Style.spacingSmall
                                    spacing: Style.spacingSmall

                                    Text {
                                        text: datum
                                        font.pixelSize: Style.fontSizeSmall
                                        color: Style.text
                                        Layout.preferredWidth: 80
                                    }

                                    Text {
                                        text: platform
                                        font.pixelSize: Style.fontSizeSmall
                                        color: Style.text
                                        Layout.preferredWidth: 60
                                    }

                                    Text {
                                        text: fahrer
                                        font.pixelSize: Style.fontSizeSmall
                                        color: Style.text
                                        Layout.preferredWidth: 80
                                    }

                                    Text {
                                        text: umsatz
                                        font.pixelSize: Style.fontSizeSmall
                                        color: Style.text
                                        Layout.preferredWidth: 60
                                    }

                                    Rectangle {
                                        Layout.preferredWidth: 70
                                        Layout.preferredHeight: 18
                                        color: Style.success
                                        radius: Style.radiusSmall

                                        Text {
                                            anchors.centerIn: parent
                                            text: status
                                            font.pixelSize: Style.fontSizeSmall
                                            color: Style.text
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    // BottomBar (aus Abrechnungsseite kopiert)
    RowLayout {
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 24
        spacing: 32
        z: 1000
        
        // Home-Button
        MouseArea {
            id: homeArea
            width: 56; height: 56
            cursorShape: Qt.PointingHandCursor
            hoverEnabled: true
            onClicked: {
                if (currentView === "icons") {
                    goHome()
                } else {
                    currentView = "icons"
                    showDataView = false
                    wizardVisible = false
                    selectedImportType = ""
                }
            }
            Image {
                anchors.centerIn: parent
                source: homeArea.pressed ? "assets/icons/home_gray.svg"
                    : homeArea.containsMouse ? "assets/icons/home_orange.svg" : "assets/icons/home_white.svg"
                width: homeArea.pressed ? 32 : homeArea.containsMouse ? 40 : 32
                height: width
                fillMode: Image.PreserveAspectFit
            }
        }
        
        // Check-Button (deaktiviert für jetzt)
        MouseArea {
            id: checkArea
            width: 56; height: 56
            cursorShape: Qt.PointingHandCursor
            hoverEnabled: true
            onClicked: {
                // Deaktiviert für jetzt
                console.log("Check-Button deaktiviert")
            }
            Image {
                anchors.centerIn: parent
                source: checkArea.pressed ? "assets/icons/check_gray.svg"
                    : checkArea.containsMouse ? "Style/assets/icons/check_orange.svg" : "Style/assets/icons/check_white.svg"
                width: checkArea.pressed ? 32 : checkArea.containsMouse ? 40 : 32
                height: width
                fillMode: Image.PreserveAspectFit
            }
        }
        
        // Redo-Button (deaktiviert für jetzt)
        MouseArea {
            id: redoArea
            width: 56; height: 56
            cursorShape: Qt.PointingHandCursor
            hoverEnabled: true
            onClicked: {
                // Deaktiviert für jetzt
                console.log("Redo-Button deaktiviert")
            }
            Image {
                anchors.centerIn: parent
                source: redoArea.pressed ? "assets/icons/redo_gray.svg"
                    : redoArea.containsMouse ? "assets/icons/redo_orange.svg" : "assets/icons/redo_white.svg"
                width: redoArea.pressed ? 32 : redoArea.containsMouse ? 40 : 32
                height: width
                fillMode: Image.PreserveAspectFit
            }
        }
    }

    // Funktionen
    function goHome() {
        // Zurück zur Hauptseite
        stackVisible = false
    }

    function loadData() {
        // Lade Daten basierend auf den aktuellen Filtern
        console.log("Lade Daten...")
    }

    function exportData() {
        // Export-Funktion
        console.log("Exportiere Daten...")
    }

    function importOption1() {
        showMessage("Import", "Option 1 wird importiert...")
    }

    function importOption2() {
        showMessage("Import", "Option 2 wird importiert...")
    }

    function importOption3() {
        showMessage("Import", "Option 3 wird importiert...")
    }

    function importUberData() {
        showMessage("Import", "Uber-Daten werden importiert...")
    }

    function importBoltData() {
        showMessage("Import", "Bolt-Daten werden importiert...")
    }

    function import40100Data() {
        showMessage("Import", "40100-Daten werden importiert...")
    }

    function showMessage(title, message) {
        console.log(title + ": " + message)
    }
    
    // Import-Status-Overlay (integriert)
    Rectangle {
        id: importStatusOverlay
        anchors.fill: parent
        color: "transparent"
        visible: isImporting
        z: 2000  // Über allem anderen
        
        // Hintergrund-Overlay
        Rectangle {
            anchors.fill: parent
            color: "#80000000"  // Semi-transparent schwarz
        }
        
        // Haupt-Container
        Rectangle {
            width: 400
            height: 300
            anchors.centerIn: parent
            radius: 10
            color: "#ffffff"
            border.color: "#cccccc"
            border.width: 1
            
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 20
                spacing: 15
                
                // Titel
                Text {
                    text: "Import läuft..."
                    font.pixelSize: 18
                    font.bold: true
                    Layout.alignment: Qt.AlignHCenter
                }
                
                // Spinner/Loader
                BusyIndicator {
                    id: spinner
                    running: isImporting
                    Layout.alignment: Qt.AlignHCenter
                    Layout.preferredWidth: 50
                    Layout.preferredHeight: 50
                }
                
                // Status-Text
                Text {
                    id: statusText
                    text: "Bereite Import vor..."
                    font.pixelSize: 14
                    wrapMode: Text.WordWrap
                    Layout.fillWidth: true
                    Layout.alignment: Qt.AlignHCenter
                }
                
                // Fortschrittsbalken
                ProgressBar {
                    id: progressBar
                    value: importProgress / 100
                    Layout.fillWidth: true
                    Layout.preferredHeight: 20
                }
                
                // Fortschritts-Text
                Text {
                    text: importCurrentFile + " von " + importTotalFiles + " Dateien verarbeitet"
                    font.pixelSize: 12
                    color: "#666666"
                    Layout.alignment: Qt.AlignHCenter
                }
            }
        }
        
        // Connections für Status-Updates
        Connections {
            target: datenBackend
            
            function onImportStatusChanged(status) {
                statusText.text = status
            }
            
            function onImportFinished(success, message) {
                if (success) {
                    // Erfolgs-Meldung anzeigen
                    // Entferne die Dialoge und deren open()-Aufrufe
                } else {
                    // Fehler-Meldung anzeigen
                    // Entferne die Dialoge und deren open()-Aufrufe
                }
            }
        }
    }
} 