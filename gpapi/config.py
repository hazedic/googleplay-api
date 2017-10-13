from . import googleplay_pb2
import time
import os
import sys

VERSION = sys.version_info[0]
if VERSION == 2:
    import ConfigParser
else:
    import configparser


DFE_TARGETS = "CAEScFfqlIEG6gUYogFWrAISK1WDAg+hAZoCDgIU1gYEOIACFkLMAeQBnASLATlASUuyAyqCAjY5igOMBQzfA/IClwFbApUC4ANbtgKVAS7OAX8YswHFBhgDwAOPAmGEBt4OfKkB5weSB5AFASkiN68akgMaxAMSAQEBA9kBO7UBFE1KVwIDBGs3go6BBgEBAgMECQgJAQIEAQMEAQMBBQEBBAUEFQYCBgUEAwMBDwIBAgOrARwBEwMEAg0mrwESfTEcAQEKG4EBMxghChMBDwYGASI3hAEODEwXCVh/EREZA4sBYwEdFAgIIwkQcGQRDzQ2fTC2AjfVAQIBAYoBGRg2FhYFBwEqNzACJShzFFblAo0CFxpFNBzaAd0DHjIRI4sBJZcBPdwBCQGhAUd2A7kBLBVPngEECHl0UEUMtQETigHMAgUFCc0BBUUlTywdHDgBiAJ+vgKhAU0uAcYCAWQ/5ALUAw1UwQHUBpIBCdQDhgL4AY4CBQICjARbGFBGWzA1CAEMOQH+BRAOCAZywAIDyQZ2MgM3BxsoAgUEBwcHFia3AgcGTBwHBYwBAlcBggFxSGgIrAEEBw4QEqUCASsWadsHCgUCBQMD7QICA3tXCUw7ugJZAwGyAUwpIwM5AwkDBQMJA5sBCw8BNxBVVBwVKhebARkBAwsQEAgEAhESAgQJEBCZATMdzgEBBwG8AQQYKSMUkAEDAwY/CTs4/wEaAUt1AwEDAQUBAgIEAwYEDx1dB2wGeBFgTQ"
LANG = "en_US"
TIMEZONE = 'America/New_York'
GOOGLE_PUBKEY = "AAAAgMom/1a/v0lblO2Ubrt60J2gcuXSljGFQXgcyZWveWLEwo6prwgi3iJIZdodyhKZQrNWp5nKJ3srRXcUW+F1BD3baEVGcmEgqaLZUNBjm057pKRI16kB0YppeGx5qIQ5QjKzsR8ETQbKLNWgRY0QRNVz34kMJR3P/LgHax/6rmf5AAAAAwEAAQ=="

# parse phone config from the file 'device.properties'.
# if you want to add another phone, just create another section in
# the file. Some configurations for common phones can be found here:
# https://github.com/yeriomin/play-store-api/tree/master/src/main/resources
if VERSION == 2:
    config = ConfigParser.ConfigParser()
else:
    config = configparser.ConfigParser()

filepath = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                        'device.properties')
config.read(filepath)
device = {}
# initialize device, because we need to setup UserAgent
# before the end of login method. If the login defines a different
# device, it won't cause conflicts
for (key, value) in config.items('angler'):
    device[key] = value


def getDevicesCodenames():
    """Returns a list containing devices codenames"""
    return config.sections()


def getDevicesReadableNames():
    """Returns codename and readable name for each device"""
    sections = getDevicesCodenames()
    output = []
    for s in sections:
        output.append({'codename': s,
                       'readableName': config[s]['userreadablename']})
    return output


def getUserAgent():
    return ("Android-Finsky/8.1.72.S-all [6] [PR] 165478484 ("
            "api=3"
            ",versionCode={versionCode}"
            ",sdk={sdk}"
            ",device={device}"
            ",hardware={hardware}"
            ",product={product}").format(versionCode=device['vending.version'],
                                         sdk=device['build.version.sdk_int'],
                                         device=device['build.device'],
                                         hardware=device['build.hardware'],
                                         product=device['build.product'])


def getDeviceConfig():
    libList = device['sharedlibraries'].split(",")
    featureList = device['features'].split(",")
    localeList = device['locales'].split(",")
    glList = device['gl.extensions'].split(",")
    platforms = device['platforms'].split(",")

    hasFiveWayNavigation = (device['hasfivewaynavigation'] == 'true')
    hasHardKeyboard = (device['hashardkeyboard'] == 'true')
    deviceConfig = googleplay_pb2.DeviceConfigurationProto()
    deviceConfig.touchScreen = int(device['touchscreen'])
    deviceConfig.keyboard = int(device['keyboard'])
    deviceConfig.navigation = int(device['navigation'])
    deviceConfig.screenLayout = int(device['screenlayout'])
    deviceConfig.hasHardKeyboard = hasHardKeyboard
    deviceConfig.hasFiveWayNavigation = hasFiveWayNavigation
    deviceConfig.screenDensity = int(device['screen.density'])
    deviceConfig.screenWidth = int(device['screen.width'])
    deviceConfig.screenHeight = int(device['screen.height'])
    deviceConfig.glEsVersion = int(device['gl.version'])
    for x in platforms:
        deviceConfig.nativePlatform.append(x)
    for x in libList:
        deviceConfig.systemSharedLibrary.append(x)
    for x in featureList:
        deviceConfig.systemAvailableFeature.append(x)
    for x in localeList:
        deviceConfig.systemSupportedLocale.append(x)
    for x in glList:
        deviceConfig.glExtension.append(x)
    return deviceConfig


def getAndroidBuild():
    androidBuild = googleplay_pb2.AndroidBuildProto()
    androidBuild.id = device['build.fingerprint']
    androidBuild.product = device['build.hardware']
    androidBuild.carrier = device['build.brand']
    androidBuild.radio = device['build.radio']
    androidBuild.bootloader = device['build.bootloader']
    androidBuild.device = device['build.device']
    androidBuild.sdkVersion = int(device['build.version.sdk_int'])
    androidBuild.model = device['build.model']
    androidBuild.manufacturer = device['build.manufacturer']
    androidBuild.buildProduct = device['build.product']
    androidBuild.client = device['client']
    androidBuild.otaInstalled = False
    androidBuild.timestamp = int(time.time())
    androidBuild.googleServices = int(device['gsf.version'])
    return androidBuild


def getAndroidCheckin():
    androidCheckin = googleplay_pb2.AndroidCheckinProto()
    androidCheckin.build.CopyFrom(getAndroidBuild())
    androidCheckin.lastCheckinMsec = 0
    androidCheckin.cellOperator = device['celloperator']
    androidCheckin.simOperator = device['simoperator']
    androidCheckin.roaming = device['roaming']
    androidCheckin.userNumber = 0
    return androidCheckin


def getAndroidCheckinRequest(device_codename):
    for (key, value) in config.items(device_codename):
        device[key] = value
    request = googleplay_pb2.AndroidCheckinRequest()
    request.id = 0
    request.checkin.CopyFrom(getAndroidCheckin())
    request.locale = LANG
    request.timeZone = TIMEZONE
    request.version = 3
    request.deviceConfiguration.CopyFrom(getDeviceConfig())
    request.fragment = 0
    return request
