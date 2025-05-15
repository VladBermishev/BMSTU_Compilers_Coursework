package org.intellij.sdk.language.psi;
import com.intellij.psi.tree.IElementType;
import org.intellij.sdk.language.BasicLanguage;
import org.jetbrains.annotations.NonNls;
import org.jetbrains.annotations.NotNull;

public class BasicTokenType extends IElementType {

    public BasicTokenType(@NotNull @NonNls String debugName) {
        super(debugName, BasicLanguage.INSTANCE);
    }

    @Override
    public String toString() {
        return "BasicTokenType." + super.toString();
    }

}
