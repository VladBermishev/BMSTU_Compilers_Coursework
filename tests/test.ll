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
  %".9" = load i32, i32* %"items.len.1.1"
  %"bin_cmp_val" = icmp sge i32 %".9", 1
  %"if.cond" = icmp ne i1 %"bin_cmp_val", 0
  br i1 %"if.cond", label %"entry.if.then", label %"entry.if.else"
entry.if.then:
  %"idx_sub" = sub i32 1, 1
  %"gep_load" = load i32**, i32*** %"items.1"
  %"gep_idx" = getelementptr inbounds i32*, i32** %"gep_load", i32 %"idx_sub"
  %"gep_idx_load" = load i32*, i32** %"gep_idx"
  %"str_copy_val" = call i32* @"StringCopy"(i32* %"gep_idx_load")
  store i32* %"str_copy_val", i32** %"Join"
  br label %"entry.if.end"
entry.if.else:
  %"gep_idx.1" = getelementptr inbounds [1 x i32], [1 x i32]* @".str.1", i32 0, i32 0
  store i32* %"gep_idx.1", i32** %"Join"
  br label %"entry.if.end"
entry.if.end:
  %".15" = load i32, i32* %"items.len.1.1"
  %".16" = alloca i32, i32 1
  store i32 2, i32* %".16"
  br label %"entry.if.end.for.cond"
entry.if.end.for.cond:
  %"for.idx" = load i32, i32* %".16"
  %".19" = icmp sle i32 %"for.idx", %".15"
  br i1 %".19", label %"entry.if.end.for.body", label %"entry.if.end.for.end"
entry.if.end.for.body:
  %"JoinS.load" = load i32*, i32** %"Join"
  %"sepS.load" = load i32*, i32** %"sep.1"
  %"str_concat_val" = call i32* @"StringConcat"(i32* %"JoinS.load", i32* %"sepS.load")
  %"iI.load" = load i32, i32* %".16"
  %"idx_sub.1" = sub i32 %"iI.load", 1
  %"gep_load.1" = load i32**, i32*** %"items.1"
  %"gep_idx.2" = getelementptr inbounds i32*, i32** %"gep_load.1", i32 %"idx_sub.1"
  %"gep_idx_load.1" = load i32*, i32** %"gep_idx.2"
  %"str_concat_val.1" = call i32* @"StringConcat"(i32* %"str_concat_val", i32* %"gep_idx_load.1")
  %"str_copy_val.1" = call i32* @"StringCopy"(i32* %"str_concat_val.1")
  store i32* %"str_copy_val.1", i32** %"Join"
  br label %"entry.if.end.for.inc"
entry.if.end.for.inc:
  %"for.idx.1" = load i32, i32* %".16"
  %".21" = add i32 %"for.idx.1", 1
  store i32 %".21", i32* %".16"
  br label %"entry.if.end.for.cond"
entry.if.end.for.end:
  br label %"return"
return:
  %".27" = load i32*, i32** %"Join"
  ret i32* %".27"
}

@".str.1" = global [1 x i32] [i32 0]