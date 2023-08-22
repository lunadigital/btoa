add_library(rndr
    Arnold.cc
    AtAov.cc
    AtRenderData.cc
)

set(ARNOLD_SDK_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../arnold)

add_library(driver SHARED driver.cc)
set(CMAKE_CXX_FLAGS_DEBUG "-Wall -O2 -shared -fPIC")

find_package(Qt5 REQUIRED COMPONENTS Widgets Gui)

target_include_directories(rndr PUBLIC ${ARNOLD_SDK_DIR}/include)
target_include_directories(driver PUBLIC ${ARNOLD_SDK_DIR}/include)

target_link_libraries(rndr PUBLIC ${ARNOLD_SDK_DIR}/bin/libai.so PRIVATE Qt5::Widgets PRIVATE Qt5::Gui)
target_link_libraries(driver PUBLIC ${ARNOLD_SDK_DIR}/bin/libai.so)