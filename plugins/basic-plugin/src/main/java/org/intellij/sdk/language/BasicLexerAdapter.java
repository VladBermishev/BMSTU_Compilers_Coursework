package org.intellij.sdk.language;

import com.intellij.lexer.FlexAdapter;

public class BasicLexerAdapter extends FlexAdapter {

    public BasicLexerAdapter() {
        super(new BasicLexer(null));
    }

}