set(CMAKE_CXX_STANDARD 23)
set(CXX_SOURCES_NAMES "main")

set(HEADER_INSTALL_PREFIX "/usr/local/include")
set(LLVM_INSTALL_PREFIX "/usr/local/lib")

#add_executable(std-library main.cpp)

foreach (name ${CXX_SOURCES_NAMES})
    add_custom_command(
            OUTPUT
                "${CMAKE_CURRENT_BINARY_DIR}/${name}.ll"
            COMMENT
                "Generating LLVM IR for ${CMAKE_CURRENT_SOURCE_DIR}/${name}.cpp"
            COMMAND
                clang -S -emit-llvm -std=c++23 "${CMAKE_CURRENT_SOURCE_DIR}/${name}.cpp" -o "${CMAKE_CURRENT_BINARY_DIR}/std.ll"
            DEPENDS
                "${CMAKE_CURRENT_SOURCE_DIR}/${name}.cpp"
    )
    list(APPEND LLVM_RESULTS "${CMAKE_CURRENT_BINARY_DIR}/${name}.ll")
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