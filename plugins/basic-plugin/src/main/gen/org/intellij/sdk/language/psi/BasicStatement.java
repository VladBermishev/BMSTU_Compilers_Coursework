// This is a generated file. Not intended for manual editing.
package org.intellij.sdk.language.psi;

import java.util.List;
import org.jetbrains.annotations.*;
import com.intellij.psi.PsiElement;

public interface BasicStatement extends PsiElement {

  @Nullable
  BasicAssignStatement getAssignStatement();

  @Nullable
  BasicFuncCall getFuncCall();

  @Nullable
  BasicFuncCallOrArrayIndex getFuncCallOrArrayIndex();

  @Nullable
  BasicIfStatement getIfStatement();

  @Nullable
  BasicLoopStmt getLoopStmt();

  @Nullable
  BasicVariableDecl getVariableDecl();

}
