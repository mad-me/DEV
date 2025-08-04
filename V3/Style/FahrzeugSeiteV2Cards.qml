import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Rectangle {
    id: root
    property var goHome: function() {
        // Fallback: Blende die Fahrzeugseite aus und zeige das MainMenu
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

    // Einfaches Error-Overlay (sehr vorsichtig implementiert)
    Rectangle {
        id: errorOverlay
        anchors.fill: parent
        color: "#000000"
        opacity: 0.8
        visible: false
        z: 3000 // Höchster Z-Index
        
        Rectangle {
            width: 400
            height: 150
            anchors.centerIn: parent
            radius: Style.radiusNormal
            color: "#1a1a1a"
            border.color: "#ff4444"
            border.width: 2
            
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 20
                spacing: 16
                
                Text {
                    text: "⚠️ Fehler aufgetreten"
                    font.family: ubuntuFont.name
                    font.pixelSize: 18
                    font.bold: true
                    color: "#ff4444"
                    Layout.fillWidth: true
                    horizontalAlignment: Text.AlignHCenter
                }
                
                Text {
                    id: errorMessage
                    text: "Ein Fehler ist aufgetreten"
                    font.family: ubuntuFont.name
                    font.pixelSize: 14
                    color: "#cccccc"
                    Layout.fillWidth: true
                    horizontalAlignment: Text.AlignHCenter
                    wrapMode: Text.WordWrap
                }
                
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 16
                    
                    Item { Layout.fillWidth: true }
                    
                    // Schließen-Button
                    Rectangle {
                        width: 48
                        height: 48
                        radius: 24
                        color: "transparent"
                        border.width: 0
                        
                        MouseArea {
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: errorOverlay.visible = false
                            
                            Image {
                                anchors.centerIn: parent
                                source: parent.containsMouse ? "assets/icons/close_red.svg" : "assets/icons/close_gray.svg"
                                width: parent.containsMouse ? 32 : 28
                                height: width
                                fillMode: Image.PreserveAspectFit
                            }
                        }
                    }
                }
            }
        }
        
        // ESC-Taste zum Schließen
        Keys.onEscapePressed: errorOverlay.visible = false
    }

    // QML-Overlay für Wochen-Daten
    Rectangle {
        id: weekDataOverlay
        anchors.fill: parent
        color: "#000000"
        opacity: 0.8
        visible: false
        z: 1000

                 // Overlay-Inhalt
         Rectangle {
             id: overlayContent
             width: Math.min(800, parent.width - 40)
             height: Math.min(overlayContentColumn.height + 120, parent.height - 40)  // Dynamische Höhe basierend auf Inhalt
             anchors.centerIn: parent
             radius: Style.radiusNormal
             color: "#1a1a1a"
             border.color: "#333333"
             border.width: 1

            // Header
            Rectangle {
                id: overlayHeader
                anchors.top: parent.top
                anchors.left: parent.left
                anchors.right: parent.right
                height: 60
                color: "transparent"
                border.color: "#333333"
                border.width: 0

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 16

                    Text {
                        id: overlayTitle
                        text: "Kalenderwoche - Fahrzeug"
                        font.family: ubuntuFont.name
                        font.pixelSize: 18
                        font.bold: true
                        color: "#ff8c00"
                        Layout.fillWidth: true
                    }

                                         Rectangle {
                         width: 32
                         height: 32
                         radius: 16
                         color: "transparent"
                         border.width: 0
                         
                         MouseArea {
                             anchors.fill: parent
                             hoverEnabled: true
                             cursorShape: Qt.PointingHandCursor
                             onClicked: weekDataOverlay.visible = false
                             
                             Text {
                                 anchors.centerIn: parent
                                 text: "×"
                                 font.pixelSize: 20
                                 color: parent.containsMouse ? "#ff8c00" : "#cccccc"
                             }
                         }
                     }
                }
            }

                                                   // ScrollView für alle Daten
              ScrollView {
                  anchors.top: overlayHeader.bottom
                  anchors.left: parent.left
                  anchors.right: parent.right
                  anchors.bottom: parent.bottom
                  anchors.margins: 16
                  clip: true
                  contentHeight: overlayContentColumn.height

                                                                           ColumnLayout {
                          id: overlayContentColumn
                          width: parent.width
                          spacing: 12

                         // Revenue-Sektion
                         Text {
                             text: "📈 Revenue"
                             font.family: ubuntuFont.name
                             font.pixelSize: 18
                             font.bold: true
                             color: "#4CAF50"
                             Layout.fillWidth: true
                             Layout.topMargin: 10
                         }

                                                   // Revenue-Daten
                          Repeater {
                              id: revenueDataRepeater
                              model: []

                              Rectangle {
                                  Layout.fillWidth: true
                                  height: 80
                                  radius: 8
                                  color: "#2a2a2a"
                                  border.color: "#333333"
                                  border.width: 1

                                  RowLayout {
                                      anchors.fill: parent
                                      anchors.margins: 12
                                      spacing: 16

                                      ColumnLayout {
                                          Layout.fillWidth: true
                                          spacing: 4

                                          Text {
                                              text: (modelData.driver || "N/A") + " - " + (modelData.deal || "N/A")
                                              font.family: ubuntuFont.name
                                              font.pixelSize: 14
                                              color: "#cccccc"
                                          }

                                          Text {
                                              text: (modelData.income || 0) + " €"
                                              font.family: ubuntuFont.name
                                              font.pixelSize: 16
                                              font.bold: true
                                              color: "#4CAF50"
                                          }

                                          Text {
                                              text: (modelData.total || 0) + " €"
                                              font.family: ubuntuFont.name
                                              font.pixelSize: 12
                                              color: "#b0b0b0"
                                          }
                                      }
                                      
                                                                             // Löschen-Button für Revenue-Eintrag
                                       Rectangle {
                                           Layout.preferredWidth: 24
                                           Layout.preferredHeight: 24
                                           radius: 12
                                           color: "transparent"
                                           border.width: 0
                                           
                                           MouseArea {
                                               anchors.fill: parent
                                               hoverEnabled: true
                                               onClicked: {
                                                   // Revenue-Eintrag löschen
                                                   console.log("Lösche Revenue-Eintrag:", modelData)
                                                   fahrzeugBackendV2.deleteRevenueEntry(overlayTitle.text.split(" - ")[1], parseInt(overlayTitle.text.split(" ")[1]), modelData)
                                               }
                                               
                                               Image {
                                                   anchors.centerIn: parent
                                                   source: parent.containsMouse ? "assets/icons/delete_orange.svg" : "assets/icons/delete_gray.svg"
                                                   width: parent.containsMouse ? 16 : 14
                                                   height: width
                                                   fillMode: Image.PreserveAspectFit
                                               }
                                           }
                                       }
                                  }
                              }
                          }

                         // Keine Revenue-Daten-Nachricht
                         Text {
                             text: "Keine Revenue-Daten für diese Woche vorhanden."
                             font.family: ubuntuFont.name
                             font.pixelSize: 14
                             color: "#666666"
                             horizontalAlignment: Text.AlignHCenter
                             Layout.fillWidth: true
                             Layout.topMargin: 10
                             visible: revenueDataRepeater.count === 0
                         }

                         // Trennlinie
                         Rectangle {
                             Layout.fillWidth: true
                             height: 1
                             color: "#333333"
                             Layout.topMargin: 20
                             Layout.bottomMargin: 20
                         }

                         // Running-Costs-Sektion
                         Text {
                             text: "💰 Running-Costs"
                             font.family: ubuntuFont.name
                             font.pixelSize: 18
                             font.bold: true
                             color: "#FF9800"
                             Layout.fillWidth: true
                             Layout.topMargin: 10
                         }

                         // Running-Costs-Daten
                         GridLayout {
                             Layout.fillWidth: true
                             columns: 3
                             rowSpacing: 8
                             columnSpacing: 8

                                                           Repeater {
                                  id: runningCostsDataRepeater
                                  model: []

                                  Rectangle {
                                      Layout.preferredWidth: 200
                                      Layout.preferredHeight: 80
                                      radius: 8
                                      color: "#2a2a2a"
                                      border.color: "#333333"
                                      border.width: 1

                                      RowLayout {
                                          anchors.fill: parent
                                          anchors.margins: 12
                                          spacing: 16

                                          ColumnLayout {
                                              Layout.fillWidth: true
                                              spacing: 4

                                              Text {
                                                  text: modelData.category || "N/A"
                                                  font.family: ubuntuFont.name
                                                  font.pixelSize: 14
                                                  color: "#cccccc"
                                              }

                                              Text {
                                                  text: (modelData.amount || 0) + " €"
                                                  font.family: ubuntuFont.name
                                                  font.pixelSize: 16
                                                  font.bold: true
                                                  color: "#FF9800"
                                              }

                                              Text {
                                                  text: modelData.timestamp || "N/A"
                                                  font.family: ubuntuFont.name
                                                  font.pixelSize: 12
                                                  color: "#b0b0b0"
                                              }
                                          }
                                          
                                                                                     // Löschen-Button für Running-Costs-Eintrag
                                           Rectangle {
                                               Layout.preferredWidth: 24
                                               Layout.preferredHeight: 24
                                               radius: 12
                                               color: "transparent"
                                               border.width: 0
                                               
                                               MouseArea {
                                                   anchors.fill: parent
                                                   hoverEnabled: true
                                                   onClicked: {
                                                       // Running-Costs-Eintrag löschen
                                                       console.log("Lösche Running-Costs-Eintrag:", modelData)
                                                       fahrzeugBackendV2.deleteRunningCostsEntry(overlayTitle.text.split(" - ")[1], parseInt(overlayTitle.text.split(" ")[1]), modelData)
                                                   }
                                                   
                                                   Image {
                                                       anchors.centerIn: parent
                                                       source: parent.containsMouse ? "assets/icons/delete_orange.svg" : "assets/icons/delete_gray.svg"
                                                       width: parent.containsMouse ? 16 : 14
                                                       height: width
                                                       fillMode: Image.PreserveAspectFit
                                                   }
                                               }
                                           }
                                      }
                                  }
                              }
                         }

                         // Keine Running-Costs-Daten-Nachricht
                         Text {
                             text: "Keine Running-Costs-Daten für diese Woche vorhanden."
                             font.family: ubuntuFont.name
                             font.pixelSize: 14
                             color: "#666666"
                             horizontalAlignment: Text.AlignHCenter
                             Layout.fillWidth: true
                             Layout.topMargin: 10
                             visible: runningCostsDataRepeater.count === 0
                         }
                     }
            }
        }

                 // ESC-Taste zum Schließen
         Keys.onEscapePressed: weekDataOverlay.visible = false
     }
     
     // Bestätigungsdialog für das Löschen von Fahrzeugen
     Rectangle {
         id: deleteConfirmDialog
         anchors.fill: parent
         color: "#000000"
         opacity: 0.8
         visible: false
         z: 2000
         
         property string licensePlate: ""
         
         Rectangle {
             width: 400
             height: 200
             anchors.centerIn: parent
             radius: Style.radiusNormal
             color: "#1a1a1a"
             border.color: "#333333"
             border.width: 1
             
             ColumnLayout {
                 anchors.fill: parent
                 anchors.margins: 20
                 spacing: 16
                 
                 Text {
                     text: "Fahrzeug löschen?"
                     font.family: ubuntuFont.name
                     font.pixelSize: 18
                     font.bold: true
                     color: "#ff4444"
                     Layout.fillWidth: true
                     horizontalAlignment: Text.AlignHCenter
                 }
                 
                 Text {
                     text: "Möchten Sie das Fahrzeug '" + deleteConfirmDialog.licensePlate + "' wirklich löschen?"
                     font.family: ubuntuFont.name
                     font.pixelSize: 14
                     color: "#cccccc"
                     Layout.fillWidth: true
                     horizontalAlignment: Text.AlignHCenter
                     wrapMode: Text.WordWrap
                 }
                 
                 RowLayout {
                     Layout.fillWidth: true
                     spacing: 16
                     
                     // Spacer um Icons nach rechts zu schieben
                     Item {
                         Layout.fillWidth: true
                     }
                     
                     // Abbrechen-Button mit Close-Icon
                     Rectangle {
                         Layout.preferredWidth: 48
                         height: 48
                         radius: 24
                         color: "transparent"
                         border.width: 0
                         
                         MouseArea {
                             anchors.fill: parent
                             hoverEnabled: true
                             cursorShape: Qt.PointingHandCursor
                             onClicked: deleteConfirmDialog.visible = false
                             
                             Image {
                                 anchors.centerIn: parent
                                 source: parent.containsMouse ? "assets/icons/close_red.svg" : "assets/icons/close_gray.svg"
                                 width: parent.containsMouse ? 32 : 28
                                 height: width
                                 fillMode: Image.PreserveAspectFit
                             }
                         }
                     }
                     
                     // Löschen-Button mit Delete-Icon
                     Rectangle {
                         Layout.preferredWidth: 48
                         height: 48
                         radius: 24
                         color: "transparent"
                         border.width: 0
                         
                         MouseArea {
                             anchors.fill: parent
                             hoverEnabled: true
                             cursorShape: Qt.PointingHandCursor
                             onClicked: {
                                 fahrzeugBackendV2.deleteVehicle(deleteConfirmDialog.licensePlate)
                                 deleteConfirmDialog.visible = false
                             }
                             
                             Image {
                                 anchors.centerIn: parent
                                 source: parent.containsMouse ? "assets/icons/delete_orange.svg" : "assets/icons/delete_white.svg"
                                 width: parent.containsMouse ? 32 : 28
                                 height: width
                                 fillMode: Image.PreserveAspectFit
                             }
                         }
                     }
                 }
             }
         }
         
         // ESC-Taste zum Schließen
         Keys.onEscapePressed: deleteConfirmDialog.visible = false
     }
     
     // Bestätigungsdialog für das Löschen von Running-Costs
     Rectangle {
         id: deleteRunningCostsDialog
         anchors.fill: parent
         color: "#000000"
         opacity: 0.8
         visible: false
         z: 2000
         
         property string licensePlate: ""
         property int week: 0
         property int count: 0
         
         Rectangle {
             width: 450
             height: 220
             anchors.centerIn: parent
             radius: Style.radiusNormal
             color: "#1a1a1a"
             border.color: "#333333"
             border.width: 1
             
             ColumnLayout {
                 anchors.fill: parent
                 anchors.margins: 20
                 spacing: 16
                 
                 Text {
                     text: "Ausgaben löschen?"
                     font.family: ubuntuFont.name
                     font.pixelSize: 18
                     font.bold: true
                     color: "#ff8c00"
                     Layout.fillWidth: true
                     horizontalAlignment: Text.AlignHCenter
                 }
                 
                 Text {
                     text: "Möchten Sie auch die " + deleteRunningCostsDialog.count + " Ausgaben-Einträge für KW " + deleteRunningCostsDialog.week + " löschen?"
                     font.family: ubuntuFont.name
                     font.pixelSize: 14
                     color: "#cccccc"
                     Layout.fillWidth: true
                     horizontalAlignment: Text.AlignHCenter
                     wrapMode: Text.WordWrap
                 }
                 
                 Text {
                     text: "Dies kann nicht rückgängig gemacht werden."
                     font.family: ubuntuFont.name
                     font.pixelSize: 12
                     color: "#ff4444"
                     Layout.fillWidth: true
                     horizontalAlignment: Text.AlignHCenter
                     wrapMode: Text.WordWrap
                 }
                 
                 RowLayout {
                     Layout.fillWidth: true
                     spacing: 16
                     
                     // Spacer um Icons nach rechts zu schieben
                     Item {
                         Layout.fillWidth: true
                     }
                     
                     // Abbrechen-Button mit Close-Icon
                     Rectangle {
                         Layout.preferredWidth: 48
                         height: 48
                         radius: 24
                         color: "transparent"
                         border.width: 0
                         
                         MouseArea {
                             anchors.fill: parent
                             hoverEnabled: true
                             cursorShape: Qt.PointingHandCursor
                             onClicked: deleteRunningCostsDialog.visible = false
                             
                             Image {
                                 anchors.centerIn: parent
                                 source: parent.containsMouse ? "assets/icons/close_red.svg" : "assets/icons/close_gray.svg"
                                 width: parent.containsMouse ? 32 : 28
                                 height: width
                                 fillMode: Image.PreserveAspectFit
                             }
                         }
                     }
                     
                     // Löschen-Button mit Delete-Icon
                     Rectangle {
                         Layout.preferredWidth: 48
                         height: 48
                         radius: 24
                         color: "transparent"
                         border.width: 0
                         
                         MouseArea {
                             anchors.fill: parent
                             hoverEnabled: true
                             cursorShape: Qt.PointingHandCursor
                             onClicked: {
                                 fahrzeugBackendV2.deleteRunningCostsForWeek(deleteRunningCostsDialog.licensePlate, deleteRunningCostsDialog.week)
                                 deleteRunningCostsDialog.visible = false
                             }
                             
                             Image {
                                 anchors.centerIn: parent
                                 source: parent.containsMouse ? "assets/icons/delete_orange.svg" : "assets/icons/delete_white.svg"
                                 width: parent.containsMouse ? 32 : 28
                                 height: width
                                 fillMode: Image.PreserveAspectFit
                             }
                         }
                     }
                 }
             }
         }
         
         // ESC-Taste zum Schließen
         Keys.onEscapePressed: deleteRunningCostsDialog.visible = false
     }

    // Home-Button (außerhalb des Headers, links)
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
            } else {
                console.warn("goHome ist nicht definiert oder keine Funktion!");
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
        anchors.margins: Style.spacingHuge
        anchors.topMargin: 52
        anchors.bottomMargin: 115
        anchors.rightMargin: 100
        anchors.leftMargin: 100
        spacing: 16

        // Header mit Titel und Status
        RowLayout {
            Layout.fillWidth: true
            spacing: Style.spacingLarge
            
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
                        // Ansichtswechsel: Cards ↔ Kalenderwochen
                        if (typeof fahrzeugBackendV2.toggleViewMode === "function") {
                            fahrzeugBackendV2.toggleViewMode()
                        } else {
                            console.log("toggleViewMode nicht verfügbar")
                        }
                    }
                }
                
                Text {
                    anchors.left: parent.left
                    anchors.verticalCenter: parent.verticalCenter
                                            text: fahrzeugBackendV2 && fahrzeugBackendV2.isCalendarView ? "Kalenderwochen-Übersicht" : "Fahrzeugverwaltung"
                    font.family: ubuntuFont.name
                    font.pixelSize: 36
                    font.bold: true
                    color: titleMouseArea.containsMouse ? "#ff8c00" : "white"
                    
                    // Hover-Effekt: Leichte Vergrößerung
                    scale: titleMouseArea.containsMouse ? 1.05 : 1.0
                    
                    Behavior on scale {
                        NumberAnimation { duration: 150 }
                    }
                    
                    Behavior on color {
                        ColorAnimation { duration: 150 }
                    }
                }
            }
            
            // Toggle Switch (nur in normaler Ansicht)
            Rectangle {
                Layout.preferredWidth: 50
                height: 50
                radius: Style.radiusNormal
                color: "transparent"
                border.width: 0
                visible: !fahrzeugBackendV2 || !fahrzeugBackendV2.isCalendarView
                
                // Toggle Switch Background
                Rectangle {
                    width: 40
                    height: 20
                    radius: 10
                                            color: fahrzeugBackendV2 && fahrzeugBackendV2.showOnlyActive ? "#ff8c00" : "#555555"
                    anchors.centerIn: parent
                    
                    // Toggle Knob
                    Rectangle {
                        id: toggleKnob
                        width: 16
                        height: 16
                        radius: 8
                        color: "white"
                        anchors.verticalCenter: parent.verticalCenter
                        anchors.left: parent.left
                        anchors.leftMargin: fahrzeugBackendV2 && fahrzeugBackendV2.showOnlyActive ? 20 : 2
                        
                        Behavior on anchors.leftMargin {
                            NumberAnimation { duration: 200; easing.type: Easing.OutQuad }
                        }
                    }
                }
                
                MouseArea {
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                                                onClicked: {
                                if (fahrzeugBackendV2) {
                                    fahrzeugBackendV2.showOnlyActive = !fahrzeugBackendV2.showOnlyActive
                                }
                            }
                }
            }
        }

        // Suchfeld und Aktionen
        RowLayout {
            Layout.fillWidth: true
            spacing: Style.spacingLarge
            
                         // Erweiterte Suchleiste
             Rectangle {
                 Layout.fillWidth: true
                 height: 64
                 radius: Style.radiusNormal
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
                        console.log("Suchleiste aktiviert")
                        parent.suchfeldAktiv = true;
                        suchfeld.forceActiveFocus();
                    }
                }
                
                Image {
                    id: suchIcon
                    source: parent.iconHovered ? "assets/icons/vehicle_orange.svg" : "assets/icons/vehicle_gray.svg"
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.horizontalCenterOffset: 9
                    width: parent.iconHovered ? 40 : 28
                    height: parent.iconHovered ? 40 : 28
                    visible: !parent.suchfeldAktiv
                    opacity: 0.7
                }
                
                TextField {
                    id: suchfeld
                    anchors.top: parent.top
                    anchors.bottom: parent.bottom
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.margins: 2
                    anchors.rightMargin: 15
                    font.pixelSize: 32
                    font.family: spaceMonoFont.name
                    color: "white"
                    background: null
                    padding: 32
                    horizontalAlignment: TextInput.AlignHCenter
                    verticalAlignment: TextInput.AlignVCenter
                    placeholderText: "Fahrzeug suchen..."
                    selectionColor: "#a2ffb5"
                    selectedTextColor: "#232323"
                    visible: parent.suchfeldAktiv
                    cursorVisible: true
                    onTextChanged: {
                        console.log("Suchtext geändert:", text)
                        fahrzeugBackendV2.filterText = text
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
            
            // Refresh-Button entfernt
        }

        // Cards-Container mit echtem Grid-Layout
        GridView {
            id: cardsGridView
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            
            // Performance-Optimierungen
            cacheBuffer: 1000  // Größerer Cache für bessere Performance
            maximumFlickVelocity: 2500  // Schnelleres Scrollen
            boundsBehavior: Flickable.StopAtBounds  // Bessere Scroll-Performance
            
            // Responsive Grid-Eigenschaften
            cellWidth: 396  // 380 + 16 spacing
            cellHeight: 296 // 280 + 16 spacing
            
            // Automatische Spaltenberechnung
            onWidthChanged: {
                var availableWidth = width - 16 // Abstand berücksichtigen
                var cardsPerRow = Math.max(1, Math.floor(availableWidth / 396))
                cellWidth = availableWidth / cardsPerRow
            }
            
            // Fahrzeug-Cards
                            model: fahrzeugBackendV2 ? fahrzeugBackendV2.fahrzeugList : []
            
            // Loading-Indikator
            Rectangle {
                id: loadingIndicator
                anchors.centerIn: parent
                width: 200
                height: 60
                radius: Style.radiusNormal
                color: "#1a1a1a"
                border.color: "#333333"
                border.width: 1
                                    visible: fahrzeugBackendV2 && fahrzeugBackendV2.isLoading
                z: 100
                
                RowLayout {
                    anchors.centerIn: parent
                    spacing: 12
                    
                    // Spinner-Animation
                    Rectangle {
                        width: 20
                        height: 20
                        radius: 10
                        color: "#ff8c00"
                        
                        RotationAnimation on rotation {
                            from: 0
                            to: 360
                            duration: 1000
                            loops: Animation.Infinite
                        }
                    }
                    
                    Text {
                        text: "Fahrzeuge werden geladen..."
                        font.family: ubuntuFont.name
                        font.pixelSize: 14
                        color: "#cccccc"
                    }
                }
            }
            
            // Pagination-Controls (sehr vorsichtig hinzugefügt)
            Rectangle {
                id: paginationControls
                anchors.bottom: parent.bottom
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.bottomMargin: 20
                width: 300
                height: 50
                radius: Style.radiusNormal
                color: "#1a1a1a"
                border.color: "#333333"
                border.width: 1
                                    visible: fahrzeugBackendV2 && fahrzeugBackendV2.totalVehicles > fahrzeugBackendV2.pageSize
                z: 50
                
                RowLayout {
                    anchors.centerIn: parent
                    spacing: 16
                    
                    // Zurück-Button
                    Rectangle {
                        width: 40
                        height: 40
                        radius: 20
                        color: "transparent"
                        border.width: 0
                        
                        MouseArea {
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            enabled: fahrzeugBackendV2 && fahrzeugBackendV2.currentPage > 0
                            onClicked: fahrzeugBackendV2.loadPreviousPage()
                            
                            Image {
                                anchors.centerIn: parent
                                source: parent.enabled && parent.containsMouse ? "assets/icons/close_orange.svg" : "assets/icons/close_gray.svg"
                                width: parent.enabled && parent.containsMouse ? 24 : 20
                                height: width
                                fillMode: Image.PreserveAspectFit
                                rotation: 180  // Pfeil nach links
                            }
                        }
                    }
                    
                    // Seiten-Anzeige
                    Text {
                        text: "Seite " + (fahrzeugBackendV2 ? (fahrzeugBackendV2.currentPage + 1) : 1) + " von " + (fahrzeugBackendV2 ? Math.ceil(fahrzeugBackendV2.totalVehicles / fahrzeugBackendV2.pageSize) : 1)
                        font.family: ubuntuFont.name
                        font.pixelSize: 14
                        color: "#cccccc"
                    }
                    
                    // Weiter-Button
                    Rectangle {
                        width: 40
                        height: 40
                        radius: 20
                        color: "transparent"
                        border.width: 0
                        
                        MouseArea {
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            enabled: fahrzeugBackendV2 && fahrzeugBackendV2.currentPage < Math.ceil(fahrzeugBackendV2.totalVehicles / fahrzeugBackendV2.pageSize) - 1
                            onClicked: fahrzeugBackendV2.loadNextPage()
                            
                            Image {
                                anchors.centerIn: parent
                                source: parent.enabled && parent.containsMouse ? "assets/icons/close_orange.svg" : "assets/icons/close_gray.svg"
                                width: parent.enabled && parent.containsMouse ? 24 : 20
                                height: width
                                fillMode: Image.PreserveAspectFit
                            }
                        }
                    }
                }
            }
            

            
                         delegate: Rectangle {
                 id: vehicleCard
                 width: 380
                 height: 280
                 radius: Style.radiusNormal
                 color: "transparent"
                 border.width: 0
                 z: 1 // Standard Z-Index für normale Cards
                 
                 // Hover-Effekt: Vergrößerung um 1.05x
                 property real hoverScale: (vehicleCardMouseArea.containsMouse || statusBadgeMouseArea.containsMouse || editButtonMouseArea.containsMouse || deleteButtonMouseArea.containsMouse) ? 1.05 : 1.0
                 
                 // Transform mit Zentrierung
                 transform: Scale {
                     xScale: vehicleCard.hoverScale
                     yScale: vehicleCard.hoverScale
                     origin.x: vehicleCard.width / 2
                     origin.y: vehicleCard.height / 2
                 }
                 
                 // Animation für smooth Übergänge
                 Behavior on hoverScale {
                     NumberAnimation { 
                         duration: 150
                         easing.type: Easing.OutCubic
                     }
                 }
            
                property bool selected: {
                    if (!fahrzeugBackendV2 || !fahrzeugBackendV2.selectedVehicle || !modelData) return false
                    return fahrzeugBackendV2.selectedVehicle.kennzeichen === modelData.kennzeichen
                }
                
                // Gradient-Hintergrund (wie in Abrechnungsseite)
                Rectangle {
                    anchors.fill: parent
                    radius: Style.radiusNormal
                    gradient: Gradient {
                        GradientStop { position: 0.0; color: "#050505" }
                        GradientStop { position: 0.8; color: "#050505" }
                        GradientStop { position: 1.0; color: "#1a1a1a" }
                    }
                    z: -1
                }
                
                                 MouseArea {
                     id: vehicleCardMouseArea
                     anchors.fill: parent
                     hoverEnabled: true
                     onClicked: fahrzeugBackendV2.selectVehicle(modelData.kennzeichen)
                     onDoubleClicked: {
                         // Doppelklick: Edit-Modus mit vorausgefüllten Daten
                         showVehicleFormOverlayForEdit(modelData)
                     }
                 }
                
                // Card-Inhalt
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 12
                    
                    // Header mit Kennzeichen und Status
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 12
                        
                        Text {
                            text: modelData.kennzeichen || "Kein Kennzeichen"
                            font.family: ubuntuFont.name
                            font.pixelSize: 24
                            font.bold: true
                            color: "white"
                            Layout.fillWidth: true
                        }
                        
                        // Status-Badge (klickbar) - nur in normaler Ansicht
                        Rectangle {
                            Layout.preferredWidth: 80
                            height: 28
                            radius: 14
                            color: "transparent"
                            border.width: 0
                            visible: !fahrzeugBackendV2 || !fahrzeugBackendV2.isCalendarView
                            
                            MouseArea {
                                id: statusBadgeMouseArea
                                anchors.fill: parent
                                hoverEnabled: true
                                cursorShape: Qt.PointingHandCursor
                                onClicked: {
                                    // Status-Toggle: Aktiv → Wartung → Inaktiv → Aktiv
                                    var currentStatus = modelData.status || "Aktiv"
                                    var newStatus
                                    if (currentStatus === "Aktiv") newStatus = "Wartung"
                                    else if (currentStatus === "Wartung") newStatus = "Inaktiv"
                                    else newStatus = "Aktiv"
                                    
                                    // Backend-Methode zum Aktualisieren des Status
                                    fahrzeugBackendV2.updateVehicleStatus(modelData.kennzeichen, newStatus)
                                }
                            }
                            
                            Text {
                                anchors.centerIn: parent
                                text: modelData.status || "Aktiv"
                                font.family: ubuntuFont.name
                                font.pixelSize: 12
                                color: {
                                    if (modelData.status === "Aktiv") return "#4CAF50"
                                    else if (modelData.status === "Wartung") return "#9E9E9E"
                                    else return "#F44336"
                                }
                                horizontalAlignment: Text.AlignCenter
                            }
                        }
                    }
                    
                    // Fahrzeug-Details oder Kalenderwochen
                    Item {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        
                                                 // Normale Fahrzeug-Details
                         GridLayout {
                             anchors.fill: parent
                             columns: 2
                             rowSpacing: 8
                             columnSpacing: 16
                             visible: !fahrzeugBackendV2 || !fahrzeugBackendV2.isCalendarView
                             
                             // Modell und Baujahr in einer Zeile
                             Text {
                                 text: "Modell/Baujahr:"
                                 font.family: ubuntuFont.name
                                 font.pixelSize: 14
                                 color: "#b0b0b0"
                             }
                             
                             // Modell und Baujahr
                             Text {
                                 Layout.fillWidth: true
                                 height: 32
                                 text: (modelData.modell || "-") + " / " + (modelData.baujahr || "-")
                                 font.family: ubuntuFont.name
                                 font.pixelSize: 14
                                 color: "white"
                                 verticalAlignment: Text.AlignVCenter
                             }
                             
                             // Stammfahrer
                             Text {
                                 text: "Stammfahrer:"
                                 font.family: ubuntuFont.name
                                 font.pixelSize: 14
                                 color: "#b0b0b0"
                             }
                             
                             Text {
                                 Layout.fillWidth: true
                                 height: 32
                                 text: modelData.stammfahrer || "-"
                                 font.family: ubuntuFont.name
                                 font.pixelSize: 14
                                 color: "white"
                                 verticalAlignment: Text.AlignVCenter
                             }
                             
                             // Referenz
                             Text {
                                 text: "Referenz:"
                                 font.family: ubuntuFont.name
                                 font.pixelSize: 14
                                 color: "#b0b0b0"
                             }
                             
                             Text {
                                 Layout.fillWidth: true
                                 height: 32
                                 text: modelData.rfrnc || "-"
                                 font.family: ubuntuFont.name
                                 font.pixelSize: 14
                                 color: "white"
                                 verticalAlignment: Text.AlignVCenter
                             }
                             
                             // Versicherung
                             Text {
                                 text: "Versicherung:"
                                 font.family: ubuntuFont.name
                                 font.pixelSize: 14
                                 color: "#b0b0b0"
                             }
                             
                             Text {
                                 Layout.fillWidth: true
                                 height: 32
                                 text: modelData.versicherung ? modelData.versicherung + " €" : "-"
                                 font.family: ubuntuFont.name
                                 font.pixelSize: 14
                                 color: "white"
                                 verticalAlignment: Text.AlignVCenter
                             }
                             
                             // Finanzierung
                             Text {
                                 text: "Finanzierung:"
                                 font.family: ubuntuFont.name
                                 font.pixelSize: 14
                                 color: "white"
                             }
                             
                             Text {
                                 Layout.fillWidth: true
                                 height: 32
                                 text: modelData.finanzierung ? modelData.finanzierung + " €" : "-"
                                 font.family: ubuntuFont.name
                                 font.pixelSize: 14
                                 color: "white"
                                 verticalAlignment: Text.AlignVCenter
                             }
                             
                             // Notizen (falls vorhanden)
                             Text {
                                 text: "Notizen:"
                                 font.family: ubuntuFont.name
                                 font.pixelSize: 14
                                 color: "#b0b0b0"
                                 visible: modelData.notizen && modelData.notizen !== ""
                             }
                             
                             Text {
                                 Layout.fillWidth: true
                                 height: 32
                                 text: modelData.notizen || "-"
                                 font.family: ubuntuFont.name
                                 font.pixelSize: 12
                                 color: "#cccccc"
                                 visible: modelData.notizen && modelData.notizen !== ""
                                 verticalAlignment: Text.AlignVCenter
                             }
                            
                            
                        }
                        
                        // Kalenderwochen-Grid
                        GridLayout {
                            anchors.fill: parent
                            columns: Math.min(12, (modelData.calendar_weeks ? modelData.calendar_weeks.length : 0) + 1)  // Dynamische Spalten
                            rowSpacing: 2
                            columnSpacing: 2
                            visible: fahrzeugBackendV2 && fahrzeugBackendV2.isCalendarView
                            
                            // Kalenderwochen-Daten
                            Repeater {
                                model: modelData.calendar_weeks || []
                                
                                Text {
                                    width: 24
                                    height: 24
                                    text: modelData.week.toString()
                                    font.family: ubuntuFont.name
                                    font.pixelSize: 12
                                    font.bold: true
                                    color: modelData.has_data ? "#4CAF50" : "#F44336"
                                    horizontalAlignment: Text.AlignHCenter
                                    verticalAlignment: Text.AlignVCenter
                                    
                                    // Tooltip
                                    ToolTip {
                                        text: "KW " + modelData.week + ": " + (modelData.has_data ? "Daten vorhanden" : "Keine Daten")
                                        visible: parentMouseArea.containsMouse
                                    }
                                    
                                    MouseArea {
                                        id: parentMouseArea
                                        anchors.fill: parent
                                        hoverEnabled: true
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: {
                                            // Kalenderwoche wurde geklickt
                                            console.log("Kalenderwoche geklickt:", modelData.week, "has_data:", modelData.has_data)
                                            if (modelData.has_data) {
                                                // Daten vorhanden: QML-Overlay anzeigen
                                                console.log("Zeige QML-Overlay für:", modelData.week)
                                                var vehicleKennzeichen = modelData.kennzeichen || ""
                                                console.log("Fahrzeug-Kennzeichen:", vehicleKennzeichen)
                                                showWeekDataOverlay(vehicleKennzeichen, modelData.week)
                                            } else {
                                                // Keine Daten: Neuen Eintrag erstellen
                                                console.log("Erstelle neuen Eintrag für:", modelData.week)
                                                var vehicleKennzeichen = modelData.kennzeichen || ""
                                                fahrzeugBackendV2.createWeekDataEntry(vehicleKennzeichen, modelData.week)
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                    
                                         // Aktions-Buttons (rechts)
                     RowLayout {
                         Layout.fillWidth: true
                         spacing: 8
                         
                         // Spacer um Buttons nach rechts zu schieben
                         Item {
                             Layout.fillWidth: true
                         }
                         
                         // Edit/Check-Button
                         Rectangle {
                             Layout.preferredWidth: 32
                             height: 32
                             radius: 16
                             color: "transparent"
                             border.width: 0
                             
                             MouseArea {
                                 id: editButtonMouseArea
                                 anchors.fill: parent
                                 hoverEnabled: true
                                 onClicked: {
                                     // Hier könnte eine andere Aktion hinzugefügt werden
                                     console.log("Edit-Button geklickt für:", modelData.kennzeichen)
                                 }
                                 
                                 Image {
                                     anchors.centerIn: parent
                                     source: parent.containsMouse ? "assets/icons/edit_orange.svg" : "assets/icons/edit_white.svg"
                                     width: parent.containsMouse ? 20 : 16
                                     height: width
                                     fillMode: Image.PreserveAspectFit
                                 }
                             }
                         }
                         
                         // Delete-Button
                         Rectangle {
                             Layout.preferredWidth: 32
                             height: 32
                             radius: 16
                             color: "transparent"
                             border.width: 0
                             
                             MouseArea {
                                 id: deleteButtonMouseArea
                                 anchors.fill: parent
                                 hoverEnabled: true
                                 onClicked: {
                                     // Bestätigungsdialog anzeigen
                                     deleteConfirmDialog.licensePlate = modelData.kennzeichen
                                     deleteConfirmDialog.visible = true
                                 }
                                 
                                 Image {
                                     anchors.centerIn: parent
                                     source: parent.containsMouse ? "assets/icons/delete_orange.svg" : "assets/icons/delete_white.svg"
                                     width: parent.containsMouse ? 20 : 16
                                     height: width
                                     fillMode: Image.PreserveAspectFit
                                 }
                             }
                         }
                     }
                }
            }
        }
    }
    
    // BottomBar mit erweiterten Aktionen
    RowLayout {
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 24
        spacing: 32
        

        
        // Add-Button
        MouseArea {
            id: addArea
            width: 56; height: 56
            cursorShape: Qt.PointingHandCursor
            hoverEnabled: true
            onClicked: showVehicleFormOverlay()
            Image {
                anchors.centerIn: parent
                source: addArea.pressed ? "assets/icons/add_gray.svg"
                    : addArea.containsMouse ? "assets/icons/add_orange.svg" : "assets/icons/add_white.svg"
                width: addArea.pressed ? 40 : addArea.containsMouse ? 48 : 40
                height: width
                fillMode: Image.PreserveAspectFit
            }
        }
        

    }

    // Funktion zum Anzeigen des QML-Overlays
    function showWeekDataOverlay(licensePlate, week) {
        overlayTitle.text = "KW " + week + " - " + licensePlate
        
        // Backend-Methode aufrufen, um Daten zu laden
        fahrzeugBackendV2.loadWeekDataForOverlay(licensePlate, week)
        
        // Overlay anzeigen
        weekDataOverlay.visible = true
        weekDataOverlay.forceActiveFocus()
    }
    
         // Funktion zum Anzeigen des Fahrzeug-Formular-Overlays
     function showVehicleFormOverlay() {
         // Reset alle Felder für neues Fahrzeug
         licensePlateField.text = ""
         referenceField.text = ""
         modelField.text = ""
         yearField.text = ""
         insuranceField.text = ""
         creditField.text = ""
         statusField.currentIndex = 0
         stammfahrerField.text = ""
         notesField.text = ""
         
         // Titel ändern
         vehicleFormTitle.text = "Neues Fahrzeug anlegen"
         
         vehicleFormOverlay.visible = true
         vehicleFormOverlay.forceActiveFocus()
     }
     
     // Funktion zum Anzeigen des Fahrzeug-Formular-Overlays im Edit-Modus
     function showVehicleFormOverlayForEdit(vehicleData) {
         // Felder mit Fahrzeugdaten vorausfüllen
         licensePlateField.text = vehicleData.kennzeichen || ""
         referenceField.text = vehicleData.rfrnc || ""
         modelField.text = vehicleData.modell || ""
         yearField.text = vehicleData.baujahr || ""
         insuranceField.text = vehicleData.versicherung || ""
         creditField.text = vehicleData.finanzierung || ""
         stammfahrerField.text = vehicleData.stammfahrer || ""
         notesField.text = vehicleData.notizen || ""
         
         // Status setzen
         var statusIndex = 0
         if (vehicleData.status === "Wartung") statusIndex = 1
         else if (vehicleData.status === "Inaktiv") statusIndex = 2
         statusField.currentIndex = statusIndex
         
         // Titel ändern
         vehicleFormTitle.text = "Fahrzeug bearbeiten: " + vehicleData.kennzeichen
         
         vehicleFormOverlay.visible = true
         vehicleFormOverlay.forceActiveFocus()
     }
    
    // Overlay für Fahrzeug-Formular
    Rectangle {
        id: vehicleFormOverlay
        anchors.fill: parent
        color: "#000000"
        opacity: 0.8
        visible: false
        z: 2000
        
        MouseArea {
            anchors.fill: parent
            onClicked: vehicleFormOverlay.visible = false
        }
        
        Rectangle {
            anchors.centerIn: parent
            width: Math.min(parent.width * 0.4, 400)
            height: Math.min(parent.height * 0.8, 600)
            color: "#1a1a1a"
            border.color: "#333333"
            border.width: 1
            radius: 8
            
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 20
                spacing: 16
                
                // Header
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 16
                    
                                         Text {
                         id: vehicleFormTitle
                         text: "Neues Fahrzeug anlegen"
                         font.family: ubuntuFont.name
                         font.pixelSize: 24
                         font.bold: true
                         color: "white"
                         Layout.fillWidth: true
                         visible: !text.includes("bearbeiten")
                     }
                    
                                         // Close-Icon entfernt - wird unten verwendet
                }
                
                // Abstand zwischen Titel und Formular
                Item {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 20
                }
                
                // Formular
                ScrollView {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    
                    GridLayout {
                        width: parent.width
                        anchors.horizontalCenter: parent.horizontalCenter
                        columns: 2
                        rowSpacing: 12
                        columnSpacing: 16
                        
                        // Kennzeichen
                        Text {
                            text: "Kennzeichen *"
                            font.family: ubuntuFont.name
                            font.pixelSize: 14
                            color: "white"
                            font.bold: true
                            horizontalAlignment: Text.AlignRight
                            Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
                        }
                        
                        TextField {
                            id: licensePlateField
                            Layout.fillWidth: true
                            height: 48
                            font.family: ubuntuFont.name
                            font.pixelSize: 16
                            color: "white"
                            background: Rectangle {
                                color: "#2a2a2a"
                                border.color: "#555555"
                                border.width: 1
                                radius: 6
                            }
                            placeholderText: "z.B. W135CTX"
                        }
                        
                        // Referenz
                        Text {
                            text: "Referenz"
                            font.family: ubuntuFont.name
                            font.pixelSize: 14
                            color: "white"
                            font.bold: true
                            horizontalAlignment: Text.AlignRight
                            Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
                        }
                        
                        TextField {
                            id: referenceField
                            Layout.fillWidth: true
                            height: 48
                            font.family: ubuntuFont.name
                            font.pixelSize: 16
                            color: "white"
                            background: Rectangle {
                                color: "#2a2a2a"
                                border.color: "#555555"
                                border.width: 1
                                radius: 6
                            }
                            placeholderText: "Referenz-Nummer"
                        }
                        
                        // Modell
                        Text {
                            text: "Modell"
                            font.family: ubuntuFont.name
                            font.pixelSize: 14
                            color: "white"
                            font.bold: true
                            horizontalAlignment: Text.AlignRight
                            Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
                        }
                        
                        TextField {
                            id: modelField
                            Layout.fillWidth: true
                            height: 48
                            font.family: ubuntuFont.name
                            font.pixelSize: 16
                            color: "white"
                            background: Rectangle {
                                color: "#2a2a2a"
                                border.color: "#555555"
                                border.width: 1
                                radius: 6
                            }
                            placeholderText: "z.B. Mercedes Sprinter"
                        }
                        
                        // Baujahr
                        Text {
                            text: "Baujahr"
                            font.family: ubuntuFont.name
                            font.pixelSize: 14
                            color: "white"
                            font.bold: true
                            horizontalAlignment: Text.AlignRight
                            Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
                        }
                        
                        TextField {
                            id: yearField
                            Layout.fillWidth: true
                            height: 48
                            font.family: ubuntuFont.name
                            font.pixelSize: 16
                            color: "white"
                            background: Rectangle {
                                color: "#2a2a2a"
                                border.color: "#555555"
                                border.width: 1
                                radius: 6
                            }
                            placeholderText: "z.B. 2020"
                        }
                        
                        // Versicherung
                        Text {
                            text: "Versicherung (€)"
                            font.family: ubuntuFont.name
                            font.pixelSize: 14
                            color: "white"
                            font.bold: true
                            horizontalAlignment: Text.AlignRight
                            Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
                        }
                        
                        TextField {
                            id: insuranceField
                            Layout.fillWidth: true
                            height: 48
                            font.family: ubuntuFont.name
                            font.pixelSize: 16
                            color: "white"
                            background: Rectangle {
                                color: "#2a2a2a"
                                border.color: "#555555"
                                border.width: 1
                                radius: 6
                            }
                            placeholderText: "0.00"
                        }
                        
                        // Finanzierung
                        Text {
                            text: "Finanzierung (€)"
                            font.family: ubuntuFont.name
                            font.pixelSize: 14
                            color: "white"
                            font.bold: true
                            horizontalAlignment: Text.AlignRight
                            Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
                        }
                        
                        TextField {
                            id: creditField
                            Layout.fillWidth: true
                            height: 48
                            font.family: ubuntuFont.name
                            font.pixelSize: 16
                            color: "white"
                            background: Rectangle {
                                color: "#2a2a2a"
                                border.color: "#555555"
                                border.width: 1
                                radius: 6
                            }
                            placeholderText: "0.00"
                        }
                        
                        // Status
                        Text {
                            text: "Status"
                            font.family: ubuntuFont.name
                            font.pixelSize: 14
                            color: "white"
                            font.bold: true
                            horizontalAlignment: Text.AlignRight
                            Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
                        }
                        
                        ComboBox {
                            id: statusField
                            Layout.fillWidth: true
                            height: 48
                            font.family: ubuntuFont.name
                            font.pixelSize: 16
                            background: Rectangle {
                                color: "#2a2a2a"
                                border.color: "#555555"
                                border.width: 1
                                radius: 6
                            }
                            model: ["Aktiv", "Wartung", "Inaktiv"]
                            currentIndex: 0
                        }
                        
                        // Stammfahrer
                        Text {
                            text: "Stammfahrer"
                            font.family: ubuntuFont.name
                            font.pixelSize: 14
                            color: "white"
                            font.bold: true
                            horizontalAlignment: Text.AlignRight
                            Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
                        }
                        
                        TextField {
                            id: stammfahrerField
                            Layout.fillWidth: true
                            height: 48
                            font.family: ubuntuFont.name
                            font.pixelSize: 16
                            color: "white"
                            background: Rectangle {
                                color: "#2a2a2a"
                                border.color: "#555555"
                                border.width: 1
                                radius: 6
                            }
                            placeholderText: "z.B. Mustermann"
                        }
                        
                        // Notizen
                        Text {
                            text: "Notizen"
                            font.family: ubuntuFont.name
                            font.pixelSize: 14
                            color: "white"
                            font.bold: true
                            horizontalAlignment: Text.AlignRight
                            Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
                        }
                        
                        TextArea {
                            id: notesField
                            Layout.fillWidth: true
                            Layout.preferredHeight: 80
                            font.family: ubuntuFont.name
                            font.pixelSize: 16
                            color: "white"
                            background: Rectangle {
                                color: "#2a2a2a"
                                border.color: "#555555"
                                border.width: 1
                                radius: 6
                            }
                            placeholderText: "Zusätzliche Notizen..."
                            wrapMode: TextArea.Wrap
                        }
                    }
                }
                
                // Buttons mit Icons
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 16
                    
                    Item { Layout.fillWidth: true }
                    
                    // Abbrechen-Button mit Close-Icon
                    Rectangle {
                        width: 48
                        height: 48
                        radius: 24
                        color: "transparent"
                        border.width: 0
                        
                        MouseArea {
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: vehicleFormOverlay.visible = false
                            
                            Image {
                                anchors.centerIn: parent
                                source: parent.containsMouse ? "assets/icons/close_red.svg" : "assets/icons/close_gray.svg"
                                width: parent.containsMouse ? 32 : 28
                                height: width
                                fillMode: Image.PreserveAspectFit
                            }
                        }
                    }
                    
                    // Speichern-Button mit Save-Icon
                    Rectangle {
                        width: 48
                        height: 48
                        radius: 24
                        color: "transparent"
                        border.width: 0
                        
                        MouseArea {
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                                                         onClicked: {
                                 // Validierung
                                 if (!licensePlateField.text.trim()) {
                                     console.log("Fehler: Kennzeichen ist erforderlich!")
                                     return
                                 }
                                 
                                 // Daten sammeln
                                 var vehicleData = {
                                     license_plate: licensePlateField.text.trim(),
                                     rfrnc: referenceField.text.trim(),
                                     model: modelField.text.trim(),
                                     year: yearField.text.trim(),
                                     insurance: insuranceField.text.trim(),
                                     credit: creditField.text.trim(),
                                     status: statusField.currentText,
                                     stammfahrer: stammfahrerField.text.trim(),
                                     notes: notesField.text.trim()
                                 }
                                 
                                 // Prüfen ob es sich um Edit oder Neues Fahrzeug handelt
                                 var isEditMode = vehicleFormTitle.text.includes("bearbeiten")
                                 
                                 if (isEditMode) {
                                     // Edit-Modus: Fahrzeug aktualisieren
                                     fahrzeugBackendV2.updateVehicleFromForm(vehicleData)
                                 } else {
                                     // Neues Fahrzeug: Speichern
                                     fahrzeugBackendV2.saveVehicleFromForm(vehicleData)
                                 }
                                 
                                 // Overlay schließen
                                 vehicleFormOverlay.visible = false
                                 
                                 // Felder zurücksetzen
                                 licensePlateField.text = ""
                                 referenceField.text = ""
                                 modelField.text = ""
                                 yearField.text = ""
                                 insuranceField.text = ""
                                 creditField.text = ""
                                 statusField.currentIndex = 0
                                 stammfahrerField.text = ""
                                 notesField.text = ""
                             }
                            
                            Image {
                                anchors.centerIn: parent
                                source: parent.containsMouse ? "assets/icons/save_orange.svg" : "assets/icons/save_white.svg"
                                width: parent.containsMouse ? 32 : 28
                                height: width
                                fillMode: Image.PreserveAspectFit
                            }
                        }
                    }
                }
            }
            
            // ESC-Taste zum Schließen
            Keys.onEscapePressed: vehicleFormOverlay.visible = false
        }
    }

         // Connections für Backend-Signale
     Connections {
         target: fahrzeugBackendV2
         
         function onWeekDataLoaded(licensePlate, week, revenueData, runningCostsData) {
             // Revenue-Daten setzen
             revenueDataRepeater.model = revenueData || []
             
             // Running-Costs-Daten setzen
             runningCostsDataRepeater.model = runningCostsData || []
         }
         
         function onAskDeleteRunningCosts(licensePlate, week, count) {
             // Bestätigungsdialog für Running-Costs anzeigen
             deleteRunningCostsDialog.licensePlate = licensePlate
             deleteRunningCostsDialog.week = week
             deleteRunningCostsDialog.count = count
             deleteRunningCostsDialog.visible = true
         }
         
         // Neuer Error-Handler (sehr vorsichtig hinzugefügt)
         function onErrorOccurred(errorMessage) {
             console.log("Error-Signal empfangen:", errorMessage)
             errorMessage.text = errorMessage || "Ein unbekannter Fehler ist aufgetreten"
             errorOverlay.visible = true
         }
     }
} 