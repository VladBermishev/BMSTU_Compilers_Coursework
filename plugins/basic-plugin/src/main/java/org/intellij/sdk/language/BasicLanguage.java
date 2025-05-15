package org.intellij.sdk.language;
import com.intellij.lang.Language;

public class BasicLanguage extends Language {

    public static final BasicLanguage INSTANCE = new BasicLanguage();

    private BasicLanguage() {
        super("TBasic");
    }
}
