#pragma once

#include "QtAov.h"
#include "QtAovBuffer.h"

#include <QDialog>
#include <QGraphicsView>
#include <QThread>
#include <QMenuBar>

using namespace arnoldserver::gui;

class MainWindow : public QDialog
{
    private:
        const uint32_t DEFAULT_WINDOW_WIDTH = 960;
        const uint32_t DEFAULT_WINDOW_HEIGHT = 540;

        QThread thread;

        QMenuBar *menu;
        QGraphicsView *view;

    public:
        MainWindow();
        ~MainWindow();

        static QtAovBuffer buffer;

        static void updatePixmaps();

    public slots:
        void openExampleScene();
};