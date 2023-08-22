#pragma once

#include <QObject>

class QRenderThread : public QObject
{
    public:
        QRenderThread();
        ~QRenderThread();

    public slots:
        void run();
};