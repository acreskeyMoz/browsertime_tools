#!/bin/bash
set -x -e -v

# Invoke like `env ANDROID_SERIAL=... bash one.sh -n 3 -vv https://google.com`.

: GECKODRIVER_PATH ${GECKODRIVER_PATH:=/Users/acreskey/dev/gecko-driver/mozilla-central/target/debug/geckodriver}
: TMP ${TMP:=/tmp}
: RESULT_TOP_DIR ${RESULT_TOP_DIR:=browsertime-results}
: BROWSER ${BROWSER:=firefox}

URL=${@: -1}
URL=${URL#"https://"}
URL=${URL#"http://"}

# N.B.: yargs doesn't parse `--firefox.android.intentArgument --ez`
# properly, so always use `=--ez`!
if [[ -n $ANDROID_SERIAL ]] ; then
    DEVICE_SERIAL_ARGS="--firefox.android.deviceSerial=$ANDROID_SERIAL --chrome.android.deviceSerial=$ANDROID_SERIAL"
else
    DEVICE_SERIAL_ARGS=
fi

current_time=$(date "+%Y.%m.%d-%H.%M.%S")

if [[ $BROWSER == *"firefox"* ]] ; then
        env RUST_BACKTRACE=1 RUST_LOG=trace bin/browsertime.js \
            --android \
            --skipHar \
            --firefox.geckodriverPath="$GECKODRIVER_PATH" \
            --firefox.android.package "org.mozilla.geckoview_example" \
            --firefox.android.activity "org.mozilla.geckoview_example.GeckoViewActivity" \
            --firefox.android.intentArgument=-a \
            --firefox.android.intentArgument=android.intent.action.VIEW \
            --firefox.android.intentArgument=-d \
            --firefox.android.intentArgument="data:," \
            --firefox.profileTemplate $TMP/firefox-profile \
            --browser firefox \
            --resultDir "$RESULT_TOP_DIR/$URL/results/$current_time" \
            $DEVICE_SERIAL_ARGS \
            "$@"
fi
