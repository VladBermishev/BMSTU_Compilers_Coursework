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

public class BasicGlobalSymbolImpl extends ASTWrapperPsiElement implements BasicGlobalSymbol {

  public BasicGlobalSymbolImpl(@NotNull ASTNode node) {
    super(node);
  }

  public void accept(@NotNull BasicVisitor visitor) {
    visitor.visitGlobalSymbol(this);
  }

  @Override
  public void accept(@NotNull PsiElementVisitor visitor) {
    if (visitor instanceof BasicVisitor) accept((BasicVisitor)visitor);
    else super.accept(visitor);
  }

  @Override
  @Nullable
  public BasicFunctionDecl getFunctionDecl() {
    return findChildByClass(BasicFunctionDecl.class);
  }

  @Override
  @Nullable
  public BasicFunctionDef getFunctionDef() {
    return findChildByClass(BasicFunctionDef.class);
  }

  @Override
  @Nullable
  public BasicPreprocessorCommand getPreprocessorCommand() {
    return findChildByClass(BasicPreprocessorCommand.class);
  }

  @Override
  @Nullable
  public BasicSubroutineDecl getSubroutineDecl() {
    return findChildByClass(BasicSubroutineDecl.class);
  }

  @Override
  @Nullable
  public BasicSubroutineDef getSubroutineDef() {
    return findChildByClass(BasicSubroutineDef.class);
  }

  @Override
  @Nullable
  public BasicVariableDecl getVariableDecl() {
    return findChildByClass(BasicVariableDecl.class);
  }

}
