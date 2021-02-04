# Arnold for Blender #

BtoA is an unofficial Blender add-on for Autodesk's Arnold render engine.

### Current functionality ###

![Blender scene rendered in Arnold](https://bitbucket.org/luna-digital/btoa/raw/6531748064be792af98c537d1816d6841bf029e8/examples/lambert.png)

* BtoA can only send polygon objects and camera data to Arnold at the moment - no support for curves, fonts, or other data.
* There is basic support for lights, including point lights, distant lights, and spot lights. Area lights have been implemented but are buggy and need more work.
* The add-on supports lambert shaders, but nothing else at the moment.
* Renders show up in the Render Result view, but there is no viewport rendering yet.

We're in the early days of development, and will be updating code publicly as we make progress. We guarantee that the code you see here will always be up-to-date with what we're working on internally.

The add-on automatically detects the Arnold installation from the $ARNOLD_ROOT environment variable. If this variable is not set, you can manually set the installation location in the add-on preferences.

### How to install ###

1. Install the Arnold SDK.
2. Make sure the `LD_LIBRARY_PATH` environment variable is set to the `bin` folder in the SDK.
3. Optionally, you can set the `ARNOLD_ROOT` environment variable to the root directory of your SDK installation. If you do, Blender will find Arnold automatically. If you don't, you just have to set the path in the add-on preferences.
4. Install the BtoA add-on by downloading this repo as a zip and installing in the Blender preferences.

### Getting involved ###
This add-on is developed and maintained by Aaron Powell at Luna Digital, Ltd. (aaron@lunadigital.tv). Feel free to reach out if you're interested in testing or contributing!

### Example renders ###
![Arnold light types in Blender](https://bitbucket.org/luna-digital/btoa/raw/8ca83472a8ac33bc0f9b8238c0c882b7e4828925/examples/arnold_light_types.jpg)