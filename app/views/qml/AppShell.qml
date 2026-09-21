import QtQuick
import QtQuick.Layouts

Item {
    RowLayout {
        anchors.fill: parent
        spacing: 0

        Sidebar {
            Layout.preferredWidth: 260
            Layout.fillHeight: true
        }

        MainView {
            Layout.fillWidth: true
            Layout.fillHeight: true
        }
    }
}
