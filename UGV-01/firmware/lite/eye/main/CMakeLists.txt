idf_component_register(
    SRCS "eye_main.c"
    REQUIRES driver esp_wifi esp_netif esp_event esp_http_server nvs_flash)
target_compile_options(${COMPONENT_LIB} PRIVATE -Wextra -Werror)
