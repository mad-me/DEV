import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import Style 1.0

Rectangle {
    id: root
    anchors.fill: parent
    color: Style.background
    radius: Style.radiusNormal
    
    // Properties für Navigation zur Startseite
    property var goHome: null
    property bool selectionComplete: false
    
    // Auswahl-Properties
    property string selectedFahrer: ""
    property string selectedFahrzeug: ""
    property string selectedKW: ""
    
    // Backend-Referenzen
    property var abrechnungsBackend: null
    property var datenBackend: null
    property var mitarbeiterBackend: null
    property var fahrzeugBackend: null

    FontLoader {
        id: ubuntuFont
        source: "assets/fonts/Ubuntu-Regular.ttf"
    }
    
    FontLoader {
        id: spaceMonoFont
        source: "assets/fonts/SpaceMono-Regular.ttf"
    }

    // Header
    Rectangle {
        id: header
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: 80
        color: "transparent"
        
        RowLayout {
            anchors.fill: parent
            anchors.margins: 20
            
            // Zurück-Button
            MouseArea {
                width: 60
                height: 60
                onClicked: {
                    if (goHome) goHome()
                }
                cursorShape: Qt.PointingHandCursor
                
                Image {
                    anchors.centerIn: parent
                    source: "assets/icons/home_gray.svg"
                    width: 40
                    height: 40
                    fillMode: Image.PreserveAspectFit
                }
            }
            
            // Platzhalter für symmetrisches Layout (ohne Titel)
            Item {
                Layout.fillWidth: true
            }
            
            // Platzhalter für symmetrisches Layout
            Item {
                width: 60
                height: 60
            }
        }
    }

    // Hauptinhalt - Alle Cards in einem Container auf gleicher Höhe
    Rectangle {
        anchors.top: header.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: 40
        anchors.bottomMargin: 120  // Extra Platz für Button
        color: "transparent"
        clip: true
        z: 1
        
        // Container für alle Cards - Vertikal zentriert
        RowLayout {
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.verticalCenter: parent.verticalCenter
            anchors.margins: 60
            spacing: 40
            
            // Fahrer-Karten (dynamische Spalten, max 7 Cards pro Spalte)
            RowLayout {
                spacing: 15
                
                Repeater {
                    model: {
                        let list = mitarbeiterBackend ? mitarbeiterBackend.mitarbeiterList : []
                        let columns = Math.max(1, Math.ceil(list.length / 7))
                        let result = []
                        for (let i = 0; i < columns; i++) {
                            let column = []
                            for (let j = 0; j < 7; j++) {
                                let index = i * 7 + j
                                if (index < list.length) {
                                    column.push(list[index])
                                }
                            }
                            result.push(column)
                        }
                        return result
                    }
                    
                    ColumnLayout {
                        spacing: 15
                        
                        Repeater {
                            model: modelData
                            
                                                                                                                                                                                                                                                                                                                                                                                                                                                                               Rectangle {
                                                                                                                                                id: fahrerCard
                                     width: 180
                                     height: 120
                                     radius: Style.radiusLarge
                                                                        gradient: Gradient {
                                                                            GradientStop { position: 0.0; color: "#1a1a1a" }
                                                                            GradientStop { position: 0.1; color: "#1a1a1a" }
                                                                            GradientStop { position: 1.0; color: "#050505" }
                                                                        }
                                  
                                                                     // Hover-Effekt für Größe
                                   scale: fahrerMouseArea.containsMouse || selectedFahrer === ((modelData.first_name + " " + modelData.last_name) || modelData) ? 1.05 : 1.0
                                  
                                  // Smooth Animation für Scale
                                  Behavior on scale {
                                      NumberAnimation { duration: 150; easing.type: Easing.OutCubic }
                                  }
                                
                                                                                                                                   MouseArea {
                                      id: fahrerMouseArea
                                      anchors.fill: parent
                                      hoverEnabled: true
                                      onClicked: {
                                          let fahrerName = (modelData.first_name + " " + modelData.last_name) || modelData
                                          if (selectedFahrer === fahrerName) {
                                              // Deselect wenn bereits ausgewählt
                                              selectedFahrer = ""
                                          } else {
                                              // Select wenn nicht ausgewählt
                                              selectedFahrer = fahrerName
                                          }
                                          checkSelectionComplete()
                                      }
                                      cursorShape: Qt.PointingHandCursor
                                  }
                                
                                ColumnLayout {
                                    anchors.centerIn: parent
                                    spacing: 5
                                    
                                                                                                                                                   Text {
                                          text: modelData.last_name || ""
                                          font.pixelSize: selectedFahrer === ((modelData.first_name + " " + modelData.last_name) || modelData) ? 22 : 18
                                          font.bold: true
                                          color: selectedFahrer === ((modelData.first_name + " " + modelData.last_name) || modelData) ? "#f7931e" : Style.text
                                          font.family: ubuntuFont.name
                                          horizontalAlignment: Text.AlignHCenter
                                          Layout.alignment: Qt.AlignHCenter
                                      }
                                      
                                      Text {
                                          text: modelData.first_name || ""
                                          font.pixelSize: selectedFahrer === ((modelData.first_name + " " + modelData.last_name) || modelData) ? 20 : 16
                                          font.bold: false
                                          color: selectedFahrer === ((modelData.first_name + " " + modelData.last_name) || modelData) ? "#f7931e" : Style.text
                                          font.family: ubuntuFont.name
                                          horizontalAlignment: Text.AlignHCenter
                                          Layout.alignment: Qt.AlignHCenter
                                      }
                                }
                                
                                // Hover-Effekt
                                Rectangle {
                                    anchors.fill: parent
                                    color: parent.MouseArea.containsMouse && selectedFahrer !== ((modelData.first_name + " " + modelData.last_name) || modelData) ? "#333" : "transparent"
                                    radius: Style.radiusLarge
                                    opacity: 0.3
                                }
                            }
                        }
                    }
                }
            }

            // Fahrzeug-Karten (dynamische Spalten, max 7 Cards pro Spalte)
            RowLayout {
                spacing: 15
                
                Repeater {
                    model: {
                        let list = fahrzeugBackend ? fahrzeugBackend.fahrzeugList : []
                        let columns = Math.max(1, Math.ceil(list.length / 7))
                        let result = []
                        for (let i = 0; i < columns; i++) {
                            let column = []
                            for (let j = 0; j < 7; j++) {
                                let index = i * 7 + j
                                if (index < list.length) {
                                    column.push(list[index])
                                }
                            }
                            result.push(column)
                        }
                        return result
                    }
                    
                    ColumnLayout {
                        spacing: 15
                        
                        Repeater {
                            model: modelData
                            
                                                                                                                                                                                                                                                                                                                                                                                                                                                                               Rectangle {
                                                                                                                                                id: fahrzeugCard
                                     width: 180
                                     height: 120
                                     radius: Style.radiusLarge
                                                                        gradient: Gradient {
                                                                            GradientStop { position: 0.0; color: "#1a1a1a" }
                                                                            GradientStop { position: 0.1; color: "#1a1a1a" }
                                                                            GradientStop { position: 1.0; color: "#050505" }
                                                                        }
                                  
                                                                     // Hover-Effekt für Größe
                                   scale: fahrzeugMouseArea.containsMouse || selectedFahrzeug === (modelData.kennzeichen || modelData) ? 1.05 : 1.0
                                  
                                  // Smooth Animation für Scale
                                  Behavior on scale {
                                      NumberAnimation { duration: 150; easing.type: Easing.OutCubic }
                                  }
                                
                                                                                                                                   MouseArea {
                                      id: fahrzeugMouseArea
                                      anchors.fill: parent
                                      hoverEnabled: true
                                      onClicked: {
                                          let fahrzeugName = modelData.kennzeichen || modelData
                                          if (selectedFahrzeug === fahrzeugName) {
                                              // Deselect wenn bereits ausgewählt
                                              selectedFahrzeug = ""
                                          } else {
                                              // Select wenn nicht ausgewählt
                                              selectedFahrzeug = fahrzeugName
                                          }
                                          checkSelectionComplete()
                                      }
                                      cursorShape: Qt.PointingHandCursor
                                  }
                                
                                                                                                                                   Text {
                                      anchors.centerIn: parent
                                      text: modelData.kennzeichen || modelData
                                      font.pixelSize: selectedFahrzeug === (modelData.kennzeichen || modelData) ? 22 : 18
                                      font.bold: true
                                      color: selectedFahrzeug === (modelData.kennzeichen || modelData) ? "#f7931e" : Style.text
                                      font.family: ubuntuFont.name
                                      horizontalAlignment: Text.AlignHCenter
                                      wrapMode: Text.WordWrap
                                  }
                                
                                // Hover-Effekt
                                Rectangle {
                                    anchors.fill: parent
                                    color: parent.MouseArea.containsMouse && selectedFahrzeug !== (modelData.kennzeichen || modelData) ? "#333" : "transparent"
                                    radius: Style.radiusLarge
                                    opacity: 0.3
                                }
                            }
                        }
                    }
                }
            }

            // Kalenderwoche-Karten (dynamische Spalten, max 7 Cards pro Spalte)
            RowLayout {
                spacing: 15
                
                Repeater {
                    model: {
                        let list = abrechnungsBackend ? abrechnungsBackend.kw_list : []
                        let columns = Math.max(1, Math.ceil(list.length / 7))
                        let result = []
                        for (let i = 0; i < columns; i++) {
                            let column = []
                            for (let j = 0; j < 7; j++) {
                                let index = i * 7 + j
                                if (index < list.length) {
                                    column.push(list[index])
                                }
                            }
                            result.push(column)
                        }
                        return result
                    }
                    
                    ColumnLayout {
                        spacing: 15
                        
                        Repeater {
                            model: modelData
                            
                                                                                                                                                                                                                                                                                                                                                                                                                                                                               Rectangle {
                                                                                                                                                id: kwCard
                                     width: 90
                                     height: 120
                                     radius: Style.radiusLarge
                                                                        gradient: Gradient {
                                                                            GradientStop { position: 0.0; color: "#1a1a1a" }
                                                                            GradientStop { position: 0.1; color: "#1a1a1a" }
                                                                            GradientStop { position: 1.0; color: "#050505" }
                                                                        }
                                  
                                                                     // Hover-Effekt für Größe
                                   scale: kwMouseArea.containsMouse || selectedKW === modelData ? 1.05 : 1.0
                                  
                                  // Smooth Animation für Scale
                                  Behavior on scale {
                                      NumberAnimation { duration: 150; easing.type: Easing.OutCubic }
                                  }
                                
                                                                                                                                   MouseArea {
                                      id: kwMouseArea
                                      anchors.fill: parent
                                      hoverEnabled: true
                                      onClicked: {
                                          if (selectedKW === modelData) {
                                              // Deselect wenn bereits ausgewählt
                                              selectedKW = ""
                                          } else {
                                              // Select wenn nicht ausgewählt
                                              selectedKW = modelData
                                          }
                                          checkSelectionComplete()
                                      }
                                      cursorShape: Qt.PointingHandCursor
                                  }
                                
                                                                                                                                                                                                                                                                       Text {
                                       anchors.centerIn: parent
                                       text: modelData
                                      font.pixelSize: selectedKW === modelData ? 24 : 20
                                      font.bold: true
                                      color: selectedKW === modelData ? "#f7931e" : Style.text
                                      font.family: ubuntuFont.name
                                      horizontalAlignment: Text.AlignHCenter
                                  }
                                
                                // Hover-Effekt
                                Rectangle {
                                    anchors.fill: parent
                                    color: parent.MouseArea.containsMouse && selectedKW !== modelData ? "#333" : "transparent"
                                    radius: Style.radiusLarge
                                    opacity: 0.3
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    // Weiter-Button mit Icon - Direkt im Hauptcontainer
    Rectangle {
        id: weiterButton
        anchors.bottom: parent.bottom
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottomMargin: 80  // Näher am unteren Rand
        width: 80
        height: 80
        radius: 40
        color: "transparent"
        enabled: selectionComplete
        visible: true
        opacity: 1.0
        z: 100000
        
        Component.onCompleted: {
            console.log("Weiter-Button erstellt, Sichtbar:", visible, "Z-Index:", z, "Position:", x, y, "Größe:", width, height)
        }
        
        MouseArea {
            id: weiterMouseArea
            anchors.fill: parent
            enabled: selectionComplete
            hoverEnabled: true
            onClicked: {
                if (selectionComplete) {
                    console.log("Weiter-Button geklickt!")
                    // Den gleichen Ablauf wie nach dem Wizard ausführen
                    abrechnungsBackend.process_cards_selection(selectedFahrer, selectedFahrzeug, selectedKW)
                }
            }
            cursorShape: selectionComplete ? Qt.PointingHandCursor : Qt.ArrowCursor
        }
        
        Image {
            anchors.centerIn: parent
            source: {
                if (!selectionComplete) {
                    "assets/icons/check_gray.svg"
                } else if (weiterMouseArea.containsMouse) {
                    "assets/icons/check_orange.svg"
                } else {
                    "assets/icons/check_white.svg"
                }
            }
            width: {
                if (!selectionComplete) {
                    40
                } else if (weiterMouseArea.containsMouse) {
                    48  // Ein bisschen größer beim Hover
                } else {
                    40
                }
            }
            height: width
            fillMode: Image.PreserveAspectFit
        }
        

        
        // Smooth Animation für Icon-Größe
        Behavior on width {
            NumberAnimation { duration: 200; easing.type: Easing.OutCubic }
        }
        Behavior on height {
            NumberAnimation { duration: 200; easing.type: Easing.OutCubic }
        }
    }

    // Funktionen
    function checkSelectionComplete() {
        selectionComplete = selectedFahrer !== "" && selectedFahrzeug !== "" && selectedKW !== ""
        console.log("Selection complete:", selectionComplete, "Fahrer:", selectedFahrer, "Fahrzeug:", selectedFahrzeug, "KW:", selectedKW)
    }
    
    // Initial check
    Component.onCompleted: {
        checkSelectionComplete()
        // Letzte Kalenderwoche automatisch vorewählen
        selectLastKW()
    }
    
    // Funktion zum Vorewählen der letzten Kalenderwoche und aktueller Werte
    function selectLastKW() {
        if (abrechnungsBackend && abrechnungsBackend.kw_list && abrechnungsBackend.kw_list.length > 0) {
            // KW-Liste nach Nummer sortieren (höchste zuerst)
            let kwList = abrechnungsBackend.kw_list.slice() // Kopie erstellen
            kwList.sort((a, b) => parseInt(b) - parseInt(a)) // Nach Nummer absteigend sortieren
            let lastKW = kwList[0] // Erste nach Sortierung ist die höchste
            selectedKW = lastKW
            console.log("Letzte Kalenderwoche vorewählt:", lastKW, "aus sortierter Liste:", kwList)
            
            // Aktuellen Fahrer vorewählen (falls verfügbar)
            if (abrechnungsBackend.current_fahrer && abrechnungsBackend.current_fahrer !== "") {
                selectedFahrer = abrechnungsBackend.current_fahrer
                console.log("Aktueller Fahrer vorewählt:", selectedFahrer)
            }
            
            // Aktuelles Fahrzeug vorewählen (falls verfügbar)
            if (abrechnungsBackend.current_fahrzeug && abrechnungsBackend.current_fahrzeug !== "") {
                selectedFahrzeug = abrechnungsBackend.current_fahrzeug
                console.log("Aktuelles Fahrzeug vorewählt:", selectedFahrzeug)
            }
            
            checkSelectionComplete()
        }
    }
} 