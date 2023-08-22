#include "QRenderThread.h"

#include "../rndr/Arnold.h"

QRenderThread::QRenderThread()
{
    
}

QRenderThread::~QRenderThread()
{

}

void QRenderThread::run()
{
    renderAssScene("flakes.ass");
}