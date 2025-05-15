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

public class BasicArithmExprImpl extends ASTWrapperPsiElement implements BasicArithmExpr {

  public BasicArithmExprImpl(@NotNull ASTNode node) {
    super(node);
  }

  public void accept(@NotNull BasicVisitor visitor) {
    visitor.visitArithmExpr(this);
  }

  @Override
  public void accept(@NotNull PsiElementVisitor visitor) {
    if (visitor instanceof BasicVisitor) accept((BasicVisitor)visitor);
    else super.accept(visitor);
  }

  @Override
  @Nullable
  public BasicAddOp getAddOp() {
    return findChildByClass(BasicAddOp.class);
  }

  @Override
  @Nullable
  public BasicArithmExpr getArithmExpr() {
    return findChildByClass(BasicArithmExpr.class);
  }

  @Override
  @NotNull
  public BasicTerm getTerm() {
    return findNotNullChildByClass(BasicTerm.class);
  }

}
