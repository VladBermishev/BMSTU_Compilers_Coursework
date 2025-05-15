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

public class BasicNonEmptyStatementsImpl extends ASTWrapperPsiElement implements BasicNonEmptyStatements {

  public BasicNonEmptyStatementsImpl(@NotNull ASTNode node) {
    super(node);
  }

  public void accept(@NotNull BasicVisitor visitor) {
    visitor.visitNonEmptyStatements(this);
  }

  @Override
  public void accept(@NotNull PsiElementVisitor visitor) {
    if (visitor instanceof BasicVisitor) accept((BasicVisitor)visitor);
    else super.accept(visitor);
  }

  @Override
  @Nullable
  public BasicExitStatement getExitStatement() {
    return findChildByClass(BasicExitStatement.class);
  }

  @Override
  @Nullable
  public BasicNonEmptyStatements getNonEmptyStatements() {
    return findChildByClass(BasicNonEmptyStatements.class);
  }

  @Override
  @Nullable
  public BasicStatement getStatement() {
    return findChildByClass(BasicStatement.class);
  }

}
