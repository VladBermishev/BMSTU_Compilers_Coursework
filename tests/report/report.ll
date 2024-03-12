; ModuleID = "/home/user/code/BMSTU/compilers/coursework/src/ast_v2.py"
target triple = "x86_64-unknown-linux-gnu"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"

@"llvm.global_ctors" = appending global [1 x {i32, ptr, ptr}] [{i32, ptr, ptr} {i32 65535, ptr @variable_decl_constructor, ptr null}]
define void @"variable_decl_constructor"()
{
entry:
  ret void
}

declare void @"PrintI"(i32 %"val")

declare void @"PrintL"(i64 %"val")

declare void @"PrintF"(float %"val")

declare void @"PrintD"(double %"val")

declare void @"PrintS"(i32* %"val")

declare i32* @"StringConcat"(i32* %"lhs", i32* %"rhs")

declare i32* @"StringCopy"(i32* %"lhs")

define i32* @"Join"(i32* %"sep", i32** %"items", i32 %"items.len.1")
{
entry:
  %"Join" = alloca i32*, i32 1
  store i32* null, i32** %"Join"
  %"sep.1" = alloca i32*, i32 1
  store i32* %"sep", i32** %"sep.1"
  %"items.1" = alloca i32**, i32 1
  store i32** %"items", i32*** %"items.1"
  %"items.len.1.1" = alloca i32, i32 1
  store i32 %"items.len.1", i32* %"items.len.1.1"
  br label %"return"
return:
  %".10" = load i32*, i32** %"Join"
  ret i32* %".10"
}
