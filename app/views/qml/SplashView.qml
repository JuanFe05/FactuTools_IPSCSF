import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: root
    color: Theme.background

    signal finalizado()

    readonly property var mensajes: [
        "Inicializando aplicación...",
        "Cargando configuración...",
        "Conectando con la base de datos...",
        "Verificando actualizaciones..."
    ]
    property int indiceMensaje: 0

    ColumnLayout {
        anchors.centerIn: parent
        spacing: 18

        Image {
            id: logo
            source: (typeof AppCtl !== "undefined" && AppCtl) ? AppCtl.logoUrl : "../resources/images/Logo.png"
            Layout.alignment: Qt.AlignHCenter
            Layout.preferredWidth: 140
            Layout.preferredHeight: 140
            fillMode: Image.PreserveAspectFit
            visible: status === Image.Ready
        }

        Text {
            text: (typeof AppCtl !== "undefined" && AppCtl) ? AppCtl.clinicName : "IPS Clínica Salud Florida"
            color: Theme.primaryDark
            font.pixelSize: 20
            font.bold: true
            Layout.alignment: Qt.AlignHCenter
        }

        Text {
            text: (typeof AppCtl !== "undefined" && AppCtl) ? AppCtl.appName : "FactuTools"
            color: Theme.primary
            font.pixelSize: 30
            font.bold: true
            Layout.alignment: Qt.AlignHCenter
        }

        Text {
            text: "Bienvenidos a " + ((typeof AppCtl !== "undefined" && AppCtl) ? AppCtl.appName : "FactuTools")
            color: Theme.text
            font.pixelSize: 15
            Layout.alignment: Qt.AlignHCenter
        }

        Text {
            text: "Cargando aplicación..."
            color: Theme.text
            font.pixelSize: 14
            font.bold: true
            Layout.alignment: Qt.AlignHCenter
            Layout.topMargin: 8
        }

        LoadingDots {
            Layout.alignment: Qt.AlignHCenter
        }

        Text {
            text: root.mensajes[root.indiceMensaje]
            color: Theme.text
            font.pixelSize: 12
            opacity: 0.7
            Layout.alignment: Qt.AlignHCenter
        }
    }

    Timer {
        interval: 650
        running: true
        repeat: true
        onTriggered: {
            if (root.indiceMensaje < root.mensajes.length - 1) {
                root.indiceMensaje += 1
            } else {
                stop()
                finalizarTimer.start()
            }
        }
    }

    Timer {
        id: finalizarTimer
        interval: 400
        onTriggered: root.finalizado()
    }
}
