package org.intellij.sdk.language.psi;
import com.intellij.extapi.psi.PsiFileBase;
import com.intellij.openapi.fileTypes.FileType;
import com.intellij.psi.FileViewProvider;
import org.intellij.sdk.language.BasicFileType;
import org.intellij.sdk.language.BasicLanguage;
import org.jetbrains.annotations.NotNull;

public class BasicFile extends PsiFileBase {

    public BasicFile(@NotNull FileViewProvider viewProvider) {
        super(viewProvider, BasicLanguage.INSTANCE);
    }

    @NotNull
    @Override
    public FileType getFileType() {
        return BasicFileType.INSTANCE;
    }

    @Override
    public String toString() {
        return "TBasic File";
    }

}