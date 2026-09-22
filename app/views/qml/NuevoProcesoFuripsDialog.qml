import QtQuick
import QtQuick.Controls
import QtQuick.Dialogs
import QtQuick.Layouts

Dialog {
    id: root
    title: "Nuevo proceso"
    modal: true
    standardButtons: Dialog.NoButton
    width: 480
    anchors.centerIn: Overlay.overlay

    property var separacionCtl: (typeof SeparacionFuripsCtl !== "undefined") ? SeparacionFuripsCtl : null

    readonly property bool listoParaAnalizar: root.separacionCtl
        && root.separacionCtl.carpetaSeleccionada !== ""
        && !root.separacionCtl.procesando

    background: Rectangle {
        color: Theme.background
        radius: 16
        border.width: 1
        border.color: "#e5e8f0"
    }

    header: Label {
        text: root.title
        color: Theme.primaryDark
        font.pixelSize: 17
        font.bold: true
        padding: 20
        background: Rectangle { color: Theme.background; radius: 16 }
    }

    FolderDialog {
        id: dialogoCarpeta
        title: "Seleccionar carpeta con archivos FURIPS"
        onAccepted: if (root.separacionCtl) root.separacionCtl.seleccionarCarpeta(selectedFolder)
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 18

        // Sección — Carpeta
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 8

            Text {
                text: "Carpeta"
                font.bold: true
                font.pixelSize: 13
                color: Theme.primaryDark
            }

            RowLayout {
                Layout.fillWidth: true
                spacing: 8

                SecondaryButton {
                    text: "Seleccionar carpeta"
                    onClicked: dialogoCarpeta.open()
                }

                Text {
                    Layout.fillWidth: true
                    elide: Text.ElideMiddle
                    color: Theme.text
                    text: (root.separacionCtl && root.separacionCtl.carpetaSeleccionada)
                          ? root.separacionCtl.carpetaSeleccionada
                          : "Ninguna carpeta seleccionada"
                }
            }

            ColumnLayout {
                visible: root.separacionCtl && root.separacionCtl.carpetaSeleccionada !== ""
                spacing: 4
                Layout.fillWidth: true

                Text {
                    text: root.separacionCtl ? ("Archivos FURIPS encontrados: " + root.separacionCtl.totalTxtEncontrados) : ""
                    font.pixelSize: 12
                    color: Theme.text
                }
                Text {
                    text: root.separacionCtl && root.separacionCtl.erroresPrevios.length === 0
                          ? "Carpeta lista para analizar"
                          : "Carpeta con advertencias"
                    font.pixelSize: 12
                    font.bold: true
                    color: root.separacionCtl && root.separacionCtl.erroresPrevios.length === 0
                           ? Theme.success
                           : Theme.danger
                }
                Text {
                    visible: root.separacionCtl && root.separacionCtl.erroresPrevios.length > 0
                    text: root.separacionCtl ? ("Advertencias: " + root.separacionCtl.erroresPrevios.join(", ")) : ""
                    font.pixelSize: 12
                    color: Theme.danger
                    wrapMode: Text.WordWrap
                    Layout.fillWidth: true
                }
            }
        }

        Item { Layout.fillHeight: true }

        Rectangle { Layout.fillWidth: true; height: 1; color: "#e5e8f0" }

        // Sección — Acciones
        RowLayout {
            Layout.fillWidth: true
            spacing: 12

            Item { Layout.fillWidth: true }

            SecondaryButton {
                text: "Cancelar"
                onClicked: root.close()
            }
            PrimaryButton {
                text: "Analizar"
                cargando: root.separacionCtl ? root.separacionCtl.procesando : false
                textoCargando: "Analizando..."
                enabled: root.listoParaAnalizar
                onClicked: {
                    if (root.separacionCtl) root.separacionCtl.analizar()
                    root.close()
                }
            }
        }
    }
}
