// This is a generated file. Not intended for manual editing.
package org.intellij.sdk.language.psi;

import java.util.List;
import org.jetbrains.annotations.*;
import com.intellij.psi.PsiElement;

public interface BasicGlobalSymbol extends PsiElement {

  @Nullable
  BasicFunctionDecl getFunctionDecl();

  @Nullable
  BasicFunctionDef getFunctionDef();

  @Nullable
  BasicPreprocessorCommand getPreprocessorCommand();

  @Nullable
  BasicSubroutineDecl getSubroutineDecl();

  @Nullable
  BasicSubroutineDef getSubroutineDef();

  @Nullable
  BasicVariableDecl getVariableDecl();

}
