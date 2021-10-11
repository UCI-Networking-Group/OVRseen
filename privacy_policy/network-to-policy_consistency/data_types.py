#!/usr/bin/env python3

# This file contains the mapping from the data types in json_keys.py into PoliCheck's data types.

# Rahmadi's Quest1
QUEST1A__PI_VALUES = {
    # device_id: A soft ID that may change upon factory reset.
    "Q1A_Device ID": "device_id",
    "Q1A_First Name": "person_name",
    "Q1A_Last Name": "person_name",
    "Q1A_Email": "email",
    # serial_number: A hard ID that should not change.
    "Q1A_Serial Number": "serial_number",
    "Q1A_MAC Address": "mac_address",
    # TODO: figure out what are the following 4 sys versions bind to (OS/firmware/hardware...?)
    "Q1A_System Version": "system_version",
    "Q1A_Version": "system_version",
    "Q1A_Runtime Version": "system_version",
    "Q1A_OS Version": "system_version",
}

# Hieu/Nastia's Quest1
QUEST1B__PII_VALUES = {
    "Q1B_Device ID": "device_id",
    "Q1B_First Name": "person_name",
    "Q1B_Last Name": "person_name",
    "Q1B_Email": "email",
    "Q1B_Serial Number": "serial_number",
    "Q1B_MAC Address": "mac_address",
    "Q1B_System Version": "system_version",
    "Q1B_Version": "system_version",
    "Q1B_Runtime Version": "system_version",
    "Q1B_OS Version": "system_version",
}

# Hieu Quest2
QUEST2A__PII_VALUES = {
    "Q2A_Device ID": "device_id",
    "Q2A_First Name": "person_name",
    "Q2A_Last Name": "person_name",
    "Q2A_Email": "email",
    "Q2A_Email Hieu": "email",
    "Q2A_Serial Number": "serial_number",
    "Q2A_MAC Address": "mac_address",
    "Q2A_System Version": "system_version",
    "Q2A_Version": "system_version",
    "Q2A_Version Trunc": "system_version",
    "Q2A_Runtime Version": "system_version",
    "Q2A_OS Version": "system_version",
}

# Rahmadi Quest2
QUEST2B__PII_VALUES = {
    "Q2B_Device ID": "device_id",
    #"Q2B_First Name": "person_name",
    #"Q2B_Last Name": "person_name",
    #"Q2B_Email": "email",
    "Q2B_Serial Number": "serial_number",
    "Q2B_MAC Address": "mac_address",
    "Q2B_System Version": "system_version",
    "Q2B_Version": "system_version",
    "Q2B_Version Trunc": "system_version",
    "Q2B_Runtime Version": "system_version",
    "Q2B_OS Version": "system_version",
}

# NOTE: These will be agnostic of device for now (we can retrieve the device later)
# Retrieved by looking at values of HTTP headers and HTTP body
OTHER__PII_VALUES = {
    "DEVICE_Oculus_Model": "hardware_info",
    "DEVICE_Oculus_Model_2": "hardware_info",
    "DEVICE_Oculus_Model_3": "hardware_info",

    "UNITY_VERSION": "sdk_version",
    "UNITY_VERSION_1": "sdk_version",
    "UNITY_VERSION_2": "sdk_version",
    "UNITY_VERSION_3": "sdk_version",

    "CPU_VENDOR": "hardware_info",
    "CPU_FLAGS": "hardware_info",
    "CPU_FLAGS_2": "hardware_info",
    "CPU_FLAGS_3": "hardware_info",
    "CPU_FLAGS_4": "hardware_info",

    "GPU_INFO_NAME": "hardware_info",
    "GPU_INFO_DRIVER": "hardware_info",
    "GPU_INFO_DRIVER_2": "hardware_info",
    "OPENGL_VERSION": "hardware_info",

    "SCREEN_RESOLUTION": "hardware_info",
    "SCREEN_RESOLUTION_2": "hardware_info",
    "SCREEN_RESOLUTION_3": "hardware_info",
    "SCREEN_RESOLUTION_4": "hardware_info",

    "DEVICE_ID": "device_id",
    "DEVICE_ID_2": "device_id",
    "DEVICE_ID_3": "device_id",

    "ANDROID_ID": "android_id",
    "ANDROID_ID_2": "android_id",

    "UNREAL_VERSION": "sdk_version",
    "UNREAL_VERSION_2": "sdk_version",
    "UNREAL_VERSION_3": "sdk_version",

    "SYSTEM_BUILD": "system_version",
    "SYSTEM_VERSION": "system_version",
}

OTHER__PII_VALUES__BY_KEY = {
    "System Version__BY_KEY": "system_version",
    "Serial Number__BY_KEY": "serial_number",
    "APP_NAME__BY_KEY": "app_name",
    "APP_NAME_2__BY_KEY": "app_name",
    "APP_NAME_3__BY_KEY": "app_name",
    "APP_NAME_4__BY_KEY": "app_name",
    "APP_NAME_5__BY_KEY": "app_name",
    "APP_NAME_6__BY_KEY": "app_name",
    "APP_NAME_7__BY_KEY": "app_name",
    "APP_NAME_8__BY_KEY": "app_name",
    "APP_NAME_9__BY_KEY": "app_name",
    "APP_NAME_10__BY_KEY": "app_name",
    "APP_VERSION__BY_KEY": "app_name",
    "APP_VERSION_2__BY_KEY": "app_name",
    "CLIENT_LIB__BY_KEY": "sdk_version",
    "CLIENT_LIB_2__BY_KEY": "sdk_version",

    "LOCATION_2__BY_KEY": "geographical_location",
    "LOCATION_3__BY_KEY": "geographical_location",
    "UNITY_VERSION__BY_KEY": "sdk_version",
    "UNITY_VERSION_2__BY_KEY": "sdk_version",
    "UNITY_VERSION_3__BY_KEY": "sdk_version",
    "UNITY_VERSION_4__BY_KEY": "sdk_version",
    "UNITY_VERSION_5__BY_KEY": "sdk_version",
    "UNITY_ARCORE__BY_KEY": "sdk_version",
    "OS_VERSION__BY_KEY": "system_version",
    "OS_VERSION_2__BY_KEY": "system_version",

    "OS_VERSION_4__BY_KEY": "system_version",


    "BUILD_2__BY_KEY": "build_version",
    "BUILD_3__BY_KEY": "build_version",
    "COOKIE__BY_KEY": "cookie",
    "APP_SESSION__BY_KEY": "session_info",
    "USER_ID__BY_KEY": "user_id",
    "USER_ID_2__BY_KEY": "user_id",
    "USER_ID_3__BY_KEY": "user_id",
    "USER_ID_4__BY_KEY": "user_id",
    "USER_ID_5__BY_KEY": "user_id",
    "USER_ID_6__BY_KEY": "user_id",
    "PLAYFAB_ID__BY_KEY": "user_id",
    "ANDROID_ID__BY_KEY": "android_id",
    "ANDROID_ID_2__BY_KEY": "android_id",
    "ANDROID_ID_3__BY_KEY": "android_id",
    "SESSION_ID__BY_KEY": "session_info",
    "SESSION_ID_2__BY_KEY": "session_info",
    "DEVICE_ID__BY_KEY": "device_id",
    "DEVICE_ID_2__BY_KEY": "device_id",
    "DEVICE_ID_3__BY_KEY": "device_id",
    "DO_NOT_TRACK__BY_KEY": "flags",
    "EVENT_ID__BY_KEY": "session_info",
    "EVENT_ID_2__BY_KEY": "session_info",
    "EVENT_ID_3__BY_KEY": "session_info",
    "EVENT_COUNT__BY_KEY": "session_info",
    "EVENT_COUNT_2__BY_KEY": "session_info",
    "SESSION_COUNT__BY_KEY": "session_info",
    "SESSION_COUNT_2__BY_KEY": "session_info",
    "WEBSOCKET__BY_KEY": "flags",
    "PLAY_SESSION__BY_KEY": "usage_time",
    "PLAY_SESSION_2__BY_KEY": "usage_time",
    "PLAY_SESSION_3__BY_KEY": "usage_time",
    "VR_SHELL_BUILD__BY_KEY": "sdk_version",

    "ANALYTIC__BY_KEY": "session_info",
    "TRACKING__BY_KEY": "flags",

    "JAIL__BY_KEY": "flags",
    "JAIL_2__BY_KEY": "flags",
    "GPS__BY_KEY": "geographical_location",
    "EMAIL__BY_KEY": "email",
    "POSITION__BY_KEY": "vr_position",
    "ROTATION__BY_KEY": "vr_rotation",
    "VR_PLAY_AREA__BY_KEY": "vr_play_area",
    "VR_PLAY_AREA_2__BY_KEY": "vr_play_area",
    "VR_PLAY_AREA_3__BY_KEY": "vr_play_area",
    "VR_TRACKED__BY_KEY": "vr_play_area",
    "VR_TRACKED_2__BY_KEY": "vr_play_area",
    "VR_FIELD_OF_VIEW__BY_KEY": "vr_field_of_view",
    "VR_USER_DEVICE_IPD__BY_KEY": "vr_ipd",
    "SECONDS_PLAYED__BY_KEY": "usage_time",
    "SECONDS_PLAYED_2__BY_KEY": "usage_time",
    "SECONDS_PLAYED_3__BY_KEY": "usage_time",
    "SENSOR_GYROSCOPE__BY_KEY": "vr_movement",
    "SENSOR_ACCELEROMETER__BY_KEY": "vr_movement",
    "SENSOR_MAGNETOMETER__BY_KEY": "vr_movement",
    "SENSOR_PROXIMITY__BY_KEY": "vr_movement",
    "SENSOR_FLAGS": "vr_movement",
    "LEFT_HAND_PREF__BY_KEY": "vr_movement",
    "SUBTITLE_ON__BY_KEY": "flags",
    "LANGUAGE__BY_KEY": "language",
    "LANGUAGE_2__BY_KEY": "language",
    "LANGUAGE_3__BY_KEY": "language",
    "LANGUAGE_4__BY_KEY": "language",
    "CONNECTION_TYPE__BY_KEY": "flags",
    "INSTALL_MODE__BY_KEY": "flags",
    "INSTALL_STORE__BY_KEY": "flags",
    "DEVICE_INFO_FLAGS__BY_KEY": "hardware_info",
    "PLATFORM__BY_KEY": "hardware_info",
    "PLATFORM_2__BY_KEY": "hardware_info",
    "PLATFORM_3__BY_KEY": "hardware_info",

    "PLATFORM_CPU_COUNT__BY_KEY": "hardware_info",
    "PLATFORM_CPU_FREQ__BY_KEY": "hardware_info",
    "DEVICE_MODEL__BY_KEY": "hardware_info",
    "DEVICE_MODEL_2__BY_KEY": "hardware_info",
    "DEVICE_MODEL_3__BY_KEY": "hardware_info",
    "DEVICE_MODEL_4__BY_KEY": "hardware_info",
    "DEVICE_MODEL_5__BY_KEY": "hardware_info",
    "DEVICE_RAM__BY_KEY": "hardware_info",
    "DEVICE_VRAM__BY_KEY": "hardware_info",
    "SCREEN_SIZE__BY_KEY": "hardware_info",
    "SCREEN_DPI__BY_KEY": "hardware_info",
    "FULLSCREEN__BY_KEY": "hardware_info",
    "SCREEN_ORIENTATION__BY_KEY": "hardware_info",
    "REFRESH_RATE__BY_KEY": "hardware_info",
    "GPU_INFO_1__BY_KEY": "hardware_info",
    "GPU_INFO_2__BY_KEY": "hardware_info",
    "GPU_INFO_3__BY_KEY": "hardware_info",
    "GPU_INFO_4__BY_KEY": "hardware_info",
    "GPU_INFO_5__BY_KEY": "hardware_info",
    "GPU_INFO_6__BY_KEY": "hardware_info",
    "GPU_INFO_7__BY_KEY": "hardware_info",
    "GPU_INFO_8__BY_KEY": "hardware_info",
    "GPU_INFO_9__BY_KEY": "hardware_info",
    "GPU_INFO_10__BY_KEY": "hardware_info",
    "GPU_INFO_11__BY_KEY": "hardware_info",
    "GPU_INFO_12__BY_KEY": "hardware_info",
    "GPU_INFO_13__BY_KEY": "hardware_info",
    "SCRIPTING_BACKEND__BY_KEY": "flags",
}

OTHER__PII_VALUES__WEBSOCKET = {
    "PLAY_SESSION_STATUS__BY_KEY": "session_info",
    "PLAY_SESSION_STATUS_2__BY_KEY": "session_info",
    "PLAY_SESSION_STATUS_3__BY_KEY": "session_info",
    "PLAY_SESSION_MSG": "session_info",
    "PLAY_SESSION_MSG_2": "session_info",
    "PLAY_SESSION_MSG_3": "session_info",
    "PLAY_SESSION_MSG_4": "session_info",
    "PLAY_SESSION_ID__BY_KEY": "session_info",
    "PLAY_SESSION_ID_2__BY_KEY": "session_info",
    "PLAY_SESSION_ID_3__BY_KEY": "session_info",
    "PLAY_SESSION_ID_4__BY_KEY": "session_info",
}

# merge the above dict into one. Make sure the keys are unique
PII_VALUES = dict()
PII_VALUES.update(QUEST2A__PII_VALUES)
PII_VALUES.update(QUEST2B__PII_VALUES)
PII_VALUES.update(OTHER__PII_VALUES)
PII_VALUES.update(OTHER__PII_VALUES__BY_KEY)
PII_VALUES.update(OTHER__PII_VALUES__WEBSOCKET)
PII_VALUES['Location'] = "geographical_location"
