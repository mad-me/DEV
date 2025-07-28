import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import Style 1.0

Rectangle {
    id: root
    width: Screen.width
    height: Screen.height
    color: Style.background
    radius: Style.radiusNormal
    
    // Property für Navigation zur Startseite
    property var goHome: null

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
        anchors.margins: Math.max(24, parent.width * 0.05)
        spacing: Math.max(32, parent.height * 0.03)
        visible: werteGeladen

        // Summenzeile (zentriert, responsive)
        RowLayout {
            Layout.alignment: Qt.AlignHCenter
            spacing: Math.max(32, parent.width * 0.03)
            RowLayout {
                spacing: 4
                Image { source: "assets/icons/sales_gray.svg"; width: 24; height: 24; fillMode: Image.PreserveAspectFit }
                Text { text: (abrechnungsBackend ? abrechnungsBackend.headcard_umsatz.toFixed(2) : "0.00") + " €"; font.pixelSize: Math.max(18, root.width * 0.018); color: "white"; font.bold: true; font.family: ubuntuFont.name }
            }
            RowLayout {
                spacing: 4
                visible: abrechnungsBackend && abrechnungsBackend.headcard_trinkgeld > 0
                Image { source: "assets/icons/tips_gray.svg"; width: 24; height: 24; fillMode: Image.PreserveAspectFit }
                Text { text: (abrechnungsBackend ? abrechnungsBackend.headcard_trinkgeld.toFixed(2) : "0.00") + " €"; font.pixelSize: Math.max(18, root.width * 0.018); color: "white"; font.bold: true; font.family: ubuntuFont.name }
            }
            RowLayout {
                spacing: 4
                Image { source: "assets/icons/cash_gray.svg"; width: 24; height: 24; fillMode: Image.PreserveAspectFit }
                Text { text: (abrechnungsBackend ? abrechnungsBackend.headcard_cash.toFixed(2) : "0.00") + " €"; font.pixelSize: Math.max(18, root.width * 0.018); color: "white"; font.bold: true; font.family: ubuntuFont.name }
            }
            RowLayout {
                spacing: 4
                Image { source: "assets/icons/credit_card_gray.svg"; width: 24; height: 24; fillMode: Image.PreserveAspectFit }
                Text { text: (abrechnungsBackend ? abrechnungsBackend.headcard_credit_card.toFixed(2) : "0.00") + " €"; font.pixelSize: Math.max(18, root.width * 0.018); color: "white"; font.bold: true; font.family: ubuntuFont.name }
            }
            RowLayout {
                spacing: 4
                visible: abrechnungsBackend && abrechnungsBackend.headcard_garage !== undefined
                Image { source: "assets/icons/parking_gray.svg"; width: 24; height: 24; fillMode: Image.PreserveAspectFit }
                Text { text: (abrechnungsBackend ? abrechnungsBackend.headcard_garage.toFixed(2) : "0.00") + " €"; font.pixelSize: Math.max(18, root.width * 0.018); color: "white"; font.bold: true; font.family: ubuntuFont.name }
            }
            // Deal-Icon und Deal-Typ
            RowLayout {
                spacing: Math.max(15, parent.width * 0.015) // Responsive Abstand
                MouseArea {
                    id: dealIconArea
                    width: Math.max(40, parent.width * 0.04) // Responsive Größe
                    height: Math.max(40, parent.width * 0.04)
                    hoverEnabled: true
                    z: 10
                    Layout.alignment: Qt.AlignVCenter
                    cursorShape: Qt.PointingHandCursor
                    onEntered: { }
                    onExited: { }
                    onClicked: {
                        console.log("🔵 OVERLAY ÖFFNEN");
                        
                        // WICHTIG: wizardSelection vor dem Laden aktualisieren
                        wizardSelection = abrechnungsBackend.get_current_selection();
                        console.log("DEBUG: wizardSelection beim Öffnen aktualisiert:", wizardSelection);
                        
                        // Konfiguration laden VOR dem Anzeigen des Overlays
                        updateMatchedPlatforms();
                        
                        // Overlay sichtbar machen
                        dealOverlay.visible = true;
                        
                        // WICHTIG: overlayConfigApplied sofort setzen, damit Berechnungen funktionieren
                        overlayConfigApplied = true;
                        console.log("DEBUG: overlayConfigApplied auf true gesetzt beim Öffnen");
                        console.log("DEBUG: Overlay geöffnet, overlayIncome:", overlayIncome + "€");
                        console.log("DEBUG: Overlay geöffnet, overlayErgebnis:", overlayErgebnis + "€");
                        
                        // Speicher-Status nur zurücksetzen, wenn keine gespeicherte Konfiguration vorhanden ist
                        if (!overlayConfigCache || overlayConfigCache.length === 0) {
                            overlayConfigSaved = false;
                            console.log("  ↪️ overlayConfigSaved auf false gesetzt (keine Cache)");
                        } else {
                            console.log("  ✅ overlayConfigSaved bleibt unverändert (Cache vorhanden)");
                        }
                        // BottomBar sichtbar halten
                        bottomBar.visible = true;
                        bottomBarVisible = true;
                    }
                    Image {
                        anchors.centerIn: parent
                        width: Math.max(40, parent.width * 0.04) // Responsive Größe
                        height: Math.max(40, parent.width * 0.04)
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
                    text: abrechnungsBackend ? abrechnungsBackend.deal : "P"
                    font.pixelSize: Math.max(18, root.width * 0.018) // Gleiche Größe wie andere Werte
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

        // Cards für Plattformen (zentriert, responsive)
        RowLayout {
            id: cardsRow
            Layout.alignment: Qt.AlignHCenter
            Layout.fillWidth: true
            Layout.topMargin: -Math.max(32, parent.height * 0.025) // Weiter nach oben versetzen
            spacing: visibleCardCount > 2 ? Math.max(24, parent.width * 0.02) : Math.max(32, parent.width * 0.03)
            // Taxi Card
            ColumnLayout {
                spacing: Math.max(12, parent.height * 0.01)
                Layout.alignment: Qt.AlignTop
                Layout.preferredWidth: Math.max(220, parent.width * 0.22)
                Layout.fillWidth: false
                visible: card40100.zeile1 !== "-" && !isNaN(parseFloat(card40100.zeile1))
                Text { text: card40100.label; font.pixelSize: Math.max(20, root.width * 0.02); color: "#f79009"; font.bold: true; font.family: ubuntuFont.name }
                Rectangle {
                    Layout.preferredWidth: Math.max(220, parent.width * 0.22)
                    Layout.preferredHeight: Math.max(220, parent.width * 0.22)
                    color: "black"
                    radius: Style.radiusLarge
                    border.width: 0
                    ColumnLayout {
                        anchors.fill: parent
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        Layout.margins: Math.max(16, parent.width * 0.02)
                        spacing: Math.max(12, parent.height * 0.01)
                        Text { text: card40100.zeile1 + ' €'; font.pixelSize: Math.max(18, root.width * 0.018); color: Style.text; font.family: ubuntuFont.name }
                        Text { text: card40100.zeile2 + ' €'; font.pixelSize: Math.max(18, root.width * 0.018); color: Style.text; font.family: ubuntuFont.name }
                        Text { text: card40100.zeile3 + ' €'; font.pixelSize: Math.max(18, root.width * 0.018); font.bold: true; color: Style.text; font.family: ubuntuFont.name }
                    }
                }
            }
            // Uber Card
            ColumnLayout {
                spacing: Math.max(12, parent.height * 0.01)
                Layout.alignment: Qt.AlignTop
                Layout.preferredWidth: Math.max(220, parent.width * 0.22)
                Layout.fillWidth: false
                visible: cardUber.zeile1 !== "-" && parseFloat(cardUber.zeile1) > 0
                Text { text: cardUber.label === "Uber" ? "UBER" : cardUber.label; font.pixelSize: Math.max(20, root.width * 0.02); color: "#f79009"; font.bold: true; font.family: ubuntuFont.name }
                Rectangle {
                    Layout.preferredWidth: Math.max(220, parent.width * 0.22)
                    Layout.preferredHeight: Math.max(220, parent.width * 0.22)
                    color: "black"
                    radius: Style.radiusLarge
                    border.width: 0
                    ColumnLayout {
                        anchors.fill: parent
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        Layout.margins: Math.max(16, parent.width * 0.02)
                        spacing: Math.max(12, parent.height * 0.01)
                        Text { text: cardUber.zeile1 + ' €'; font.pixelSize: Math.max(18, root.width * 0.018); color: Style.text; font.family: ubuntuFont.name }
                        Text { text: cardUber.zeile2 + ' €'; font.pixelSize: Math.max(18, root.width * 0.018); color: Style.text; font.family: ubuntuFont.name }
                        Text { text: cardUber.zeile3 + ' €'; font.pixelSize: Math.max(18, root.width * 0.018); font.bold: true; color: Style.text; font.family: ubuntuFont.name }
                    }
                }
            }
            // Bolt Card
            ColumnLayout {
                spacing: Math.max(12, parent.height * 0.01)
                Layout.alignment: Qt.AlignTop
                Layout.preferredWidth: Math.max(220, parent.width * 0.22)
                Layout.fillWidth: false
                visible: cardBolt.zeile1 !== "-" && parseFloat(cardBolt.zeile1) > 0
                Text { text: cardBolt.label === "Bolt" ? "BOLT" : cardBolt.label; font.pixelSize: Math.max(20, root.width * 0.02); color: "#f79009"; font.bold: true; font.family: ubuntuFont.name }
                Rectangle {
                    Layout.preferredWidth: Math.max(220, parent.width * 0.22)
                    Layout.preferredHeight: Math.max(220, parent.width * 0.22)
                    color: "black"
                    radius: Style.radiusLarge
                    border.width: 0
                    ColumnLayout {
                        anchors.fill: parent
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        Layout.margins: Math.max(16, parent.width * 0.02)
                        spacing: Math.max(12, parent.height * 0.01)
                        Text { text: cardBolt.zeile1 + ' €'; font.pixelSize: Math.max(18, root.width * 0.018); color: Style.text; font.family: ubuntuFont.name }
                        Text { text: cardBolt.zeile2 + ' €'; font.pixelSize: Math.max(18, root.width * 0.018); color: Style.text; font.family: ubuntuFont.name }
                        Text { text: cardBolt.zeile3 + ' €'; font.pixelSize: Math.max(18, root.width * 0.018); font.bold: true; color: Style.text; font.family: ubuntuFont.name }
                    }
                }
            }
            // Input-Card als zusätzliche Card rechts
            ColumnLayout {
                spacing: Math.max(12, parent.height * 0.01)
                Layout.alignment: Qt.AlignTop
                Layout.preferredWidth: Math.max(220, parent.width * 0.22)
                Layout.fillWidth: false
                // Titel für die Eingabefelder
                Text {
                    text: "Input"
                    font.pixelSize: Math.max(20, root.width * 0.02)
                    color: "#f79009"
                    font.bold: true
                    font.family: ubuntuFont.name
                }
                // Input-Card
                Rectangle {
                    Layout.preferredWidth: Math.max(220, parent.width * 0.22)
                    Layout.preferredHeight: Math.max(220, parent.width * 0.22)
                    color: "black"
                    radius: Style.radiusLarge
                    border.width: 0
                    ColumnLayout {
                        anchors.fill: parent
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        Layout.margins: Math.max(16, parent.width * 0.02)
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
                                text: abrechnungsBackend ? abrechnungsBackend.inputGas : ""
                                onTextChanged: if (abrechnungsBackend) abrechnungsBackend.inputGas = text
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
                                text: abrechnungsBackend ? abrechnungsBackend.inputEinsteiger : ""
                                onTextChanged: {
                                    if (abrechnungsBackend) {
                                    abrechnungsBackend.inputEinsteiger = text;
                                    overlayIncome = calculateOverlayIncome();
                                    }
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
                                text: abrechnungsBackend ? abrechnungsBackend.inputExpense : ""
                                onTextChanged: {
                                    if (abrechnungsBackend && abrechnungsBackend.inputExpense !== text)
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
                // Ergebnis-Card unter der Input-Card
                Rectangle {
                    Layout.preferredWidth: Math.max(220, parent.width * 0.22)
                    Layout.preferredHeight: Math.max(110, parent.width * 0.11)
                    color: "transparent"
                    radius: Style.radiusLarge
                    border.width: 0
                    visible: werteGeladen
                    z: 10
                    Text {
                        anchors.fill: parent
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        text: (abrechnungsBackend ? abrechnungsBackend.ergebnis.toFixed(2) : "0.00") + ' €'
                        font.pixelSize: Math.max(24, root.width * 0.024)
                        font.bold: true
                        color: Style.primary
                        font.family: ubuntuFont.name
                    }
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
    
    // Property um zu tracken, ob das Overlay gespeichert wurde
    property bool overlayConfigSaved: false
    
    // Properties für ursprüngliche Werte beim Öffnen des Overlays
    property var originalMatchedSliderValues: []
    property var originalMatchedDeals: []
    property real originalPauschale: 500
    property real originalUmsatzgrenze: 1200
    
    // Properties für den letzten Speicherstand
    property var lastSavedMatchedSliderValues: []
    property var lastSavedMatchedDeals: []
    property real lastSavedPauschale: 500
    property real lastSavedUmsatzgrenze: 1200
    property bool lastSavedValuesInitialized: false
    
    // Property für BottomBar-Sichtbarkeit
    property bool bottomBarVisible: true
    
    // Property für Card-Zentrierung
    property int visibleCardCount: 0
    
    // Timer für BottomBar-Sichtbarkeit
    Timer {
        id: bottomBarTimer
        interval: 100
        repeat: false
        onTriggered: {
            bottomBar.visible = true;
            bottomBarVisible = true;
        }
    }
    
    // Funktion zur Berechnung der sichtbaren Cards
    function updateVisibleCardCount() {
        var count = 0;
        if (card40100.zeile1 !== "-" && !isNaN(parseFloat(card40100.zeile1))) count++;
        if (cardUber.zeile1 !== "-" && parseFloat(cardUber.zeile1) > 0) count++;
        if (cardBolt.zeile1 !== "-" && parseFloat(cardBolt.zeile1) > 0) count++;
        count++; // Input-Card ist immer sichtbar
        visibleCardCount = count;
    }
    

    


    // Hilfsfunktion, ob mindestens eine relevante Plattform auf P steht
    function hasPDeal() {
        var relevantPlatforms = ["Taxi", "Uber", "Bolt", "Einsteiger"];
        
        for (var i = 0; i < matchedPlatforms.length; i++) {
            if (relevantPlatforms.indexOf(matchedPlatforms[i]) !== -1) {
                var dealType = matchedDeals[i];
                if (dealType === 0) { // 0 = P-Deal
                    return true; // Mindestens eine relevante Plattform ist auf P
                }
            }
        }
        return false; // Keine relevante Plattform ist auf P
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
                        // Taxi hat "Real" statt "Total"
                        if (ergebnisse[i].details[j].label === "Real") {
                            var valueStr = ergebnisse[i].details[j].value;
                            // Entferne €-Symbol und Leerzeichen
                            valueStr = valueStr.replace("€", "").replace(" ", "").trim();
                            return parseFloat(valueStr);
                        }
                    }
                }
            }
            if (ergebnisse[i].label === "Uber" && name === "Uber") {
                if (ergebnisse[i].details) {
                    for (var j = 0; j < ergebnisse[i].details.length; j++) {
                        if (ergebnisse[i].details[j].label === "Total") {
                            var valueStr = ergebnisse[i].details[j].value;
                            valueStr = valueStr.replace("€", "").replace(" ", "").trim();
                            return parseFloat(valueStr);
                        }
                    }
                }
            }
            if (ergebnisse[i].label === "Bolt" && name === "Bolt") {
                if (ergebnisse[i].details) {
                    for (var j = 0; j < ergebnisse[i].details.length; j++) {
                        if (ergebnisse[i].details[j].label === "Echter Umsatz") {
                            var valueStr = ergebnisse[i].details[j].value;
                            valueStr = valueStr.replace("€", "").replace(" ", "").trim();
                            return parseFloat(valueStr);
                        }
                    }
                }
            }
        }
        return 0;
    }

    // Einkommen = Plattformen × Faktor (ohne Abzüge)
    property real overlayIncome: 0.0
    onOverlayIncomeChanged: {
        console.log("DEBUG: overlayIncome geändert auf:", overlayIncome + "€");
    }
    
    // Anteil = Einkommen - Tank - Garage - Expenses
    property real overlayErgebnis: 0.0
    onOverlayErgebnisChanged: {
        console.log("DEBUG: overlayErgebnis geändert auf:", overlayErgebnis + "€");
    }
    
    // Flag um zu verhindern, dass overlayIncome zu früh berechnet wird
    property bool overlayConfigApplied: false
    
    function calculateOverlayIncome() {
        // WICHTIG: Nicht berechnen, bevor die Konfiguration angewendet wurde
        if (!overlayConfigApplied) {
            console.log("DEBUG: Konfiguration noch nicht angewendet, überspringe Berechnung");
            return 0;
        }
        
        var income = 0;
        
        // Pauschale und Umsatzgrenze direkt aus dem Backend holen
        var pauschale = abrechnungsBackend.pauschale || 500;
        var umsatzgrenze = abrechnungsBackend.umsatzgrenze || 1200;
        
        // Prüfen, ob mindestens eine relevante Plattform auf P steht
        var hasAnyPDeal = false;
        var relevantPlatforms = ["Taxi", "Uber", "Bolt", "Einsteiger"];
        
        for (var i = 0; i < matchedPlatforms.length; i++) {
            if (relevantPlatforms.indexOf(matchedPlatforms[i]) !== -1) {
                var dealType = matchedDeals[i];
                if (dealType === 0) { // 0 = P-Deal
                    hasAnyPDeal = true;
                    console.log("DEBUG: P-Deal gefunden für", matchedPlatforms[i]);
                    break;
                }
            }
        }
        
        console.log("DEBUG: Mindestens eine Plattform auf P?", hasAnyPDeal);
        
        // 1. Pauschale und Grenzzuschlag (nur wenn mindestens eine Plattform auf P steht)
        if (hasAnyPDeal) {
            // Pauschale hinzufügen
            income += pauschale;
            console.log("DEBUG: Pauschale hinzugefügt:", pauschale + "€");
        
            // Grenzzuschlag prüfen
            var taxiUmsatz = getEchterUmsatzForPlattform("Taxi");
            var uberUmsatz = getEchterUmsatzForPlattform("Uber");
            var boltUmsatz = getEchterUmsatzForPlattform("Bolt");
            var summeUmsatz = taxiUmsatz + uberUmsatz + boltUmsatz;
            
            if (summeUmsatz > umsatzgrenze) {
                var bonus = (summeUmsatz - umsatzgrenze) * 0.1;
                income += bonus;
                console.log("DEBUG: Grenzzuschlag hinzugefügt:", bonus + "€");
            }
        } else {
            console.log("DEBUG: Keine P-Deals gefunden, Pauschale wird NICHT hinzugefügt");
        }
        
        // 2. Faktor-basierte Berechnung für alle Plattformen
        for (var i = 0; i < matchedPlatforms.length; i++) {
            if (["Taxi", "Uber", "Bolt", "Einsteiger"].indexOf(matchedPlatforms[i]) !== -1) {
                var umsatz = getEchterUmsatzForPlattform(matchedPlatforms[i]);
                var sliderValue = matchedSliderValues[i] !== undefined ? matchedSliderValues[i] : 0;
                var faktor = sliderValue / 100; // Slider-Wert in Faktor umwandeln (0-100 -> 0.0-1.0)
                
                // WICHTIG: Verwende Backend-Faktoren, wenn sie verfügbar sind
                if (matchedPlatforms[i] === "Taxi" && abrechnungsBackend.taxi_faktor !== undefined) {
                    faktor = abrechnungsBackend.taxi_faktor;
                    console.log("DEBUG: Verwende Backend Taxi-Faktor:", faktor);
                } else if (matchedPlatforms[i] === "Uber" && abrechnungsBackend.uber_faktor !== undefined) {
                    faktor = abrechnungsBackend.uber_faktor;
                    console.log("DEBUG: Verwende Backend Uber-Faktor:", faktor);
                } else if (matchedPlatforms[i] === "Bolt" && abrechnungsBackend.bolt_faktor !== undefined) {
                    faktor = abrechnungsBackend.bolt_faktor;
                    console.log("DEBUG: Verwende Backend Bolt-Faktor:", faktor);
                } else if (matchedPlatforms[i] === "Einsteiger" && abrechnungsBackend.einsteiger_faktor !== undefined) {
                    faktor = abrechnungsBackend.einsteiger_faktor;
                    console.log("DEBUG: Verwende Backend Einsteiger-Faktor:", faktor);
                }
                
                var plattformIncome = umsatz * faktor;
                income += plattformIncome;
                console.log("DEBUG: Plattform", matchedPlatforms[i], "Umsatz:", umsatz + "€, Slider:", sliderValue + "%, Faktor:", faktor + ", Income:", plattformIncome + "€");
            }
        }
        
        // WICHTIG: Debug-Ausgabe der Backend-Faktoren
        console.log("DEBUG: Backend-Faktoren:");
        console.log("  Taxi-Faktor:", abrechnungsBackend.taxi_faktor);
        console.log("  Uber-Faktor:", abrechnungsBackend.uber_faktor);
        console.log("  Bolt-Faktor:", abrechnungsBackend.bolt_faktor);
        console.log("  Einsteiger-Faktor:", abrechnungsBackend.einsteiger_faktor);
        console.log("  Tank-Faktor:", abrechnungsBackend.tank_faktor);
        console.log("  Garage-Faktor:", abrechnungsBackend.garage_faktor);
        
        console.log("DEBUG: Einkommen (ohne Abzüge):", income + "€");
        console.log("DEBUG: calculateOverlayIncome() gibt zurück:", income);
        return income;
    }
    
    function calculateOverlayAnteil() {
        // Anteil = Einkommen - Tank - Garage - Expenses
        var einkommen = calculateOverlayIncome();
        var abzuege = 0;
        
        // 1. Tank-Abzug
        var tankIndex = matchedPlatforms.indexOf("Tank");
        if (tankIndex !== -1) {
            var tankValue = Number(abrechnungsBackend.inputGas) || 0;
            var tankPercent = matchedSliderValues[tankIndex] || 0;
            var tankFaktor = tankPercent / 100;
            
            // WICHTIG: Verwende Backend Tank-Faktor, wenn verfügbar
            if (abrechnungsBackend.tank_faktor !== undefined) {
                tankFaktor = abrechnungsBackend.tank_faktor;
                console.log("DEBUG: Verwende Backend Tank-Faktor:", tankFaktor);
            }
            
            var tankAbzug = tankValue * tankFaktor;
            abzuege += tankAbzug;
            if (tankAbzug > 0) console.log("DEBUG: Tank Abzug:", tankValue + "€ × " + tankFaktor + " = " + tankAbzug + "€");
        }
        
        // 2. Garage-Abzug
        var garageIndex = matchedPlatforms.indexOf("Garage");
        if (garageIndex !== -1) {
            var garageValue = Number(abrechnungsBackend.headcard_garage) || 0;
            var garagePercent = matchedSliderValues[garageIndex] || 0;
            var garageFaktor = garagePercent / 100;
            
            // WICHTIG: Verwende Backend Garage-Faktor, wenn verfügbar
            if (abrechnungsBackend.garage_faktor !== undefined) {
                garageFaktor = abrechnungsBackend.garage_faktor;
                console.log("DEBUG: Verwende Backend Garage-Faktor:", garageFaktor);
            }
            
            var garageAbzug = garageValue * garageFaktor;
            abzuege += garageAbzug;
            if (garageAbzug > 0) console.log("DEBUG: Garage Abzug:", garageValue + "€ × " + garageFaktor + " = " + garageAbzug + "€");
        }
        
        // 3. Expenses-Abzug (falls verfügbar)
        var expenses = 0;
        if (abrechnungsBackend && abrechnungsBackend.expenses) {
            expenses = abrechnungsBackend.expenses || 0;
            if (expenses > 0) {
                abzuege += expenses;
                console.log("DEBUG: Expenses Abzug:", expenses + "€");
            }
        }
        
        // Finales Ergebnis = Einkommen - Abzüge
        var anteil = einkommen - abzuege;
        if (abzuege > 0) console.log("DEBUG: Gesamtabzüge:", abzuege + "€");
        console.log("DEBUG: Anteil (Einkommen - Abzüge):", anteil + "€");
        return anteil;
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
                                    
                                    // Automatische Slider-Anpassung basierend auf Deal-Typ
                                    var sliderArr = matchedSliderValues.slice();
                                    
                                    if (next === 0) {
                                        // P-Deal: Slider auf 0 setzen (kein Anteil)
                                        sliderArr[index] = 0;
                                    } else if (next === 1) {
                                        // %-Deal: Slider auf 50 setzen (50% Anteil)
                                        sliderArr[index] = 50;
                                    } else if (next === 2) {
                                        // C-Deal: Slider auf aktuellen Wert belassen oder 0 falls undefined
                                        if (sliderArr[index] === undefined) {
                                            sliderArr[index] = 0;
                                        }
                                    }
                                    matchedSliderValues = sliderArr;
                                    
                                    // Wenn Taxi geändert wird, Einsteiger auch ändern
                                    if (matchedPlatforms[index] === "Taxi") {
                                        var einsteigerIndex = matchedPlatforms.indexOf("Einsteiger");
                                        if (einsteigerIndex !== -1) {
                                            arr[einsteigerIndex] = next;
                                            matchedDeals = arr;
                                            
                                            // Gleiche Slider-Logik für Einsteiger
                                            if (next === 0) {
                                                sliderArr[einsteigerIndex] = 0;
                                            } else if (next === 1) {
                                                sliderArr[einsteigerIndex] = 50;
                                            } else if (next === 2) {
                                                if (sliderArr[einsteigerIndex] === undefined) {
                                                    sliderArr[einsteigerIndex] = 0;
                                                }
                                            }
                                            matchedSliderValues = sliderArr;
                                        }
                                    }
                                    
                                    console.log("DEBUG: Deal geändert für", matchedPlatforms[index], "von", current, "zu", next, "Slider:", sliderArr[index]);
                                    
                                    // WICHTIG: Letzten Speicherstand aktualisieren, wenn sich Deal-Typen ändern
                                    saveLastSavedValues();
                                    console.log("DEBUG: Letzten Speicherstand aktualisiert nach Deal-Änderung");
                                    
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
                                Component.onCompleted: {
                                    console.log("DEBUG: Deal-Box für", matchedPlatforms[index], "gesetzt auf:", dealOptions[matchedDeals[index] !== undefined ? matchedDeals[index] : 0]);
                                }
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
                                        // Pauschale an Backend senden
                                        if (abrechnungsBackend && abrechnungsBackend.setPauschale) {
                                            abrechnungsBackend.setPauschale(value);
                                        }
                                        // WICHTIG: overlayConfigApplied sicherstellen
                                        overlayConfigApplied = true;
                                        // WICHTIG: Letzten Speicherstand aktualisieren bei Slider-Änderungen
                                        saveLastSavedValues();
                                        console.log("DEBUG: Letzten Speicherstand aktualisiert nach Pauschale-Slider-Änderung");
                                        // Einkommen sofort neu berechnen
                                        forceOverlayIncomeUpdate();
                                        // WICHTIG: Explizite Aktualisierung der Anzeige
                                        overlayIncome = calculateOverlayIncome();
                                        overlayErgebnis = calculateOverlayAnteil();
                                        console.log("DEBUG: Anzeige explizit aktualisiert nach Pauschale-Slider");
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
                                        // Umsatzgrenze an Backend senden
                                        if (abrechnungsBackend && abrechnungsBackend.setUmsatzgrenze) {
                                            abrechnungsBackend.setUmsatzgrenze(value);
                                        }
                                        // WICHTIG: overlayConfigApplied sicherstellen
                                        overlayConfigApplied = true;
                                        // WICHTIG: Letzten Speicherstand aktualisieren bei Slider-Änderungen
                                        saveLastSavedValues();
                                        console.log("DEBUG: Letzten Speicherstand aktualisiert nach Umsatzgrenze-Slider-Änderung");
                                        // Einkommen sofort neu berechnen
                                        forceOverlayIncomeUpdate();
                                        // WICHTIG: Explizite Aktualisierung der Anzeige
                                        overlayIncome = calculateOverlayIncome();
                                        overlayErgebnis = calculateOverlayAnteil();
                                        console.log("DEBUG: Anzeige explizit aktualisiert nach Umsatzgrenze-Slider");
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
                                        console.log("DEBUG: Slider bewegt für", matchedPlatforms[index], "auf", value);
                                        // WICHTIG: overlayConfigApplied sicherstellen
                                        overlayConfigApplied = true;
                                        // WICHTIG: Letzten Speicherstand aktualisieren bei Slider-Änderungen
                                        saveLastSavedValues();
                                        console.log("DEBUG: Letzten Speicherstand aktualisiert nach Slider-Änderung");
                                        // Einkommen sofort neu berechnen
                                        forceOverlayIncomeUpdate();
                                        // WICHTIG: Explizite Aktualisierung der Anzeige
                                        overlayIncome = calculateOverlayIncome();
                                        overlayErgebnis = calculateOverlayAnteil();
                                        console.log("DEBUG: Anzeige explizit aktualisiert nach Slider-Bewegung");
                                    }
                                }
                                onValueChanged: {
                                    // Automatische Slider-Anpassung basierend auf Deal-Typ
                                    var currentDeal = matchedDeals[index];
                                    var currentSlider = matchedSliderValues[index];
                                    
                                    if (currentDeal === 1 && (currentSlider === undefined || currentSlider !== 50)) {
                                        // %-Deal: Immer 50% erzwingen
                                        var arr = matchedSliderValues.slice();
                                        arr[index] = 50;
                                        matchedSliderValues = arr;
                                        console.log("DEBUG: %-Deal erkannt, Slider auf 50 gesetzt für", matchedPlatforms[index]);
                                        // Einkommen sofort neu berechnen
                                        forceOverlayIncomeUpdate();
                                    } else if (currentDeal === 0 && currentSlider !== 0) {
                                        // P-Deal: Immer 0% erzwingen
                                        var arr = matchedSliderValues.slice();
                                        arr[index] = 0;
                                        matchedSliderValues = arr;
                                        console.log("DEBUG: P-Deal erkannt, Slider auf 0 gesetzt für", matchedPlatforms[index]);
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
                                Component.onCompleted: {
                                    console.log("DEBUG: Slider-Text für", matchedPlatforms[index], "gesetzt auf:", (matchedDeals[index] === 1 ? 50 : Math.round(matchedSliderValues[index] !== undefined ? matchedSliderValues[index] : 0)) + " %");
                                }
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
                            Component.onCompleted: {
                                console.log("DEBUG: Einkommen-Text erstellt, overlayIncome:", overlayIncome);
                            }
                            onTextChanged: {
                                console.log("DEBUG: Einkommen-Text geändert auf:", text);
                            }

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
                                console.log("💾 SPEICHERN-BUTTON GEKLICKT");
                                
                                // 1. Aktuelle Konfiguration im Cache speichern
                                saveOverlayConfiguration();
                                console.log("  ✅ Konfiguration im Cache gespeichert");
                                
                                // 2. Konfiguration als neue Standard-Konfiguration annehmen
                                updateOriginalValues();
                                console.log("  ✅ Konfiguration als neue Standard-Konfiguration angenommen");
                                
                                // 3. Letzten Speicherstand mit aktuellen Werten überschreiben
                                saveLastSavedValues();
                                console.log("  ✅ Letzten Speicherstand aktualisiert");
                                
                                // 4. Einkommen (ohne Abzüge) als Income speichern
                                console.log("QML: overlayConfigCache vor Backend-Call:", JSON.stringify(overlayConfigCache));
                                abrechnungsBackend.speichereUmsatzCustom(overlayIncome, JSON.stringify(overlayConfigCache));
                                
                                // 5. Konfiguration in Datenbank finalisieren (nur für Custom-Deals)
                                if (abrechnungsBackend.deal === "C") {
                                    console.log("  🔍 Versuche Konfiguration in Datenbank zu speichern...");
                                    console.log("  wizardSelection:", wizardSelection);
                                    console.log("  fahrer_id:", wizardSelection ? wizardSelection.fahrer_id : "undefined");
                                    console.log("  fahrer:", wizardSelection ? wizardSelection.fahrer : "undefined");
                                    
                                    if (wizardSelection && wizardSelection.fahrer_id) {
                                        saveOverlayConfigToDatabase();
                                        console.log("  ✅ Konfiguration in Datenbank finalisiert");
                                    } else {
                                        console.log("  ⚠️ wizardSelection nicht verfügbar, überspringe Datenbank-Speicherung");
                                    }
                                }
                                
                                // 6. Markiere als gespeichert
                                overlayConfigSaved = true;
                                console.log("  ✅ overlayConfigSaved auf true gesetzt");
                                console.log("  ✅ Werte gespeichert, Overlay wird geschlossen");
                                
                                // WICHTIG: overlayAlreadyOpened zurücksetzen beim Schließen
                                overlayAlreadyOpened = false;
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
                        onClicked: {
                            console.log("🔴 SCHLIEßEN-BUTTON GEKLICKT");
                            console.log("  overlayConfigSaved:", overlayConfigSaved);
                            console.log("  overlayConfigCache:", JSON.stringify(overlayConfigCache));
                            console.log("  lastSavedValuesInitialized:", lastSavedValuesInitialized);
                            console.log("  lastSavedMatchedSliderValues.length:", lastSavedMatchedSliderValues.length);
                            
                            // IMMER auf den Originalzustand zurücksetzen beim Schließen
                            console.log("  ↪️ Zurücksetzen auf Originalzustand");
                            restoreOriginalValues();
                            // WICHTIG: overlayAlreadyOpened zurücksetzen beim Schließen
                            overlayAlreadyOpened = false;
                            dealOverlay.visible = false;
                        }
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
                var details = results[i].details || [];
                var real_umsatz = 0;
                var total = 0;
                var bargeld = 0;
                var anteil = 0;

                // Werte aus den Details extrahieren
                for (var j = 0; j < details.length; j++) {
                    if (details[j].label === "Real") {
                        real_umsatz = parseFloat(String(details[j].value).replace(/[^\d.,-]/g, "").replace(',', '.')) || 0;
                    }
                    if (details[j].label === "Total") {
                        total = parseFloat(String(details[j].value).replace(/[^\d.,-]/g, "").replace(',', '.')) || 0;
                    }
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
                        zeile1: real_umsatz.toFixed(2),  // Erste Zeile zeigt jetzt echten Umsatz
                        zeile2: bargeld.toFixed(2),
                        zeile3: credit_card.toFixed(2)
                    };
                } else {
                    return {
                        label: "Taxi",
                        zeile1: real_umsatz.toFixed(2),  // Erste Zeile zeigt jetzt echten Umsatz
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
            // BottomBar immer sichtbar machen wenn Ergebnisse geladen werden
            bottomBar.visible = true;
            bottomBarVisible = true;
            // Card-Anzahl aktualisieren für bessere Zentrierung
            updateVisibleCardCount();
        }
        
        function onDealChanged() {
            // Ergebnis automatisch neu berechnen wenn sich der Deal-Typ ändert
            console.log("DEBUG: Deal geändert, berechne Ergebnis neu");
            if (abrechnungsBackend && abrechnungsBackend.update_ergebnis) {
                abrechnungsBackend.update_ergebnis();
            }
        }
        
        function onInputGasChanged() {
            // Ergebnis automatisch neu berechnen wenn sich Tank-Wert ändert
            console.log("DEBUG: Tank-Wert geändert, berechne Ergebnis neu");
            forceOverlayIncomeUpdate();
            if (abrechnungsBackend && abrechnungsBackend.update_ergebnis) {
                abrechnungsBackend.update_ergebnis();
            }
        }
        
        function onHeadcardGarageChanged() {
            // Ergebnis automatisch neu berechnen wenn sich Garage-Wert ändert
            console.log("DEBUG: Garage-Wert geändert, berechne Ergebnis neu");
            forceOverlayIncomeUpdate();
            if (abrechnungsBackend && abrechnungsBackend.update_ergebnis) {
                abrechnungsBackend.update_ergebnis();
            }
        }
        
        function onInputEinsteigerChanged() {
            // Ergebnis automatisch neu berechnen wenn sich Einsteiger-Wert ändert
            console.log("DEBUG: Einsteiger-Wert geändert, berechne Ergebnis neu");
            forceOverlayIncomeUpdate();
            if (abrechnungsBackend && abrechnungsBackend.update_ergebnis) {
                abrechnungsBackend.update_ergebnis();
            }
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
        
        // WICHTIG: wizardSelection korrekt setzen
        wizardSelection = abrechnungsBackend.get_current_selection();
        console.log("DEBUG: wizardSelection in Component.onCompleted gesetzt:", wizardSelection);
        
        // Stelle sicher, dass BottomBar sichtbar ist
        bottomBar.visible = true;
        bottomBarVisible = true;
        // Timer starten für zusätzliche Sicherheit
        bottomBarTimer.start();
        bottomBarVisible = true;

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
        
        // Deal-Typ setzen, wenn gemischte Konfiguration
        if (!isPercent && !isPauschale) {
            console.log("DEBUG: Deal-Typ auf 'C' gesetzt (gemischte Konfiguration)");
            abrechnungsBackend.setDeal("C");
        }
        
        // 2. Konfiguration als JSON im Cache speichern
        var config = getOverlayConfig();
        overlayConfigCache = config;
        console.log("DEBUG: Konfiguration im Cache gespeichert:", JSON.stringify(overlayConfigCache));
        
        // 3. Backend-Konfiguration anwenden
        applyOverlayConfigurationToBackend();
        
        // 4. Speicher-Status setzen
        overlayConfigSaved = true;
        console.log("DEBUG: overlayConfigSaved auf true gesetzt");
    }
    
    function saveOverlayConfigToDatabase() {
        if (!overlayConfigCache || overlayConfigCache.length === 0) {
            return;
        }
        
        if (!wizardSelection || !wizardSelection.fahrer_id) {
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
            
            console.log("DEBUG: Overlay-Konfiguration erfolgreich in Datenbank gespeichert");
            console.log("DEBUG: Cache geleert und Speicher-Status zurückgesetzt");
            
            // Cache leeren nach erfolgreichem Speichern
            overlayConfigCache = [];
            // Speicher-Status zurücksetzen, da Cache geleert wurde
            overlayConfigSaved = false;
        } catch (e) {
            console.error("Fehler beim Speichern der Overlay-Konfiguration in Datenbank:", e);
        }
    }
    
    function loadOverlayConfiguration() {
        // loadOverlayConfiguration() gestartet
        console.log("DEBUG: loadOverlayConfiguration() gestartet");
        console.log("DEBUG: overlayAlreadyOpened:", overlayAlreadyOpened);
        console.log("DEBUG: wizardSelection:", wizardSelection);
        
        // Lade gespeicherte Konfiguration immer beim Öffnen des Overlays
        
        // Prüfe Deal-Typ
        var dealType = abrechnungsBackend.deal;
        console.log("DEBUG: Aktueller Deal-Typ:", dealType);
        console.log("DEBUG: abrechnungsBackend:", abrechnungsBackend);
        
        // WICHTIG: Immer versuchen, gespeicherte Konfiguration zu laden, unabhängig vom Deal-Typ
        if (!wizardSelection || !wizardSelection.fahrer_id) {
            console.log("DEBUG: Kein wizardSelection oder fahrer_id verfügbar");
            // WICHTIG: Auch hier Flag setzen, damit Einkommen berechnet wird
            overlayConfigApplied = true;
            console.log("DEBUG: overlayConfigApplied auf true gesetzt (kein wizardSelection)");
            return;
        }
        
        var driverId = wizardSelection.fahrer_id;
        console.log("DEBUG: Lade Konfiguration für Driver ID:", driverId);
        try {
            var config = abrechnungsBackend.ladeOverlayKonfiguration(driverId);
            console.log("DEBUG: Backend-Konfiguration geladen:", JSON.stringify(config));
            if (config && config.length > 0) {
                console.log("DEBUG: Konfiguration gefunden, wende an...");
                
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
                
                console.log("DEBUG: Extrahierte Werte:");
                console.log("  Taxi: Deal=", taxiDeal, "Slider=", taxiSlider);
                console.log("  Uber: Deal=", uberDeal, "Slider=", uberSlider);
                console.log("  Bolt: Deal=", boltDeal, "Slider=", boltSlider);
                console.log("  Einsteiger: Deal=", einsteigerDeal, "Slider=", einsteigerSlider);
                console.log("  Garage: Slider=", garageSlider);
                console.log("  Tank: Slider=", tankSlider);
                
                // Werte auf die entsprechenden Indizes anwenden
                var taxiIndex = matchedPlatforms.indexOf("Taxi");
                var uberIndex = matchedPlatforms.indexOf("Uber");
                var boltIndex = matchedPlatforms.indexOf("Bolt");
                var einsteigerIndex = matchedPlatforms.indexOf("Einsteiger");
                var garageIndex = matchedPlatforms.indexOf("Garage");
                var tankIndex = matchedPlatforms.indexOf("Tank");
                
                console.log("DEBUG: Gefundene Indizes:");
                console.log("  Taxi Index:", taxiIndex);
                console.log("  Uber Index:", uberIndex);
                console.log("  Bolt Index:", boltIndex);
                console.log("  Einsteiger Index:", einsteigerIndex);
                console.log("  Garage Index:", garageIndex);
                console.log("  Tank Index:", tankIndex);
                
                if (taxiIndex !== -1) {
                    newDeals[taxiIndex] = taxiDeal;
                    newSliders[taxiIndex] = taxiSlider;
                    console.log("DEBUG: Taxi-Werte angewendet");
                }
                
                if (uberIndex !== -1) {
                    newDeals[uberIndex] = uberDeal;
                    newSliders[uberIndex] = uberSlider;
                    console.log("DEBUG: Uber-Werte angewendet");
                }
                
                if (boltIndex !== -1) {
                    newDeals[boltIndex] = boltDeal;
                    newSliders[boltIndex] = boltSlider;
                    console.log("DEBUG: Bolt-Werte angewendet");
                }
                
                if (einsteigerIndex !== -1) {
                    newDeals[einsteigerIndex] = einsteigerDeal;
                    newSliders[einsteigerIndex] = einsteigerSlider;
                    console.log("DEBUG: Einsteiger-Werte angewendet");
                }
                
                if (garageIndex !== -1) {
                    newSliders[garageIndex] = garageSlider;
                    console.log("DEBUG: Garage-Werte angewendet");
                }
                
                if (tankIndex !== -1) {
                    newSliders[tankIndex] = tankSlider;
                    console.log("DEBUG: Tank-Werte angewendet");
                }
                
                console.log("DEBUG: Arrays vor Update:");
                console.log("  matchedDeals:", JSON.stringify(matchedDeals));
                console.log("  matchedSliderValues:", JSON.stringify(matchedSliderValues));
                
                // Arrays aktualisieren
                matchedDeals = newDeals;
                matchedSliderValues = newSliders;
                
                console.log("DEBUG: Arrays nach Update:");
                console.log("  matchedDeals:", JSON.stringify(matchedDeals));
                console.log("  matchedSliderValues:", JSON.stringify(matchedSliderValues));
                
                // WICHTIG: Backend-Faktoren mit geladenen Werten setzen
                applyOverlayConfigurationToBackend();
                console.log("DEBUG: Backend-Faktoren mit geladenen Werten gesetzt");
                
                // WICHTIG: Kurze Verzögerung, damit die Backend-Faktoren gesetzt werden können
                Qt.callLater(function() {
                    // Einkommen neu berechnen
                    forceOverlayIncomeUpdate();
                    console.log("DEBUG: Einkommen neu berechnet");
                });
                
                // WICHTIG: Cache mit geladener Konfiguration aktualisieren
                var loadedConfig = getOverlayConfig();
                overlayConfigCache = loadedConfig;
                console.log("DEBUG: Cache mit geladener Konfiguration aktualisiert:", JSON.stringify(overlayConfigCache));
                
                return; // Beende hier, da Konfiguration erfolgreich geladen wurde
            } else {
                console.log("DEBUG: Keine Konfiguration gefunden");
            }
        } catch (e) {
            console.log("DEBUG: Fehler beim Laden der Konfiguration:", e);
        }
        
        // Wenn Deal-Typ "C" ist, lade custom_deal_config aus der Datenbank
        if (dealType === "C") {
            console.log("DEBUG: Custom-Deal erkannt, lade custom_deal_config aus Datenbank...");
            console.log("DEBUG: wizardSelection:", wizardSelection);
            
            if (!wizardSelection || !wizardSelection.fahrer) {
                console.log("DEBUG: Kein wizardSelection oder fahrer verfügbar");
                console.log("DEBUG: Verwende Cache-Konfiguration falls verfügbar...");
                
                // Versuche Cache-Konfiguration zu verwenden
                if (overlayConfigCache && overlayConfigCache.length > 0) {
                    console.log("DEBUG: Verwende Cache-Konfiguration:", JSON.stringify(overlayConfigCache));
                    applyCustomDealConfig(overlayConfigCache);
                    forceOverlayIncomeUpdate();
                    return;
                }
                return;
            }
            
            var fahrername = wizardSelection.fahrer;
            console.log("DEBUG: Lade custom_deal_config für Fahrer:", fahrername);
            
            try {
                var customConfig = abrechnungsBackend.ladeCustomDealConfig(fahrername);
                console.log("DEBUG: Custom-Deal-Konfiguration aus Datenbank geladen:", JSON.stringify(customConfig));
                
                if (customConfig && customConfig.length > 0) {
                    console.log("DEBUG: Custom-Deal-Konfiguration aus Datenbank gefunden, wende an...");
                    applyCustomDealConfig(customConfig);
                    // WICHTIG: Force update nach dem Anwenden der Custom-Deal-Konfiguration
                    forceOverlayIncomeUpdate();
                    return;
                } else {
                    console.log("DEBUG: Keine Custom-Deal-Konfiguration in Datenbank gefunden");
                    console.log("DEBUG: Verwende Cache-Konfiguration falls verfügbar...");
                    
                    // Versuche Cache-Konfiguration zu verwenden
                    if (overlayConfigCache && overlayConfigCache.length > 0) {
                        console.log("DEBUG: Verwende Cache-Konfiguration:", JSON.stringify(overlayConfigCache));
                        applyCustomDealConfig(overlayConfigCache);
                        forceOverlayIncomeUpdate();
                        return;
                    }
                }
            } catch (error) {
                console.log("DEBUG: Fehler beim Laden der Custom-Deal-Konfiguration aus Datenbank:", error);
                console.log("DEBUG: Verwende Cache-Konfiguration falls verfügbar...");
                
                // Versuche Cache-Konfiguration zu verwenden
                if (overlayConfigCache && overlayConfigCache.length > 0) {
                    console.log("DEBUG: Verwende Cache-Konfiguration:", JSON.stringify(overlayConfigCache));
                    applyCustomDealConfig(overlayConfigCache);
                    forceOverlayIncomeUpdate();
                    return;
                }
            }
        }
        

        console.log("=== DEBUG: loadOverlayConfiguration() beendet ===");
        
        // WICHTIG: overlayConfigApplied IMMER am Ende setzen
        overlayConfigApplied = true;
        console.log("DEBUG: overlayConfigApplied auf true gesetzt (am Ende)");
        
        // WICHTIG: Properties explizit aktualisieren
        overlayIncome = calculateOverlayIncome();
        overlayErgebnis = calculateOverlayAnteil();
        console.log("DEBUG: Properties explizit aktualisiert (am Ende):");
        console.log("  overlayIncome:", overlayIncome + "€");
        console.log("  overlayErgebnis:", overlayErgebnis + "€");
    }
    
    function forceOverlayIncomeUpdate() {
        // Force update der overlayIncome und overlayErgebnis Properties
        var newIncome = calculateOverlayIncome();
        var newErgebnis = calculateOverlayAnteil();
        
        console.log("DEBUG: forceOverlayIncomeUpdate() - Neue Werte:");
        console.log("  overlayIncome:", newIncome + "€");
        console.log("  overlayErgebnis:", newErgebnis + "€");
        
        // WICHTIG: Properties explizit aktualisieren
        overlayIncome = newIncome;
        overlayErgebnis = newErgebnis;
        
        console.log("DEBUG: Properties aktualisiert:");
        console.log("  overlayIncome Property:", overlayIncome + "€");
        console.log("  overlayErgebnis Property:", overlayErgebnis + "€");
        
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
            return false;
        }
        
        // Prüfe, ob Einkommen positiv ist
        if (overlayIncome <= 0) {
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

    }

    // Funktion zum Speichern der ursprünglichen Werte
    function saveOriginalValues() {
        originalMatchedSliderValues = matchedSliderValues.slice();
        originalMatchedDeals = matchedDeals.slice();
        originalPauschale = abrechnungsBackend.pauschale || 500;
        originalUmsatzgrenze = abrechnungsBackend.umsatzgrenze || 1200;
        console.log("DEBUG: Ursprüngliche Werte gespeichert");
        console.log("  Original Slider:", JSON.stringify(originalMatchedSliderValues));
        console.log("  Original Deals:", JSON.stringify(originalMatchedDeals));
        console.log("  Original Pauschale:", originalPauschale);
        console.log("  Original Umsatzgrenze:", originalUmsatzgrenze);
    }
    
    // Funktion zum Wiederherstellen der ursprünglichen Werte
    function restoreOriginalValues() {
        matchedSliderValues = originalMatchedSliderValues.slice();
        matchedDeals = originalMatchedDeals.slice();
        
        // Backend-Werte wiederherstellen
        if (abrechnungsBackend && abrechnungsBackend.setPauschale) {
            abrechnungsBackend.setPauschale(originalPauschale);
        }
        if (abrechnungsBackend && abrechnungsBackend.setUmsatzgrenze) {
            abrechnungsBackend.setUmsatzgrenze(originalUmsatzgrenze);
        }
        
        // Backend-Faktoren auf ursprüngliche Werte zurücksetzen
        applyOverlayConfigurationToBackend();
        
        // Ergebnis neu berechnen (wird bereits in applyOverlayConfigurationToBackend gemacht)
        
        console.log("DEBUG: Ursprüngliche Werte wiederhergestellt");
        console.log("  Restored Slider:", JSON.stringify(matchedSliderValues));
        console.log("  Restored Deals:", JSON.stringify(matchedDeals));
        console.log("  Restored Pauschale:", originalPauschale);
        console.log("  Restored Umsatzgrenze:", originalUmsatzgrenze);
    }
    
    // Funktion zum Überschreiben der Original-Werte mit aktuellen Werten
    function updateOriginalValues() {
        originalMatchedSliderValues = matchedSliderValues.slice();
        originalMatchedDeals = matchedDeals.slice();
        originalPauschale = abrechnungsBackend.pauschale || 500;
        originalUmsatzgrenze = abrechnungsBackend.umsatzgrenze || 1200;
        
        console.log("DEBUG: Original-Werte mit aktuellen Werten überschrieben");
        console.log("  Updated Original Slider:", JSON.stringify(originalMatchedSliderValues));
        console.log("  Updated Original Deals:", JSON.stringify(originalMatchedDeals));
        console.log("  Updated Original Pauschale:", originalPauschale);
        console.log("  Updated Original Umsatzgrenze:", originalUmsatzgrenze);
    }
    
    // Funktion zum Speichern des letzten Speicherstands
    function saveLastSavedValues() {
        lastSavedMatchedSliderValues = matchedSliderValues.slice();
        lastSavedMatchedDeals = matchedDeals.slice();
        lastSavedPauschale = abrechnungsBackend.pauschale || 500;
        lastSavedUmsatzgrenze = abrechnungsBackend.umsatzgrenze || 1200;
        lastSavedValuesInitialized = true;
        
        console.log("DEBUG: Letzter Speicherstand gespeichert");
        console.log("  Last Saved Slider:", JSON.stringify(lastSavedMatchedSliderValues));
        console.log("  Last Saved Deals:", JSON.stringify(lastSavedMatchedDeals));
        console.log("  Last Saved Pauschale:", lastSavedPauschale);
        console.log("  Last Saved Umsatzgrenze:", lastSavedUmsatzgrenze);
        console.log("  Last Saved Values Initialized:", lastSavedValuesInitialized);
    }
    
    // Funktion zum Wiederherstellen des letzten Speicherstands
    function restoreLastSavedValues() {
        // WICHTIG: Prüfen, ob letzte Werte initialisiert sind
        if (!lastSavedValuesInitialized || lastSavedMatchedSliderValues.length === 0) {
            console.log("DEBUG: Letzte Werte nicht initialisiert, verwende Original-Werte");
            // Verwende Original-Werte als Fallback
            if (originalMatchedSliderValues.length > 0) {
                matchedSliderValues = originalMatchedSliderValues.slice();
                matchedDeals = originalMatchedDeals.slice();
                console.log("DEBUG: Original-Werte als Fallback verwendet");
            } else {
                console.log("WARNUNG: Keine Original-Werte verfügbar, behalte aktuelle Werte");
                // Behalte aktuelle Werte bei, da keine besseren verfügbar sind
            }
        } else {
            console.log("DEBUG: Verwende gespeicherte letzte Werte");
            matchedSliderValues = lastSavedMatchedSliderValues.slice();
            matchedDeals = lastSavedMatchedDeals.slice();
        }
        
        // Backend-Werte wiederherstellen mit Validierung
        if (abrechnungsBackend && abrechnungsBackend.setPauschale) {
            try {
                abrechnungsBackend.setPauschale(lastSavedPauschale);
                console.log("DEBUG: Pauschale erfolgreich auf", lastSavedPauschale, "gesetzt");
            } catch (e) {
                console.log("WARNUNG: Pauschale konnte nicht gesetzt werden:", e);
            }
        }
        if (abrechnungsBackend && abrechnungsBackend.setUmsatzgrenze) {
            try {
                abrechnungsBackend.setUmsatzgrenze(lastSavedUmsatzgrenze);
                console.log("DEBUG: Umsatzgrenze erfolgreich auf", lastSavedUmsatzgrenze, "gesetzt");
            } catch (e) {
                console.log("WARNUNG: Umsatzgrenze konnte nicht gesetzt werden:", e);
            }
        }
        
        // Backend-Faktoren auf letzten Speicherstand zurücksetzen
        applyOverlayConfigurationToBackend();
        
        // WICHTIG: overlayConfigApplied sicherstellen, damit Berechnungen funktionieren
        overlayConfigApplied = true;
        console.log("DEBUG: overlayConfigApplied auf true gesetzt nach Wiederherstellung");
        
        // WICHTIG: Einkommen nach Wiederherstellung neu berechnen
        forceOverlayIncomeUpdate();
        
        console.log("DEBUG: Letzter Speicherstand wiederhergestellt");
        console.log("  Restored Slider:", JSON.stringify(matchedSliderValues));
        console.log("  Restored Deals:", JSON.stringify(matchedDeals));
        console.log("  Restored Pauschale:", lastSavedPauschale);
        console.log("  Restored Umsatzgrenze:", lastSavedUmsatzgrenze);
    }
    
            // Beim Öffnen des Overlays Plattformen extrahieren, Deals und Slider initialisieren
        function updateMatchedPlatforms() {
            // updateMatchedPlatforms() gestartet
            console.log("overlayAlreadyOpened:", overlayAlreadyOpened);
            console.log("overlayConfigCache:", JSON.stringify(overlayConfigCache));
            
            // WICHTIG: wizardSelection beim Öffnen des Overlays aktualisieren
            wizardSelection = abrechnungsBackend.get_current_selection();
            console.log("DEBUG: wizardSelection in updateMatchedPlatforms gesetzt:", wizardSelection);
        
            // Erstelle neue Konfiguration basierend auf aktuellen Backend-Werten
            console.log("DEBUG: Erstelle neue Konfiguration");
            var results = abrechnungsBackend.ergebnisse;
            var platforms = [];
            var deals = [];
            var sliders = [];
            var globalDeal = abrechnungsBackend.deal;
            
            // Debug-Info reduziert
            
            // Pauschale und Umsatzgrenze immer ganz oben, Werte immer aus Backend-Properties
            platforms.push("Pauschale");
            deals.push(null); // keine Click-Box
            var pauschaleValue = abrechnungsBackend.deal === "%" ? 0 : Number(abrechnungsBackend.pauschale);
            sliders.push(pauschaleValue);
            // Pauschale gesetzt
            
            platforms.push("Umsatzgrenze");
            deals.push(null); // keine Click-Box
            var umsatzgrenzeValue = abrechnungsBackend.deal === "%" ? 0 : Number(abrechnungsBackend.umsatzgrenze);
            sliders.push(umsatzgrenzeValue);
            // Umsatzgrenze gesetzt
            
            // Plattformen extrahieren
            for (var i = 0; i < results.length; i++) {
                var entry = results[i];
                if (entry.type === "summary" && entry.details && entry.details.length > 0) {
                    var plattform = entry.label;
                    console.log("DEBUG: Gefundene Plattform:", plattform);
                    if (["Uber", "Bolt", "40100", "31300", "Taxi"].indexOf(plattform) !== -1) {
                        if (plattform === "40100" || plattform === "31300" || plattform === "Taxi") {
                            // Prüfen, ob "Taxi" schon in der Liste ist, um Duplikate zu vermeiden
                            if (platforms.indexOf("Taxi") === -1) {
                                platforms.push("Taxi");
                                            // Verwende Backend-Faktoren anstatt Standard-Werte
            var taxiFaktor = abrechnungsBackend.taxi_faktor || 0.0;
            var taxiSlider = taxiFaktor * 100;
            console.log("DEBUG: Taxi-Faktor aus Backend:", taxiFaktor, "Slider:", taxiSlider);
            // Deal-Typ basiert auf Backend-Deal, nicht auf globalDeal
            var taxiDeal = abrechnungsBackend.deal === "%" ? 1 : (abrechnungsBackend.deal === "P" ? 0 : 2);
            deals.push(taxiDeal);
            sliders.push(taxiSlider);
            // Taxi hinzugefügt
                            }
                        } else {
                            platforms.push(plattform);
                            // Verwende Backend-Faktoren anstatt Standard-Werte
                            var platformFaktor = 0.0;
                            if (plattform === "Uber") {
                                platformFaktor = abrechnungsBackend.uber_faktor || 0.0;
                            } else if (plattform === "Bolt") {
                                platformFaktor = abrechnungsBackend.bolt_faktor || 0.0;
                            }
                            var platformSlider = platformFaktor * 100;
                            console.log("DEBUG:", plattform, "-Faktor aus Backend:", platformFaktor, "Slider:", platformSlider);
                            // Deal-Typ basiert auf Backend-Deal, nicht auf globalDeal
                            var platformDeal = abrechnungsBackend.deal === "%" ? 1 : (abrechnungsBackend.deal === "P" ? 0 : 2);
                            deals.push(platformDeal);
                            sliders.push(platformSlider);
                            // Plattform hinzugefügt
                        }
                    }
                }
            }
            // Einsteiger-Zeile immer nach den Plattformen einfügen
            platforms.push("Einsteiger");
            // Verwende Backend-Faktor anstatt Standard-Wert
            var einsteigerFaktor = abrechnungsBackend.einsteiger_faktor || 0.0;
            var einsteigerSlider = einsteigerFaktor * 100;
            console.log("DEBUG: Einsteiger-Faktor aus Backend:", einsteigerFaktor, "Slider:", einsteigerSlider);
            // Deal-Typ basiert auf Backend-Deal, nicht auf globalDeal
            var einsteigerDeal = abrechnungsBackend.deal === "%" ? 1 : (abrechnungsBackend.deal === "P" ? 0 : 2);
            deals.push(einsteigerDeal);
            sliders.push(einsteigerSlider);
            // Einsteiger hinzugefügt
            
            // Garage-Zeile, wenn Wert vorhanden
            if (abrechnungsBackend.headcard_garage > 0) {
                platforms.push("Garage");
                deals.push(2); // Immer C
                // Verwende Backend-Faktor anstatt Standard-Wert
                var garageFaktor = abrechnungsBackend.garage_faktor || 0.5;
                var garageSlider = garageFaktor * 100;
                console.log("DEBUG: Garage-Faktor aus Backend:", garageFaktor, "Slider:", garageSlider);
                sliders.push(garageSlider);
                // Garage hinzugefügt
            }
            // Tank am Ende
            platforms.push("Tank"); // Immer Tank am Ende
            deals.push(2); // Immer C
            // Verwende Backend-Faktor anstatt Standard-Wert
            var tankFaktor = abrechnungsBackend.tank_faktor || 0.0;
            var tankSlider = tankFaktor * 100;
            console.log("DEBUG: Tank-Faktor aus Backend:", tankFaktor, "Slider:", tankSlider);
            sliders.push(tankSlider);
            // Tank hinzugefügt
            
            // Arrays erstellt
            
            matchedPlatforms = platforms;
            matchedDeals = deals;
            matchedSliderValues = sliders;
            
            // Arrays initialisiert
            
            // WICHTIG: Original-Werte VOR dem Laden der Konfiguration speichern
            saveOriginalValues();
            
            // Lade gespeicherte Konfiguration
            loadOverlayConfiguration();
            
            // WICHTIG: Letzten Speicherstand NACH dem Laden der Konfiguration setzen
            saveLastSavedValues();
            
            // Force update nach dem Laden
            forceOverlayIncomeUpdate();
            
            // WICHTIG: Flag setzen, dass Konfiguration angewendet wurde
            overlayConfigApplied = true;
            console.log("DEBUG: overlayConfigApplied auf true gesetzt in updateMatchedPlatforms");
            // updateMatchedPlatforms() beendet
        }

    // Neue, verbesserte BottomBar mit Hover-Animation:
    Rectangle {
        id: bottomBar
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.bottomMargin: bottomBarHovered ? 80 : 24
        width: 280
        height: 80
        color: Style.background
        radius: 20
        border.color: Style.border
        border.width: 1
        visible: bottomBarVisible
        z: 99999
        
        // Hover-Detection für die gesamte Bar
        property bool bottomBarHovered: false
        
        // Schatten-Effekt (ohne QtGraphicalEffects)
        Rectangle {
            anchors.fill: parent
            anchors.topMargin: 4
            color: "#40000000"
            radius: 20
            z: -1
        }
        
        // Hover-Bereich für die gesamte Bar
        MouseArea {
            id: bottomBarHoverArea
            anchors.fill: parent
            hoverEnabled: true
            onEntered: {
                bottomBar.bottomBarHovered = true
            }
            onExited: {
                // Verzögerung, um zu prüfen, ob Maus auf einem Button ist
                checkButtonHoverTimer.start()
            }
        }
        
        // Timer für Button-Hover-Check
        Timer {
            id: checkButtonHoverTimer
            interval: 50
            onTriggered: {
                // Prüfe, ob Maus auf einem der Buttons ist
                if (!homeArea.containsMouse && !checkArea.containsMouse && !redoArea.containsMouse) {
                    bottomBar.bottomBarHovered = false
                }
            }
        }

        RowLayout {
            anchors.centerIn: parent
            spacing: 40

            // Home-Button
            Rectangle {
                id: homeButton
                width: 56
                height: 56
                radius: 28
                color: homeArea.pressed ? Style.primary : homeArea.containsMouse ? Style.accent : "transparent"
                border.color: homeArea.containsMouse ? Style.accent : Style.border
                border.width: homeArea.containsMouse ? 2 : 1

                MouseArea {
                    id: homeArea
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    hoverEnabled: true
                    onEntered: {
                        bottomBar.bottomBarHovered = true
                    }
                    onClicked: {
                        // Zurück zur Startseite/Dashboard
                        if (root.goHome && typeof root.goHome === "function") {
                            root.goHome();
                        } else {
                            console.warn("goHome Funktion nicht verfügbar!");
                        }
                    }
                }

                Image {
                    anchors.centerIn: parent
                    source: homeArea.pressed ? "assets/icons/home_gray.svg"
                        : homeArea.containsMouse ? "assets/icons/home_orange.svg" : "assets/icons/home_white.svg"
                    width: homeArea.pressed ? 28 : homeArea.containsMouse ? 32 : 28
                    height: width
                    fillMode: Image.PreserveAspectFit
                }

                Behavior on color {
                    ColorAnimation { duration: 200 }
                }
                Behavior on border.color {
                    ColorAnimation { duration: 200 }
                }
            }

            // Check-Button (Speichern)
            Rectangle {
                id: checkButton
                width: 56
                height: 56
                radius: 28
                color: checkArea.pressed ? Style.primary : checkArea.containsMouse ? Style.accent : "transparent"
                border.color: checkArea.containsMouse ? Style.accent : Style.border
                border.width: checkArea.containsMouse ? 2 : 1

                MouseArea {
                    id: checkArea
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    hoverEnabled: true
                    onEntered: {
                        bottomBar.bottomBarHovered = true
                    }
                    onClicked: {
                        console.log("🔵 CHECK-BUTTON GEKLICKT");
                        
                        // Speichere Overlay-Konfiguration in Datenbank, falls vorhanden
                        if (overlayConfigCache && overlayConfigCache.length > 0) {
                            console.log("💾 Speichere Overlay-Konfiguration...");
                            saveOverlayConfigToDatabase();
                        }
                        
                        console.log("🚀 Rufe abrechnungsBackend.speichereUmsatz() auf...");
                        abrechnungsBackend.speichereUmsatz();
                        
                        // Reset overlayAlreadyOpened beim finalen Speichern
                        overlayAlreadyOpened = false;
                        // Overlay nach dem Speichern schließen
                        dealOverlay.visible = false;
                        
                        console.log("✅ CHECK-BUTTON AUSFÜHRUNG BEENDET");
                    }
                }

                Image {
                    anchors.centerIn: parent
                    source: checkArea.pressed ? "assets/icons/check_gray.svg"
                        : checkArea.containsMouse ? "assets/icons/check_orange.svg" : "assets/icons/check_white.svg"
                    width: checkArea.pressed ? 28 : checkArea.containsMouse ? 32 : 28
                    height: width
                    fillMode: Image.PreserveAspectFit
                }

                Behavior on color {
                    ColorAnimation { duration: 200 }
                }
                Behavior on border.color {
                    ColorAnimation { duration: 200 }
                }
            }

            // Redo-Button (Neu starten)
            Rectangle {
                id: redoButton
                width: 56
                height: 56
                radius: 28
                color: redoArea.pressed ? Style.primary : redoArea.containsMouse ? Style.accent : "transparent"
                border.color: redoArea.containsMouse ? Style.accent : Style.border
                border.width: redoArea.containsMouse ? 2 : 1

                MouseArea {
                    id: redoArea
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    hoverEnabled: true
                    onEntered: {
                        bottomBar.bottomBarHovered = true
                    }
                    onClicked: {
                        // Wizard öffnen und komplette Neuauswertung starten
                        abrechnungsBackend.show_wizard_only();
                        // Reset overlayAlreadyOpened beim Wizard-Neustart
                        overlayAlreadyOpened = false;
                        // Cache leeren beim Wizard-Neustart
                        overlayConfigCache = [];
                        // Speicher-Status zurücksetzen
                        overlayConfigSaved = false;
                    }
                }

                Image {
                    anchors.centerIn: parent
                    source: redoArea.pressed ? "assets/icons/redo_gray.svg"
                        : redoArea.containsMouse ? "assets/icons/redo_orange.svg" : "assets/icons/redo_white.svg"
                    width: redoArea.pressed ? 28 : redoArea.containsMouse ? 32 : 28
                    height: width
                    fillMode: Image.PreserveAspectFit
                }

                Behavior on color {
                    ColorAnimation { duration: 200 }
                }
                Behavior on border.color {
                    ColorAnimation { duration: 200 }
                }
            }
        }

        // Animation beim Ein-/Ausblenden
        Behavior on opacity {
            NumberAnimation { duration: 300 }
        }
        
        // Smooth Animation für Hover-Effekt
        Behavior on anchors.bottomMargin {
            NumberAnimation { duration: 250; easing.type: Easing.OutCubic }
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
        // applyOverlayConfigurationToBackend() gestartet
        
        // Plattform-Faktoren berechnen - Verwende Backend-Werte als Standard
        var taxiFaktor = abrechnungsBackend.taxi_faktor || 0.0;
        var uberFaktor = abrechnungsBackend.uber_faktor || 0.0;
        var boltFaktor = abrechnungsBackend.bolt_faktor || 0.0;
        var taxiIndex = matchedPlatforms.indexOf("Taxi");
        var uberIndex = matchedPlatforms.indexOf("Uber");
        var boltIndex = matchedPlatforms.indexOf("Bolt");
        
        // Indizes gefunden
        
        if (taxiIndex !== -1) {
            taxiFaktor = matchedSliderValues[taxiIndex] !== undefined ? matchedSliderValues[taxiIndex] / 100.0 : taxiFaktor;
            // Taxi-Faktor berechnet
        }
        if (uberIndex !== -1) {
            uberFaktor = matchedSliderValues[uberIndex] !== undefined ? matchedSliderValues[uberIndex] / 100.0 : uberFaktor;
            // Uber-Faktor berechnet
        }
        if (boltIndex !== -1) {
            boltFaktor = matchedSliderValues[boltIndex] !== undefined ? matchedSliderValues[boltIndex] / 100.0 : boltFaktor;
            // Bolt-Faktor berechnet
        }
        
        // Einsteiger, Tank, Garage Faktoren berechnen - Verwende Backend-Werte als Standard
        var einsteigerFaktor = abrechnungsBackend.einsteiger_faktor || 0.0;
        var tankFaktor = abrechnungsBackend.tank_faktor || 0.0;
        var garageFaktor = abrechnungsBackend.garage_faktor || 0.5;
        for (var i = 0; i < matchedPlatforms.length; i++) {
            if (matchedPlatforms[i] === "Einsteiger") {
                einsteigerFaktor = matchedSliderValues[i] !== undefined ? matchedSliderValues[i] / 100.0 : einsteigerFaktor;
                // Einsteiger-Faktor berechnet
            }
            if (matchedPlatforms[i] === "Tank") {
                tankFaktor = matchedSliderValues[i] !== undefined ? matchedSliderValues[i] / 100.0 : tankFaktor;
                // Tank-Faktor berechnet
            }
            if (matchedPlatforms[i] === "Garage") {
                garageFaktor = matchedSliderValues[i] !== undefined ? matchedSliderValues[i] / 100.0 : garageFaktor;
                // Garage-Faktor berechnet
            }
        }
        
        // Einkommen ohne Einsteiger berechnen
        var overlayIncomeOhneEinsteiger = overlayIncome;
        var einsteigerIndex = matchedPlatforms.indexOf("Einsteiger");
        if (einsteigerIndex !== -1) {
            var einsteigerUmsatz = getEchterUmsatzForPlattform("Einsteiger");
            var einsteigerSlider = matchedSliderValues[einsteigerIndex] !== undefined ? matchedSliderValues[einsteigerIndex] : 0;
            overlayIncomeOhneEinsteiger -= einsteigerUmsatz * (einsteigerSlider / 100.0);
            console.log("DEBUG: OverlayIncomeOhneEinsteiger berechnet:", overlayIncomeOhneEinsteiger);
        }
        
        // Setze Backend-Faktoren:
        console.log("  Taxi:", taxiFaktor);
        console.log("  Uber:", uberFaktor);
        console.log("  Bolt:", boltFaktor);
        console.log("  Einsteiger:", einsteigerFaktor);
        console.log("  Tank:", tankFaktor);
        console.log("  Garage:", garageFaktor);
        console.log("  OverlayIncomeOhneEinsteiger:", overlayIncomeOhneEinsteiger);
        
        // Backend-Methoden aufrufen
        if (abrechnungsBackend && abrechnungsBackend.setTaxiFaktor) {
            abrechnungsBackend.setTaxiFaktor(taxiFaktor);
        }
        if (abrechnungsBackend && abrechnungsBackend.setUberFaktor) {
            abrechnungsBackend.setUberFaktor(uberFaktor);
        }
        if (abrechnungsBackend && abrechnungsBackend.setBoltFaktor) {
            abrechnungsBackend.setBoltFaktor(boltFaktor);
        }
        if (abrechnungsBackend && abrechnungsBackend.setEinsteigerFaktor) {
            abrechnungsBackend.setEinsteigerFaktor(einsteigerFaktor);
        }
        if (abrechnungsBackend && abrechnungsBackend.setTankFaktor) {
            abrechnungsBackend.setTankFaktor(tankFaktor);
        }
        if (abrechnungsBackend && abrechnungsBackend.setGarageFaktor) {
            abrechnungsBackend.setGarageFaktor(garageFaktor);
        }
        if (abrechnungsBackend && abrechnungsBackend.setOverlayIncomeOhneEinsteiger) {
            abrechnungsBackend.setOverlayIncomeOhneEinsteiger(overlayIncomeOhneEinsteiger);
        }
        
        // WICHTIG: Ergebnis sofort neu berechnen nach Backend-Update
        if (abrechnungsBackend && abrechnungsBackend.update_ergebnis) {
            abrechnungsBackend.update_ergebnis();
        }
        
        // applyOverlayConfigurationToBackend() beendet
    }
    
    function applyCustomDealConfig(customConfig) {
        // applyCustomDealConfig() gestartet
        console.log("DEBUG: Wende Custom-Deal-Konfiguration aus Datenbank an:", JSON.stringify(customConfig));
        
        // Konfiguration auf matchedDeals und matchedSliderValues anwenden
        var newDeals = matchedDeals.slice();
        var newSliders = matchedSliderValues.slice();
        
        // Custom-Deal-Konfiguration ist ein Array von Objekten mit platform, deal, slider
        for (var i = 0; i < customConfig.length; i++) {
            var item = customConfig[i];
            var platform = item.platform;
            var deal = item.deal || "C"; // Standard: C für Custom-Deal
            var slider = item.slider;
            
            console.log("DEBUG: Verarbeite Item:", platform, deal, slider);
            
            // Finde den Index für diese Plattform
            var platformIndex = matchedPlatforms.indexOf(platform);
            
            if (platformIndex !== -1) {
                // Deal-Typ für alle Plattformen setzen
                var dealValue = 2; // Standard: C für Custom-Deal
                if (deal === "%") dealValue = 1;
                else if (deal === "P") dealValue = 0;
                
                newDeals[platformIndex] = dealValue;
                newSliders[platformIndex] = slider;
                
                console.log("DEBUG: Angewendet für", platform, "Deal:", dealValue, "Slider:", slider);
            } else {
                console.log("DEBUG: Plattform", platform, "nicht gefunden in matchedPlatforms");
            }
        }
        
        // Arrays aktualisieren
        matchedDeals = newDeals;
        matchedSliderValues = newSliders;
        
        console.log("DEBUG: Custom-Deal-Konfiguration aus Datenbank angewendet");
        console.log("  Neue matchedDeals:", JSON.stringify(matchedDeals));
        console.log("  Neue matchedSliderValues:", JSON.stringify(matchedSliderValues));
        
        // WICHTIG: Backend-Faktoren aus den neuen Werten setzen
        applyOverlayConfigurationToBackend();
        
        // WICHTIG: Flag setzen, dass Konfiguration angewendet wurde
        overlayConfigApplied = true;
    }


}

