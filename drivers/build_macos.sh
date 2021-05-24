ARNOLD_SDK=/Applications/Autodesk/Arnold-6.0.1.0-darwin
c++ src/driver_display_callback.cpp -o build/driver_display_callback_v6.0.1.dylib -Wall -O2 -shared -fPIC -I$ARNOLD_SDK/include -L$ARNOLD_SDK/bin -lai -std=gnu++11

ARNOLD_SDK=/Applications/Autodesk/Arnold-6.2.0.0-darwin
c++ src/driver_display_callback.cpp -o build/driver_display_callback_v6.2.dylib -Wall -O2 -shared -fPIC -I$ARNOLD_SDK/include -L$ARNOLD_SDK/bin -lai -std=gnu++11