import QtQuick

Row {
    id: root
    property color colorPunto: Theme.primary
    spacing: 10

    Repeater {
        model: 3

        delegate: Rectangle {
            width: 10
            height: 10
            radius: 5
            color: root.colorPunto
            opacity: 0.3

            SequentialAnimation on opacity {
                loops: Animation.Infinite
                PauseAnimation { duration: index * 150 }
                NumberAnimation { from: 0.3; to: 1.0; duration: 400 }
                NumberAnimation { from: 1.0; to: 0.3; duration: 400 }
            }
        }
    }
}
