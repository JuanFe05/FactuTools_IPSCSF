import QtQuick
import QtQuick.Layouts

Rectangle {
    id: root
    width: 260

    property string vistaActual: "renombrar"
    signal vistaSeleccionada(string vista)

    readonly property var opcionesMenu: [
        { id: "renombrar", texto: "Renombramiento de soportes" },
        { id: "separacionFurips", texto: "Separación de FURIPS" }
    ]

    gradient: Gradient {
        orientation: Gradient.Vertical
        GradientStop { position: 0.0; color: "#1938bc" }
        GradientStop { position: 1.0; color: "#000000" }
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 24
        spacing: 32

        ColumnLayout {
            spacing: 4
            Layout.fillWidth: true

            Text {
                text: (typeof AppCtl !== "undefined" && AppCtl) ? AppCtl.clinicName : "IPS Clínica Salud Florida"
                color: Theme.background
                font.pixelSize: 15
                font.bold: true
                wrapMode: Text.WordWrap
                horizontalAlignment: Text.AlignHCenter
                Layout.fillWidth: true
            }

            Text {
                text: (typeof AppCtl !== "undefined" && AppCtl) ? AppCtl.appName : "FactuTools"
                color: "#c7d0f5"
                font.pixelSize: 12
                horizontalAlignment: Text.AlignHCenter
                Layout.fillWidth: true
            }
        }

        ColumnLayout {
            Layout.fillWidth: true
            spacing: 8

            Repeater {
                model: root.opcionesMenu

                delegate: Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 48
                    radius: 8
                    color: root.vistaActual === modelData.id ? "#2947c9" : "transparent"

                    RowLayout {
                        anchors.fill: parent
                        anchors.leftMargin: 12
                        anchors.rightMargin: 12
                        spacing: 10

                        Rectangle {
                            Layout.preferredWidth: 4
                            Layout.fillHeight: true
                            radius: 2
                            color: root.vistaActual === modelData.id ? Theme.background : "transparent"
                        }

                        Text {
                            text: modelData.texto
                            color: root.vistaActual === modelData.id ? Theme.background : "#c7d0f5"
                            font.pixelSize: 13
                            font.bold: root.vistaActual === modelData.id
                            wrapMode: Text.WordWrap
                            Layout.fillWidth: true
                        }
                    }

                    MouseArea {
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor
                        onClicked: root.vistaSeleccionada(modelData.id)
                    }
                }
            }
        }

        Item { Layout.fillHeight: true }

        Text {
            text: (typeof AppCtl !== "undefined" && AppCtl) ? ("v" + AppCtl.appVersion) : ""
            color: "#8b94c9"
            font.pixelSize: 11
            Layout.alignment: Qt.AlignHCenter
        }
    }
}
