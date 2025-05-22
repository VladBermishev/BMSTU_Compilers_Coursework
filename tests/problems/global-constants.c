#include <stdio.h>
/* Clang(C) reporting 'error: initializer element is not a compile-time constant' */
/* Clang(Cpp)
@llvm.global_ctors = appending global [1 x { i32, ptr, ptr }] [{ i32, ptr, ptr } { i32 65535, ptr @_GLOBAL__sub_I_example.cpp, ptr null }]

define internal void @__cxx_global_var_init() section ".text.startup" {
entry:
  %0 = load i32, ptr @x, align 4
  %1 = load i32, ptr @y, align 4
  %add = add nsw i32 %0, %1
  store i32 %add, ptr @z, align 4
  ret void
}
define internal void @_GLOBAL__sub_I_example.cpp() section ".text.startup" {
entry:
  call void @__cxx_global_var_init()
  ret void
}

*/
int x = 10;
int y = 20;
int z = x + y;
int main(int argc, char** argv){
    struct{int* x; int y[3];} a;
    a.y[1] = 10;
    return 0;
}