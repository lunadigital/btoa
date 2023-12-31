ARNOLD_SDK=/Users/username/Autodesk/ArnoldServer
c++ src/btoa_display_driver.cpp src/renderdata.cpp -o build/ai_display_driver.dylib -Wall -O2 -shared -fPIC -I$ARNOLD_SDK/include -L$ARNOLD_SDK/bin -lai -std=gnu++11
