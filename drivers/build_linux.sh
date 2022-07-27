ARNOLD_SDK=/opt/Arnold-7.1.2.0-linux
c++ src/btoa_display_driver.cpp -o build/ai_display_driver.so -Wall -O2 -shared -fPIC -I$ARNOLD_SDK/include -L$ARNOLD_SDK/bin -lai -std=gnu++11