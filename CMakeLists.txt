cmake_minimum_required(VERSION 3.20.0)
project(TBasicCompiler)

set(APPLICATION_DIR ${CMAKE_CURRENT_SOURCE_DIR})
set(SOURCES_DIR ${CMAKE_CURRENT_SOURCE_DIR}/src/)
set(VENV_DIR ${CMAKE_CURRENT_SOURCE_DIR}/venv/)
set(BINARY_INSTALL_DIR "/usr/local/bin")

file(GLOB_RECURSE SOURCES ${SOURCES_DIR}/*)

add_custom_command(OUTPUT ${APPLICATION_DIR}/bin/
        COMMAND ${VENV_DIR}/bin/pyinstaller -F
            --paths ${VENV_DIR}/lib/python3.12/site-packages
            --paths ${APPLICATION_DIR}
            --workpath ${CMAKE_CURRENT_BINARY_DIR}/py-build
            --distpath ${APPLICATION_DIR}/bin/
            --clean  ${SOURCES_DIR}/main.py
            --name "tbasic"
        DEPENDS ${SOURCES}
)
add_custom_target(compiler-build
        WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
        DEPENDS ${APPLICATION_DIR}/bin/
        COMMENT "Building compiler"
)

install(FILES
        ${APPLICATION_DIR}/bin/tbasic
        DESTINATION "${BINARY_INSTALL_DIR}"
        PERMISSIONS OWNER_READ OWNER_WRITE OWNER_EXECUTE GROUP_READ GROUP_EXECUTE WORLD_READ WORLD_EXECUTE
)

add_subdirectory(src)