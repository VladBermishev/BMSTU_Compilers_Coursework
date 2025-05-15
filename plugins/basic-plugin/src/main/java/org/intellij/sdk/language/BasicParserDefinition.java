package org.intellij.sdk.language;

import com.intellij.lang.ASTNode;
import com.intellij.lang.ParserDefinition;
import com.intellij.lang.PsiParser;
import com.intellij.lexer.Lexer;
import com.intellij.openapi.project.Project;
import com.intellij.psi.FileViewProvider;
import com.intellij.psi.PsiElement;
import com.intellij.psi.PsiFile;
import com.intellij.psi.tree.IFileElementType;
import com.intellij.psi.tree.TokenSet;
import org.intellij.sdk.language.parser.BasicParser;
import org.intellij.sdk.language.psi.BasicFile;
import org.intellij.sdk.language.psi.BasicTokenSets;
import org.intellij.sdk.language.psi.BasicTypes;
import org.jetbrains.annotations.NotNull;

final class BasicParserDefinition implements ParserDefinition {

    public static final IFileElementType FILE = new IFileElementType(BasicLanguage.INSTANCE);

    @NotNull
    @Override
    public Lexer createLexer(Project project) {
        return new BasicLexerAdapter();
    }

    @NotNull
    @Override
    public TokenSet getCommentTokens() {
        return BasicTokenSets.COMMENTS;
    }

    @NotNull
    @Override
    public TokenSet getStringLiteralElements() {
        return BasicTokenSets.CONSTANTS;
    }

    @NotNull
    @Override
    public PsiParser createParser(final Project project) {
        return new BasicParser();
    }

    @NotNull
    @Override
    public IFileElementType getFileNodeType() {
        return FILE;
    }

    @NotNull
    @Override
    public PsiFile createFile(@NotNull FileViewProvider viewProvider) {
        return new BasicFile(viewProvider);
    }

    @NotNull
    @Override
    public PsiElement createElement(ASTNode node) {
        return BasicTypes.Factory.createElement(node);
    }

}