package org.intellij.sdk.language;
import com.intellij.lexer.FlexLexer;
import com.intellij.psi.tree.IElementType;
import org.intellij.sdk.language.psi.BasicTypes;
import com.intellij.psi.TokenType;

%%

%class BasicLexer
%implements FlexLexer
%unicode
%ignorecase
%function advance
%type IElementType
%eof{  return;
%eof}

CRLF=\R
FLOAT_CONST=[0-9]+\.([0-9]*)?(e[-+]?[0-9]+)?
INT_CONST=[0-9]+
STRING_CONST=\"[^\"]*\"
INCLUDE_PATH=<[^>]*>
IDENT=[A-Za-z_][A-Za-z0-9_]*
WHITE_SPACE=[\ \n\t\f]
COMMENT=\'[^\r\n]*

%states INCLUDE
%%
<YYINITIAL> {
    "," { yybegin(YYINITIAL); return BasicTypes.COMMA; }
    "(" { yybegin(YYINITIAL); return BasicTypes.LBRACKET; }
    ")" { yybegin(YYINITIAL); return BasicTypes.RBRACKET; }
    "{" { yybegin(YYINITIAL); return BasicTypes.LCBRACKET; }
    "}" { yybegin(YYINITIAL); return BasicTypes.RCBRACKET; }
    ">" { yybegin(YYINITIAL); return BasicTypes.GT; }
    "<" { yybegin(YYINITIAL); return BasicTypes.LT; }
    "=" { yybegin(YYINITIAL); return BasicTypes.EQ; }
    "<>" { yybegin(YYINITIAL); return BasicTypes.NE; }
    "<=" { yybegin(YYINITIAL); return BasicTypes.LE; }
    ">=" { yybegin(YYINITIAL); return BasicTypes.GE; }
    "+" { yybegin(YYINITIAL); return BasicTypes.PLUS; }
    "-" { yybegin(YYINITIAL); return BasicTypes.MINUS; }
    "*" { yybegin(YYINITIAL); return BasicTypes.MULT; }
    "/" { yybegin(YYINITIAL); return BasicTypes.DIV; }
    "%" { yybegin(YYINITIAL); return BasicTypes.INT_TYPE; }
    "&" { yybegin(YYINITIAL); return BasicTypes.LONG_TYPE; }
    "!" { yybegin(YYINITIAL); return BasicTypes.FLOAT_TYPE; }
    "#" { yybegin(YYINITIAL); return BasicTypes.DOUBLE_TYPE; }
    "$" { yybegin(YYINITIAL); return BasicTypes.STRING_TYPE; }
    "@" { yybegin(YYINITIAL); return BasicTypes.AUTO_TYPE; }
    "if" { yybegin(YYINITIAL); return BasicTypes.IF; }
    "then" { yybegin(YYINITIAL); return BasicTypes.THEN;}
    "else" { yybegin(YYINITIAL); return BasicTypes.ELSE;}
    "for" { yybegin(YYINITIAL); return BasicTypes.FOR;}
    "to" { yybegin(YYINITIAL); return BasicTypes.TO;}
    "next" { yybegin(YYINITIAL); return BasicTypes.NEXT;}
    "exit" { yybegin(YYINITIAL); return BasicTypes.EXIT;}
    "do" { yybegin(YYINITIAL); return BasicTypes.DO;}
    "loop" { yybegin(YYINITIAL); return BasicTypes.LOOP;}
    "while" { yybegin(YYINITIAL); return BasicTypes.WHILE;}
    "until" { yybegin(YYINITIAL); return BasicTypes.UNTIL;}
    "sub" { yybegin(YYINITIAL); return BasicTypes.SUB;}
    "function" { yybegin(YYINITIAL); return BasicTypes.FUNCTION;}
    "declare" { yybegin(YYINITIAL); return BasicTypes.DECLARE;}
    "end" { yybegin(YYINITIAL); return BasicTypes.END;}
    "dim" { yybegin(YYINITIAL); return BasicTypes.DIM;}
    "print" { yybegin(YYINITIAL); return BasicTypes.PRINT;}
    "#include" { yybegin(INCLUDE); return BasicTypes.INCLUDE;}
    "#pragma" { yybegin(YYINITIAL); return BasicTypes.PRAGMA;}
    {INT_CONST} { yybegin(YYINITIAL); return BasicTypes.INT_CONST;}
    {FLOAT_CONST} { yybegin(YYINITIAL); return BasicTypes.REAL_CONST;}
    {STRING_CONST} { yybegin(YYINITIAL); return BasicTypes.STRING_CONST;}
    {IDENT} { yybegin(YYINITIAL); return BasicTypes.IDENTIFIER;}
    {COMMENT} { yybegin(YYINITIAL); return BasicTypes.COMMENT; }
    ({CRLF}|{WHITE_SPACE})+ { yybegin(YYINITIAL); return TokenType.WHITE_SPACE; }
}
<INCLUDE>{
    {INCLUDE_PATH} { yybegin(YYINITIAL); return BasicTypes.INCLUDE_PATH; }
    ({CRLF}|{WHITE_SPACE})+ { yybegin(INCLUDE); return TokenType.WHITE_SPACE; }
}

[^] { return TokenType.BAD_CHARACTER; }