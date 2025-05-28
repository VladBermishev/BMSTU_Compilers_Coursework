set(CMAKE_CXX_STANDARD 23)
set(CXX_SOURCES_NAMES "main")

set(HEADER_INSTALL_PREFIX "/usr/local/include")
set(LLVM_INSTALL_PREFIX "/usr/local/lib")

add_executable(std-library main.cpp)
target_link_libraries(std-library
        ${CMAKE_CURRENT_BINARY_DIR}/prog.o
)
target_link_options(std-library
        PUBLIC -lstdc++
)

foreach (name ${CXX_SOURCES_NAMES})
    add_custom_command(
            OUTPUT
                "${CMAKE_CURRENT_BINARY_DIR}/std.ll"
            COMMENT
                "Generating LLVM IR for ${CMAKE_CURRENT_SOURCE_DIR}/${name}.cpp"
            COMMAND
                clang -S -emit-llvm -std=c++23 -fPIE "${CMAKE_CURRENT_SOURCE_DIR}/${name}.cpp" -o "${CMAKE_CURRENT_BINARY_DIR}/std.ll"
            DEPENDS
                "${CMAKE_CURRENT_SOURCE_DIR}/${name}.cpp"
    )
    add_custom_command(
            OUTPUT
            "${CMAKE_CURRENT_BINARY_DIR}/std.o"
            COMMENT
            "Generating LLVM IR for ${CMAKE_CURRENT_SOURCE_DIR}/${name}.cpp"
            COMMAND
            clang -c -std=c++23 -fPIE "${CMAKE_CURRENT_SOURCE_DIR}/${name}.cpp" -o "${CMAKE_CURRENT_BINARY_DIR}/std.o"
            DEPENDS
            "${CMAKE_CURRENT_BINARY_DIR}/std.ll"
    )
    list(APPEND LLVM_RESULTS "${CMAKE_CURRENT_BINARY_DIR}/std.ll" "${CMAKE_CURRENT_BINARY_DIR}/std.o")
endforeach ()

add_custom_target(std-library-llvm ALL DEPENDS ${LLVM_RESULTS})

install(FILES
        "${CMAKE_CURRENT_SOURCE_DIR}/std.basic"
        DESTINATION "${HEADER_INSTALL_PREFIX}/tbasic"
)
install(FILES
        "${CMAKE_CURRENT_BINARY_DIR}/std.ll"
        DESTINATION "${LLVM_INSTALL_PREFIX}/tbasic"
)
install(FILES
        "${CMAKE_CURRENT_BINARY_DIR}/std.o"
        DESTINATION "${LLVM_INSTALL_PREFIX}/tbasic"
)