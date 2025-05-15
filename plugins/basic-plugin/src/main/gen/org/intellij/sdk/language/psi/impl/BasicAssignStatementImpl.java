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

public class BasicAssignStatementImpl extends ASTWrapperPsiElement implements BasicAssignStatement {

  public BasicAssignStatementImpl(@NotNull ASTNode node) {
    super(node);
  }

  public void accept(@NotNull BasicVisitor visitor) {
    visitor.visitAssignStatement(this);
  }

  @Override
  public void accept(@NotNull PsiElementVisitor visitor) {
    if (visitor instanceof BasicVisitor) accept((BasicVisitor)visitor);
    else super.accept(visitor);
  }

  @Override
  @NotNull
  public BasicExpr getExpr() {
    return findNotNullChildByClass(BasicExpr.class);
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
