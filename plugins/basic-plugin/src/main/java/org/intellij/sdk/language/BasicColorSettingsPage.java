package org.intellij.sdk.language;

import com.intellij.openapi.editor.colors.TextAttributesKey;
import com.intellij.openapi.fileTypes.SyntaxHighlighter;
import com.intellij.openapi.options.colors.AttributesDescriptor;
import com.intellij.openapi.options.colors.ColorDescriptor;
import com.intellij.openapi.options.colors.ColorSettingsPage;
import org.jetbrains.annotations.NotNull;
import org.jetbrains.annotations.Nullable;

import javax.swing.*;
import java.util.Map;

final class BasicColorSettingsPage implements ColorSettingsPage {

    private static final AttributesDescriptor[] DESCRIPTORS = new AttributesDescriptor[]{
            new AttributesDescriptor("Operators", BasicSyntaxHighlighter.OPERATION),
            new AttributesDescriptor("Comma", BasicSyntaxHighlighter.COMMA),
            new AttributesDescriptor("Keywords", BasicSyntaxHighlighter.KEYWORD),
            new AttributesDescriptor("Identifier", BasicSyntaxHighlighter.IDENTIFIER),
            new AttributesDescriptor("String literals", BasicSyntaxHighlighter.STRING_CONST),
            new AttributesDescriptor("Numbers", BasicSyntaxHighlighter.NUMBER),
            new AttributesDescriptor("Comment", BasicSyntaxHighlighter.COMMENT),
            new AttributesDescriptor("Func call", BasicSyntaxHighlighter.FUNC_CALL),
            new AttributesDescriptor("Brackets", BasicSyntaxHighlighter.BRACKETS),
            new AttributesDescriptor("Parenthesis", BasicSyntaxHighlighter.PAREN),
            new AttributesDescriptor("Types", BasicSyntaxHighlighter.TYPES),
            new AttributesDescriptor("Bad value", BasicSyntaxHighlighter.BAD_CHARACTER)
    };

    @Override
    public Icon getIcon() {
        return BasicIcons.FILE;
    }

    @NotNull
    @Override
    public SyntaxHighlighter getHighlighter() {
        return new BasicSyntaxHighlighter();
    }

    @NotNull
    @Override
    public String getDemoText() {
        return """
                Function Join$(sep$, items$())
                    If Len%(items$) >= 1 Then
                        Join$ = items$(1)
                    Else
                        Join$ = ""
                    End If
                    For i% = 2 To Len%(items$)
                        Join$ = Join$ + sep$ + items$(i%)
                    Next i%
                End Function""";
    }

    @Nullable
    @Override
    public Map<String, TextAttributesKey> getAdditionalHighlightingTagToDescriptorMap() {
        return null;
    }

    @Override
    public AttributesDescriptor @NotNull [] getAttributeDescriptors() {
        return DESCRIPTORS;
    }

    @Override
    public ColorDescriptor @NotNull [] getColorDescriptors() {
        return ColorDescriptor.EMPTY_ARRAY;
    }

    @NotNull
    @Override
    public String getDisplayName() {
        return "TBasic";
    }

}