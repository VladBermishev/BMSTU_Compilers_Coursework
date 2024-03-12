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

define i32* @"Join"()
{
entry:
  %"Join" = alloca i32*, i32 1
  store i32* null, i32** %"Join"
  %".3" = alloca i32, i32 1
  store i32 2, i32* %".3"
  br label %"entry.for.cond"
entry.for.cond:
  %"for.idx" = load i32, i32* %".3"
  %".6" = icmp sle i32 %"for.idx", 10
  br i1 %".6", label %"entry.for.body", label %"entry.for.end"
entry.for.body:
  %"iI.load" = load i32, i32* %".3"
  %"bin_cmp_val" = icmp eq i32 %"iI.load", 10
  %"if.cond" = icmp ne i1 %"bin_cmp_val", 0
  br i1 %"if.cond", label %"entry.for.body.if.then", label %"entry.for.body.if.end"
entry.for.body.if.then:
  br label %"entry.for.end"
entry.for.body.if.end:
  br label %"entry.for.inc"
entry.for.inc:
  %"for.idx.1" = load i32, i32* %".3"
  %".8" = add i32 %"for.idx.1", 1
  store i32 %".8", i32* %".3"
  br label %"entry.for.cond"
entry.for.end:
  br label %"return"
return:
  %".15" = load i32*, i32** %"Join"
  ret i32* %".15"
}
