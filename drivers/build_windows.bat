set ARNOLD_SDK="C:\path\to\Arnold-6.0.1.0-windows"
cl /LD src/driver_display_callback.cpp /I %ARNOLD_SDK%/include %ARNOLD_SDK%/lib/ai.lib /link /out:build/driver_display_callback_v6.0.1.dll

set ARNOLD_SDK="C:\path\to\Arnold-6.2.0.0-windows"
cl /LD src/driver_display_callback.cpp /I %ARNOLD_SDK%/include %ARNOLD_SDK%/lib/ai.lib /link /out:build/driver_display_callback_v6.2.dll