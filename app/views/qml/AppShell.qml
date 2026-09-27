import QtQuick
import QtQuick.Layouts

Item {
    id: root
    property string vistaActual: "renombrar"

    RowLayout {
        anchors.fill: parent
        spacing: 0

        Sidebar {
            Layout.preferredWidth: 260
            Layout.fillHeight: true
            vistaActual: root.vistaActual
            onVistaSeleccionada: (vista) => root.vistaActual = vista
        }

        MainView {
            visible: root.vistaActual === "renombrar"
            Layout.fillWidth: true
            Layout.fillHeight: true
        }

        SeparacionFuripsView {
            visible: root.vistaActual === "separacionFurips"
            Layout.fillWidth: true
            Layout.fillHeight: true
        }
    }
}
