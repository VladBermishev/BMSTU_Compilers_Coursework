package org.intellij.sdk.language.psi;

import com.intellij.psi.tree.TokenSet;

public interface BasicTokenSets {

    TokenSet IDENTIFIERS = TokenSet.create(BasicTypes.IDENTIFIER);
    TokenSet KEYWORDS = TokenSet.create(
            BasicTypes.SUB, BasicTypes.FUNCTION, BasicTypes.END, BasicTypes.DECLARE, BasicTypes.DIM, BasicTypes.PRINT,
            BasicTypes.IF, BasicTypes.THEN, BasicTypes.ELSE, BasicTypes.FOR, BasicTypes.TO, BasicTypes.NEXT, BasicTypes.EXIT,
            BasicTypes.DO, BasicTypes.LOOP, BasicTypes.UNTIL
            );
    TokenSet OPERATORS = TokenSet.create( BasicTypes.PLUS, BasicTypes.MINUS, BasicTypes.MULT, BasicTypes.DIV);
    TokenSet COMPARE_OPERATORS = TokenSet.create(
        BasicTypes.GT, BasicTypes.LT, BasicTypes.GE, BasicTypes.LE, BasicTypes.EQ, BasicTypes.NE
    );
    TokenSet PAREN = TokenSet.create(BasicTypes.LBRACKET, BasicTypes.RBRACKET);
    TokenSet BRACKETS = TokenSet.create(BasicTypes.LCBRACKET, BasicTypes.RCBRACKET);
    TokenSet TYPES = TokenSet.create(BasicTypes.INT_TYPE, BasicTypes.LONG_TYPE, BasicTypes.FLOAT_TYPE, BasicTypes.DOUBLE_TYPE, BasicTypes.STRING_TYPE);
    TokenSet CONSTANTS = TokenSet.create(BasicTypes.INT_CONST, BasicTypes.REAL_CONST, BasicTypes.STRING_CONST);
    TokenSet COMMENTS = TokenSet.create(BasicTypes.COMMENT);
    TokenSet PP_COMMANDS = TokenSet.create(BasicTypes.PRAGMA, BasicTypes.INCLUDE);
    TokenSet PP_COMMANDS_INFO = TokenSet.create(BasicTypes.INCLUDE_PATH);

}