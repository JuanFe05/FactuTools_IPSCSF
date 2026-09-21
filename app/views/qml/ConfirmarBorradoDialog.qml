import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Dialog {
    id: root
    title: "¿Estás seguro de que deseas borrar todos los datos del proceso actual?"
    modal: true
    standardButtons: Dialog.NoButton
    width: 420
    anchors.centerIn: Overlay.overlay

    signal confirmado()

    background: Rectangle {
        color: Theme.background
        radius: 16
        border.width: 1
        border.color: "#e5e8f0"
    }

    header: Label {
        text: root.title
        color: Theme.danger
        font.pixelSize: 15
        font.bold: true
        wrapMode: Text.WordWrap
        padding: 20
        background: Rectangle { color: Theme.background; radius: 16 }
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 10

        Text {
            text: "Se perderán la empresa, tipo de atención, fecha, carpeta y resultados del proceso actual."
            color: Theme.text
            wrapMode: Text.WordWrap
            Layout.fillWidth: true
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
                text: "Borrar todo"
                colorAcento: Theme.danger
                onClicked: {
                    root.confirmado()
                    root.close()
                }
            }
        }
    }
}
