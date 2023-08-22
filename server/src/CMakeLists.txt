cmake_minimum_required(VERSION 3.27.1)

project(ArnoldServer)

add_executable(${PROJECT_NAME} main.cc)

add_subdirectory(lib/rndr)
add_subdirectory(lib/gui)

target_include_directories(${PROJECT_NAME}
    PRIVATE lib/rndr
    PRIVATE lib/gui
)

find_package(cppzmq)
#find_package(Qt5 REQUIRED COMPONENTS Widgets Gui Concurrent)

target_link_libraries(${PROJECT_NAME}
    PUBLIC rndr
    PUBLIC gui
    PUBLIC cppzmq
)