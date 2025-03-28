set ARNOLD_SDK="C:\path\to\sdk"
cl /LD src/btoa_display_driver.cpp src/renderdata.cpp /I %ARNOLD_SDK%/include %ARNOLD_SDK%/lib/ai.lib /link /out:build/btoa_display_driver.dll