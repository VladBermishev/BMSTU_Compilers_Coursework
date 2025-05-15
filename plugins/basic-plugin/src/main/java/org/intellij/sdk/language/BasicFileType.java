package org.intellij.sdk.language;
import com.intellij.openapi.fileTypes.LanguageFileType;
import org.jetbrains.annotations.NotNull;
import javax.swing.*;

public final class BasicFileType extends LanguageFileType{

    public static final BasicFileType INSTANCE = new BasicFileType();

    private BasicFileType() {
        super(BasicLanguage.INSTANCE);
    }

    @NotNull
    @Override
    public String getName() {
        return "TBasic File";
    }

    @NotNull
    @Override
    public String getDescription() {
        return "TBasic language file";
    }

    @NotNull
    @Override
    public String getDefaultExtension() {
        return "basic";
    }

    @Override
    public Icon getIcon() {
        return BasicIcons.FILE;
    }

}
