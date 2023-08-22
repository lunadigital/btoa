#include "MainWindow.h"

#include "QRenderThread.h"
#include "../rndr/Arnold.h"

#include <ai.h>

#include <QAction>
#include <QGroupBox>
#include <QObject>
#include <QSignalMapper>
#include <QTimer>
#include <QVBoxLayout>

QtAovBuffer MainWindow::buffer = QtAovBuffer();

MainWindow::MainWindow()
{
    setWindowTitle("Arnold RenderServer");
    resize(QSize(DEFAULT_WINDOW_WIDTH + 35, DEFAULT_WINDOW_HEIGHT + 90));

    QVBoxLayout *mainLayout = new QVBoxLayout(this);
    mainLayout->setContentsMargins(0, 0, 0, 0);

    // Configure menu bar
    menu = new QMenuBar(this);

    QMenu *file = new QMenu("File");
    file->addAction("Open...");
    file->addAction("Save As...");
    
    /*
    file->addSeparator();

    QSignalMapper *signalMapper = new QSignalMapper(this);
    
    QAction *cornellBoxAction = new QAction(tr("&Cornell Box"), this);
    QObject::connect(cornellBoxAction, &QAction::triggered, this, &MainWindow::openExampleScene);

    QMenu *examples = new QMenu("Example Scenes");
    examples->addAction(cornellBoxAction);
    
    file->addMenu(examples);
    */

    menu->addMenu(file);
    
    mainLayout->setMenuBar(menu);

    // Image viewer
    view = new QGraphicsView;
    mainLayout->addWidget(view);

    QGraphicsScene *scene = new QGraphicsScene;

    buffer.setResolution(960, 540);
    buffer.add(scene, "beauty", AI_TYPE_RGBA);

    view->setScene(scene);
    view->setStyleSheet("border: none; outline: none;");

    mainLayout->addWidget(view);

    // Status bar
    QGroupBox *statusbar = new QGroupBox;

    mainLayout->addWidget(statusbar);

    // Test render
    
    QTimer *timer = new QTimer(this);
    QObject::connect(timer, &QTimer::timeout, this, &MainWindow::updatePixmaps);
    timer->start(100);
}

MainWindow::~MainWindow()
{
    
}

void MainWindow::updatePixmaps()
{
    QtAov *beauty = buffer.findAovByName("beauty");
    if (beauty->redraw) beauty->draw();
}

void MainWindow::openExampleScene()
{
    QRenderThread *renderer = new QRenderThread();
    renderer->moveToThread(&thread);
    QObject::connect(&thread, &QThread::started, renderer, &QRenderThread::run);
    
    thread.start();
}