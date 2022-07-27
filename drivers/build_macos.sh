c++ src/btoa_display_driver.cpp -o "build/btoa_display_driver_v$(echo $(kick --version) | awk '{print $2}')".dylib -Wall -O2 -shared -fPIC -I$ARNOLD_ROOT/include -L$ARNOLD_ROOT/bin -lai -std=gnu++11
