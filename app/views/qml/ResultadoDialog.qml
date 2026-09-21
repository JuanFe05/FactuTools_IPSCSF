import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Dialog {
    id: root
    modal: true
    standardButtons: Dialog.NoButton
    width: 520
    anchors.centerIn: Overlay.overlay

    property bool exito: true
    property var resumen: ({})

    readonly property bool esRenombrado: root.resumen.accion === "renombrar"

    title: root.esRenombrado
        ? (root.exito ? "Renombrado completado" : "Renombrado finalizado con inconsistencias")
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

        // Sección: Análisis
        ColumnLayout {
            Layout.fillWidth: true
            Layout.preferredHeight: root.esRenombrado ? 130 : 120
            spacing: 8

            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 4
                color: Theme.primary
                radius: 2
            }

            Text {
                text: "Análisis"
                font.pixelSize: 13
                font.bold: true
                color: Theme.primary
            }

            ColumnLayout {
                Layout.fillWidth: true
                spacing: 6

                Text {
                    text: "✓ " + (root.resumen.subcarpetas || 0) + " subcarpetas encontradas"
                    font.pixelSize: 12
                    color: Theme.text
                }
                Text {
                    text: "✓ " + (root.resumen.registrosEncontrados || 0) + " registros encontrados"
                    font.pixelSize: 12
                    color: Theme.success
                    font.bold: true
                }
                Text {
                    visible: (root.resumen.registrosNoEncontrados || 0) > 0
                    text: "⚠ " + (root.resumen.registrosNoEncontrados || 0) + " registros sin coincidencia"
                    font.pixelSize: 12
                    color: Theme.danger
                }
            }
        }

        // Sección: Ejecución (solo si fue renombrado)
        ColumnLayout {
            visible: root.esRenombrado
            Layout.fillWidth: true
            Layout.preferredHeight: visible ? 140 : 0
            Layout.topMargin: 16
            spacing: 8

            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 4
                color: root.exito ? Theme.success : Theme.danger
                radius: 2
            }

            Text {
                text: root.exito ? "Ejecución exitosa" : "Ejecución con errores"
                font.pixelSize: 13
                font.bold: true
                color: root.exito ? Theme.success : Theme.danger
            }

            ColumnLayout {
                Layout.fillWidth: true
                spacing: 6

                Text {
                    text: "✓ " + (root.resumen.carpetasRenombradas || 0) + " carpetas renombradas"
                    font.pixelSize: 12
                    color: Theme.success
                    font.bold: true
                }
                Text {
                    text: "✓ " + (root.resumen.archivosRenombrados || 0) + " archivos renombrados"
                    font.pixelSize: 12
                    color: Theme.success
                    font.bold: true
                }
                Text {
                    visible: (root.resumen.subcarpetasConError || 0) > 0
                    text: "✗ " + (root.resumen.subcarpetasConError || 0) + " subcarpeta" + ((root.resumen.subcarpetasConError || 0) !== 1 ? "s" : "") + " con errores"
                    font.pixelSize: 12
                    color: Theme.danger
                    font.bold: true
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
