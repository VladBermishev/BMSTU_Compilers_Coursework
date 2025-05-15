package org.intellij.sdk.language.psi;

import com.intellij.psi.tree.IElementType;
import org.intellij.sdk.language.BasicLanguage;
import org.jetbrains.annotations.NonNls;
import org.jetbrains.annotations.NotNull;

public class BasicElementType extends IElementType {

    public BasicElementType(@NotNull @NonNls String debugName) {
        super(debugName, BasicLanguage.INSTANCE);
    }

}
