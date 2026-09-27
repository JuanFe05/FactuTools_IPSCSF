import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Dialog {
    id: root
    title: "¿Deseas iniciar el proceso de renombramiento?"
    modal: true
    standardButtons: Dialog.NoButton
    width: 420
    anchors.centerIn: Overlay.overlay

    property string empresa: ""
    property var renombrarCtl: (typeof RenombrarCtl !== "undefined") ? RenombrarCtl : null

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

        Text { text: "Empresa: " + root.empresa; color: Theme.text }
        Text {
            text: "Carpeta: " + (root.renombrarCtl ? root.renombrarCtl.carpetaSeleccionada : "")
            color: Theme.text
            wrapMode: Text.WrapAnywhere
            Layout.fillWidth: true
        }
        Text {
            text: "Subcarpetas: " + (root.renombrarCtl ? root.renombrarCtl.totalSubcarpetas : 0)
            color: Theme.text
        }
        Text {
            text: "Archivos PDF: " + (root.renombrarCtl ? root.renombrarCtl.totalPdfs : 0)
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
                text: "Iniciar renombramiento"
                onClicked: {
                    root.confirmado()
                    root.close()
                }
            }
        }
    }
}
