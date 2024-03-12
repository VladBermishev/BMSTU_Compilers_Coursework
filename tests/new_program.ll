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

define double @"SumArray"(double* %"Values", i32 %"Values.len.1")
{
entry:
  %"SumArray" = alloca double, i32 1
  store double              0x0, double* %"SumArray"
  %"Values.1" = alloca double*, i32 1
  store double* %"Values", double** %"Values.1"
  %"Values.len.1.1" = alloca i32, i32 1
  store i32 %"Values.len.1", i32* %"Values.len.1.1"
  %".7" = sitofp i32 0 to double
  store double %".7", double* %"SumArray"
  %".9" = load i32, i32* %"Values.len.1.1"
  %".10" = alloca i32, i32 1
  store i32 1, i32* %".10"
  br label %"entry.for.cond"
entry.for.cond:
  %"for.idx" = load i32, i32* %".10"
  %".13" = icmp sle i32 %"for.idx", %".9"
  br i1 %".13", label %"entry.for.body", label %"entry.for.end"
entry.for.body:
  %"SumArrayD.load" = load double, double* %"SumArray"
  %"iI.load" = load i32, i32* %".10"
  %"idx_sub" = sub i32 %"iI.load", 1
  %"gep_load" = load double*, double** %"Values.1"
  %"gep_idx" = getelementptr inbounds double, double* %"gep_load", i32 %"idx_sub"
  %"gep_idx_load" = load double, double* %"gep_idx"
  %"bin_add_val" = fadd double %"SumArrayD.load", %"gep_idx_load"
  store double %"bin_add_val", double* %"SumArray"
  br label %"entry.for.inc"
entry.for.inc:
  %"for.idx.1" = load i32, i32* %".10"
  %".15" = add i32 %"for.idx.1", 1
  store i32 %".15", i32* %".10"
  br label %"entry.for.cond"
entry.for.end:
  br label %"return"
return:
  %".21" = load double, double* %"SumArray"
  ret double %".21"
}

define float @"Polynom"(float %"x", float* %"coefs", i32 %"coefs.len.1")
{
entry:
  %"Polynom" = alloca float, i32 1
  store float              0x0, float* %"Polynom"
  %"x.1" = alloca float, i32 1
  store float %"x", float* %"x.1"
  %"coefs.1" = alloca float*, i32 1
  store float* %"coefs", float** %"coefs.1"
  %"coefs.len.1.1" = alloca i32, i32 1
  store i32 %"coefs.len.1", i32* %"coefs.len.1.1"
  %".9" = sitofp i32 0 to float
  store float %".9", float* %"Polynom"
  %".11" = load i32, i32* %"coefs.len.1.1"
  %".12" = alloca i32, i32 1
  store i32 1, i32* %".12"
  br label %"entry.for.cond"
entry.for.cond:
  %"for.idx" = load i32, i32* %".12"
  %".15" = icmp sle i32 %"for.idx", %".11"
  br i1 %".15", label %"entry.for.body", label %"entry.for.end"
entry.for.body:
  %"PolynomF.load" = load float, float* %"Polynom"
  %"xF.load" = load float, float* %"x.1"
  %"bin_mul_val" = fmul float %"PolynomF.load", %"xF.load"
  %"iI.load" = load i32, i32* %".12"
  %"idx_sub" = sub i32 %"iI.load", 1
  %"gep_load" = load float*, float** %"coefs.1"
  %"gep_idx" = getelementptr inbounds float, float* %"gep_load", i32 %"idx_sub"
  %"gep_idx_load" = load float, float* %"gep_idx"
  %"bin_add_val" = fadd float %"bin_mul_val", %"gep_idx_load"
  store float %"bin_add_val", float* %"Polynom"
  br label %"entry.for.inc"
entry.for.inc:
  %"for.idx.1" = load i32, i32* %".12"
  %".17" = add i32 %"for.idx.1", 1
  store i32 %".17", i32* %".12"
  br label %"entry.for.cond"
entry.for.end:
  br label %"return"
return:
  %".23" = load float, float* %"Polynom"
  ret float %".23"
}

define float @"Polynom1111"(float %"x")
{
entry:
  %"Polynom1111" = alloca float, i32 1
  store float              0x0, float* %"Polynom1111"
  %"x.1" = alloca float, i32 1
  store float %"x", float* %"x.1"
  %"coefsF" = alloca [4 x float], i32 1
  %".5" = alloca i32, i32 1
  store i32 1, i32* %".5"
  br label %"entry.for.cond"
entry.for.cond:
  %"for.idx" = load i32, i32* %".5"
  %".8" = icmp sle i32 %"for.idx", 4
  br i1 %".8", label %"entry.for.body", label %"entry.for.end"
entry.for.body:
  %"iI.load" = load i32, i32* %".5"
  %"idx_sub" = sub i32 %"iI.load", 1
  %"gep_idx" = getelementptr inbounds [4 x float], [4 x float]* %"coefsF", i32 0, i32 %"idx_sub"
  %".13" = sitofp i32 1 to float
  store float %".13", float* %"gep_idx"
  br label %"entry.for.inc"
entry.for.inc:
  %"for.idx.1" = load i32, i32* %".5"
  %".10" = add i32 %"for.idx.1", 1
  store i32 %".10", i32* %".5"
  br label %"entry.for.cond"
entry.for.end:
  %"xF.load" = load float, float* %"x.1"
  %"gep_idx.1" = getelementptr inbounds [4 x float], [4 x float]* %"coefsF", i32 0, i32 0
  %"call" = call float @"Polynom"(float %"xF.load", float* %"gep_idx.1", i32 4)
  store float %"call", float* %"Polynom1111"
  br label %"return"
return:
  %".18" = load float, float* %"Polynom1111"
  ret float %".18"
}

define void @"Fibonacci"(i64* %"res", i32 %"res.len.1")
{
entry:
  %"res.1" = alloca i64*, i32 1
  store i64* %"res", i64** %"res.1"
  %"res.len.1.1" = alloca i32, i32 1
  store i32 %"res.len.1", i32* %"res.len.1.1"
  %"nI" = alloca i32, i32 1
  %".7" = load i32, i32* %"res.len.1.1"
  store i32 %".7", i32* %"nI"
  %"nI.load" = load i32, i32* %"nI"
  %"bin_cmp_val" = icmp sge i32 %"nI.load", 1
  %"if.cond" = icmp ne i1 %"bin_cmp_val", 0
  br i1 %"if.cond", label %"entry.if.then", label %"entry.if.end"
entry.if.then:
  %"idx_sub" = sub i32 1, 1
  %"gep_load" = load i64*, i64** %"res.1"
  %"gep_idx" = getelementptr inbounds i64, i64* %"gep_load", i32 %"idx_sub"
  %".10" = zext i32 1 to i64
  store i64 %".10", i64* %"gep_idx"
  br label %"entry.if.end"
entry.if.end:
  %"nI.load.1" = load i32, i32* %"nI"
  %"bin_cmp_val.1" = icmp sge i32 %"nI.load.1", 2
  %"if.cond.1" = icmp ne i1 %"bin_cmp_val.1", 0
  br i1 %"if.cond.1", label %"entry.if.end.if.then", label %"entry.if.end.if.end"
entry.if.end.if.then:
  %"idx_sub.1" = sub i32 2, 1
  %"gep_load.1" = load i64*, i64** %"res.1"
  %"gep_idx.1" = getelementptr inbounds i64, i64* %"gep_load.1", i32 %"idx_sub.1"
  %".14" = zext i32 1 to i64
  store i64 %".14", i64* %"gep_idx.1"
  br label %"entry.if.end.if.end"
entry.if.end.if.end:
  %"iI" = alloca i32, i32 1
  store i32 3, i32* %"iI"
  br label %"entry.if.end.if.end.for.cond"
entry.if.end.if.end.for.cond:
  %"iI.load" = load i32, i32* %"iI"
  %"nI.load.2" = load i32, i32* %"nI"
  %"bin_cmp_val.2" = icmp sle i32 %"iI.load", %"nI.load.2"
  %"while.cond" = icmp ne i1 %"bin_cmp_val.2", 0
  br i1 %"while.cond", label %"entry.if.end.if.end.for.body", label %"entry.if.end.if.end.for.end"
entry.if.end.if.end.for.body:
  %"iI.load.1" = load i32, i32* %"iI"
  %"idx_sub.2" = sub i32 %"iI.load.1", 1
  %"gep_load.2" = load i64*, i64** %"res.1"
  %"gep_idx.2" = getelementptr inbounds i64, i64* %"gep_load.2", i32 %"idx_sub.2"
  %"iI.load.2" = load i32, i32* %"iI"
  %"bin_sub_val" = sub i32 %"iI.load.2", 1
  %"idx_sub.3" = sub i32 %"bin_sub_val", 1
  %"gep_load.3" = load i64*, i64** %"res.1"
  %"gep_idx.3" = getelementptr inbounds i64, i64* %"gep_load.3", i32 %"idx_sub.3"
  %"gep_idx_load" = load i64, i64* %"gep_idx.3"
  %"iI.load.3" = load i32, i32* %"iI"
  %"bin_sub_val.1" = sub i32 %"iI.load.3", 2
  %"idx_sub.4" = sub i32 %"bin_sub_val.1", 1
  %"gep_load.4" = load i64*, i64** %"res.1"
  %"gep_idx.4" = getelementptr inbounds i64, i64* %"gep_load.4", i32 %"idx_sub.4"
  %"gep_idx_load.1" = load i64, i64* %"gep_idx.4"
  %"bin_add_val" = add i64 %"gep_idx_load", %"gep_idx_load.1"
  store i64 %"bin_add_val", i64* %"gep_idx.2"
  %"iI.load.4" = load i32, i32* %"iI"
  %"bin_add_val.1" = add i32 %"iI.load.4", 1
  store i32 %"bin_add_val.1", i32* %"iI"
  br label %"entry.if.end.if.end.for.cond"
entry.if.end.if.end.for.end:
  br label %"return"
return:
  ret void
}

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
define void @"Main"(i32** %"args", i32 %"args.len.1")
{
entry:
  %"args.1" = alloca i32**, i32 1
  store i32** %"args", i32*** %"args.1"
  %"args.len.1.1" = alloca i32, i32 1
  store i32 %"args.len.1", i32* %"args.len.1.1"
  %"gep_idx" = getelementptr inbounds [22 x i32], [22 x i32]* @".str.2", i32 0, i32 0
  call void @"PrintS"(i32* %"gep_idx")
  %"gep_idx.1" = getelementptr inbounds [3 x i32], [3 x i32]* @".str.3", i32 0, i32 0
  %"gep_load" = load i32**, i32*** %"args.1"
  %"gep_idx.2" = getelementptr inbounds i32*, i32** %"gep_load", i32 0
  %".8" = load i32, i32* %"args.len.1.1"
  %"call" = call i32* @"Join"(i32* %"gep_idx.1", i32** %"gep_idx.2", i32 %".8")
  call void @"PrintS"(i32* %"call")
  %"gep_idx.3" = getelementptr inbounds [2 x i32], [2 x i32]* @".str.4", i32 0, i32 0
  call void @"PrintS"(i32* %"gep_idx.3")
  %"fibsL" = alloca [100 x i64], i32 1
  %"gep_idx.4" = getelementptr inbounds [100 x i64], [100 x i64]* %"fibsL", i32 0, i32 0
  call void @"Fibonacci"(i64* %"gep_idx.4", i32 100)
  %"gep_idx.5" = getelementptr inbounds [24 x i32], [24 x i32]* @".str.5", i32 0, i32 0
  call void @"PrintS"(i32* %"gep_idx.5")
  %"idx_sub" = sub i32 50, 1
  %"gep_idx.6" = getelementptr inbounds [100 x i64], [100 x i64]* %"fibsL", i32 0, i32 %"idx_sub"
  %"gep_idx_load" = load i64, i64* %"gep_idx.6"
  call void @"PrintL"(i64 %"gep_idx_load")
  %"gep_idx.7" = getelementptr inbounds [2 x i32], [2 x i32]* @".str.6", i32 0, i32 0
  call void @"PrintS"(i32* %"gep_idx.7")
  %"ysD" = alloca [101 x double], i32 1
  %"gep_idx.8" = getelementptr inbounds [47 x i32], [47 x i32]* @".str.7", i32 0, i32 0
  call void @"PrintS"(i32* %"gep_idx.8")
  %".16" = alloca i32, i32 1
  store i32 -50, i32* %".16"
  br label %"entry.for.cond"
entry.for.cond:
  %"for.idx" = load i32, i32* %".16"
  %".19" = icmp sle i32 %"for.idx", 50
  br i1 %".19", label %"entry.for.body", label %"entry.for.end"
entry.for.body:
  %"yF" = alloca float, i32 1
  %"xI.load" = load i32, i32* %".16"
  %".24" = sitofp i32 %"xI.load" to float
  %"call.1" = call float @"Polynom1111"(float %".24")
  store float %"call.1", float* %"yF"
  %"gep_idx.9" = getelementptr inbounds [5 x i32], [5 x i32]* @".str.8", i32 0, i32 0
  call void @"PrintS"(i32* %"gep_idx.9")
  %"xI.load.1" = load i32, i32* %".16"
  call void @"PrintI"(i32 %"xI.load.1")
  %"gep_idx.10" = getelementptr inbounds [7 x i32], [7 x i32]* @".str.9", i32 0, i32 0
  call void @"PrintS"(i32* %"gep_idx.10")
  %"yF.load" = load float, float* %"yF"
  call void @"PrintF"(float %"yF.load")
  %"gep_idx.11" = getelementptr inbounds [2 x i32], [2 x i32]* @".str.10", i32 0, i32 0
  call void @"PrintS"(i32* %"gep_idx.11")
  %"xI.load.2" = load i32, i32* %".16"
  %"bin_add_val" = add i32 %"xI.load.2", 51
  %"idx_sub.1" = sub i32 %"bin_add_val", 1
  %"gep_idx.12" = getelementptr inbounds [101 x double], [101 x double]* %"ysD", i32 0, i32 %"idx_sub.1"
  %"yF.load.1" = load float, float* %"yF"
  %".31" = fpext float %"yF.load.1" to double
  store double %".31", double* %"gep_idx.12"
  br label %"entry.for.inc"
entry.for.inc:
  %"for.idx.1" = load i32, i32* %".16"
  %".21" = add i32 %"for.idx.1", 1
  store i32 %".21", i32* %".16"
  br label %"entry.for.cond"
entry.for.end:
  %"gep_idx.13" = getelementptr inbounds [33 x i32], [33 x i32]* @".str.11", i32 0, i32 0
  call void @"PrintS"(i32* %"gep_idx.13")
  %"gep_idx.14" = getelementptr inbounds [101 x double], [101 x double]* %"ysD", i32 0, i32 0
  %"call.2" = call double @"SumArray"(double* %"gep_idx.14", i32 101)
  call void @"PrintD"(double %"call.2")
  %"gep_idx.15" = getelementptr inbounds [2 x i32], [2 x i32]* @".str.12", i32 0, i32 0
  call void @"PrintS"(i32* %"gep_idx.15")
  br label %"return"
return:
  ret void
}

@".str.2" = global [22 x i32] [i32 1040, i32 1088, i32 1075, i32 1091, i32 1084, i32 1077, i32 1085, i32 1090, i32 1099, i32 32, i32 1087, i32 1088, i32 1086, i32 1075, i32 1088, i32 1072, i32 1084, i32 1084, i32 1099, i32 58, i32 32, i32 0]
@".str.3" = global [3 x i32] [i32 44, i32 32, i32 0]
@".str.4" = global [2 x i32] [i32 10, i32 0]
@".str.5" = global [24 x i32] [i32 53, i32 48, i32 45, i32 1077, i32 32, i32 1095, i32 1080, i32 1089, i32 1083, i32 1086, i32 32, i32 1060, i32 1080, i32 1073, i32 1086, i32 1085, i32 1072, i32 1095, i32 1095, i32 1080, i32 32, i32 8212, i32 32, i32 0]
@".str.6" = global [2 x i32] [i32 10, i32 0]
@".str.7" = global [47 x i32] [i32 1058, i32 1072, i32 1073, i32 1083, i32 1080, i32 1094, i32 1072, i32 32, i32 1079, i32 1085, i32 1072, i32 1095, i32 1077, i32 1085, i32 1080, i32 1081, i32 32, i32 1092, i32 1091, i32 1085, i32 1082, i32 1094, i32 1080, i32 1080, i32 32, i32 121, i32 32, i32 61, i32 32, i32 120, i32 179, i32 32, i32 43, i32 32, i32 120, i32 178, i32 32, i32 43, i32 32, i32 120, i32 32, i32 43, i32 32, i32 49, i32 58, i32 10, i32 0]
@".str.8" = global [5 x i32] [i32 120, i32 32, i32 61, i32 32, i32 0]
@".str.9" = global [7 x i32] [i32 44, i32 32, i32 121, i32 32, i32 61, i32 32, i32 0]
@".str.10" = global [2 x i32] [i32 10, i32 0]
@".str.11" = global [33 x i32] [i32 1057, i32 1091, i32 1084, i32 1084, i32 1072, i32 32, i32 1087, i32 1077, i32 1088, i32 1077, i32 1095, i32 1080, i32 1089, i32 1083, i32 1077, i32 1085, i32 1085, i32 1099, i32 1093, i32 32, i32 1079, i32 1085, i32 1072, i32 1095, i32 1077, i32 1085, i32 1080, i32 1081, i32 32, i32 121, i32 58, i32 32, i32 0]
@".str.12" = global [2 x i32] [i32 10, i32 0]