add_library(gui
    MainWindow.cc 
    QtAov.cc
    QtAovBuffer.cc
    QRenderThread.cc
)

find_package(Qt5 REQUIRED COMPONENTS Gui Widgets)

target_link_libraries(gui
    PRIVATE rndr
    PUBLIC Qt5::Gui
    PUBLIC Qt5::Widgets
)
