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

public class BasicLoopStmtImpl extends ASTWrapperPsiElement implements BasicLoopStmt {

  public BasicLoopStmtImpl(@NotNull ASTNode node) {
    super(node);
  }

  public void accept(@NotNull BasicVisitor visitor) {
    visitor.visitLoopStmt(this);
  }

  @Override
  public void accept(@NotNull PsiElementVisitor visitor) {
    if (visitor instanceof BasicVisitor) accept((BasicVisitor)visitor);
    else super.accept(visitor);
  }

  @Override
  @Nullable
  public BasicForLoop getForLoop() {
    return findChildByClass(BasicForLoop.class);
  }

  @Override
  @Nullable
  public BasicWhileLoop getWhileLoop() {
    return findChildByClass(BasicWhileLoop.class);
  }

}
