set ARNOLD_SDK="C:\Program Files\Autodesk\Arnold-7.1.2.0-windows"
cl /LD src/driver_display_callback.cpp /I %ARNOLD_SDK%/include %ARNOLD_SDK%/lib/ai.lib /link /out:build/ai_display_driver.dll