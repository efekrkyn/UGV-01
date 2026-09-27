# The host-tested core and board arithmetic are compiled unchanged; app_main.c is the only ESP-IDF code.
idf_component_register(
    SRCS "app_main.c"
         "../../lite_core.c" "../../arm_path.c" "../../lite_link.c" "../../hmac_sha256.c" "../../board_math.c" "../../vl53l0x.c"
         "../../../stm32/can_protocol.c" "../../../stm32/servo_control.c" "../../../stm32/light_bar.c"
    INCLUDE_DIRS "." "../.."
    REQUIRES driver esp_adc esp_wifi esp_netif esp_event esp_timer nvs_flash)
# Shared host-tested code must stay warning-free under the Xtensa GCC too.
target_compile_options(${COMPONENT_LIB} PRIVATE -Wextra -Werror)
