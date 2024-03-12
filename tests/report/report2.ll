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
  %"iI" = alloca i32, i32 1
  store i32 0, i32* %"iI"
  br label %"entry.for.cond"
entry.for.cond:
  %"iI.load" = load i32, i32* %"iI"
  %"bin_cmp_val" = icmp slt i32 %"iI.load", 10
  %"while.cond" = icmp ne i1 %"bin_cmp_val", 0
  br i1 %"while.cond", label %"entry.for.body", label %"entry.for.end"
entry.for.body:
  %"iI.load.1" = load i32, i32* %"iI"
  %"bin_add_val" = add i32 %"iI.load.1", 1
  store i32 %"bin_add_val", i32* %"iI"
  br label %"entry.for.cond"
entry.for.end:
  br label %"return"
return:
  %".15" = load i32*, i32** %"Join"
  ret i32* %".15"
}
