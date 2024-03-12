#include <cstdio>
#include <cstring>
#include <cstdlib>
#include <cwchar>
#include <clocale>
extern "C" void PrintI(int val){ printf("%d", val); }
extern "C" void PrintL(long val){ printf("%ld", val); }
extern "C" void PrintD(double val){ printf("%lf", val); }
extern "C" void PrintF(float val){ printf("%f", val); }
extern "C" void PrintS(wchar_t* val){ printf("%ls", val); }
extern "C" wchar_t* StringConcat(wchar_t* lhs, wchar_t* rhs){
    unsigned long __sz_lhs = wcslen(lhs), __sz_rhs = wcslen(rhs);
    lhs = (wchar_t*)reallocarray(lhs, __sz_lhs + __sz_rhs + 1, sizeof(wchar_t));
    return wcscat(lhs, rhs);
}
extern "C" wchar_t* StringCopy(wchar_t* str){
    unsigned long __sz = wcslen(str);
    wchar_t* result = (wchar_t*)calloc(__sz + 1, sizeof(wchar_t));
    wcsncpy(result, str, __sz);
    return result;
}
extern "C" wchar_t* Main(wchar_t** argv, int len);
int main(int argc, char** argv){
    setlocale(LC_ALL, "C.UTF-8");
    wchar_t** args = (wchar_t**)calloc(argc, sizeof(wchar_t*));
    for(int idx = 0; idx < argc; idx++){
        unsigned long __sz = strlen(argv[idx]);
        args[idx] = (wchar_t*) calloc(__sz + 1,sizeof(wchar_t));
        for(int row_idx = 0; row_idx < __sz; row_idx++)
            args[idx][row_idx] = argv[idx][row_idx];
    }
    Main(args, argc);
    for(int idx = 0; idx < argc; idx++)
        free(args[idx]);
    free(args);
    return 0;
}