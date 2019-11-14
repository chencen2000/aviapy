#-------------------------------------------------
#
# Project created by QtCreator 2019-01-18T20:19:52
#
#-------------------------------------------------
QT       += widgets
CONFIG(debug, debug|release){
TARGET = CAlgDarkDefectInspectParamD
}else{
TARGET = CAlgDarkDefectInspectParam
}

TEMPLATE = lib
CONFIG += dll


DEFINES += ALGINSPECT_EXPORT
DESTDIR += $$PWD/Bin
# The following define makes your compiler emit warnings if you use
# any feature of Qt which has been marked as deprecated (the exact warnings
# depend on your compiler). Please consult the documentation of the
# deprecated API in order to know how to port your code away from it.
DEFINES += QT_DEPRECATED_WARNINGS

# You can also make your code fail to compile if you use deprecated APIs.
# In order to do so, uncomment the following line.
# You can also select to disable deprecated APIs only up to a certain version of Qt.
#DEFINES += QT_DISABLE_DEPRECATED_BEFORE=0x060000    # disables all the APIs deprecated before Qt 6.0.0

SOURCES += \
        AlgInspectParamImpl.cpp





HEADERS += \
        AlgInspectParamImpl.h \
    AlgUpperSurfaceInspectParam.h


LIBS += -L$$PWD/Lib/halcon/ -lhalconcpp


INCLUDEPATH += $$PWD/Inc/halcon
INCLUDEPATH += $$PWD/Inc/halcon/halconcpp
INCLUDEPATH += $$PWD/Inc
DEPENDPATH += $$PWD/Inc/halcon/halconcpp


unix {
    target.path = /usr/lib
    INSTALLS += target
}
