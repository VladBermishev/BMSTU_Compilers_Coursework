// Copyright 2000-2022 JetBrains s.r.o. and other contributors. Use of this source code is governed by the Apache 2.0 license that can be found in the LICENSE file.

package org.intellij.sdk.language;

import com.intellij.lexer.Lexer;
import com.intellij.openapi.editor.DefaultLanguageHighlighterColors;
import com.intellij.openapi.editor.HighlighterColors;
import com.intellij.openapi.editor.colors.TextAttributesKey;
import com.intellij.openapi.fileTypes.SyntaxHighlighterBase;
import com.intellij.psi.TokenType;
import com.intellij.psi.tree.IElementType;
import org.intellij.sdk.language.psi.BasicTokenSets;
import org.intellij.sdk.language.psi.BasicTypes;
import org.jetbrains.annotations.NotNull;

import static com.intellij.openapi.editor.colors.TextAttributesKey.createTextAttributesKey;

public class BasicSyntaxHighlighter extends SyntaxHighlighterBase {

    public static final TextAttributesKey COMMA =
            createTextAttributesKey("BASIC_COMMA", DefaultLanguageHighlighterColors.COMMA);
    public static final TextAttributesKey IDENTIFIER =
            createTextAttributesKey("BASIC_IDENTIFIER", DefaultLanguageHighlighterColors.IDENTIFIER);
    public static final TextAttributesKey STRING_CONST =
            createTextAttributesKey("BASIC_STRING", DefaultLanguageHighlighterColors.STRING);
    public static final TextAttributesKey NUMBER =
            createTextAttributesKey("BASIC_NUMBER", DefaultLanguageHighlighterColors.NUMBER);
    public static final TextAttributesKey COMMENT =
            createTextAttributesKey("BASIC_COMMENT", DefaultLanguageHighlighterColors.LINE_COMMENT);
    public static final TextAttributesKey BAD_CHARACTER =
            createTextAttributesKey("BASIC_BAD_CHARACTER", HighlighterColors.BAD_CHARACTER);
    public static final TextAttributesKey KEYWORD =
            TextAttributesKey.createTextAttributesKey("BASIC_KEYWORD", DefaultLanguageHighlighterColors.KEYWORD);
    public static final TextAttributesKey FUNC_CALL =
            TextAttributesKey.createTextAttributesKey("BASIC_FUNC_CALL", DefaultLanguageHighlighterColors.FUNCTION_CALL);
    public static final TextAttributesKey OPERATION =
            TextAttributesKey.createTextAttributesKey("BASIC_OPERATION", DefaultLanguageHighlighterColors.OPERATION_SIGN);
    public static final TextAttributesKey BRACKETS =
            TextAttributesKey.createTextAttributesKey("BASIC_BRACKETS", DefaultLanguageHighlighterColors.BRACKETS);
    public static final TextAttributesKey PAREN =
            TextAttributesKey.createTextAttributesKey("BASIC_PAREN", DefaultLanguageHighlighterColors.PARENTHESES);
    public static final TextAttributesKey PP_COMMANDS =
            TextAttributesKey.createTextAttributesKey("PREPROCESSOR_COMMANDS", DefaultLanguageHighlighterColors.METADATA);
    public static final TextAttributesKey PP_COMMANDS_INFO =
            TextAttributesKey.createTextAttributesKey("PREPROCESSOR_COMMANDS_INFO", DefaultLanguageHighlighterColors.STRING);
    public static final TextAttributesKey TYPES =
            TextAttributesKey.createTextAttributesKey("BASIC_TYPES");

    private static final TextAttributesKey[] COMMA_KEYS = new TextAttributesKey[]{COMMA};
    private static final TextAttributesKey[] BAD_CHAR_KEYS = new TextAttributesKey[]{BAD_CHARACTER};
    private static final TextAttributesKey[] KEYWORD_KEYS = new TextAttributesKey[]{KEYWORD};
    private static final TextAttributesKey[] IDENTIFIER_KEYS = new TextAttributesKey[]{IDENTIFIER};
    private static final TextAttributesKey[] STRING_KEYS = new TextAttributesKey[]{STRING_CONST};
    private static final TextAttributesKey[] NUMBER_KEYS = new TextAttributesKey[]{NUMBER};
    private static final TextAttributesKey[] FUNC_CALL_KEYS = new TextAttributesKey[]{FUNC_CALL};
    private static final TextAttributesKey[] OPERATION_KEYS = new TextAttributesKey[]{OPERATION};
    private static final TextAttributesKey[] BRACKET_KEYS = new TextAttributesKey[]{BRACKETS};
    private static final TextAttributesKey[] PAREN_KEYS = new TextAttributesKey[]{PAREN};
    private static final TextAttributesKey[] TYPE_KEYS = new TextAttributesKey[]{TYPES};
    private static final TextAttributesKey[] COMMENT_KEYS = new TextAttributesKey[]{COMMENT};
    private static final TextAttributesKey[] PREPROCESSOR_KEYS = new TextAttributesKey[]{PP_COMMANDS};
    private static final TextAttributesKey[] PREPROCESSOR_INFO_KEYS = new TextAttributesKey[]{PP_COMMANDS_INFO};
    private static final TextAttributesKey[] EMPTY_KEYS = new TextAttributesKey[0];

    @NotNull
    @Override
    public Lexer getHighlightingLexer() {
        return new BasicLexerAdapter();
    }

    @Override
    public TextAttributesKey @NotNull [] getTokenHighlights(IElementType tokenType) {
        if (tokenType.equals(BasicTypes.COMMA)) {
            return COMMA_KEYS;
        }
        if (tokenType.equals(BasicTypes.PRINT)) {
            return FUNC_CALL_KEYS;
        }
        if (BasicTokenSets.KEYWORDS.contains(tokenType)) {
            return KEYWORD_KEYS;
        }
        if (BasicTokenSets.TYPES.contains(tokenType)) {
            return TYPE_KEYS;
        }
        if (BasicTokenSets.BRACKETS.contains(tokenType)) {
            return BRACKET_KEYS;
        }
        if (BasicTokenSets.PAREN.contains(tokenType)) {
            return PAREN_KEYS;
        }
        if (BasicTokenSets.PP_COMMANDS.contains(tokenType)) {
            return PREPROCESSOR_KEYS;
        }
        if (BasicTokenSets.PP_COMMANDS_INFO.contains(tokenType)) {
            return PREPROCESSOR_INFO_KEYS;
        }
        if (BasicTokenSets.OPERATORS.contains(tokenType) || BasicTokenSets.COMPARE_OPERATORS.contains(tokenType)) {
            return OPERATION_KEYS;
        }
        if (tokenType.equals(BasicTypes.IDENTIFIER)) {
            return IDENTIFIER_KEYS;
        }
        if (tokenType.equals(BasicTypes.STRING_CONST)) {
            return STRING_KEYS;
        }
        if (BasicTokenSets.CONSTANTS.contains(tokenType)) {
            return NUMBER_KEYS;
        }
        if (tokenType.equals(BasicTypes.COMMENT)) {
            return COMMENT_KEYS;
        }
        if (tokenType.equals(TokenType.BAD_CHARACTER)) {
            return BAD_CHAR_KEYS;
        }
        return EMPTY_KEYS;
    }

}