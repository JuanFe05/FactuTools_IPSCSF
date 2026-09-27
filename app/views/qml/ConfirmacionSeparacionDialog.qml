import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Dialog {
    id: root
    title: "¿Deseas iniciar el proceso de separación?"
    modal: true
    standardButtons: Dialog.NoButton
    width: 420
    anchors.centerIn: Overlay.overlay

    property var separacionCtl: (typeof SeparacionFuripsCtl !== "undefined") ? SeparacionFuripsCtl : null

    signal confirmado()

    background: Rectangle {
        color: Theme.background
        radius: 16
        border.width: 1
        border.color: "#e5e8f0"
    }

    header: Label {
        text: root.title
        color: Theme.primaryDark
        font.pixelSize: 16
        font.bold: true
        wrapMode: Text.WordWrap
        padding: 20
        background: Rectangle { color: Theme.background; radius: 16 }
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 10

        Text {
            text: "Carpeta: " + (root.separacionCtl ? root.separacionCtl.carpetaSeleccionada : "")
            color: Theme.text
            wrapMode: Text.WrapAnywhere
            Layout.fillWidth: true
        }
        Text {
            text: "Archivos FURIPS encontrados: " + (root.separacionCtl ? root.separacionCtl.totalTxtEncontrados : 0)
            color: Theme.text
        }
        Text {
            text: "Carpetas que se crearán: " + (root.separacionCtl ? root.separacionCtl.carpetasACrear : 0)
            color: Theme.text
        }

        Item { Layout.fillHeight: true }

        RowLayout {
            Layout.fillWidth: true
            spacing: 12

            Item { Layout.fillWidth: true }

            SecondaryButton {
                text: "Cancelar"
                onClicked: root.close()
            }
            PrimaryButton {
                text: "Iniciar separación"
                onClicked: {
                    root.confirmado()
                    root.close()
                }
            }
        }
    }
}
