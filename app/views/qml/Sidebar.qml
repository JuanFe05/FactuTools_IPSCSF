import QtQuick
import QtQuick.Layouts

Rectangle {
    id: root
    width: 260

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
                Layout.fillWidth: true
            }

            Text {
                text: "FactuTools"
                color: "#c7d0f5"
                font.pixelSize: 12
            }
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 48
            radius: 8
            color: "#2947c9"

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 12
                anchors.rightMargin: 12
                spacing: 10

                Rectangle {
                    width: 4
                    Layout.fillHeight: true
                    radius: 2
                    color: Theme.background
                }

                Text {
                    text: "Renombramiento de soportes"
                    color: Theme.background
                    font.pixelSize: 13
                    font.bold: true
                    wrapMode: Text.WordWrap
                    Layout.fillWidth: true
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
