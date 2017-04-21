#!/bin/sh

ARCH=`uname -m`

if [ "$ARCH" == "armv7l" ]; then
    export LD_LIBRARY_PATH="$SUGAR_BUNDLE_PATH/lib/arm"
    export GST_PLUGIN_PATH="$SUGAR_BUNDLE_PATH/lib/arm"
else
    export LD_LIBRARY_PATH="$SUGAR_BUNDLE_PATH/lib/i686"
    export GST_PLUGIN_PATH="$SUGAR_BUNDLE_PATH/lib/i686"
fi

exec sugar-activity cuadraditos.Cuadraditos $@

