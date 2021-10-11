#!/usr/bin/python

# This file is a part of OVRseen <https://athinagroup.eng.uci.edu/projects/ovrseen/>.
# Copyright (c) 2021 UCI Networking Group.
#
# This file incorporates content from NoMoAds <http://athinagroup.eng.uci.edu/projects/nomoads/>.
# Copyright (C) 2018 Anastasia Shuba, University of California, Irvine.
#
# OVRseen is dual licensed under the MIT License and the GNU General Public
# License version 3 (GPLv3). This file is covered by the GPLv3. If this file
# get used, GPLv3 applies to all of OVRseen.
#
# See the LICENSE.md file along with OVRseen for more details.

package_name = "package_name"
version = "package_version"
type = "type"
ats_pkg = "ats_pkg"
id = "pkt_id"
pii_label = "pii_types"
predicted = "predicted"
list_label = "list_labels"

source = "_source"
layers = "layers"
protocol = "protocol"

dst_ip = "dst_ip"
src_ip = "src_ip"
ip = "ip"
tcp = "tcp"
tcpstream = tcp + ".stream"
tcp_payload = tcp + ".payload"

http = "http"
method = "method"
uri = "uri"
headers = "headers"
referer = "referer"
domain = "domain"
host = "host"
dst_port = "dst_port"

http_req = http + ".request."
http_req_method = http_req + method
http_req_uri = http_req + uri
http_req_line = http_req + "line"
http_body = http + ".file_data"

ssl = "tls"

pkt_comment = "pkt_comment"

frame = "frame"
frame_num = frame + ".number"
frame_comment = frame + ".comment"
frame_ts = frame + ".time_epoch"

# Non HTTP packets
irc = "irc"
websocket = "websocket"
websocketdata = "data-text-lines"

# From Lab for VR
LOCATION_PII = [{"33.6459","-117.843"}, {"33.65","-117.84"},  {"33.6","-117.8"}, {"33.7","-117.8"}]

ANTMONITOR_SRC_IP = "192.168.0.2"

QUEST2A__PII_VALUES = {
    "Q2A_Device ID": "926e3754a717a4ac", # taken from antmonitor
    "Q2A_First Name": "Jane",
    "Q2A_Last Name": "Tester",
    "Q2A_Email": "janetestdevel@gmail.com",
    "Q2A_Email Hieu": "hieul@uci.edu",
    "Q2A_Serial Number": "1WMHH824D50421", # taken from settings about
    "Q2A_MAC Address": "2C:26:17:A4:6B:7F", # taken from settings about
    "Q2A_System Version": "14624000073600000", # taken from settings about
    "Q2A_Version": "26.0.0.40.502.274988273", # taken from settings about
    "Q2A_Version Trunc": "26.0.0.40.502", # taken from settings about
    "Q2A_Runtime Version": "26.0.0.40.502.274988282", # taken from settings about
    "Q2A_OS Version": "user-1462400.7360.0", # taken from settings about
}

QUEST2B__PII_VALUES = {
    "Q2B_Device ID": "baf3a5c4b06a73c4", # taken from antmonitor
    "Q2B_Serial Number": "1WMHH841QB1073", # taken from settings about
    "Q2B_MAC Address": "2C:26:17:E6:43:0F", # taken from settings about
    "Q2B_System Version": "15280600139600000", # taken from settings about
    "Q2B_Version": "26.0.0.40.502.274988273", # taken from settings about
    "Q2B_Version Trunc": "26.0.0.40.502", # taken from settings about
    "Q2B_Runtime Version": "26.0.0.40.502.274988282", # taken from settings about
    "Q2B_OS Version": "user-1462400.7360.0", # taken from settings about
}

# Retrieved by looking at values of HTTP headers and HTTP body
OTHER__PII_VALUES = {
    "DEVICE_Oculus_Model": "Oculus/Quest/hollywood",
    "DEVICE_Oculus_Model_2": r"Oculus[+ ]?Quest",
    "DEVICE_Oculus_Model_3": r"Quest[ ]?2",

    "UNITY_VERSION": r"Unity[- ]?v?20[12]\d\.\d+\.\d+", # eg: unity 2020.3.7
    "UNITY_VERSION_1": r"Unity[- ]?v?[0-6]\.\d+\.\d+",  # eg: unity 6.3.5
    "UNITY_VERSION_2": r"UnityPlayer/[\d.]+\d",  # in user agent
    "UNITY_VERSION_3": r"UnitySDK-[\d.]+\d",

    "CPU_VENDOR": "Qualcomm Technologies, Inc KONA",
    "CPU_FLAGS": "ARM64 FP ASIMD AES",
    "CPU_FLAGS_2": "ARMv7 VFPv3 NEON",
    "CPU_FLAGS_3": r"ARM64\+FP\+ASIMD\+AES",
    "CPU_FLAGS_4": r"arm64-v8a,\+armeabi-v7a,\+armeabi",

    "GPU_INFO_NAME": r"Adreno \(TM\) 650",
    "GPU_INFO_DRIVER": r"GIT@09c6a36",
    "GPU_INFO_DRIVER_2": r"GIT@a8017ed",
    "OPENGL_VERSION": r"OpenGL ES 3\.2",

    "SCREEN_RESOLUTION": "3664 x 1920",
    "SCREEN_RESOLUTION_2": "3664x1920",
    "SCREEN_RESOLUTION_3": r"\+3664,\+1920",
    "SCREEN_RESOLUTION_4": "width=3664",

    "DEVICE_ID": "b99156a32b3074c26b7731740f1cd142",
    "DEVICE_ID_2": "3530b17b58f54003a4f666cf0d1c70d7",
    "DEVICE_ID_3": "a50c4168-5a51-465b-803a-2ced4091fb5bR",

    "ANDROID_ID": "1cbb0970e6395e5f",
    "ANDROID_ID_2": "a945d90a32f8b2f8",

    "Gender": "girl",

    "UNREAL_VERSION": "X-UnrealEngine-VirtualAgeStats",  # in user agent
    "UNREAL_VERSION_2": r"UE4 0\.0\.1",
    "UNREAL_VERSION_3": "engine=UE4",  # in user agent

    "SYSTEM_BUILD": r"QQ3A\.200805\.001",  # in user agent
    "SYSTEM_VERSION": "Android 10",
}


OTHER__PII_VALUES__BY_KEY = {
    "System Version__BY_KEY": "x-build-version-incremental", # 14624000073600000
    "Serial Number__BY_KEY": "x-oc-selected-headset-serial",
    "APP_NAME__BY_KEY": "app_name",
    "APP_NAME_2__BY_KEY": "appid",
    "APP_NAME_3__BY_KEY": "application_name",
    "APP_NAME_4__BY_KEY": "applicationId",
    "APP_NAME_5__BY_KEY": "X-APPID",
    "APP_NAME_6__BY_KEY": "gameId",
    "APP_NAME_7__BY_KEY": "package_name",
    "APP_NAME_8__BY_KEY": "app_build",
    "APP_NAME_9__BY_KEY": "localprojectid",
    "APP_NAME_10__BY_KEY": "android_app_signature",
    "APP_VERSION__BY_KEY": "gameVersion",
    "APP_VERSION_2__BY_KEY": "package_version",
    "CLIENT_LIB__BY_KEY": "clientLib",
    "CLIENT_LIB_2__BY_KEY": "clientLibVersion",
    "LOCATION_2__BY_KEY": "countryCode",
    "LOCATION_3__BY_KEY": "timeZoneOffset",
    "UNITY_VERSION__BY_KEY": "x-unity-version",
    "UNITY_VERSION_2__BY_KEY": "sdk_ver",
    "UNITY_VERSION_3__BY_KEY": "engine_version",
    "UNITY_VERSION_4__BY_KEY": "X-Unity-Version", #2019.4.19
    "UNITY_VERSION_5__BY_KEY": "sdk_ver_full",
    "UNITY_ARCORE__BY_KEY": "ARCore",
    "OS_VERSION__BY_KEY": "os_version",
    "OS_VERSION_2__BY_KEY": "operatingSystem",
    "OS_VERSION_4__BY_KEY": "os_family",
    "BUILD_2__BY_KEY": "build_guid",
    "BUILD_3__BY_KEY": "build_tags",
    "COOKIE__BY_KEY": "cookie",
    "APP_SESSION__BY_KEY": "AppSession",
    "USER_ID__BY_KEY": "user_id",
    "USER_ID_2__BY_KEY": "UserID",
    "USER_ID_3__BY_KEY": "x-player",
    "USER_ID_4__BY_KEY": "x-playeruid",
    "USER_ID_5__BY_KEY": "profileId",
    "USER_ID_6__BY_KEY": "anonymousId", # baaa4d8e-c223-4acf-93d2-4a0a1d59ea52
    "PLAYFAB_ID__BY_KEY": "PlayFabIDs", # 105C0B33CAA5F314, etc.. https://playfab.com/
    "ANDROID_ID__BY_KEY": "android_id",
    "ANDROID_ID_2__BY_KEY": "android-id",
    "ANDROID_ID_3__BY_KEY": "x-android-id", # 423952a8b797966d
    "SESSION_ID__BY_KEY": "session_id",
    "SESSION_ID_2__BY_KEY": "sessionid",
    "DEVICE_ID__BY_KEY": "deviceid",
    "DEVICE_ID_2__BY_KEY": "device_id",
    "DEVICE_ID_3__BY_KEY": "device-id",
    "DO_NOT_TRACK__BY_KEY": "x-do-not-track",
    "EVENT_ID__BY_KEY": "event-id",
    "EVENT_ID_2__BY_KEY": "event_id",
    "EVENT_ID_3__BY_KEY": "objective_id",
    "EVENT_COUNT__BY_KEY": "event-count",
    "EVENT_COUNT_2__BY_KEY": "event_count",
    "SESSION_COUNT__BY_KEY": "session-count",
    "SESSION_COUNT_2__BY_KEY": "session_count",
    "WEBSOCKET__BY_KEY": "sec-websocket-key",
    "PLAY_SESSION__BY_KEY": "t_since_start",
    "PLAY_SESSION_2__BY_KEY": "startTime",
    "PLAY_SESSION_3__BY_KEY": "realtimeDuration",
    "VR_SHELL_BUILD__BY_KEY": "x-oc-vrshell-build-name",
    "ANALYTIC__BY_KEY": "analytic",
    "TRACKING__BY_KEY": "tracking",
    # rooted or not, bool flag
    "JAIL__BY_KEY": "rooted_or_jailbroken",
    "JAIL_2__BY_KEY": "rooted_jailbroken",
    "GPS__BY_KEY": "gps_enabled",
    "EMAIL__BY_KEY": "email",
    "POSITION__BY_KEY": "position",
    "ROTATION__BY_KEY": "rotation",
    "VR_PLAY_AREA__BY_KEY": "vr_play_area_geometry",
    "VR_PLAY_AREA_2__BY_KEY": "vr_play_area_dimension",
    "VR_PLAY_AREA_3__BY_KEY": "playarea",
    "VR_TRACKED__BY_KEY": "vr_tracked_area_geometry",
    "VR_TRACKED_2__BY_KEY": "vr_tracked_area_dimension",
    "VR_FIELD_OF_VIEW__BY_KEY": "vr_field_of_view",
    "VR_USER_DEVICE_IPD__BY_KEY": "vr_user_device_ipd",
    "SECONDS_PLAYED__BY_KEY": "seconds_played",
    "SECONDS_PLAYED_2__BY_KEY": "game_time", # number
    "SECONDS_PLAYED_3__BY_KEY": "gameDuration", # number
    "SENSOR_GYROSCOPE__BY_KEY": "gyroscope",
    "SENSOR_ACCELEROMETER__BY_KEY": "accelerometer",
    "SENSOR_MAGNETOMETER__BY_KEY": "magnetometer",
    "SENSOR_PROXIMITY__BY_KEY": "proximity",
    "SENSOR_FLAGS":"sensor_flags",
    "LEFT_HAND_PREF__BY_KEY": "left_handed_mode", # true|false
    "SUBTITLE_ON__BY_KEY": "subtitles", # true|false
    "LANGUAGE__BY_KEY": "language", # en
    "LANGUAGE_2__BY_KEY": "language_region", #en-us
    "LANGUAGE_3__BY_KEY": "languageCode", # en
    "LANGUAGE_4__BY_KEY": "system_language", # en
    "CONNECTION_TYPE__BY_KEY": "connection-type", #wifi
    "INSTALL_MODE__BY_KEY": "install_mode", # dev_release
    "INSTALL_STORE__BY_KEY": "install_store", # empty str (since we repackaged it)
    "DEVICE_INFO_FLAGS__BY_KEY": "device_info_flags", #"device_info_flags":3271559242
    "PLATFORM__BY_KEY": "releasePlatform", #"ANG"
    "PLATFORM_2__BY_KEY": "platform", #"AndroidPlayer"
    "PLATFORM_3__BY_KEY": "platformid", #"11"
    "PLATFORM_CPU_COUNT__BY_KEY": "cpu_count",
    "PLATFORM_CPU_FREQ__BY_KEY": "cpu_freq",
    "DEVICE_MODEL__BY_KEY": "device_model",
    "DEVICE_MODEL_2__BY_KEY": "device_type",
    "DEVICE_MODEL_3__BY_KEY": "enabled_vr_devices",
    "DEVICE_MODEL_4__BY_KEY": "vr_device_name",
    "DEVICE_MODEL_5__BY_KEY": "vr_device_model",
    "DEVICE_RAM__BY_KEY": "device_ram",
    "DEVICE_VRAM__BY_KEY": "device_vram",
    "SCREEN_SIZE__BY_KEY": "screen_size",
    "SCREEN_DPI__BY_KEY": "screen_dpi",
    "FULLSCREEN__BY_KEY": "is_fullscreen",
    "SCREEN_ORIENTATION__BY_KEY": "screen_orientation",
    "REFRESH_RATE__BY_KEY": "refresh_rate",
    "GPU_INFO_1__BY_KEY": "gpu_api",
    "GPU_INFO_2__BY_KEY": "gpu_caps",
    "GPU_INFO_3__BY_KEY": "gpu_copy_texture_support",
    "GPU_INFO_4__BY_KEY": "gpu_device_id",
    "GPU_INFO_5__BY_KEY": "gpu_vendor_id",
    "GPU_INFO_6__BY_KEY": "gpu_driver",
    "GPU_INFO_7__BY_KEY": "gpu_max_cubemap_size",
    "GPU_INFO_8__BY_KEY": "gpu_max_texture_size",
    "GPU_INFO_9__BY_KEY": "gpu_shader_caps",
    "GPU_INFO_10__BY_KEY": "gpu_supported_render_target_count",
    "GPU_INFO_11__BY_KEY": "gpu_texture_format_support",
    "GPU_INFO_12__BY_KEY": "gpu_vendor",
    "GPU_INFO_13__BY_KEY": "gpu_version",
    "SCRIPTING_BACKEND__BY_KEY": "scripting_backend",
}


OTHER__PII_VALUES__WEBSOCKET = {
    "PLAY_SESSION_STATUS__BY_KEY": "joinable",
    "PLAY_SESSION_STATUS_2__BY_KEY": "lastSeen",
    "PLAY_SESSION_STATUS_3__BY_KEY": "join_channel",
    "PLAY_SESSION_MSG": "JoinParty",
    "PLAY_SESSION_MSG_2": "SetPartyActiveGameOrWorldID",
    "PLAY_SESSION_MSG_3": "SetPartyIDForOculusRoomID",
    "PLAY_SESSION_MSG_4": "JoinOpenWorld",
    "PLAY_SESSION_ID__BY_KEY": "partyID",
    "PLAY_SESSION_ID_2__BY_KEY": "worldID",
    "PLAY_SESSION_ID_3__BY_KEY": "gameOrWorldID",
    "PLAY_SESSION_ID_4__BY_KEY": "oculusRoomID",
}


# merge the above dict into one. Make sure the keys are unique
PII_VALUES = dict()
PII_VALUES.update(QUEST2A__PII_VALUES)
PII_VALUES.update(QUEST2B__PII_VALUES)
PII_VALUES.update(OTHER__PII_VALUES)
PII_VALUES.update(OTHER__PII_VALUES__BY_KEY)
PII_VALUES.update(OTHER__PII_VALUES__WEBSOCKET)
