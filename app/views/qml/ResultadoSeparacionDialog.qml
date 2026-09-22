import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Dialog {
    id: root
    modal: true
    standardButtons: Dialog.NoButton
    width: 480
    anchors.centerIn: Overlay.overlay

    property bool exito: true
    property var resumen: ({})

    readonly property bool esSeparacion: root.resumen.accion === "separar"

    title: root.esSeparacion
        ? (root.exito ? "Separación completada" : "Separación finalizada con inconsistencias")
        : (root.exito ? "Análisis completado" : "Análisis finalizado con inconsistencias")

    background: Rectangle {
        color: Theme.background
        radius: 16
        border.width: 1
        border.color: "#e5e8f0"
    }

    header: Label {
        text: root.title
        color: root.exito ? Theme.success : Theme.danger
        font.pixelSize: 18
        font.bold: true
        wrapMode: Text.WordWrap
        padding: 20
        background: Rectangle { color: Theme.background; radius: 16 }
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 4
        spacing: 0

        ColumnLayout {
            Layout.fillWidth: true
            spacing: 8

            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 4
                color: Theme.primary
                radius: 2
            }

            Text {
                text: root.esSeparacion ? "Separación" : "Análisis"
                font.pixelSize: 13
                font.bold: true
                color: Theme.primary
            }

            ColumnLayout {
                Layout.fillWidth: true
                spacing: 6

                Text {
                    text: "✓ " + (root.resumen.totalTxt || 0) + " archivo(s) FURIPS encontrados"
                    font.pixelSize: 12
                    color: Theme.text
                }
                Text {
                    text: root.esSeparacion
                        ? ("✓ " + (root.resumen.carpetasCreadas || 0) + " carpeta(s) creadas")
                        : ("✓ " + (root.resumen.carpetasACrear || 0) + " carpeta(s) que se crearán")
                    font.pixelSize: 12
                    color: Theme.success
                    font.bold: true
                }
                Text {
                    visible: (root.resumen.facturasConError || 0) > 0
                    text: "⚠ " + (root.resumen.facturasConError || 0) + " factura(s) con error"
                    font.pixelSize: 12
                    color: Theme.danger
                }
            }
        }

        Item { Layout.fillHeight: true }

        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 1
            color: "#e5e8f0"
        }

        RowLayout {
            Layout.fillWidth: true
            Layout.topMargin: 12
            Layout.bottomMargin: 12
            Layout.leftMargin: 8
            Layout.rightMargin: 8

            Item { Layout.fillWidth: true }

            PrimaryButton {
                text: "Aceptar"
                onClicked: root.close()
            }
        }
    }
}
