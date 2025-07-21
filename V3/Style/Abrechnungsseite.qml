import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import Style 1.0

Rectangle {
    id: root
    property var goHome: function() {
        // Fallback: Blende die Abrechnungsseite aus und zeige das MainMenu
        root.visible = false;
        if (typeof mainWindow !== 'undefined') {
            mainWindow.stackVisible = false;
        }
    }
    color: Style.background
    radius: Style.radiusNormal

    FontLoader {
        id: ubuntuFont
        source: "assets/fonts/Ubuntu-Regular.ttf"
    }
    
    FontLoader {
        id: spaceMonoFont
        source: "assets/fonts/SpaceMono-Regular.ttf"
    }

    property bool werteGeladen: false
    property var summary: {"umsatz": "-", "trinkgeld": "-", "bargeld": "-"}
    property var card40100: {"label": "Taxi", "value": "-"}
    property var cardUber: {"label": "Uber", "value": "-", "zeile1": "-", "zeile2": "-", "zeile3": "-"}
    property var cardBolt: {"label": "Bolt", "value": "-"}
    property string tank: ""
    property string einsteiger: ""
    property bool wizardGestartet: false
    property var wizardSelection: ({})

    // Seite bleibt leer, solange das Wizard offen ist
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Style.spacingHuge
        anchors.topMargin: 52
        anchors.bottomMargin: 115
        anchors.rightMargin: 100
        anchors.leftMargin: 100
        spacing: 8
        visible: werteGeladen

        // Titel dynamisch setzen
        Component.onCompleted: {
            if (typeof mainWindow !== 'undefined') {
                mainWindow.title = (wizardSelection.fahrzeug ? wizardSelection.fahrzeug.split(" ")[0] : "-") + " - " + (wizardSelection.fahrer || "-");
            }
        }
        Connections {
            target: abrechnungsBackend
            function onErgebnisseChanged() {
                if (typeof mainWindow !== 'undefined') {
                    mainWindow.title = (wizardSelection.fahrzeug ? wizardSelection.fahrzeug.split(" ")[0] : "-") + " - " + (wizardSelection.fahrer || "-");
                }
            }
        }

        // Cards für Plattformen und Input-Card nebeneinander
        RowLayout {
            spacing: Style.spacingLarge * 1.6
            anchors.centerIn: parent
            anchors.horizontalCenterOffset: -84
            Layout.topMargin: 150
            // Cards für Plattformen
            ColumnLayout {
                spacing: 32 // vorher 20
                Layout.alignment: Qt.AlignTop
                Layout.preferredWidth: 288 // vorher 180
                visible: card40100.zeile1 !== "-" && !isNaN(parseFloat(card40100.zeile1))
                Text { text: card40100.label; font.pixelSize: Style.fontSizeTitle * 1.6; font.bold: true; color: "#b0b0b0"; horizontalAlignment: Text.AlignRight; Layout.alignment: Qt.AlignRight; font.family: ubuntuFont.name }
                Rectangle {
                    Layout.preferredWidth: 288
                    Layout.preferredHeight: 288
                    color: "black"
                    radius: Style.radiusLarge
                    border.width: 0
                    ColumnLayout {
                        anchors.fill: parent
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        Layout.margins: Style.spacingLarge * 1.6
                        spacing: Style.spacingLarge * 1.6
                        Text { text: card40100.zeile1 + ' €'; font.pixelSize: Style.fontSizeHeader * 1.6; color: Style.text; horizontalAlignment: Text.AlignRight; Layout.alignment: Qt.AlignRight; font.family: ubuntuFont.name }
                        Text { text: card40100.zeile2 + ' €'; font.pixelSize: Style.fontSizeHeader * 1.6; color: Style.text; horizontalAlignment: Text.AlignRight; Layout.alignment: Qt.AlignRight; font.family: ubuntuFont.name }
                        Text { text: card40100.zeile3 + ' €'; font.pixelSize: Style.fontSizeHeader * 1.6; font.bold: true; color: Style.text; horizontalAlignment: Text.AlignRight; Layout.alignment: Qt.AlignRight; font.family: ubuntuFont.name }
                    }
                }
            }
            ColumnLayout {
                spacing: 32
                Layout.alignment: Qt.AlignTop
                Layout.preferredWidth: 288
                visible: cardUber.zeile1 !== "-" && parseFloat(cardUber.zeile1) > 0
                Text { text: cardUber.label === "Uber" ? "UBER" : cardUber.label; font.pixelSize: Style.fontSizeTitle * 1.6; font.bold: true; color: "#b0b0b0"; horizontalAlignment: Text.AlignRight; Layout.alignment: Qt.AlignRight; font.family: ubuntuFont.name }
                Rectangle {
                    Layout.preferredWidth: 288
                    Layout.preferredHeight: 288
                    color: "black"
                    radius: Style.radiusLarge
                    border.width: 0
                    ColumnLayout {
                        anchors.fill: parent
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        Layout.margins: Style.spacingLarge * 1.6
                        spacing: Style.spacingLarge * 1.6
                        Text { text: cardUber.zeile1 + ' €'; font.pixelSize: Style.fontSizeHeader * 1.6; color: Style.text; horizontalAlignment: Text.AlignRight; Layout.alignment: Qt.AlignRight; font.family: ubuntuFont.name }
                        Text { text: cardUber.zeile2 + ' €'; font.pixelSize: Style.fontSizeHeader * 1.6; color: Style.text; horizontalAlignment: Text.AlignRight; Layout.alignment: Qt.AlignRight; font.family: ubuntuFont.name }
                        Text { text: cardUber.zeile3 + ' €'; font.pixelSize: Style.fontSizeHeader * 1.6; font.bold: true; color: Style.text; horizontalAlignment: Text.AlignRight; Layout.alignment: Qt.AlignRight; font.family: ubuntuFont.name }
                    }
                }
            }
            ColumnLayout {
                spacing: 32
                Layout.alignment: Qt.AlignTop
                Layout.preferredWidth: 288
                visible: cardBolt.zeile1 !== "-" && parseFloat(cardBolt.zeile1) > 0
                Text { text: cardBolt.label === "Bolt" ? "BOLT" : cardBolt.label; font.pixelSize: Style.fontSizeTitle * 1.6; font.bold: true; color: "#b0b0b0"; horizontalAlignment: Text.AlignRight; Layout.alignment: Qt.AlignRight; font.family: ubuntuFont.name }
                Rectangle {
                    Layout.preferredWidth: 288
                    Layout.preferredHeight: 288
                    color: "black"
                    radius: Style.radiusLarge
                    border.width: 0
                    ColumnLayout {
                        anchors.fill: parent
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        Layout.margins: Style.spacingLarge * 1.6
                        spacing: Style.spacingLarge * 1.6
                        Text { text: cardBolt.zeile1 + ' €'; font.pixelSize: Style.fontSizeHeader * 1.6; color: Style.text; horizontalAlignment: Text.AlignRight; Layout.alignment: Qt.AlignRight; font.family: ubuntuFont.name }
                        Text { text: cardBolt.zeile2 + ' €'; font.pixelSize: Style.fontSizeHeader * 1.6; color: Style.text; horizontalAlignment: Text.AlignRight; Layout.alignment: Qt.AlignRight; font.family: ubuntuFont.name }
                        Text { text: cardBolt.zeile3 + ' €'; font.pixelSize: Style.fontSizeHeader * 1.6; font.bold: true; color: Style.text; horizontalAlignment: Text.AlignRight; Layout.alignment: Qt.AlignRight; font.family: ubuntuFont.name }
                    }
                }
            }
            Item { width: 64 } // Platzhalter größer
            // Input-Card und Ergebnis-Element untereinander
            ColumnLayout {
                spacing: 16
                Layout.alignment: Qt.AlignTop
                Layout.preferredWidth: 288
                Layout.topMargin: 70
                // Input-Card
                Rectangle {
                    Layout.preferredWidth: 288
                    Layout.preferredHeight: 288
                    color: "black"
                    radius: Style.radiusLarge
                    border.width: 0
                    ColumnLayout {
                        anchors.fill: parent
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        Layout.margins: Style.spacingLarge * 1.6
                        spacing: 14
                        RowLayout {
                            spacing: 12
                            Layout.alignment: Qt.AlignHCenter
                            TextField {
                                id: inputField1
                                width: 150
                                Layout.preferredWidth: 150
                                Layout.alignment: Qt.AlignVCenter
                                placeholderText: ""
                                font.pixelSize: 28
                                font.family: ubuntuFont.name
                                color: Style.text
                                background: Rectangle { color: "#222"; radius: 8 }
                                padding: 10
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                                text: abrechnungsBackend.inputGas
                                onTextChanged: abrechnungsBackend.inputGas = text
                            }
                                Text {
                                text: "€"
                                font.pixelSize: 24
                                color: "#b0b0b0"
                                font.family: ubuntuFont.name
                                verticalAlignment: Text.AlignVCenter
                            }
                            Image {
                                source: "assets/icons/gas_gray.svg"
                                width: 20; height: 20
                                fillMode: Image.PreserveAspectFit
                                Layout.alignment: Qt.AlignVCenter
                            }
                        }
                        RowLayout {
                            spacing: 12
                            Layout.alignment: Qt.AlignHCenter
                            TextField {
                                id: inputField2
                                width: 150
                                Layout.preferredWidth: 150
                                Layout.alignment: Qt.AlignVCenter
                                placeholderText: ""
                                font.pixelSize: 28
                                font.family: ubuntuFont.name
                                    color: Style.text
                                background: Rectangle { color: "#222"; radius: 8 }
                                padding: 10
                                    horizontalAlignment: Text.AlignHCenter
                                    verticalAlignment: Text.AlignVCenter
                                text: abrechnungsBackend.inputEinsteiger
                                onTextChanged: {
                                    abrechnungsBackend.inputEinsteiger = text;
                                    overlayIncome = calculateOverlayIncome();
                                }
                            }
                            Text {
                                text: "€"
                                font.pixelSize: 24
                                color: "#b0b0b0"
                                font.family: ubuntuFont.name
                                    verticalAlignment: Text.AlignVCenter
                                }
                            Image {
                                source: "assets/icons/hail_gray.svg"
                                width: 20; height: 20
                                fillMode: Image.PreserveAspectFit
                                Layout.alignment: Qt.AlignVCenter
                            }
                        }
                        RowLayout {
                            spacing: 10
                            Layout.alignment: Qt.AlignHCenter
                            TextField {
                                id: inputField3
                                width: 150
                                Layout.preferredWidth: 150
                                Layout.alignment: Qt.AlignVCenter
                                placeholderText: ""
                                font.pixelSize: 28
                                font.family: ubuntuFont.name
                            color: Style.text
                                background: Rectangle { color: "#222"; radius: 8 }
                                padding: 10
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                                text: abrechnungsBackend.inputExpense
                                onTextChanged: {
                                    if (abrechnungsBackend.inputExpense !== text)
                                        abrechnungsBackend.inputExpense = text
                                }
                            }
                            Text {
                                text: "€"
                                font.pixelSize: 24
                                color: "#b0b0b0"
                                font.family: ubuntuFont.name
                                verticalAlignment: Text.AlignVCenter
                            }
                        Item {
                                width: 49
                                height: 49
                                MouseArea {
                                    id: addHoverArea
                                anchors.fill: parent
                                    hoverEnabled: true
                                    onClicked: abrechnungsBackend.show_wizard_add_cost()
                                }
                                Image {
                                    anchors.centerIn: parent
                                    source: addHoverArea.containsMouse ? "assets/icons/add_orange.svg" : "assets/icons/add_white.svg"
                                    width: 49
                                    height: 49
                                    fillMode: Image.PreserveAspectFit
                                    z: 1
                                }
                            }
                        }
                    }
                }
                // Ergebnis-Element direkt unter der Input Card
                Item {
                    id: ergebnisElement
                    width: 288
                    height: 90
                    Layout.alignment: Qt.AlignTop
                    visible: werteGeladen
                    z: 10
                    Text {
                        anchors.fill: parent
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        text: abrechnungsBackend.ergebnis.toFixed(2) + ' €'
                        font.pixelSize: 64
                        font.bold: true
                        color: Style.primary
                        visible: werteGeladen
                        font.family: ubuntuFont.name
                    }
                }
            }
        }
    }

    // Nach den Cards für Plattformen:
    RowLayout {
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.horizontalCenterOffset: -100
        anchors.top: parent.top
        anchors.topMargin: 250
        spacing: 64
        // Summenzeile (links)
        RowLayout {
            id: summenZeile
            spacing: 170
            // Umsatz
            RowLayout {
                spacing: 4
                Image {
                    source: "assets/icons/sales_gray.svg"
                    width: 16; height: 16
                    fillMode: Image.PreserveAspectFit
                    Layout.alignment: Qt.AlignVCenter
                }
                Text { 
                    text: abrechnungsBackend.headcard_umsatz.toFixed(2); 
                    font.pixelSize: Style.fontSizeHeader; 
                    font.bold: true; 
                    color: Style.text; 
                    font.family: ubuntuFont.name 
                }
                Text { text: " €"; font.pixelSize: Style.fontSizeHeader; color: Style.text; font.family: ubuntuFont.name }
            }
            // Trinkgeld nur anzeigen, wenn > 0
            RowLayout {
                spacing: 4
                visible: abrechnungsBackend.headcard_trinkgeld > 0
                Image {
                    source: "assets/icons/tips_gray.svg"
                    width: 16; height: 16
                    fillMode: Image.PreserveAspectFit
                    Layout.alignment: Qt.AlignVCenter
                }
                Text { text: abrechnungsBackend.headcard_trinkgeld.toFixed(2); font.pixelSize: Style.fontSizeHeader; font.bold: true; color: Style.text; font.family: ubuntuFont.name }
                Text { text: " €"; font.pixelSize: Style.fontSizeHeader; color: Style.text; font.family: ubuntuFont.name }
            }
            // Bargeld
            RowLayout {
                spacing: 4
                Image {
                    source: "assets/icons/cash_gray.svg"
                    width: 16; height: 16
                    fillMode: Image.PreserveAspectFit
                    Layout.alignment: Qt.AlignVCenter
                }
                Text { 
                    text: abrechnungsBackend.headcard_cash.toFixed(2); 
                    font.pixelSize: Style.fontSizeHeader; 
                    font.bold: true; 
                    color: Style.text; 
                    font.family: ubuntuFont.name 
                }
                Text { text: " €"; font.pixelSize: Style.fontSizeHeader; color: Style.text; font.family: ubuntuFont.name }
            }
            // Kreditkarte/Bankomat
            RowLayout {
                spacing: 4
                Image {
                    source: "assets/icons/credit_card_gray.svg"
                    width: 16; height: 16
                    fillMode: Image.PreserveAspectFit
                    Layout.alignment: Qt.AlignVCenter
                }
                Text { 
                    text: abrechnungsBackend.headcard_credit_card.toFixed(2); 
                    font.pixelSize: Style.fontSizeHeader; 
                    font.bold: true; 
                    color: Style.text; 
                    font.family: ubuntuFont.name 
                }
                Text { text: " €"; font.pixelSize: Style.fontSizeHeader; color: Style.text; font.family: ubuntuFont.name }
            }
            // Garage nur anzeigen, wenn > 0
            RowLayout {
                spacing: 4
                visible: abrechnungsBackend.headcard_garage > 0
                Image {
                    source: "assets/icons/parking_gray.svg"
                    width: 16; height: 16
                    fillMode: Image.PreserveAspectFit
                    Layout.alignment: Qt.AlignVCenter
                }
                Text { 
                    text: abrechnungsBackend.headcard_garage.toFixed(2); 
                    font.pixelSize: Style.fontSizeHeader; 
                    font.bold: true; 
                    color: Style.text; 
                    font.family: ubuntuFont.name 
                }
                Text { text: " €"; font.pixelSize: Style.fontSizeHeader; color: Style.text; font.family: ubuntuFont.name }
            }
            // NEU: Deal-Icon und Deal-Typ
            RowLayout {
                spacing: 15 // Abstand zwischen Icon und Text erhöht
                MouseArea {
                    id: dealIconArea
                    width: 40
                    height: 40
                    hoverEnabled: true
                    z: 10
                    anchors.verticalCenter: parent.verticalCenter
                    cursorShape: Qt.PointingHandCursor
                    onEntered: { console.log("DEBUG: Mouse entered Overlay-Icon!"); }
                    onExited: { console.log("DEBUG: Mouse exited Overlay-Icon!"); }
                    onClicked: {
                        updateMatchedPlatforms();
                        dealOverlay.visible = true;
                        overlayAlreadyOpened = true;
                    }
                    Image {
                        anchors.centerIn: parent
                        width: 40
                        height: 40
                        source: dealIconArea.containsMouse ? "assets/icons/deal_orange.svg" : "assets/icons/deal_white.svg"
                        fillMode: Image.PreserveAspectFit
                        anchors.margins: 0
                        anchors.leftMargin: 0
                        anchors.rightMargin: 0
                        anchors.topMargin: 0
                        anchors.bottomMargin: 0
                    }
                }
                Text {
                    text: abrechnungsBackend.deal
                    font.pixelSize: Style.fontSizeHeader * 1.2 // etwas größer
                    font.bold: true
                    color: Style.primary
                    font.family: ubuntuFont.name
                    verticalAlignment: Text.AlignVCenter
                    // Entferne alle Margins/Paddings
                    leftPadding: 0
                    rightPadding: 0
                    topPadding: 0
                    bottomPadding: 0
                    padding: 0
                }
            }
        }
    }

    // Property für Plattform-Liste im Overlay
    property var matchedPlatforms: []

    // Property für die Deal-Auswahl je Plattform
    property var matchedDeals: []

    // Property für die Slider-Werte je Plattform
    property var matchedSliderValues: []

    // Globale Deal-Optionen für alle Zeilen
    property var dealOptions: ["P", "%", "C"]

    // Property um zu tracken, ob das Overlay bereits in dieser Session geöffnet wurde
    property bool overlayAlreadyOpened: false
    
    // Property für den Overlay-Konfigurations-Cache
    property var overlayConfigCache: []

    // Hilfsfunktion, ob mindestens eine Box auf P steht
    function hasPDeal() {
        for (var i = 0; i < matchedDeals.length; i++) {
            if (matchedDeals[i] === 0) return true;
        }
        return false;
    }

    function getEchterUmsatzForPlattform(name) {
        // Einsteiger aus Eingabefeld
        if (name === "Einsteiger") {
            return Number(abrechnungsBackend.inputEinsteiger) || 0;
        }
        
        var ergebnisse = abrechnungsBackend.ergebnisse;
        for (var i = 0; i < ergebnisse.length; i++) {
            if (ergebnisse[i].label === "Taxi" && name === "Taxi") {
                if (ergebnisse[i].details) {
                    for (var j = 0; j < ergebnisse[i].details.length; j++) {
                        if (ergebnisse[i].details[j].label === "Total") {
                            return parseFloat(ergebnisse[i].details[j].value);
                        }
                    }
                }
            }
            if (ergebnisse[i].label === "Uber" && name === "Uber") {
                if (ergebnisse[i].details) {
                    for (var j = 0; j < ergebnisse[i].details.length; j++) {
                        if (ergebnisse[i].details[j].label === "Total") {
                            return parseFloat(ergebnisse[i].details[j].value);
                        }
                    }
                }
            }
            if (ergebnisse[i].label === "Bolt" && name === "Bolt") {
                if (ergebnisse[i].details) {
                    for (var j = 0; j < ergebnisse[i].details.length; j++) {
                        if (ergebnisse[i].details[j].label === "Echter Umsatz") {
                            return parseFloat(ergebnisse[i].details[j].value);
                        }
                    }
                }
            }
        }
        return 0;
    }

    property real overlayIncome: calculateOverlayIncome()
    
    function calculateOverlayIncome() {
        var income = 0;
        
        // Pauschale und Umsatzgrenze aus den Slider-Werten holen
        var pauschaleIndex = matchedPlatforms.indexOf("Pauschale");
        var umsatzgrenzeIndex = matchedPlatforms.indexOf("Umsatzgrenze");
        var pauschale = pauschaleIndex !== -1 ? (matchedSliderValues[pauschaleIndex] || 500) : (Number(abrechnungsBackend.pauschale) || 0);
        var umsatzgrenze = umsatzgrenzeIndex !== -1 ? (matchedSliderValues[umsatzgrenzeIndex] || 1200) : (Number(abrechnungsBackend.umsatzgrenze) || 0);
        
        var hatPDeal = false;
        var summe_P_umsatz = 0;
        // 1. Prüfen, ob mindestens eine Plattform auf P steht und Pauschale setzen
        for (var i = 0; i < matchedPlatforms.length; i++) {
            if (["Taxi", "Uber", "Bolt", "Einsteiger"].indexOf(matchedPlatforms[i]) !== -1 && matchedDeals[i] === 0) {
                hatPDeal = true;
                summe_P_umsatz += getEchterUmsatzForPlattform(matchedPlatforms[i]);
            }
        }
        if (hatPDeal) {
            income += pauschale;
            if (summe_P_umsatz > umsatzgrenze) {
                income += (summe_P_umsatz - umsatzgrenze) * 0.1;
            }
        }
        // 3. Prozent- oder Custom-Deals
        for (var i = 0; i < matchedPlatforms.length; i++) {
            if (["Taxi", "Uber", "Bolt", "Einsteiger"].indexOf(matchedPlatforms[i]) !== -1 && (matchedDeals[i] === 1 || matchedDeals[i] === 2)) {
                var umsatz = getEchterUmsatzForPlattform(matchedPlatforms[i]);
                var sliderValue = matchedSliderValues[i] !== undefined ? matchedSliderValues[i] : (matchedDeals[i] === 1 ? 50 : 0);
                income += umsatz * sliderValue / 100;
            }
        }
        // KEIN Abzug von Garage oder Tank!
        return income;
    }

    property real overlayErgebnis: {
        var ergebnis = overlayIncome;
        // Garage abziehen (Headerwert * Slider-Prozent)
        var garageIndex = matchedPlatforms.indexOf("Garage");
        if (garageIndex !== -1) {
            var garageValue = Number(abrechnungsBackend.headcard_garage) || 0;
            var garagePercent = matchedSliderValues[garageIndex] || 0;
            ergebnis -= garageValue * (garagePercent / 100);
        }
        // Tank abziehen (InputGas * Slider-Prozent)
        var tankIndex = matchedPlatforms.indexOf("Tank");
        if (tankIndex !== -1) {
            var tankValue = Number(abrechnungsBackend.inputGas) || 0;
            var tankPercent = matchedSliderValues[tankIndex] || 0;
            ergebnis -= tankValue * (tankPercent / 100);
        }
        return ergebnis;
    }

    // Overlay für leere schwarze Seite mit dünnem grauem Rahmen und ListView
    Rectangle {
        id: dealOverlay
        visible: false
        width: 520
        height: 340
        // Positioniere das Overlay fest an der rechten Seite des Fensters positionieren
        x: parent.width - width - 200
        y: 100
        color: "#000" // komplett schwarz
        radius: 8
        z: 1000
        

        
        // MouseArea für Drag & Drop
        MouseArea {
            id: dragArea
            anchors.fill: parent
            anchors.bottomMargin: 280 // Platz für den Header lassen
            drag.target: dealOverlay
            drag.axis: Drag.XAndYAxis
            drag.minimumX: 0
            drag.maximumX: parent.parent.width - dealOverlay.width
            drag.minimumY: 0
            drag.maximumY: parent.parent.height - dealOverlay.height
            
            // Cursor ändern beim Hover
            hoverEnabled: true
            cursorShape: containsMouse ? Qt.SizeAllCursor : Qt.ArrowCursor
            
            // Optional: Visueller Hinweis beim Hover
            Rectangle {
                anchors.fill: parent
                color: "transparent"
                border.color: dragArea.containsMouse ? "#555" : "transparent"
                border.width: 1
                radius: 8
            }
        }
        // MouseArea entfernt, damit ListView-Elemente voll klickbar sind
        // Headerzeile entfernt
        // ListView für Plattformen mit festen Spalten
        ListView {
            id: platformListView
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.topMargin: 60
            anchors.bottom: parent.bottom
            anchors.margins: 32
            z: 3
            model: matchedPlatforms.length
            delegate: Item {
                width: parent.width; height: 40
                GridLayout {
                    anchors.fill: parent
                    columns: 3
                    // Plattformname rechtsbündig
                    Text {
                        text: matchedPlatforms[index]
                        color: (matchedPlatforms[index] === "Pauschale" || matchedPlatforms[index] === "Umsatzgrenze") && !hasPDeal() ? "#666" : "#fff"
                        font.pixelSize: 20
                        font.family: spaceMonoFont.name
                        horizontalAlignment: Text.AlignRight
                        verticalAlignment: Text.AlignVCenter
                        Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
                        Layout.preferredWidth: 100
                    }
                    // Click-Box zentriert
                    Item {
                        width: 40; height: 40
                        Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
                        visible: ((matchedDeals[index] !== null && matchedPlatforms[index] !== "Garage" && matchedPlatforms[index] !== "Tank") && (matchedPlatforms[index] !== "Pauschale" && matchedPlatforms[index] !== "Umsatzgrenze"))
                        Rectangle {
                            width: 28; height: 28
                            anchors.centerIn: parent
                            color: "#222"
                            radius: 6
                            border.width: 0
                            MouseArea {
                                anchors.fill: parent
                                onClicked: {
                                    var current = matchedDeals[index] !== undefined ? matchedDeals[index] : 0;
                                    var next = (current + 1) % dealOptions.length;
                                    var arr = matchedDeals.slice();
                                    arr[index] = next;
                                    matchedDeals = arr;
                                    
                                    // Bei '%' Deal automatisch Slider auf 50 setzen
                                    if (next === 1) {
                                        var sliderArr = matchedSliderValues.slice();
                                        sliderArr[index] = 50;
                                        matchedSliderValues = sliderArr;
                                    }
                                    
                                    // Wenn Taxi geändert wird, Einsteiger auch ändern
                                    if (matchedPlatforms[index] === "Taxi") {
                                        var einsteigerIndex = matchedPlatforms.indexOf("Einsteiger");
                                        if (einsteigerIndex !== -1) {
                                            arr[einsteigerIndex] = next;
                                            matchedDeals = arr;
                                            
                                            // Bei '%' Deal auch für Einsteiger Slider auf 50 setzen
                                            if (next === 1) {
                                                sliderArr[einsteigerIndex] = 50;
                                                matchedSliderValues = sliderArr;
                                            }
                                        }
                                    }
                                    
                                    // Einkommen sofort neu berechnen
                                    forceOverlayIncomeUpdate();
                                }
                                cursorShape: Qt.PointingHandCursor
                            }
                            Text {
                                anchors.centerIn: parent
                                text: dealOptions[matchedDeals[index] !== undefined ? matchedDeals[index] : 0]
                                color: "#fff"
                                font.pixelSize: 16
                                font.family: spaceMonoFont.name
                            }
                        }
                    }
                    // Leeres Feld für Garage/Tank oder für Zeilen ohne Click-Box
                    Item {
                        width: 40; height: 40
                        Layout.alignment: Qt.AlignHCenter | Qt.AlignVCenter
                        visible: matchedDeals[index] === null || matchedPlatforms[index] === "Garage" || matchedPlatforms[index] === "Tank" || matchedPlatforms[index] === "Pauschale" || matchedPlatforms[index] === "Umsatzgrenze"
                    }
                    // Slider-Spalte
                    Rectangle {
                        width: 120; height: 40; color: "transparent"
                        Layout.alignment: Qt.AlignLeft | Qt.AlignVCenter
                        RowLayout {
                            anchors.fill: parent
                            spacing: 8
                            // Spezial-Slider für Pauschale
                            Slider {
                                visible: matchedPlatforms[index] === "Pauschale"
                                width: 100
                                height: 32
                                from: 500
                                to: 1000
                                stepSize: 10
                                value: hasPDeal() ? (matchedSliderValues[index] !== undefined ? matchedSliderValues[index] : 500) : 0
                                enabled: hasPDeal()
                                opacity: hasPDeal() ? 1.0 : 0.3
                                onMoved: {
                                    if (hasPDeal()) {
                                        var arr = matchedSliderValues.slice();
                                        arr[index] = value;
                                        matchedSliderValues = arr;
                                        // Einkommen sofort neu berechnen
                                        forceOverlayIncomeUpdate();
                                    }
                                }
                            }
                            Text {
                                visible: matchedPlatforms[index] === "Pauschale"
                                text: (hasPDeal() ? Math.round(matchedSliderValues[index] !== undefined ? matchedSliderValues[index] : 500) : 0) + " €"
                                color: hasPDeal() ? "#fff" : "#666"
                                font.pixelSize: 16
                                font.family: spaceMonoFont.name
                                verticalAlignment: Text.AlignVCenter
                                width: 48
                                horizontalAlignment: Text.AlignLeft
                            }
                            // Spezial-Slider für Umsatzgrenze
                            Slider {
                                visible: matchedPlatforms[index] === "Umsatzgrenze"
                                width: 100
                                height: 32
                                from: 1200
                                to: 2500
                                stepSize: 100
                                value: hasPDeal() ? (matchedSliderValues[index] !== undefined ? matchedSliderValues[index] : 1200) : 0
                                enabled: hasPDeal()
                                opacity: hasPDeal() ? 1.0 : 0.3
                                onMoved: {
                                    if (hasPDeal()) {
                                        var arr = matchedSliderValues.slice();
                                        arr[index] = value;
                                        matchedSliderValues = arr;
                                        // Einkommen sofort neu berechnen
                                        forceOverlayIncomeUpdate();
                                    }
                                }
                            }
                            Text {
                                visible: matchedPlatforms[index] === "Umsatzgrenze"
                                text: (hasPDeal() ? Math.round(matchedSliderValues[index] !== undefined ? matchedSliderValues[index] : 1200) : 0) + " €"
                                color: hasPDeal() ? "#fff" : "#666"
                                font.pixelSize: 16
                                font.family: spaceMonoFont.name
                                verticalAlignment: Text.AlignVCenter
                                width: 48
                                horizontalAlignment: Text.AlignLeft
                            }
                            // Standard-Slider für alle anderen
                            // Wenn 'P', dann leerer Platzhalter, sonst Slider und Zahl
                            Item {
                                visible: matchedPlatforms[index] !== "Pauschale" && matchedPlatforms[index] !== "Umsatzgrenze" && matchedDeals[index] === 0
                                width: 100; height: 32
                            }
                            Slider {
                                visible: matchedPlatforms[index] !== "Pauschale" && matchedPlatforms[index] !== "Umsatzgrenze" && matchedDeals[index] !== 0
                                width: 100
                                height: 32
                                from: 0
                                to: 100
                                stepSize: 1
                                value: matchedDeals[index] === 1 ? 50 : (matchedSliderValues[index] !== undefined ? matchedSliderValues[index] : 0)
                                enabled: matchedDeals[index] === 2
                                opacity: matchedDeals[index] === 2 ? 1.0 : 0.4
                                onMoved: {
                                    if (matchedDeals[index] === 2) {
                                        var arr = matchedSliderValues.slice();
                                        arr[index] = value;
                                        matchedSliderValues = arr;
                                        // Einkommen sofort neu berechnen
                                        forceOverlayIncomeUpdate();
                                    }
                                }
                                onValueChanged: {
                                    // Bei '%' Deal automatisch 50 setzen, wenn noch nicht gesetzt
                                    if (matchedDeals[index] === 1 && (matchedSliderValues[index] === undefined || matchedSliderValues[index] !== 50)) {
                                        var arr = matchedSliderValues.slice();
                                        arr[index] = 50;
                                        matchedSliderValues = arr;
                                        // Einkommen sofort neu berechnen
                                        forceOverlayIncomeUpdate();
                                    }
                                }
                            }
                            Text {
                                visible: matchedPlatforms[index] !== "Pauschale" && matchedPlatforms[index] !== "Umsatzgrenze" && matchedDeals[index] !== 0
                                text: (matchedDeals[index] === 1 ? 50 : Math.round(matchedSliderValues[index] !== undefined ? matchedSliderValues[index] : 0)) + " %"
                                color: matchedDeals[index] === 2 ? "#fff" : "#888"
                                font.pixelSize: 16
                                font.family: spaceMonoFont.name
                                verticalAlignment: Text.AlignVCenter
                                width: 48
                                horizontalAlignment: Text.AlignLeft
                            }
                        }
                    }
                }
            }
        }
        // Header mit Einkommens-Vorschau
        Rectangle {
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            height: 60
            radius: 8
            z: 4
            
            // Gradient-Hintergrund von dunklem Grau zu Schwarz
            gradient: Gradient {
                GradientStop { position: 0.0; color: "#111111" }  // Sehr dunkles Grau oben
                GradientStop { position: 1.0; color: "#000000" }  // Reines Schwarz unten
            }
            
            RowLayout {
                anchors.fill: parent
                anchors.margins: 16
                spacing: 16
                
                // Einkommen und Anteil Vorschau nebeneinander
                Row {
                    spacing: 32
                    Layout.fillWidth: true
                    
                    // Einkommen (Umsätze ohne Abzüge)
                    Column {
                        Text {
                            text: "Einkommen:"
                            color: "#888"
                            font.pixelSize: 12
                            font.family: spaceMonoFont.name
                        }
                        Text {
                            text: overlayIncome.toFixed(2) + " €"
                            color: "#fff"
                            font.pixelSize: 16
                            font.bold: true
                            font.family: spaceMonoFont.name
                        }
                    }
                    
                    // Anteil (Umsätze minus Garage und Tank)
                    Column {
                        Text {
                            text: "Anteil:"
                            color: "#888"
                            font.pixelSize: 12
                            font.family: spaceMonoFont.name
                        }
                        Text {
                            text: overlayErgebnis.toFixed(2) + " €"
                            color: "#fff"
                            font.pixelSize: 16
                            font.bold: true
                            font.family: spaceMonoFont.name
                        }
                    }
                }
                
                // Buttons
                Row {
                    spacing: 8
                    
                    // Speichern-Button
                    MouseArea {
                        width: 40; height: 40
                        onClicked: {
                            if (validateOverlayConfiguration()) {
                                saveOverlayConfiguration();
                                // Einkommen (ohne Abzüge) als Income speichern
                                console.log("QML: overlayConfigCache vor Backend-Call:", JSON.stringify(overlayConfigCache));
                                abrechnungsBackend.speichereUmsatzCustom(overlayIncome, JSON.stringify(overlayConfigCache));
                                abrechnungsBackend.update_ergebnis(); // Ergebnis nach Overlay-Speichern aktualisieren
                                dealOverlay.visible = false;
                            }
                        }
                        Image {
                            anchors.centerIn: parent
                            source: "assets/icons/check_gray.svg"
                            width: 24; height: 24
                            fillMode: Image.PreserveAspectFit
                        }
                    }
                    
                    // Schließen-Button
                    MouseArea {
                        width: 40; height: 40
                        onClicked: dealOverlay.visible = false
                        Image {
                            anchors.centerIn: parent
                            source: "assets/icons/close_red.svg"
                            width: 24; height: 24
                            fillMode: Image.PreserveAspectFit
                        }
                    }
                }
            }
        }
    }

    // CustomDealDialog auskommentieren/entfernen
    // CustomDealDialog {
    //     id: customDealDialog
    //     anchors.centerIn: parent
    //     onClosed: { customDealDialog.visible = false; }
    // }

    function parseUberCard(results, deal) {
        for (var i = 0; i < results.length; i++) {
            if (results[i].type === "summary" && results[i].label === "Uber" && results[i].details) {
                var details = results[i].details;
                var gross_total = 0;
                var cash_collected = 0;
                for (var j = 0; j < details.length; j++) {
                    if (details[j].label === "Echter Umsatz" || details[j].label === "Total")
                        gross_total = parseFloat(details[j].value.replace(/[^\d.-]/g, ""));
                    if (details[j].label === "Bargeld")
                        cash_collected = parseFloat(details[j].value.replace(/[^\d.-]/g, ""));
                }
                var credit_card = typeof abrechnungsBackend !== 'undefined' ? (abrechnungsBackend.headcard_credit_card || 0) : 0;
                if (deal === "P") {
                    return {
                        label: "Uber",
                        zeile1: gross_total.toFixed(2),
                        zeile2: cash_collected.toFixed(2),
                        zeile3: credit_card.toFixed(2)
                    };
                } else {
                    var zeile1 = gross_total;
                    var zeile2 = gross_total / 2;
                    var zeile3 = cash_collected;
                    return {
                        label: "Uber",
                        zeile1: zeile1.toFixed(2),
                        zeile2: zeile2.toFixed(2),
                        zeile3: credit_card.toFixed(2)
                    };
                }
            }
        }
        return {label: "Uber", zeile1: "-", zeile2: "-", zeile3: "-"};
    }

    function parseBoltCard(results, deal) {
        for (var i = 0; i < results.length; i++) {
            if (results[i].type === "summary" && results[i].label === "Bolt" && results[i].details) {
                var details = results[i].details;
                var echter_umsatz = 0;
                var cash_collected = 0;
                for (var j = 0; j < details.length; j++) {
                    if (details[j].label === "Echter Umsatz")
                        echter_umsatz = parseFloat(details[j].value.replace(/[^\d.-]/g, ""));
                    if (details[j].label === "Bargeld")
                        cash_collected = parseFloat(details[j].value.replace(/[^\d.-]/g, ""));
                }
                var credit_card = typeof abrechnungsBackend !== 'undefined' ? (abrechnungsBackend.headcard_credit_card || 0) : 0;
                if (deal === "P") {
                    return {
                        label: "Bolt",
                        zeile1: echter_umsatz.toFixed(2),
                        zeile2: cash_collected.toFixed(2),
                        zeile3: credit_card.toFixed(2)
                    };
                } else {
                    var net_earnings = 0;
                    for (var j = 0; j < details.length; j++) {
                        if (details[j].label === "Echter Umsatz") net_earnings = parseFloat(details[j].value.replace(/[^\d.-]/g, ""));
                    }
                    var zeile1 = net_earnings;
                    var zeile2 = zeile1 / 2;
                    return {
                        label: "Bolt",
                        zeile1: zeile1.toFixed(2),
                        zeile2: zeile2.toFixed(2),
                        zeile3: credit_card.toFixed(2)
                    };
                }
            }
        }
        return {label: "Bolt", zeile1: "-", zeile2: "-", zeile3: "-"};
    }

    function parse40100Card(results, deal) {
        for (var i = 0; i < results.length; i++) {
            if (results[i].type === "summary" && (results[i].label === "40100" || results[i].label === "Taxi")) {
                // Zeile 1: Der Gesamtwert aus der Zusammenfassung
                var total = parseFloat(String(results[i].value).replace(/[^\d.,-]/g, "").replace(',', '.')) || 0;

                var details = results[i].details || [];
                var bargeld = 0;
                var anteil = 0;

                // Werte für andere Zeilen aus den Details summieren
                for (var j = 0; j < details.length; j++) {
                    if (details[j].label === "Bargeld") {
                        bargeld += parseFloat(String(details[j].value).replace(/[^\d.,-]/g, "").replace(',', '.')) || 0;
                    }
                    if (details[j].label === "Anteil") {
                        anteil += parseFloat(String(details[j].value).replace(/[^\d.,-]/g, "").replace(',', '.')) || 0;
                    }
                }

                var credit_card = typeof abrechnungsBackend !== 'undefined' ? (abrechnungsBackend.headcard_credit_card || 0) : 0;
                
                if (deal === "P") {
                    return {
                        label: "Taxi",
                        zeile1: total.toFixed(2),
                        zeile2: bargeld.toFixed(2),
                        zeile3: credit_card.toFixed(2)
                    };
                } else {
                    return {
                        label: "Taxi",
                        zeile1: total.toFixed(2),
                        zeile2: anteil.toFixed(2),
                        zeile3: credit_card.toFixed(2)
                    };
                }
            }
        }
        return {label: "Taxi", zeile1: "-", zeile2: "-", zeile3: "-"};
    }

    Connections {
        target: abrechnungsBackend
        function onErgebnisseChanged() {
            var results = abrechnungsBackend.ergebnisse;
            var deal = abrechnungsBackend.deal;
            card40100 = parse40100Card(results, deal);
            cardUber = parseUberCard(results, deal);
            cardBolt = parseBoltCard(results, deal);
            werteGeladen = true;
            wizardSelection = abrechnungsBackend.get_current_selection();
        }
        
        function onDealChanged() {
            // Ergebnis automatisch neu berechnen wenn sich der Deal-Typ ändert
            console.log("Deal-Typ geändert, Ergebnis wird neu berechnet");
        }
        
        function onInputGasChanged() {
            // Ergebnis automatisch neu berechnen wenn sich Tank-Wert ändert
            console.log("Tank-Wert geändert, Ergebnis wird neu berechnet");
        }
        
        function onHeadcardGarageChanged() {
            // Ergebnis automatisch neu berechnen wenn sich Garage-Wert ändert
            console.log("Garage-Wert geändert, Ergebnis wird neu berechnet");
        }
        
        function onInputEinsteigerChanged() {
            // Ergebnis automatisch neu berechnen wenn sich Einsteiger-Wert ändert
            console.log("Einsteiger-Wert geändert, Ergebnis wird neu berechnet");
        }
    }

    Component.onCompleted: {
        var results = abrechnungsBackend.ergebnisse;
        var deal = abrechnungsBackend.deal;
        if (results && results.length > 0) {
            card40100 = parse40100Card(results, deal);
            cardUber = parseUberCard(results, deal);
            cardBolt = parseBoltCard(results, deal);
            werteGeladen = true;
        }
        wizardSelection = abrechnungsBackend.get_current_selection();
    }

    // Hilfsfunktion für Overlay-Konfiguration
    function getOverlayConfig() {
        var config = [];
        for (var i = 0; i < matchedPlatforms.length; i++) {
            config.push({
                platform: matchedPlatforms[i],
                deal: matchedDeals[i],
                slider: matchedSliderValues[i]
            });
        }
        return config;
    }
    
    function saveOverlayConfiguration() {
        // 1. Prüfe, ob das aktuelle Schema mit % oder P übereinstimmt
        var isPercent = true;
        var isPauschale = true;
        for (var i = 0; i < matchedDeals.length; i++) {
            if (matchedDeals[i] !== 1) isPercent = false;
            if (matchedDeals[i] !== 0) isPauschale = false;
        }
        if (!isPercent && !isPauschale) {
            abrechnungsBackend.setDeal("C");
        }
        
        // 2. Konfiguration als JSON im Cache speichern
        var config = getOverlayConfig();
        overlayConfigCache = config;
        console.log("Overlay-Konfiguration im Cache gespeichert (neu):", JSON.stringify(config));
        
        // 3. Backend-Konfiguration anwenden
        applyOverlayConfigurationToBackend();
    }
    
    function saveOverlayConfigToDatabase() {
        if (!overlayConfigCache || overlayConfigCache.length === 0) {
            console.log("Keine Overlay-Konfiguration im Cache vorhanden");
            return;
        }
        
        if (!wizardSelection || !wizardSelection.fahrer_id) {
            console.warn("Kein Fahrer ausgewählt, kann Konfiguration nicht in Datenbank speichern");
            return;
        }
        
        var driverId = wizardSelection.fahrer_id;
        var fahrer = wizardSelection.fahrer || "";
        
        // Extrahiere Werte aus der Cache-Konfiguration
        var taxiDeal = 0, taxiSlider = 0;
        var uberDeal = 0, uberSlider = 0;
        var boltDeal = 0, boltSlider = 0;
        var einsteigerDeal = 0, einsteigerSlider = 0;
        var garageSlider = 0, tankSlider = 0;
        
        for (var i = 0; i < overlayConfigCache.length; i++) {
            var item = overlayConfigCache[i];
            switch(item.platform) {
                case "Taxi":
                    taxiDeal = item.deal || 0;
                    taxiSlider = item.slider || 0;
                    break;
                case "Uber":
                    uberDeal = item.deal || 0;
                    uberSlider = item.slider || 0;
                    break;
                case "Bolt":
                    boltDeal = item.deal || 0;
                    boltSlider = item.slider || 0;
                    break;
                case "Einsteiger":
                    einsteigerDeal = item.deal || 0;
                    einsteigerSlider = item.slider || 0;
                    break;
                case "Garage":
                    garageSlider = item.slider || 0;
                    break;
                case "Tank":
                    tankSlider = item.slider || 0;
                    break;
            }
        }
        
        try {
            abrechnungsBackend.speichereOverlayKonfiguration(driverId, fahrer, taxiDeal, taxiSlider, uberDeal, uberSlider, boltDeal, boltSlider, einsteigerDeal, einsteigerSlider, garageSlider, tankSlider);
            console.log("Overlay-Konfiguration erfolgreich in Datenbank gespeichert für Fahrer ID:", driverId);
            
            // Cache leeren nach erfolgreichem Speichern
            overlayConfigCache = [];
        } catch (e) {
            console.error("Fehler beim Speichern der Overlay-Konfiguration in Datenbank:", e);
        }
    }
    
    function loadOverlayConfiguration() {
        // Lade gespeicherte Konfiguration nur beim ersten Öffnen in dieser Session
        if (overlayAlreadyOpened) {
            console.log("Overlay bereits in dieser Session geöffnet, überspringe Laden der Datenbank-Konfiguration");
            return;
        }
        
        // Lade gespeicherte Konfiguration aus dem Backend
        if (!wizardSelection || !wizardSelection.fahrer_id) {
            console.log("Kein Fahrer ausgewählt, überspringe Laden der Konfiguration");
            return;
        }
        
        var driverId = wizardSelection.fahrer_id;
        try {
            var config = abrechnungsBackend.ladeOverlayKonfiguration(driverId);
            if (config && config.length > 0) {
                console.log("Gespeicherte Konfiguration aus Datenbank geladen:", config);
                
                // Konfiguration auf matchedDeals und matchedSliderValues anwenden
                var newDeals = matchedDeals.slice();
                var newSliders = matchedSliderValues.slice();
                
                // Backend gibt Array zurück: [taxi_deal, taxi_slider, uber_deal, uber_slider, bolt_deal, bolt_slider, einsteiger_deal, einsteiger_slider, garage_slider, tank_slider]
                var taxiDeal = config[0] || 0;
                var taxiSlider = config[1] || 0;
                var uberDeal = config[2] || 0;
                var uberSlider = config[3] || 0;
                var boltDeal = config[4] || 0;
                var boltSlider = config[5] || 0;
                var einsteigerDeal = config[6] || 0;
                var einsteigerSlider = config[7] || 0;
                var garageSlider = config[8] || 0;
                var tankSlider = config[9] || 0;
                
                // Werte auf die entsprechenden Indizes anwenden
                var taxiIndex = matchedPlatforms.indexOf("Taxi");
                var uberIndex = matchedPlatforms.indexOf("Uber");
                var boltIndex = matchedPlatforms.indexOf("Bolt");
                var einsteigerIndex = matchedPlatforms.indexOf("Einsteiger");
                var garageIndex = matchedPlatforms.indexOf("Garage");
                var tankIndex = matchedPlatforms.indexOf("Tank");
                
                if (taxiIndex !== -1) {
                    newDeals[taxiIndex] = taxiDeal;
                    newSliders[taxiIndex] = taxiSlider;
                    console.log("Taxi: Deal=" + taxiDeal + ", Slider=" + taxiSlider);
                }
                
                if (uberIndex !== -1) {
                    newDeals[uberIndex] = uberDeal;
                    newSliders[uberIndex] = uberSlider;
                    console.log("Uber: Deal=" + uberDeal + ", Slider=" + uberSlider);
                }
                
                if (boltIndex !== -1) {
                    newDeals[boltIndex] = boltDeal;
                    newSliders[boltIndex] = boltSlider;
                    console.log("Bolt: Deal=" + boltDeal + ", Slider=" + boltSlider);
                }
                
                if (einsteigerIndex !== -1) {
                    newDeals[einsteigerIndex] = einsteigerDeal;
                    newSliders[einsteigerIndex] = einsteigerSlider;
                    console.log("Einsteiger: Deal=" + einsteigerDeal + ", Slider=" + einsteigerSlider);
                }
                
                if (garageIndex !== -1) {
                    newSliders[garageIndex] = garageSlider;
                    console.log("Garage: Slider=" + garageSlider);
                }
                
                if (tankIndex !== -1) {
                    newSliders[tankIndex] = tankSlider;
                    console.log("Tank: Slider=" + tankSlider);
                }
                
                // Arrays aktualisieren
                matchedDeals = newDeals;
                matchedSliderValues = newSliders;
                
                // Einkommen neu berechnen
                forceOverlayIncomeUpdate();
                
                console.log("Gespeicherte Konfiguration erfolgreich angewendet");
            }
        } catch (e) {
            console.log("Keine gespeicherte Konfiguration gefunden oder Fehler beim Laden:", e);
        }
    }
    
    function forceOverlayIncomeUpdate() {
        // Force update der overlayIncome Property
        overlayIncome = calculateOverlayIncome();
        
        // Backend-Konfiguration anwenden für Live-Updates
        applyOverlayConfigurationToBackend();
    }
    
    function validateOverlayConfiguration() {
        // Prüfe, ob mindestens eine Plattform konfiguriert ist
        var hasValidPlatform = false;
        for (var i = 0; i < matchedPlatforms.length; i++) {
            var platform = matchedPlatforms[i];
            if (["Taxi", "Uber", "Bolt", "Einsteiger"].indexOf(platform) !== -1) {
                if (matchedDeals[i] !== null && matchedDeals[i] !== undefined) {
                    hasValidPlatform = true;
                    break;
                }
            }
        }
        
        if (!hasValidPlatform) {
            console.warn("Mindestens eine Plattform muss konfiguriert sein!");
            return false;
        }
        
        // Prüfe, ob Einkommen positiv ist
        if (overlayIncome <= 0) {
            console.warn("Einkommen muss größer als 0 sein!");
            return false;
        }
        
        return true;
    }
    
    function restoreOverlayConfigFromCache() {
        if (!overlayConfigCache || overlayConfigCache.length === 0) return;
        var newDeals = matchedDeals.slice();
        var newSliders = matchedSliderValues.slice();
        for (var i = 0; i < overlayConfigCache.length; i++) {
            var item = overlayConfigCache[i];
            var idx = matchedPlatforms.indexOf(item.platform);
            if (idx !== -1) {
                if (item.deal !== null && item.deal !== undefined) newDeals[idx] = item.deal;
                if (item.slider !== null && item.slider !== undefined) newSliders[idx] = item.slider;
            }
        }
        matchedDeals = newDeals;
        matchedSliderValues = newSliders;
        forceOverlayIncomeUpdate();
        console.log("Overlay-Konfiguration aus Cache auf UI angewendet:", JSON.stringify(overlayConfigCache));
    }

    // Beim Öffnen des Overlays Plattformen extrahieren, Deals und Slider initialisieren
    function updateMatchedPlatforms() {
        if (overlayAlreadyOpened && overlayConfigCache && overlayConfigCache.length > 0) {
            restoreOverlayConfigFromCache();
        } else {
            var results = abrechnungsBackend.ergebnisse;
            var platforms = [];
            var deals = [];
            var sliders = [];
            var globalDeal = abrechnungsBackend.deal;
            // Pauschale und Umsatzgrenze immer ganz oben, Werte immer aus Backend-Properties
            platforms.push("Pauschale");
            deals.push(null); // keine Click-Box
            sliders.push(globalDeal === "%" ? 0 : Number(abrechnungsBackend.pauschale));
            platforms.push("Umsatzgrenze");
            deals.push(null); // keine Click-Box
            sliders.push(globalDeal === "%" ? 0 : Number(abrechnungsBackend.umsatzgrenze));
            // Plattformen extrahieren
            for (var i = 0; i < results.length; i++) {
                var entry = results[i];
                if (entry.type === "summary" && entry.details && entry.details.length > 0) {
                    var plattform = entry.label;
                    if (["Uber", "Bolt", "40100", "31300", "Taxi"].indexOf(plattform) !== -1) {
                        if (plattform === "40100" || plattform === "31300" || plattform === "Taxi") {
                            // Prüfen, ob "Taxi" schon in der Liste ist, um Duplikate zu vermeiden
                            if (platforms.indexOf("Taxi") === -1) {
                                platforms.push("Taxi");
                                deals.push(globalDeal === "%" ? 1 : 0); // % oder P
                                sliders.push(globalDeal === "%" ? 50 : 0);
                            }
                        } else {
                            platforms.push(plattform);
                            deals.push(globalDeal === "%" ? 1 : 0); // % oder P
                            sliders.push(globalDeal === "%" ? 50 : 0);
                        }
                    }
                }
            }
            // Einsteiger-Zeile immer nach den Plattformen einfügen
            platforms.push("Einsteiger");
            deals.push(globalDeal === "%" ? 1 : 0); // % oder P
            sliders.push(globalDeal === "%" ? 50 : 0);
            // Garage-Zeile, wenn Wert vorhanden
            if (abrechnungsBackend.headcard_garage > 0) {
                platforms.push("Garage");
                deals.push(2); // Immer C
                sliders.push(50);
            }
            // Tank am Ende
            platforms.push("Tank"); // Immer Tank am Ende
            deals.push(2); // Immer C
            sliders.push(globalDeal === "%" ? 50 : 0);
            matchedPlatforms = platforms;
            matchedDeals = deals;
            matchedSliderValues = sliders;
            
            // Lade gespeicherte Konfiguration
            loadOverlayConfiguration();
        }
    }

    // Neue BottomBar:
    RowLayout {
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 24
        spacing: 32
        // Home-Button
        MouseArea {
            id: homeArea
            width: 56; height: 56
            cursorShape: Qt.PointingHandCursor
            hoverEnabled: true
            onClicked: {
                if (typeof root.goHome === "function") {
                    root.goHome();
                    } else {
                    console.warn("goHome ist nicht definiert oder keine Funktion!");
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
        // Check-Button
        MouseArea {
            id: checkArea
            width: 56; height: 56
            cursorShape: Qt.PointingHandCursor
            hoverEnabled: true
                                    onClicked: {
                            // Speichere Overlay-Konfiguration in Datenbank, falls vorhanden
                            if (overlayConfigCache && overlayConfigCache.length > 0) {
                                saveOverlayConfigToDatabase();
                            }
                            
                            abrechnungsBackend.speichereUmsatz();
                            // Reset overlayAlreadyOpened beim finalen Speichern
                            overlayAlreadyOpened = false;
                            // Overlay nach dem Speichern schließen
                            dealOverlay.visible = false;
                        }
            Image {
                anchors.centerIn: parent
                source: checkArea.containsMouse ? "assets/icons/check_orange.svg" : "assets/icons/check_white.svg"
                width: checkArea.pressed ? 32 : checkArea.containsMouse ? 40 : 32
                height: width
                fillMode: Image.PreserveAspectFit
            }
        }
        // Redo-Button
        MouseArea {
            id: redoArea
            width: 56; height: 56
            cursorShape: Qt.PointingHandCursor
            hoverEnabled: true
            onClicked: {
                abrechnungsBackend.show_wizard_and_load_page();
                // Reset overlayAlreadyOpened beim Wizard-Neustart
                overlayAlreadyOpened = false;
                // Cache leeren beim Wizard-Neustart
                overlayConfigCache = [];
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

    // Entferne die Automatische Synchronisation: Wenn overlayConfigCache nach Wizard/Backend-Update neu gesetzt wird, NICHT mehr automatisch Werte ans Backend senden oder update_ergebnis aufrufen
    // Connections {
    //     target: abrechnungsBackend
    //     function onOverlayConfigCacheChanged() {
    //         // Automatisch Income und Overlay-Konfiguration ans Backend senden
    //         if (overlayConfigCache && overlayConfigCache.length > 0) {
    //             for (var i = 0; i < overlayConfigCache.length; i++) {
    //                 var item = overlayConfigCache[i];
    //                 if (item.platform === "Tank") {
    //                     abrechnungsBackend.inputGas = item.slider !== undefined ? item.slider.toString() : "";
    //                 }
    //                 if (item.platform === "Einsteiger") {
    //                     abrechnungsBackend.inputEinsteiger = item.slider !== undefined ? item.slider.toString() : "";
    //                 }
    //                 // Weitere Properties können hier ergänzt werden
    //             }
    //             abrechnungsBackend.speichereUmsatzCustom(overlayIncome, JSON.stringify(overlayConfigCache));
    //         }
    //     }
    // }

    function applyOverlayConfigurationToBackend() {
        // Plattform-Faktoren berechnen
        var taxiFaktor = 1.0, uberFaktor = 1.0, boltFaktor = 1.0;
        var taxiIndex = matchedPlatforms.indexOf("Taxi");
        var uberIndex = matchedPlatforms.indexOf("Uber");
        var boltIndex = matchedPlatforms.indexOf("Bolt");
        
        if (taxiIndex !== -1) {
            taxiFaktor = matchedSliderValues[taxiIndex] !== undefined ? matchedSliderValues[taxiIndex] / 100.0 : 1.0;
        }
        if (uberIndex !== -1) {
            uberFaktor = matchedSliderValues[uberIndex] !== undefined ? matchedSliderValues[uberIndex] / 100.0 : 1.0;
        }
        if (boltIndex !== -1) {
            boltFaktor = matchedSliderValues[boltIndex] !== undefined ? matchedSliderValues[boltIndex] / 100.0 : 1.0;
        }
        
        // Einsteiger, Tank, Garage Faktoren berechnen
        var einsteigerFaktor = 1.0, tankFaktor = 1.0, garageFaktor = 1.0;
        for (var i = 0; i < matchedPlatforms.length; i++) {
            if (matchedPlatforms[i] === "Einsteiger") {
                einsteigerFaktor = matchedSliderValues[i] !== undefined ? matchedSliderValues[i] / 100.0 : 1.0;
            }
            if (matchedPlatforms[i] === "Tank") {
                tankFaktor = matchedSliderValues[i] !== undefined ? matchedSliderValues[i] / 100.0 : 1.0;
            }
            if (matchedPlatforms[i] === "Garage") {
                garageFaktor = matchedSliderValues[i] !== undefined ? matchedSliderValues[i] / 100.0 : 1.0;
            }
        }
        
        // Einkommen ohne Einsteiger berechnen
        var overlayIncomeOhneEinsteiger = overlayIncome;
        var einsteigerIndex = matchedPlatforms.indexOf("Einsteiger");
        if (einsteigerIndex !== -1) {
            var einsteigerUmsatz = getEchterUmsatzForPlattform("Einsteiger");
            var einsteigerSlider = matchedSliderValues[einsteigerIndex] !== undefined ? matchedSliderValues[einsteigerIndex] : 0;
            overlayIncomeOhneEinsteiger -= einsteigerUmsatz * (einsteigerSlider / 100.0);
        }
        
        // Backend-Methoden aufrufen
        console.log("DEBUG: Rufe Backend-Methoden auf...");
        console.log("DEBUG: setTaxiFaktor verfügbar:", typeof abrechnungsBackend.setTaxiFaktor);
        console.log("DEBUG: setUberFaktor verfügbar:", typeof abrechnungsBackend.setUberFaktor);
        console.log("DEBUG: setBoltFaktor verfügbar:", typeof abrechnungsBackend.setBoltFaktor);
        console.log("DEBUG: setEinsteigerFaktor verfügbar:", typeof abrechnungsBackend.setEinsteigerFaktor);
        console.log("DEBUG: setTankFaktor verfügbar:", typeof abrechnungsBackend.setTankFaktor);
        console.log("DEBUG: setGarageFaktor verfügbar:", typeof abrechnungsBackend.setGarageFaktor);
        
        if (abrechnungsBackend.setTaxiFaktor) {
            console.log("DEBUG: Rufe setTaxiFaktor mit Wert:", taxiFaktor);
            abrechnungsBackend.setTaxiFaktor(taxiFaktor);
        }
        if (abrechnungsBackend.setUberFaktor) {
            console.log("DEBUG: Rufe setUberFaktor mit Wert:", uberFaktor);
            abrechnungsBackend.setUberFaktor(uberFaktor);
        }
        if (abrechnungsBackend.setBoltFaktor) {
            console.log("DEBUG: Rufe setBoltFaktor mit Wert:", boltFaktor);
            abrechnungsBackend.setBoltFaktor(boltFaktor);
        }
        if (abrechnungsBackend.setEinsteigerFaktor) {
            console.log("DEBUG: Rufe setEinsteigerFaktor mit Wert:", einsteigerFaktor);
            abrechnungsBackend.setEinsteigerFaktor(einsteigerFaktor);
        }
        if (abrechnungsBackend.setTankFaktor) {
            console.log("DEBUG: Rufe setTankFaktor mit Wert:", tankFaktor);
            abrechnungsBackend.setTankFaktor(tankFaktor);
        }
        if (abrechnungsBackend.setGarageFaktor) {
            console.log("DEBUG: Rufe setGarageFaktor mit Wert:", garageFaktor);
            abrechnungsBackend.setGarageFaktor(garageFaktor);
        }
        if (abrechnungsBackend.setOverlayIncomeOhneEinsteiger) {
            console.log("DEBUG: Rufe setOverlayIncomeOhneEinsteiger mit Wert:", overlayIncomeOhneEinsteiger);
            abrechnungsBackend.setOverlayIncomeOhneEinsteiger(overlayIncomeOhneEinsteiger);
        }
        console.log("DEBUG: Backend-Methoden aufgerufen");
    }

    // === Temporäre Properties für alle Faktoren ===
    property real tempTaxiFaktor: abrechnungsBackend.taxi_faktor
    property real tempUberFaktor: abrechnungsBackend.uber_faktor
    property real tempBoltFaktor: abrechnungsBackend.bolt_faktor
    property real tempEinsteigerFaktor: abrechnungsBackend.einsteiger_faktor
    property real tempTankFaktor: abrechnungsBackend.tank_faktor
    property real tempGarageFaktor: abrechnungsBackend.garage_faktor

    // Funktion zum Initialisieren der temporären Werte beim Öffnen des Overlays
    function initOverlayFaktoren() {
        tempTaxiFaktor = abrechnungsBackend.taxi_faktor;
        tempUberFaktor = abrechnungsBackend.uber_faktor;
        tempBoltFaktor = abrechnungsBackend.bolt_faktor;
        tempEinsteigerFaktor = abrechnungsBackend.einsteiger_faktor;
        tempTankFaktor = abrechnungsBackend.tank_faktor;
        tempGarageFaktor = abrechnungsBackend.garage_faktor;
    }

    // Beispiel für das Overlay (nur der relevante Ausschnitt):
    property bool customDealOverlayVisible: false
    Rectangle {
        id: customDealOverlay
        visible: customDealOverlayVisible
        width: 520
        height: 340
        x: parent.width - width - 200
        y: 100
        color: "#000"
        radius: 8
        z: 1000
        
        // MouseArea für Drag & Drop
        MouseArea {
            anchors.fill: parent
            anchors.bottomMargin: 280 // Platz für den Header lassen
            drag.target: customDealOverlay
            drag.axis: Drag.XAndYAxis
            drag.minimumX: 0
            drag.maximumX: parent.parent.width - customDealOverlay.width
            drag.minimumY: 0
            drag.maximumY: parent.parent.height - customDealOverlay.height
            
            // Cursor ändern beim Hover
            hoverEnabled: true
            cursorShape: containsMouse ? Qt.SizeAllCursor : Qt.ArrowCursor
            
            // Optional: Visueller Hinweis beim Hover
            Rectangle {
                anchors.fill: parent
                color: "transparent"
                border.color: dragArea.containsMouse ? "#555" : "transparent"
                border.width: 1
                radius: 8
            }
        }
        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 32
            spacing: 20
            
            // Taxi Faktor
            RowLayout {
                Text { text: "Taxi-Faktor:" }
                Slider {
                    from: 0; to: 1; stepSize: 0.01
                    value: tempTaxiFaktor
                    onValueChanged: tempTaxiFaktor = value
                }
                Text { text: (tempTaxiFaktor * 100).toFixed(0) + "%" }
            }
            // Uber Faktor
            RowLayout {
                Text { text: "Uber-Faktor:" }
                Slider {
                    from: 0; to: 1; stepSize: 0.01
                    value: tempUberFaktor
                    onValueChanged: tempUberFaktor = value
                }
                Text { text: (tempUberFaktor * 100).toFixed(0) + "%" }
            }
            // Bolt Faktor
            RowLayout {
                Text { text: "Bolt-Faktor:" }
                Slider {
                    from: 0; to: 1; stepSize: 0.01
                    value: tempBoltFaktor
                    onValueChanged: tempBoltFaktor = value
                }
                Text { text: (tempBoltFaktor * 100).toFixed(0) + "%" }
            }
            // Einsteiger Faktor
            RowLayout {
                Text { text: "Einsteiger-Faktor:" }
                Slider {
                    from: 0; to: 1; stepSize: 0.01
                    value: tempEinsteigerFaktor
                    onValueChanged: tempEinsteigerFaktor = value
                }
                Text { text: (tempEinsteigerFaktor * 100).toFixed(0) + "%" }
            }
            // Tank Faktor
            RowLayout {
                Text { text: "Tank-Faktor:" }
                Slider {
                    from: 0; to: 1; stepSize: 0.01
                    value: tempTankFaktor
                    onValueChanged: tempTankFaktor = value
                }
                Text { text: (tempTankFaktor * 100).toFixed(0) + "%" }
            }
            // Garage Faktor
            RowLayout {
                Text { text: "Garage-Faktor:" }
                Slider {
                    from: 0; to: 1; stepSize: 0.01
                    value: tempGarageFaktor
                    onValueChanged: tempGarageFaktor = value
                }
                Text { text: (tempGarageFaktor * 100).toFixed(0) + "%" }
            }
            // Buttons
            RowLayout {
                Button {
                    text: "Speichern"
                    onClicked: {
                        abrechnungsBackend.setTaxiFaktor(tempTaxiFaktor);
                        abrechnungsBackend.setUberFaktor(tempUberFaktor);
                        abrechnungsBackend.setBoltFaktor(tempBoltFaktor);
                        abrechnungsBackend.setEinsteigerFaktor(tempEinsteigerFaktor);
                        abrechnungsBackend.setTankFaktor(tempTankFaktor);
                        abrechnungsBackend.setGarageFaktor(tempGarageFaktor);
                        customDealOverlayVisible = false;
                    }
                }
                Button {
                    text: "Abbrechen"
                    onClicked: customDealOverlayVisible = false;
                }
            }
        }
    }
}

