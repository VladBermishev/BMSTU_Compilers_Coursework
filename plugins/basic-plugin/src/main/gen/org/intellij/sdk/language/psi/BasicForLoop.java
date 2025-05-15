// This is a generated file. Not intended for manual editing.
package org.intellij.sdk.language.psi;

import java.util.List;
import org.jetbrains.annotations.*;
import com.intellij.psi.PsiElement;

public interface BasicForLoop extends PsiElement {

  @NotNull
  List<BasicExpr> getExprList();

  @NotNull
  BasicStatements getStatements();

  @NotNull
  List<BasicVarname> getVarnameList();

}
