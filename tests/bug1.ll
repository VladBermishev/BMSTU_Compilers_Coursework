; ModuleID = "/home/user/code/BMSTU/compilers/coursework/src/ast_v2.py"
target triple = "x86_64-unknown-linux-gnu"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"

@"llvm.global_ctors" = appending global [1 x {i32, ptr, ptr}] [{i32, ptr, ptr} {i32 65535, ptr @variable_decl_constructor, ptr null}]
define void @"variable_decl_constructor"()
{
entry:
  call void @"__bas_global_var_init.arrF"()
  ret void
}

declare void @"PrintI"(i32 %"val")

declare void @"PrintL"(i64 %"val")

declare void @"PrintF"(float %"val")

declare void @"PrintD"(double %"val")

declare void @"PrintS"(i32* %"val")

declare i32* @"StringConcat"(i32* %"lhs", i32* %"rhs")

declare i32* @"StringCopy"(i32* %"lhs")

@"arrF" = global [2 x float] [float              0x0, float              0x0]
define void @"__bas_global_var_init.arrF"()
{
entry:
  %"gep_idx" = getelementptr inbounds [2 x float], [2 x float]* @"arrF", i32 0, i32 0
  %".2" = sitofp i32 1 to float
  store float %".2", float* %"gep_idx"
  %"gep_idx.1" = getelementptr inbounds [2 x float], [2 x float]* @"arrF", i32 0, i32 1
  %".4" = sitofp i32 2 to float
  store float %".4", float* %"gep_idx.1"
  ret void
}
