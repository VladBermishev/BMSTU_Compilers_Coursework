// This is a generated file. Not intended for manual editing.
package org.intellij.sdk.language.psi;

import java.util.List;
import org.jetbrains.annotations.*;
import com.intellij.psi.PsiElement;

public interface BasicPower extends PsiElement {

  @Nullable
  BasicConst getConst();

  @Nullable
  BasicExpr getExpr();

  @Nullable
  BasicFuncCallOrArrayIndex getFuncCallOrArrayIndex();

  @Nullable
  BasicVarname getVarname();

}
