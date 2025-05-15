// This is a generated file. Not intended for manual editing.
package org.intellij.sdk.language.psi.impl;

import java.util.List;
import org.jetbrains.annotations.*;
import com.intellij.lang.ASTNode;
import com.intellij.psi.PsiElement;
import com.intellij.psi.PsiElementVisitor;
import com.intellij.psi.util.PsiTreeUtil;
import static org.intellij.sdk.language.psi.BasicTypes.*;
import com.intellij.extapi.psi.ASTWrapperPsiElement;
import org.intellij.sdk.language.psi.*;

public class BasicPowerImpl extends ASTWrapperPsiElement implements BasicPower {

  public BasicPowerImpl(@NotNull ASTNode node) {
    super(node);
  }

  public void accept(@NotNull BasicVisitor visitor) {
    visitor.visitPower(this);
  }

  @Override
  public void accept(@NotNull PsiElementVisitor visitor) {
    if (visitor instanceof BasicVisitor) accept((BasicVisitor)visitor);
    else super.accept(visitor);
  }

  @Override
  @Nullable
  public BasicConst getConst() {
    return findChildByClass(BasicConst.class);
  }

  @Override
  @Nullable
  public BasicExpr getExpr() {
    return findChildByClass(BasicExpr.class);
  }

  @Override
  @Nullable
  public BasicFuncCallOrArrayIndex getFuncCallOrArrayIndex() {
    return findChildByClass(BasicFuncCallOrArrayIndex.class);
  }

  @Override
  @Nullable
  public BasicVarname getVarname() {
    return findChildByClass(BasicVarname.class);
  }

}
