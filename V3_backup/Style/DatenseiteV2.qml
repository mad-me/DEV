import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root
    width: parent ? parent.width : 1200
    height: parent ? parent.height : 800
    property var goHome: function() {
        // Fallback: Blende die Datenseite aus und zeige das MainMenu
        root.visible = false;
        if (typeof mainWindow !== 'undefined') {
            mainWindow.stackVisible = false;
        }
    }
    color: "#050505"
    radius: 8
    
    // Font-Definition
    FontLoader {
        id: ubuntuFont
        source: "assets/fonts/Ubuntu-Regular.ttf"
    }

    // Style-Definitionen
    QtObject {
        id: style
        property color background: "#050505"
        property color border: "#1a1a1a"
        property color primary: "#ff8c00"
        property color text: "#ffffff"
        property color textSecondary: "#cccccc"
        property color success: "#4CAF50"
        property color error: "#F44336"
        property color warning: "#FF9800"
        
        property int radiusNormal: 8
        property int radiusLarge: 12
        property int radiusSmall: 4
        
        property int spacingHuge: 32
        property int spacingLarge: 16
        property int spacingNormal: 12
        property int spacingSmall: 8
        
        property int fontSizeTitle: 24
        property int fontSizeNormal: 16
        property int fontSizeSmall: 14
    }
    
    // Globale Properties
    property string currentView: "dashboard" // "dashboard", "import", "export", "analytics"
    property bool isLoading: datenBackend ? datenBackend.isLoading : false
    property bool hasData: datenBackend ? datenBackend.hasData : false
    property var statisticsData: datenBackend ? datenBackend.statistics : ({})
    property string statusMessage: datenBackend ? datenBackend.statusMessage : "Bereit"
    
    // Performance Properties
    property var performanceData: datenBackend ? datenBackend.performanceData : ({})
    property bool cacheEnabled: datenBackend ? datenBackend.cacheEnabled : false
    
    // Filter Properties
    property string selectedTimeRange: "week"
    property string selectedDriver: "all"
    property string selectedPlatform: "all"
    property string searchText: ""

    // Home-Button
    MouseArea {
        id: homeButton
        anchors.left: parent.left
        anchors.leftMargin: 20
        anchors.top: parent.top
        anchors.topMargin: 48
        width: 60
        height: 60
        hoverEnabled: true
        onClicked: {
            if (typeof root.goHome === "function") {
                root.goHome();
            }
        }
        cursorShape: Qt.PointingHandCursor
        
        Image {
            anchors.centerIn: parent
            source: homeButton.containsMouse ? "assets/icons/home_orange.svg" : "assets/icons/home_gray.svg"
            width: homeButton.containsMouse ? 44 : 40
            height: width
            fillMode: Image.PreserveAspectFit
            
            Behavior on width {
                NumberAnimation { duration: 150; easing.type: Easing.OutQuad }
            }
        }
    }

    // Hauptlayout
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: style.spacingHuge
        anchors.topMargin: 52
        anchors.bottomMargin: 115
        anchors.rightMargin: 100
        anchors.leftMargin: 100
        spacing: 16

        // Header mit Titel und Status
        RowLayout {
            Layout.fillWidth: true
            spacing: style.spacingLarge
            
            // Klickbarer Titel für Ansichtswechsel
            Rectangle {
                Layout.fillWidth: true
                height: 50
                color: "transparent"
                
                MouseArea {
                    id: titleMouseArea
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: {
                        // Wechsel zwischen verschiedenen Ansichten
                        if (currentView === "dashboard") {
                            currentView = "analytics"
                        } else if (currentView === "analytics") {
                            currentView = "import"
                        } else if (currentView === "import") {
                            currentView = "export"
                        } else {
                            currentView = "dashboard"
                        }
                    }
                }
                
                Text {
                    anchors.left: parent.left
                    anchors.verticalCenter: parent.verticalCenter
                    text: {
                        switch(currentView) {
                            case "dashboard": return "Daten-Dashboard"
                            case "analytics": return "Daten-Analyse"
                            case "import": return "Daten-Import"
                            case "export": return "Daten-Export"
                            default: return "Datenverwaltung"
                        }
                    }
                    font.family: ubuntuFont.name
                    font.pixelSize: style.fontSizeTitle + 12
                    font.bold: true
                    color: titleMouseArea.containsMouse ? style.primary : style.text
                    
                    scale: titleMouseArea.containsMouse ? 1.05 : 1.0
                    
                    Behavior on scale {
                        NumberAnimation { duration: 150 }
                    }
                    
                    Behavior on color {
                        ColorAnimation { duration: 150 }
                    }
                }
            }
            
            // Status-Anzeige
            Rectangle {
                Layout.preferredWidth: 300
                height: 50
                radius: style.radiusNormal
                color: style.border
                border.color: isLoading ? style.primary : (hasData ? style.success : style.warning)
                border.width: 2
                
                RowLayout {
                    anchors.fill: parent
                    anchors.margins: style.spacingNormal
                    spacing: style.spacingSmall
                    
                    // Status-Icon
                    Text {
                        text: {
                            if (isLoading) return "🔄"
                            else if (hasData) return "📊"
                            else return "⚠️"
                        }
                        font.pixelSize: 20
                        color: style.text
                    }
                    
                    // Status-Text
                    Text {
                        Layout.fillWidth: true
                        text: statusMessage
                        font.family: ubuntuFont.name
                        font.pixelSize: style.fontSizeSmall
                        color: style.text
                        elide: Text.ElideRight
                    }
                    
                    // Performance-Indikator (wenn Cache aktiv)
                    Rectangle {
                        width: 8
                        height: 8
                        radius: 4
                        color: cacheEnabled ? style.success : "transparent"
                        visible: cacheEnabled
                    }
                }
            }
        }

        // Suchfeld
        RowLayout {
            Layout.fillWidth: true
            spacing: style.spacingLarge
            visible: currentView === "dashboard"
            
            Rectangle {
                Layout.fillWidth: true
                height: 64
                radius: style.radiusNormal
                color: "transparent"
                border.color: "transparent"
                border.width: 0
               
                property bool suchfeldAktiv: false
                property bool iconHovered: false
                
                MouseArea {
                    anchors.fill: parent
                    hoverEnabled: true
                    enabled: !parent.suchfeldAktiv
                    onEntered: parent.iconHovered = true
                    onExited: parent.iconHovered = false
                    onClicked: {
                        parent.suchfeldAktiv = true;
                        suchfeld.forceActiveFocus();
                    }
                }
                
                Image {
                    id: suchIcon
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.horizontalCenterOffset: 9
                    source: parent.iconHovered ? "assets/icons/data_orange.svg" : "assets/icons/data_gray.svg"
                    width: parent.iconHovered ? 32 : 24
                    height: parent.iconHovered ? 32 : 24
                    fillMode: Image.PreserveAspectFit
                    visible: !parent.suchfeldAktiv
                    opacity: 0.8
                }
                
                TextField {
                    id: suchfeld
                    anchors.top: parent.top
                    anchors.bottom: parent.bottom
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.margins: 2
                    anchors.rightMargin: 15
                    font.family: ubuntuFont.name
                    font.pixelSize: 32
                    color: style.text
                    background: null
                    padding: 32
                    horizontalAlignment: TextInput.AlignHCenter
                    verticalAlignment: TextInput.AlignVCenter
                    placeholderText: "Daten durchsuchen..."
                    selectionColor: "#a2ffb5"
                    selectedTextColor: "#232323"
                    visible: parent.suchfeldAktiv
                    cursorVisible: true
                    onTextChanged: {
                        searchText = text
                        if (datenBackend) {
                            datenBackend.searchData(text)
                        }
                    }
                    onActiveFocusChanged: {
                        if (!activeFocus && text.length === 0) {
                            parent.suchfeldAktiv = false;
                        }
                    }
                    Keys.onEscapePressed: {
                        text = ""
                        parent.suchfeldAktiv = false
                        focus = false
                    }
                }
            }
        }

        // Hauptinhalt basierend auf aktueller Ansicht
        StackLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            currentIndex: {
                switch(currentView) {
                    case "dashboard": return 0
                    case "analytics": return 1
                    case "import": return 2
                    case "export": return 3
                    default: return 0
                }
            }
            
            // Dashboard-Ansicht
            Rectangle {
                color: "transparent"
                
                GridLayout {
                    anchors.fill: parent
                    columns: 3
                    rowSpacing: style.spacingLarge
                    columnSpacing: style.spacingLarge
                    
                    // Linke Spalte - Filter und Statistiken
                    ColumnLayout {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        Layout.columnSpan: 1
                        spacing: style.spacingLarge
                        
                        // Filter-Karte
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 280
                            color: style.border
                            radius: style.radiusLarge
                            border.color: style.border
                            border.width: 1
                            
                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: style.spacingLarge
                                spacing: style.spacingNormal
                                
                                Text {
                                    text: "🔍 Filter & Einstellungen"
                                    font.family: ubuntuFont.name
                                    font.pixelSize: style.fontSizeTitle
                                    font.bold: true
                                    color: style.text
                                }
                                
                                // Zeitraum-Filter
                                ColumnLayout {
                                    Layout.fillWidth: true
                                    spacing: style.spacingSmall
                                    
                                    Text {
                                        text: "Zeitraum:"
                                        font.family: ubuntuFont.name
                                        font.pixelSize: style.fontSizeNormal
                                        color: style.text
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
                                            color: style.background
                                            radius: style.radiusNormal
                                            border.color: style.border
                                            border.width: 1
                                        }
                                        onCurrentValueChanged: {
                                            selectedTimeRange = currentValue
                                            if (datenBackend) {
                                                datenBackend.updateTimeRange(currentValue)
                                            }
                                        }
                                    }
                                }
                                
                                // Fahrer-Filter
                                ColumnLayout {
                                    Layout.fillWidth: true
                                    spacing: style.spacingSmall
                                    
                                    Text {
                                        text: "Fahrer:"
                                        font.family: ubuntuFont.name
                                        font.pixelSize: style.fontSizeNormal
                                        color: style.text
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
                                            color: style.background
                                            radius: style.radiusNormal
                                            border.color: style.border
                                            border.width: 1
                                        }
                                        onCurrentValueChanged: {
                                            selectedDriver = currentValue
                                            if (datenBackend) {
                                                datenBackend.updateDriverFilter(currentValue)
                                            }
                                        }
                                    }
                                }
                                
                                // Platform-Filter
                                ColumnLayout {
                                    Layout.fillWidth: true
                                    spacing: style.spacingSmall
                                    
                                    Text {
                                        text: "Platform:"
                                        font.family: ubuntuFont.name
                                        font.pixelSize: style.fontSizeNormal
                                        color: style.text
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
                                            color: style.background
                                            radius: style.radiusNormal
                                            border.color: style.border
                                            border.width: 1
                                        }
                                        onCurrentValueChanged: {
                                            selectedPlatform = currentValue
                                            if (datenBackend) {
                                                datenBackend.updatePlatformFilter(currentValue)
                                            }
                                        }
                                    }
                                }
                            }
                        }
                        
                        // Statistik-Karte
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 200
                            color: style.border
                            radius: style.radiusLarge
                            border.color: style.border
                            border.width: 1
                            
                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: style.spacingLarge
                                spacing: style.spacingNormal
                                
                                Text {
                                    text: "📊 Übersicht"
                                    font.family: ubuntuFont.name
                                    font.pixelSize: style.fontSizeTitle
                                    font.bold: true
                                    color: style.text
                                }
                                
                                // 2x2 Grid für die 4 Hauptwerte
                                GridLayout {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true
                                    columns: 2
                                    rowSpacing: style.spacingNormal
                                    columnSpacing: style.spacingLarge
                                    
                                    // Umsatz
                                    RowLayout {
                                        Layout.fillWidth: true
                                        spacing: style.spacingSmall
                                        
                                        Text {
                                            text: "💰"
                                            font.pixelSize: 20
                                        }
                                        
                                        ColumnLayout {
                                            Layout.fillWidth: true
                                            spacing: style.spacingSmall
                                            
                                            Text {
                                                text: "Umsatz"
                                                font.family: ubuntuFont.name
                                                font.pixelSize: style.fontSizeSmall
                                                color: style.textSecondary
                                            }
                                            
                                            Text {
                                                text: "€ " + (statisticsData.total_earnings || 0).toFixed(2)
                                                font.family: ubuntuFont.name
                                                font.pixelSize: style.fontSizeNormal
                                                font.bold: true
                                                color: style.text
                                            }
                                        }
                                    }
                                    
                                    // Fahrten
                                    RowLayout {
                                        Layout.fillWidth: true
                                        spacing: style.spacingSmall
                                        
                                        Text {
                                            text: "🚗"
                                            font.pixelSize: 20
                                        }
                                        
                                        ColumnLayout {
                                            Layout.fillWidth: true
                                            spacing: style.spacingSmall
                                            
                                            Text {
                                                text: "Fahrten"
                                                font.family: ubuntuFont.name
                                                font.pixelSize: style.fontSizeSmall
                                                color: style.textSecondary
                                            }
                                            
                                            Text {
                                                text: (statisticsData.total_trips || 0).toString()
                                                font.family: ubuntuFont.name
                                                font.pixelSize: style.fontSizeNormal
                                                font.bold: true
                                                color: style.text
                                            }
                                        }
                                    }
                                    
                                    // Stunden
                                    RowLayout {
                                        Layout.fillWidth: true
                                        spacing: style.spacingSmall
                                        
                                        Text {
                                            text: "⏰"
                                            font.pixelSize: 20
                                        }
                                        
                                        ColumnLayout {
                                            Layout.fillWidth: true
                                            spacing: style.spacingSmall
                                            
                                            Text {
                                                text: "Stunden"
                                                font.family: ubuntuFont.name
                                                font.pixelSize: style.fontSizeSmall
                                                color: style.textSecondary
                                            }
                                            
                                            Text {
                                                text: (statisticsData.total_hours || 0).toFixed(1) + "h"
                                                font.family: ubuntuFont.name
                                                font.pixelSize: style.fontSizeNormal
                                                font.bold: true
                                                color: style.text
                                            }
                                        }
                                    }
                                    
                                    // Durchschnitt
                                    RowLayout {
                                        Layout.fillWidth: true
                                        spacing: style.spacingSmall
                                        
                                        Text {
                                            text: "📈"
                                            font.pixelSize: 20
                                        }
                                        
                                        ColumnLayout {
                                            Layout.fillWidth: true
                                            spacing: style.spacingSmall
                                            
                                            Text {
                                                text: "Ø/Stunde"
                                                font.family: ubuntuFont.name
                                                font.pixelSize: style.fontSizeSmall
                                                color: style.textSecondary
                                            }
                                            
                                            Text {
                                                text: "€ " + (statisticsData.avg_per_hour || 0).toFixed(2)
                                                font.family: ubuntuFont.name
                                                font.pixelSize: style.fontSizeNormal
                                                font.bold: true
                                                color: style.text
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                    
                    // Mittlere Spalte - Charts
                    ColumnLayout {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        Layout.columnSpan: 1
                        spacing: style.spacingLarge
                        
                        // Umsatz-Chart
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            color: style.border
                            radius: style.radiusLarge
                            border.color: style.border
                            border.width: 1
                            
                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: style.spacingLarge
                                spacing: style.spacingNormal
                                
                                Text {
                                    text: "📊 Umsatz-Entwicklung"
                                    font.family: ubuntuFont.name
                                    font.pixelSize: style.fontSizeTitle
                                    font.bold: true
                                    color: style.text
                                }
                                
                                // Chart-Bereich
                                Rectangle {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true
                                    color: style.background
                                    radius: style.radiusNormal
                                    
                                    // Loading-Indikator
                                    Rectangle {
                                        anchors.centerIn: parent
                                        width: 100
                                        height: 100
                                        radius: 50
                                        color: "transparent"
                                        border.color: style.primary
                                        border.width: 4
                                        visible: isLoading
                                        
                                        RotationAnimation on rotation {
                                            from: 0
                                            to: 360
                                            duration: 1000
                                            loops: Animation.Infinite
                                            running: isLoading
                                        }
                                    }
                                    
                                    // Platzhalter-Text
                                    Text {
                                        anchors.centerIn: parent
                                        text: hasData ? "📈 Chart wird angezeigt..." : "📊 Keine Daten verfügbar"
                                        font.family: ubuntuFont.name
                                        font.pixelSize: style.fontSizeNormal
                                        color: style.textSecondary
                                        visible: !isLoading
                                    }
                                }
                            }
                        }
                        
                        // Platform-Verteilung
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            color: style.border
                            radius: style.radiusLarge
                            border.color: style.border
                            border.width: 1
                            
                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: style.spacingLarge
                                spacing: style.spacingNormal
                                
                                Text {
                                    text: "🍕 Platform-Verteilung"
                                    font.family: ubuntuFont.name
                                    font.pixelSize: style.fontSizeTitle
                                    font.bold: true
                                    color: style.text
                                }
                                
                                // Pie Chart Bereich
                                Rectangle {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true
                                    color: style.background
                                    radius: style.radiusNormal
                                    
                                    Text {
                                        anchors.centerIn: parent
                                        text: hasData ? "🥧 Pie Chart wird angezeigt..." : "📊 Keine Daten verfügbar"
                                        font.family: ubuntuFont.name
                                        font.pixelSize: style.fontSizeNormal
                                        color: style.textSecondary
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
                        color: style.border
                        radius: style.radiusLarge
                        border.color: style.border
                        border.width: 1
                        
                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: style.spacingLarge
                            spacing: style.spacingNormal
                            
                            Text {
                                text: "📋 Detaillierte Fahrten"
                                font.family: ubuntuFont.name
                                font.pixelSize: style.fontSizeTitle
                                font.bold: true
                                color: style.text
                            }
                            
                            // Tabellen-Header
                            Rectangle {
                                Layout.fillWidth: true
                                Layout.preferredHeight: 40
                                color: style.background
                                radius: style.radiusNormal
                                
                                RowLayout {
                                    anchors.fill: parent
                                    anchors.margins: style.spacingNormal
                                    spacing: style.spacingNormal
                                    
                                    Text {
                                        text: "Datum"
                                        font.family: ubuntuFont.name
                                        font.pixelSize: style.fontSizeSmall
                                        font.bold: true
                                        color: style.text
                                        Layout.preferredWidth: 80
                                    }
                                    
                                    Text {
                                        text: "Platform"
                                        font.family: ubuntuFont.name
                                        font.pixelSize: style.fontSizeSmall
                                        font.bold: true
                                        color: style.text
                                        Layout.preferredWidth: 60
                                    }
                                    
                                    Text {
                                        text: "Fahrer"
                                        font.family: ubuntuFont.name
                                        font.pixelSize: style.fontSizeSmall
                                        font.bold: true
                                        color: style.text
                                        Layout.preferredWidth: 80
                                    }
                                    
                                    Text {
                                        text: "Umsatz"
                                        font.family: ubuntuFont.name
                                        font.pixelSize: style.fontSizeSmall
                                        font.bold: true
                                        color: style.text
                                        Layout.preferredWidth: 60
                                    }
                                    
                                    Text {
                                        text: "Status"
                                        font.family: ubuntuFont.name
                                        font.pixelSize: style.fontSizeSmall
                                        font.bold: true
                                        color: style.text
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
                                        color: index % 2 === 0 ? style.background : style.border
                                        
                                        RowLayout {
                                            anchors.fill: parent
                                            anchors.margins: style.spacingSmall
                                            spacing: style.spacingSmall
                                            
                                            Text {
                                                text: datum
                                                font.family: ubuntuFont.name
                                                font.pixelSize: style.fontSizeSmall
                                                color: style.text
                                                Layout.preferredWidth: 80
                                            }
                                            
                                            Text {
                                                text: platform
                                                font.family: ubuntuFont.name
                                                font.pixelSize: style.fontSizeSmall
                                                color: style.text
                                                Layout.preferredWidth: 60
                                            }
                                            
                                            Text {
                                                text: fahrer
                                                font.family: ubuntuFont.name
                                                font.pixelSize: style.fontSizeSmall
                                                color: style.text
                                                Layout.preferredWidth: 80
                                            }
                                            
                                            Text {
                                                text: umsatz
                                                font.family: ubuntuFont.name
                                                font.pixelSize: style.fontSizeSmall
                                                color: style.text
                                                Layout.preferredWidth: 60
                                            }
                                            
                                            Rectangle {
                                                Layout.preferredWidth: 70
                                                Layout.preferredHeight: 18
                                                color: style.success
                                                radius: style.radiusSmall
                                                
                                                Text {
                                                    anchors.centerIn: parent
                                                    text: status
                                                    font.family: ubuntuFont.name
                                                    font.pixelSize: style.fontSizeSmall
                                                    color: style.text
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
            
            // Analytics-Ansicht
            Rectangle {
                color: "transparent"
                
                ColumnLayout {
                    anchors.fill: parent
                    spacing: style.spacingLarge
                    
                    Text {
                        text: "📈 Erweiterte Daten-Analyse"
                        font.family: ubuntuFont.name
                        font.pixelSize: style.fontSizeTitle + 8
                        font.bold: true
                        color: style.text
                        Layout.alignment: Qt.AlignHCenter
                    }
                    
                    GridLayout {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        columns: 2
                        rowSpacing: style.spacingLarge
                        columnSpacing: style.spacingLarge
                        
                        // Performance-Analyse
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            color: style.border
                            radius: style.radiusLarge
                            border.color: style.border
                            border.width: 1
                            
                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: style.spacingLarge
                                spacing: style.spacingNormal
                                
                                Text {
                                    text: "⚡ Performance-Analyse"
                                    font.family: ubuntuFont.name
                                    font.pixelSize: style.fontSizeTitle
                                    font.bold: true
                                    color: style.text
                                }
                                
                                GridLayout {
                                    Layout.fillWidth: true
                                    columns: 2
                                    rowSpacing: style.spacingNormal
                                    columnSpacing: style.spacingLarge
                                    
                                    Text {
                                        text: "Ladezeit:"
                                        font.family: ubuntuFont.name
                                        font.pixelSize: style.fontSizeNormal
                                        color: style.textSecondary
                                    }
                                    
                                    Text {
                                        text: (performanceData.load_time || 0).toFixed(0) + " ms"
                                        font.family: ubuntuFont.name
                                        font.pixelSize: style.fontSizeNormal
                                        font.bold: true
                                        color: style.text
                                    }
                                    
                                    Text {
                                        text: "Cache-Treffer:"
                                        font.family: ubuntuFont.name
                                        font.pixelSize: style.fontSizeNormal
                                        color: style.textSecondary
                                    }
                                    
                                    Text {
                                        text: (performanceData.cache_hits || 0).toString()
                                        font.family: ubuntuFont.name
                                        font.pixelSize: style.fontSizeNormal
                                        font.bold: true
                                        color: style.success
                                    }
                                    
                                    Text {
                                        text: "Cache-Fehler:"
                                        font.family: ubuntuFont.name
                                        font.pixelSize: style.fontSizeNormal
                                        color: style.textSecondary
                                    }
                                    
                                    Text {
                                        text: (performanceData.cache_misses || 0).toString()
                                        font.family: ubuntuFont.name
                                        font.pixelSize: style.fontSizeNormal
                                        font.bold: true
                                        color: style.warning
                                    }
                                }
                                
                                // Performance-Analyse-Button
                                Rectangle {
                                    Layout.fillWidth: true
                                    height: 40
                                    radius: style.radiusNormal
                                    color: analyzeMouseArea.containsMouse ? style.primary : "transparent"
                                    border.color: style.primary
                                    border.width: 2
                                    
                                    MouseArea {
                                        id: analyzeMouseArea
                                        anchors.fill: parent
                                        hoverEnabled: true
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: {
                                            if (datenBackend) {
                                                datenBackend.analyzePerformance()
                                            }
                                        }
                                    }
                                    
                                    Text {
                                        anchors.centerIn: parent
                                        text: "Performance analysieren"
                                        font.family: ubuntuFont.name
                                        font.pixelSize: style.fontSizeNormal
                                        font.bold: true
                                        color: analyzeMouseArea.containsMouse ? style.text : style.primary
                                    }
                                }
                            }
                        }
                        
                        // Cache-Management
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            color: style.border
                            radius: style.radiusLarge
                            border.color: style.border
                            border.width: 1
                            
                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: style.spacingLarge
                                spacing: style.spacingNormal
                                
                                Text {
                                    text: "🗄️ Cache-Management"
                                    font.family: ubuntuFont.name
                                    font.pixelSize: style.fontSizeTitle
                                    font.bold: true
                                    color: style.text
                                }
                                
                                Text {
                                    text: cacheEnabled ? "Cache ist aktiv" : "Cache ist leer"
                                    font.family: ubuntuFont.name
                                    font.pixelSize: style.fontSizeNormal
                                    color: cacheEnabled ? style.success : style.textSecondary
                                }
                                
                                // Cache-Buttons
                                RowLayout {
                                    Layout.fillWidth: true
                                    spacing: style.spacingNormal
                                    
                                    Rectangle {
                                        Layout.fillWidth: true
                                        height: 40
                                        radius: style.radiusNormal
                                        color: clearCacheMouseArea.containsMouse ? style.error : "transparent"
                                        border.color: style.error
                                        border.width: 2
                                        
                                        MouseArea {
                                            id: clearCacheMouseArea
                                            anchors.fill: parent
                                            hoverEnabled: true
                                            cursorShape: Qt.PointingHandCursor
                                            onClicked: {
                                                if (datenBackend) {
                                                    datenBackend.clearCache()
                                                }
                                            }
                                        }
                                        
                                        Text {
                                            anchors.centerIn: parent
                                            text: "Cache leeren"
                                            font.family: ubuntuFont.name
                                            font.pixelSize: style.fontSizeSmall
                                            font.bold: true
                                            color: clearCacheMouseArea.containsMouse ? style.text : style.error
                                        }
                                    }
                                    
                                    Rectangle {
                                        Layout.fillWidth: true
                                        height: 40
                                        radius: style.radiusNormal
                                        color: autoRefreshMouseArea.containsMouse ? style.success : "transparent"
                                        border.color: style.success
                                        border.width: 2
                                        
                                        MouseArea {
                                            id: autoRefreshMouseArea
                                            anchors.fill: parent
                                            hoverEnabled: true
                                            cursorShape: Qt.PointingHandCursor
                                            onClicked: {
                                                if (datenBackend) {
                                                    datenBackend.startAutoRefresh()
                                                }
                                            }
                                        }
                                        
                                        Text {
                                            anchors.centerIn: parent
                                            text: "Auto-Update"
                                            font.family: ubuntuFont.name
                                            font.pixelSize: style.fontSizeSmall
                                            font.bold: true
                                            color: autoRefreshMouseArea.containsMouse ? style.text : style.success
                                        }
                                    }
                                }
                            }
                        }
                        
                        // Trend-Analyse (Platzhalter)
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            color: style.border
                            radius: style.radiusLarge
                            border.color: style.border
                            border.width: 1
                            
                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: style.spacingLarge
                                spacing: style.spacingNormal
                                
                                Text {
                                    text: "📊 Trend-Analyse"
                                    font.family: ubuntuFont.name
                                    font.pixelSize: style.fontSizeTitle
                                    font.bold: true
                                    color: style.text
                                }
                                
                                Text {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true
                                    text: "Wachstumsrate: +" + (statisticsData.growth_rate || 0).toFixed(1) + "%"
                                    font.family: ubuntuFont.name
                                    font.pixelSize: style.fontSizeNormal
                                    color: style.success
                                    verticalAlignment: Text.AlignVCenter
                                    horizontalAlignment: Text.AlignHCenter
                                }
                            }
                        }
                        
                        // Datenqualität (Platzhalter)
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            color: style.border
                            radius: style.radiusLarge
                            border.color: style.border
                            border.width: 1
                            
                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: style.spacingLarge
                                spacing: style.spacingNormal
                                
                                Text {
                                    text: "✅ Datenqualität"
                                    font.family: ubuntuFont.name
                                    font.pixelSize: style.fontSizeTitle
                                    font.bold: true
                                    color: style.text
                                }
                                
                                Text {
                                    Layout.fillWidth: true
                                    Layout.fillHeight: true
                                    text: hasData ? "Daten vollständig" : "Keine Daten"
                                    font.family: ubuntuFont.name
                                    font.pixelSize: style.fontSizeNormal
                                    color: hasData ? style.success : style.warning
                                    verticalAlignment: Text.AlignVCenter
                                    horizontalAlignment: Text.AlignHCenter
                                }
                            }
                        }
                    }
                }
            }
            
            // Import-Ansicht
            Rectangle {
                color: "transparent"
                
                ColumnLayout {
                    anchors.fill: parent
                    spacing: style.spacingLarge
                    
                    Text {
                        text: "📥 Daten-Import"
                        font.family: ubuntuFont.name
                        font.pixelSize: style.fontSizeTitle + 8
                        font.bold: true
                        color: style.text
                        Layout.alignment: Qt.AlignHCenter
                    }
                    
                    GridLayout {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        columns: 3
                        rowSpacing: style.spacingLarge
                        columnSpacing: style.spacingLarge
                        
                        // Umsatz-Import
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            color: style.border
                            radius: style.radiusLarge
                            border.color: importUmsatzMouseArea.containsMouse ? style.primary : style.border
                            border.width: 2
                            
                            MouseArea {
                                id: importUmsatzMouseArea
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: {
                                    if (datenBackend) {
                                        datenBackend.show_import_wizard()
                                    }
                                }
                            }
                            
                            ColumnLayout {
                                anchors.centerIn: parent
                                spacing: style.spacingNormal
                                
                                Text {
                                    text: "🚗"
                                    font.pixelSize: 60
                                    Layout.alignment: Qt.AlignHCenter
                                }
                                
                                Text {
                                    text: "Umsatz-Daten"
                                    font.family: ubuntuFont.name
                                    font.pixelSize: style.fontSizeTitle
                                    font.bold: true
                                    color: style.text
                                    Layout.alignment: Qt.AlignHCenter
                                }
                                
                                Text {
                                    text: "Uber, Bolt, 40100"
                                    font.family: ubuntuFont.name
                                    font.pixelSize: style.fontSizeNormal
                                    color: style.textSecondary
                                    Layout.alignment: Qt.AlignHCenter
                                }
                            }
                        }
                        
                        // Gehalt-Import
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            color: style.border
                            radius: style.radiusLarge
                            border.color: importGehaltMouseArea.containsMouse ? style.primary : style.border
                            border.width: 2
                            
                            MouseArea {
                                id: importGehaltMouseArea
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: {
                                    if (datenBackend) {
                                        datenBackend.show_import_wizard()
                                    }
                                }
                            }
                            
                            ColumnLayout {
                                anchors.centerIn: parent
                                spacing: style.spacingNormal
                                
                                Text {
                                    text: "💰"
                                    font.pixelSize: 60
                                    Layout.alignment: Qt.AlignHCenter
                                }
                                
                                Text {
                                    text: "Gehaltsdaten"
                                    font.family: ubuntuFont.name
                                    font.pixelSize: style.fontSizeTitle
                                    font.bold: true
                                    color: style.text
                                    Layout.alignment: Qt.AlignHCenter
                                }
                                
                                Text {
                                    text: "PDF-Abrechnungen"
                                    font.family: ubuntuFont.name
                                    font.pixelSize: style.fontSizeNormal
                                    color: style.textSecondary
                                    Layout.alignment: Qt.AlignHCenter
                                }
                            }
                        }
                        
                        // Funk-Import
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            color: style.border
                            radius: style.radiusLarge
                            border.color: importFunkMouseArea.containsMouse ? style.primary : style.border
                            border.width: 2
                            
                            MouseArea {
                                id: importFunkMouseArea
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: {
                                    if (datenBackend) {
                                        datenBackend.show_import_wizard()
                                    }
                                }
                            }
                            
                            ColumnLayout {
                                anchors.centerIn: parent
                                spacing: style.spacingNormal
                                
                                Text {
                                    text: "📻"
                                    font.pixelSize: 60
                                    Layout.alignment: Qt.AlignHCenter
                                }
                                
                                Text {
                                    text: "Funkdaten"
                                    font.family: ubuntuFont.name
                                    font.pixelSize: style.fontSizeTitle
                                    font.bold: true
                                    color: style.text
                                    Layout.alignment: Qt.AlignHCenter
                                }
                                
                                Text {
                                    text: "31300, 40100"
                                    font.family: ubuntuFont.name
                                    font.pixelSize: style.fontSizeNormal
                                    color: style.textSecondary
                                    Layout.alignment: Qt.AlignHCenter
                                }
                            }
                        }
                    }
                }
            }
            
            // Export-Ansicht
            Rectangle {
                color: "transparent"
                
                ColumnLayout {
                    anchors.fill: parent
                    spacing: style.spacingLarge
                    
                    Text {
                        text: "📤 Daten-Export"
                        font.family: ubuntuFont.name
                        font.pixelSize: style.fontSizeTitle + 8
                        font.bold: true
                        color: style.text
                        Layout.alignment: Qt.AlignHCenter
                    }
                    
                    GridLayout {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        columns: 3
                        rowSpacing: style.spacingLarge
                        columnSpacing: style.spacingLarge
                        
                        // JSON-Export
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            color: style.border
                            radius: style.radiusLarge
                            border.color: exportJsonMouseArea.containsMouse ? style.primary : style.border
                            border.width: 2
                            
                            MouseArea {
                                id: exportJsonMouseArea
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: {
                                    if (datenBackend) {
                                        datenBackend.exportDataAsync("json")
                                    }
                                }
                            }
                            
                            ColumnLayout {
                                anchors.centerIn: parent
                                spacing: style.spacingNormal
                                
                                Text {
                                    text: "📄"
                                    font.pixelSize: 60
                                    Layout.alignment: Qt.AlignHCenter
                                }
                                
                                Text {
                                    text: "JSON-Export"
                                    font.family: ubuntuFont.name
                                    font.pixelSize: style.fontSizeTitle
                                    font.bold: true
                                    color: style.text
                                    Layout.alignment: Qt.AlignHCenter
                                }
                                
                                Text {
                                    text: "Strukturierte Daten"
                                    font.family: ubuntuFont.name
                                    font.pixelSize: style.fontSizeNormal
                                    color: style.textSecondary
                                    Layout.alignment: Qt.AlignHCenter
                                }
                            }
                        }
                        
                        // CSV-Export
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            color: style.border
                            radius: style.radiusLarge
                            border.color: exportCsvMouseArea.containsMouse ? style.primary : style.border
                            border.width: 2
                            
                            MouseArea {
                                id: exportCsvMouseArea
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: {
                                    if (datenBackend) {
                                        datenBackend.exportDataAsync("csv")
                                    }
                                }
                            }
                            
                            ColumnLayout {
                                anchors.centerIn: parent
                                spacing: style.spacingNormal
                                
                                Text {
                                    text: "📊"
                                    font.pixelSize: 60
                                    Layout.alignment: Qt.AlignHCenter
                                }
                                
                                Text {
                                    text: "CSV-Export"
                                    font.family: ubuntuFont.name
                                    font.pixelSize: style.fontSizeTitle
                                    font.bold: true
                                    color: style.text
                                    Layout.alignment: Qt.AlignHCenter
                                }
                                
                                Text {
                                    text: "Tabellendaten"
                                    font.family: ubuntuFont.name
                                    font.pixelSize: style.fontSizeNormal
                                    color: style.textSecondary
                                    Layout.alignment: Qt.AlignHCenter
                                }
                            }
                        }
                        
                        // Excel-Export
                        Rectangle {
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            color: style.border
                            radius: style.radiusLarge
                            border.color: exportExcelMouseArea.containsMouse ? style.primary : style.border
                            border.width: 2
                            
                            MouseArea {
                                id: exportExcelMouseArea
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: {
                                    if (datenBackend) {
                                        datenBackend.exportDataAsync("excel")
                                    }
                                }
                            }
                            
                            ColumnLayout {
                                anchors.centerIn: parent
                                spacing: style.spacingNormal
                                
                                Text {
                                    text: "📈"
                                    font.pixelSize: 60
                                    Layout.alignment: Qt.AlignHCenter
                                }
                                
                                Text {
                                    text: "Excel-Export"
                                    font.family: ubuntuFont.name
                                    font.pixelSize: style.fontSizeTitle
                                    font.bold: true
                                    color: style.text
                                    Layout.alignment: Qt.AlignHCenter
                                }
                                
                                Text {
                                    text: "Multi-Sheet"
                                    font.family: ubuntuFont.name
                                    font.pixelSize: style.fontSizeNormal
                                    color: style.textSecondary
                                    Layout.alignment: Qt.AlignHCenter
                                }
                            }
                        }
                    }
                    
                    // Report-Generator
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 120
                        color: style.border
                        radius: style.radiusLarge
                        border.color: reportMouseArea.containsMouse ? style.primary : style.border
                        border.width: 2
                        
                        MouseArea {
                            id: reportMouseArea
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: {
                                if (datenBackend) {
                                    datenBackend.show_generic_wizard()
                                }
                            }
                        }
                        
                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: style.spacingLarge
                            spacing: style.spacingLarge
                            
                            Text {
                                text: "📋"
                                font.pixelSize: 60
                            }
                            
                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: style.spacingSmall
                                
                                Text {
                                    text: "Berichte generieren"
                                    font.family: ubuntuFont.name
                                    font.pixelSize: style.fontSizeTitle
                                    font.bold: true
                                    color: style.text
                                }
                                
                                Text {
                                    text: "Erstelle detaillierte PDF-Berichte mit Monats- und Quartalsübersichten"
                                    font.family: ubuntuFont.name
                                    font.pixelSize: style.fontSizeNormal
                                    color: style.textSecondary
                                    wrapMode: Text.WordWrap
                                    Layout.fillWidth: true
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    // Bottom Navigation Bar
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
                currentView = "dashboard"
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
        
        // Import-Button
        MouseArea {
            id: importArea
            width: 56; height: 56
            cursorShape: Qt.PointingHandCursor
            hoverEnabled: true
            onClicked: {
                currentView = "import"
            }
            Image {
                anchors.centerIn: parent
                source: importArea.pressed ? "assets/icons/import_gray.svg"
                    : importArea.containsMouse ? "assets/icons/import_orange.svg" : "assets/icons/import_white.svg"
                width: importArea.pressed ? 32 : importArea.containsMouse ? 40 : 32
                height: width
                fillMode: Image.PreserveAspectFit
            }
        }
        
        // Export-Button
        MouseArea {
            id: exportArea
            width: 56; height: 56
            cursorShape: Qt.PointingHandCursor
            hoverEnabled: true
            onClicked: {
                currentView = "export"
            }
            Image {
                anchors.centerIn: parent
                source: exportArea.pressed ? "assets/icons/receipt_gray.svg"
                    : exportArea.containsMouse ? "assets/icons/receipt_orange.svg" : "assets/icons/receipt_white.svg"
                width: exportArea.pressed ? 32 : exportArea.containsMouse ? 40 : 32
                height: width
                fillMode: Image.PreserveAspectFit
            }
        }
        
        // Analytics-Button
        MouseArea {
            id: analyticsArea
            width: 56; height: 56
            cursorShape: Qt.PointingHandCursor
            hoverEnabled: true
            onClicked: {
                currentView = "analytics"
            }
            Image {
                anchors.centerIn: parent
                source: analyticsArea.pressed ? "assets/icons/charts_gray.svg"
                    : analyticsArea.containsMouse ? "assets/icons/charts_orange.svg" : "assets/icons/charts_white.svg"
                width: analyticsArea.pressed ? 32 : analyticsArea.containsMouse ? 40 : 32
                height: width
                fillMode: Image.PreserveAspectFit
            }
        }
        
        // Refresh-Button
        MouseArea {
            id: refreshArea
            width: 56; height: 56
            cursorShape: Qt.PointingHandCursor
            hoverEnabled: true
            onClicked: {
                if (datenBackend) {
                    datenBackend.refreshData()
                }
            }
            Image {
                anchors.centerIn: parent
                source: refreshArea.pressed ? "assets/icons/redo_gray.svg"
                    : refreshArea.containsMouse ? "assets/icons/redo_orange.svg" : "assets/icons/redo_white.svg"
                width: refreshArea.pressed ? 32 : refreshArea.containsMouse ? 40 : 32
                height: width
                fillMode: Image.PreserveAspectFit
            }
        }
    }

    // Error-Handling mit Toast-Nachrichten
    Rectangle {
        id: toastNotification
        anchors.top: parent.top
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.topMargin: 20
        width: Math.min(400, parent.width - 40)
        height: 60
        radius: style.radiusNormal
        color: style.error
        border.color: "white"
        border.width: 1
        visible: false
        z: 2000
        
        property string toastMessage: ""
        property int toastDuration: 3000
        
        RowLayout {
            anchors.fill: parent
            anchors.margins: 12
            spacing: 12
            
            Text {
                text: "⚠"
                font.pixelSize: 20
                font.bold: true
                color: "white"
            }
            
            Text {
                Layout.fillWidth: true
                text: toastNotification.toastMessage
                font.family: ubuntuFont.name
                font.pixelSize: 14
                color: "white"
                wrapMode: Text.WordWrap
                verticalAlignment: Text.AlignVCenter
            }
            
            MouseArea {
                width: 20
                height: 20
                onClicked: toastNotification.visible = false
                cursorShape: Qt.PointingHandCursor
                
                Text {
                    anchors.centerIn: parent
                    text: "×"
                    font.pixelSize: 18
                    font.bold: true
                    color: "white"
                }
            }
        }
        
        Timer {
            id: toastTimer
            interval: toastNotification.toastDuration
            onTriggered: toastNotification.visible = false
        }
        
        function showToast(message) {
            toastMessage = message
            visible = true
            toastTimer.restart()
        }
    }

    // Verbindungen zum Backend
    Connections {
        target: datenBackend
        
        function onErrorOccurred(title, message) {
            toastNotification.showToast(title + ": " + message)
        }
        
        function onDataChanged() {
            // Daten wurden aktualisiert
            console.log("Daten aktualisiert")
        }
        
        function onLoadingChanged() {
            // Loading-Status geändert
            console.log("Loading-Status:", isLoading)
        }
    }

    // Initialisierung
    Component.onCompleted: {
        console.log("Modernisierte Datenseite geladen")
        
        // Lade initiale Daten
        if (datenBackend) {
            datenBackend.loadData("week", "all", "all")
        }
    }
}


