// This is a generated file. Not intended for manual editing.
package org.intellij.sdk.language.parser;

import com.intellij.lang.PsiBuilder;
import com.intellij.lang.PsiBuilder.Marker;
import static org.intellij.sdk.language.psi.BasicTypes.*;
import static com.intellij.lang.parser.GeneratedParserUtilBase.*;
import com.intellij.psi.tree.IElementType;
import com.intellij.lang.ASTNode;
import com.intellij.psi.tree.TokenSet;
import com.intellij.lang.PsiParser;
import com.intellij.lang.LightPsiParser;

@SuppressWarnings({"SimplifiableIfStatement", "UnusedAssignment"})
public class BasicParser implements PsiParser, LightPsiParser {

  public ASTNode parse(IElementType t, PsiBuilder b) {
    parseLight(t, b);
    return b.getTreeBuilt();
  }

  public void parseLight(IElementType t, PsiBuilder b) {
    boolean r;
    b = adapt_builder_(t, b, this, null);
    Marker m = enter_section_(b, 0, _COLLAPSE_, null);
    r = parse_root_(t, b);
    exit_section_(b, 0, m, t, r, true, TRUE_CONDITION);
  }

  protected boolean parse_root_(IElementType t, PsiBuilder b) {
    return parse_root_(t, b, 0);
  }

  static boolean parse_root_(IElementType t, PsiBuilder b, int l) {
    return Program(b, l + 1);
  }

  /* ********************************************************** */
  // PLUS | MINUS
  public static boolean AddOp(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "AddOp")) return false;
    if (!nextTokenIs(b, "<add op>", MINUS, PLUS)) return false;
    boolean r;
    Marker m = enter_section_(b, l, _NONE_, ADD_OP, "<add op>");
    r = consumeToken(b, PLUS);
    if (!r) r = consumeToken(b, MINUS);
    exit_section_(b, l, m, r, false, null);
    return r;
  }

  /* ********************************************************** */
  // (Expr (COMMA NonEmptyArgumentsList)?)?
  public static boolean ArgumentsList(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "ArgumentsList")) return false;
    Marker m = enter_section_(b, l, _NONE_, ARGUMENTS_LIST, "<arguments list>");
    ArgumentsList_0(b, l + 1);
    exit_section_(b, l, m, true, false, null);
    return true;
  }

  // Expr (COMMA NonEmptyArgumentsList)?
  private static boolean ArgumentsList_0(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "ArgumentsList_0")) return false;
    boolean r;
    Marker m = enter_section_(b);
    r = Expr(b, l + 1);
    r = r && ArgumentsList_0_1(b, l + 1);
    exit_section_(b, m, null, r);
    return r;
  }

  // (COMMA NonEmptyArgumentsList)?
  private static boolean ArgumentsList_0_1(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "ArgumentsList_0_1")) return false;
    ArgumentsList_0_1_0(b, l + 1);
    return true;
  }

  // COMMA NonEmptyArgumentsList
  private static boolean ArgumentsList_0_1_0(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "ArgumentsList_0_1_0")) return false;
    boolean r;
    Marker m = enter_section_(b);
    r = consumeToken(b, COMMA);
    r = r && NonEmptyArgumentsList(b, l + 1);
    exit_section_(b, m, null, r);
    return r;
  }

  /* ********************************************************** */
  // Term (AddOp ArithmExpr)? | AddOp Term
  public static boolean ArithmExpr(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "ArithmExpr")) return false;
    boolean r;
    Marker m = enter_section_(b, l, _NONE_, ARITHM_EXPR, "<arithm expr>");
    r = ArithmExpr_0(b, l + 1);
    if (!r) r = ArithmExpr_1(b, l + 1);
    exit_section_(b, l, m, r, false, null);
    return r;
  }

  // Term (AddOp ArithmExpr)?
  private static boolean ArithmExpr_0(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "ArithmExpr_0")) return false;
    boolean r;
    Marker m = enter_section_(b);
    r = Term(b, l + 1);
    r = r && ArithmExpr_0_1(b, l + 1);
    exit_section_(b, m, null, r);
    return r;
  }

  // (AddOp ArithmExpr)?
  private static boolean ArithmExpr_0_1(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "ArithmExpr_0_1")) return false;
    ArithmExpr_0_1_0(b, l + 1);
    return true;
  }

  // AddOp ArithmExpr
  private static boolean ArithmExpr_0_1_0(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "ArithmExpr_0_1_0")) return false;
    boolean r;
    Marker m = enter_section_(b);
    r = AddOp(b, l + 1);
    r = r && ArithmExpr(b, l + 1);
    exit_section_(b, m, null, r);
    return r;
  }

  // AddOp Term
  private static boolean ArithmExpr_1(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "ArithmExpr_1")) return false;
    boolean r;
    Marker m = enter_section_(b);
    r = AddOp(b, l + 1);
    r = r && Term(b, l + 1);
    exit_section_(b, m, null, r);
    return r;
  }

  /* ********************************************************** */
  // (Varname EQ Expr) | (FuncCallOrArrayIndex EQ Expr)
  public static boolean AssignStatement(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "AssignStatement")) return false;
    if (!nextTokenIs(b, IDENTIFIER)) return false;
    boolean r;
    Marker m = enter_section_(b);
    r = AssignStatement_0(b, l + 1);
    if (!r) r = AssignStatement_1(b, l + 1);
    exit_section_(b, m, ASSIGN_STATEMENT, r);
    return r;
  }

  // Varname EQ Expr
  private static boolean AssignStatement_0(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "AssignStatement_0")) return false;
    boolean r;
    Marker m = enter_section_(b);
    r = Varname(b, l + 1);
    r = r && consumeToken(b, EQ);
    r = r && Expr(b, l + 1);
    exit_section_(b, m, null, r);
    return r;
  }

  // FuncCallOrArrayIndex EQ Expr
  private static boolean AssignStatement_1(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "AssignStatement_1")) return false;
    boolean r;
    Marker m = enter_section_(b);
    r = FuncCallOrArrayIndex(b, l + 1);
    r = r && consumeToken(b, EQ);
    r = r && Expr(b, l + 1);
    exit_section_(b, m, null, r);
    return r;
  }

  /* ********************************************************** */
  // GT | LT | GE | LE | EQ | NE
  public static boolean CmpOp(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "CmpOp")) return false;
    boolean r;
    Marker m = enter_section_(b, l, _NONE_, CMP_OP, "<cmp op>");
    r = consumeToken(b, GT);
    if (!r) r = consumeToken(b, LT);
    if (!r) r = consumeToken(b, GE);
    if (!r) r = consumeToken(b, LE);
    if (!r) r = consumeToken(b, EQ);
    if (!r) r = consumeToken(b, NE);
    exit_section_(b, l, m, r, false, null);
    return r;
  }

  /* ********************************************************** */
  // (COMMA CommaList)?
  public static boolean CommaList(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "CommaList")) return false;
    Marker m = enter_section_(b, l, _NONE_, COMMA_LIST, "<comma list>");
    CommaList_0(b, l + 1);
    exit_section_(b, l, m, true, false, null);
    return true;
  }

  // COMMA CommaList
  private static boolean CommaList_0(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "CommaList_0")) return false;
    boolean r;
    Marker m = enter_section_(b);
    r = consumeToken(b, COMMA);
    r = r && CommaList(b, l + 1);
    exit_section_(b, m, null, r);
    return r;
  }

  /* ********************************************************** */
  // INT_CONST | REAL_CONST | STRING_CONST
  public static boolean Const(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "Const")) return false;
    boolean r;
    Marker m = enter_section_(b, l, _NONE_, CONST, "<const>");
    r = consumeToken(b, INT_CONST);
    if (!r) r = consumeToken(b, REAL_CONST);
    if (!r) r = consumeToken(b, STRING_CONST);
    exit_section_(b, l, m, r, false, null);
    return r;
  }

  /* ********************************************************** */
  // (ELSE Statements)?
  public static boolean ElseStatement(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "ElseStatement")) return false;
    Marker m = enter_section_(b, l, _NONE_, ELSE_STATEMENT, "<else statement>");
    ElseStatement_0(b, l + 1);
    exit_section_(b, l, m, true, false, null);
    return true;
  }

  // ELSE Statements
  private static boolean ElseStatement_0(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "ElseStatement_0")) return false;
    boolean r;
    Marker m = enter_section_(b);
    r = consumeToken(b, ELSE);
    r = r && Statements(b, l + 1);
    exit_section_(b, m, null, r);
    return r;
  }

  /* ********************************************************** */
  // EXIT FOR | EXIT FOR Varname | EXIT DO | EXIT LOOP | EXIT SUB | EXIT FUNCTION
  public static boolean ExitStatement(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "ExitStatement")) return false;
    if (!nextTokenIs(b, EXIT)) return false;
    boolean r;
    Marker m = enter_section_(b);
    r = parseTokens(b, 0, EXIT, FOR);
    if (!r) r = ExitStatement_1(b, l + 1);
    if (!r) r = parseTokens(b, 0, EXIT, DO);
    if (!r) r = parseTokens(b, 0, EXIT, LOOP);
    if (!r) r = parseTokens(b, 0, EXIT, SUB);
    if (!r) r = parseTokens(b, 0, EXIT, FUNCTION);
    exit_section_(b, m, EXIT_STATEMENT, r);
    return r;
  }

  // EXIT FOR Varname
  private static boolean ExitStatement_1(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "ExitStatement_1")) return false;
    boolean r;
    Marker m = enter_section_(b);
    r = consumeTokens(b, 0, EXIT, FOR);
    r = r && Varname(b, l + 1);
    exit_section_(b, m, null, r);
    return r;
  }

  /* ********************************************************** */
  // ArithmExpr (CmpOp ArithmExpr)?
  public static boolean Expr(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "Expr")) return false;
    boolean r;
    Marker m = enter_section_(b, l, _NONE_, EXPR, "<expr>");
    r = ArithmExpr(b, l + 1);
    r = r && Expr_1(b, l + 1);
    exit_section_(b, l, m, r, false, null);
    return r;
  }

  // (CmpOp ArithmExpr)?
  private static boolean Expr_1(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "Expr_1")) return false;
    Expr_1_0(b, l + 1);
    return true;
  }

  // CmpOp ArithmExpr
  private static boolean Expr_1_0(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "Expr_1_0")) return false;
    boolean r;
    Marker m = enter_section_(b);
    r = CmpOp(b, l + 1);
    r = r && ArithmExpr(b, l + 1);
    exit_section_(b, m, null, r);
    return r;
  }

  /* ********************************************************** */
  // FOR Varname EQ Expr TO Expr Statements NEXT Varname
  public static boolean ForLoop(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "ForLoop")) return false;
    if (!nextTokenIs(b, FOR)) return false;
    boolean r;
    Marker m = enter_section_(b);
    r = consumeToken(b, FOR);
    r = r && Varname(b, l + 1);
    r = r && consumeToken(b, EQ);
    r = r && Expr(b, l + 1);
    r = r && consumeToken(b, TO);
    r = r && Expr(b, l + 1);
    r = r && Statements(b, l + 1);
    r = r && consumeToken(b, NEXT);
    r = r && Varname(b, l + 1);
    exit_section_(b, m, FOR_LOOP, r);
    return r;
  }

  /* ********************************************************** */
  // PRINT NonEmptyArgumentsList
  public static boolean FuncCall(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "FuncCall")) return false;
    if (!nextTokenIs(b, PRINT)) return false;
    boolean r;
    Marker m = enter_section_(b);
    r = consumeToken(b, PRINT);
    r = r && NonEmptyArgumentsList(b, l + 1);
    exit_section_(b, m, FUNC_CALL, r);
    return r;
  }

  /* ********************************************************** */
  // IDENTIFIER LBRACKET ArgumentsList RBRACKET | Varname LBRACKET ArgumentsList RBRACKET
  public static boolean FuncCallOrArrayIndex(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "FuncCallOrArrayIndex")) return false;
    if (!nextTokenIs(b, IDENTIFIER)) return false;
    boolean r;
    Marker m = enter_section_(b);
    r = FuncCallOrArrayIndex_0(b, l + 1);
    if (!r) r = FuncCallOrArrayIndex_1(b, l + 1);
    exit_section_(b, m, FUNC_CALL_OR_ARRAY_INDEX, r);
    return r;
  }

  // IDENTIFIER LBRACKET ArgumentsList RBRACKET
  private static boolean FuncCallOrArrayIndex_0(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "FuncCallOrArrayIndex_0")) return false;
    boolean r;
    Marker m = enter_section_(b);
    r = consumeTokens(b, 0, IDENTIFIER, LBRACKET);
    r = r && ArgumentsList(b, l + 1);
    r = r && consumeToken(b, RBRACKET);
    exit_section_(b, m, null, r);
    return r;
  }

  // Varname LBRACKET ArgumentsList RBRACKET
  private static boolean FuncCallOrArrayIndex_1(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "FuncCallOrArrayIndex_1")) return false;
    boolean r;
    Marker m = enter_section_(b);
    r = Varname(b, l + 1);
    r = r && consumeToken(b, LBRACKET);
    r = r && ArgumentsList(b, l + 1);
    r = r && consumeToken(b, RBRACKET);
    exit_section_(b, m, null, r);
    return r;
  }

  /* ********************************************************** */
  // DECLARE FunctionProto
  public static boolean FunctionDecl(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "FunctionDecl")) return false;
    if (!nextTokenIs(b, DECLARE)) return false;
    boolean r;
    Marker m = enter_section_(b);
    r = consumeToken(b, DECLARE);
    r = r && FunctionProto(b, l + 1);
    exit_section_(b, m, FUNCTION_DECL, r);
    return r;
  }

  /* ********************************************************** */
  // FunctionProto Statements END FUNCTION
  public static boolean FunctionDef(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "FunctionDef")) return false;
    if (!nextTokenIs(b, FUNCTION)) return false;
    boolean r;
    Marker m = enter_section_(b);
    r = FunctionProto(b, l + 1);
    r = r && Statements(b, l + 1);
    r = r && consumeTokens(b, 0, END, FUNCTION);
    exit_section_(b, m, FUNCTION_DEF, r);
    return r;
  }

  /* ********************************************************** */
  // FUNCTION Varname LBRACKET ParametersList RBRACKET
  public static boolean FunctionProto(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "FunctionProto")) return false;
    if (!nextTokenIs(b, FUNCTION)) return false;
    boolean r;
    Marker m = enter_section_(b);
    r = consumeToken(b, FUNCTION);
    r = r && Varname(b, l + 1);
    r = r && consumeToken(b, LBRACKET);
    r = r && ParametersList(b, l + 1);
    r = r && consumeToken(b, RBRACKET);
    exit_section_(b, m, FUNCTION_PROTO, r);
    return r;
  }

  /* ********************************************************** */
  // SubroutineDecl | SubroutineDef | FunctionDecl | FunctionDef | VariableDecl | PreprocessorCommand
  public static boolean GlobalSymbol(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "GlobalSymbol")) return false;
    boolean r;
    Marker m = enter_section_(b, l, _NONE_, GLOBAL_SYMBOL, "<global symbol>");
    r = SubroutineDecl(b, l + 1);
    if (!r) r = SubroutineDef(b, l + 1);
    if (!r) r = FunctionDecl(b, l + 1);
    if (!r) r = FunctionDef(b, l + 1);
    if (!r) r = VariableDecl(b, l + 1);
    if (!r) r = PreprocessorCommand(b, l + 1);
    exit_section_(b, l, m, r, false, null);
    return r;
  }

  /* ********************************************************** */
  // IF Expr THEN Statements ElseStatement END IF
  public static boolean IfStatement(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "IfStatement")) return false;
    if (!nextTokenIs(b, IF)) return false;
    boolean r;
    Marker m = enter_section_(b);
    r = consumeToken(b, IF);
    r = r && Expr(b, l + 1);
    r = r && consumeToken(b, THEN);
    r = r && Statements(b, l + 1);
    r = r && ElseStatement(b, l + 1);
    r = r && consumeTokens(b, 0, END, IF);
    exit_section_(b, m, IF_STATEMENT, r);
    return r;
  }

  /* ********************************************************** */
  // PRAGMA IDENTIFIER
  public static boolean IncludeCommand(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "IncludeCommand")) return false;
    if (!nextTokenIs(b, PRAGMA)) return false;
    boolean r;
    Marker m = enter_section_(b);
    r = consumeTokens(b, 0, PRAGMA, IDENTIFIER);
    exit_section_(b, m, INCLUDE_COMMAND, r);
    return r;
  }

  /* ********************************************************** */
  // LCBRACKET InitializerListValues RCBRACKET
  public static boolean InitializerList(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "InitializerList")) return false;
    if (!nextTokenIs(b, LCBRACKET)) return false;
    boolean r;
    Marker m = enter_section_(b);
    r = consumeToken(b, LCBRACKET);
    r = r && InitializerListValues(b, l + 1);
    r = r && consumeToken(b, RCBRACKET);
    exit_section_(b, m, INITIALIZER_LIST, r);
    return r;
  }

  /* ********************************************************** */
  // Expr | InitializerList
  public static boolean InitializerListValue(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "InitializerListValue")) return false;
    boolean r;
    Marker m = enter_section_(b, l, _NONE_, INITIALIZER_LIST_VALUE, "<initializer list value>");
    r = Expr(b, l + 1);
    if (!r) r = InitializerList(b, l + 1);
    exit_section_(b, l, m, r, false, null);
    return r;
  }

  /* ********************************************************** */
  // InitializerListValue (COMMA InitializerListValues)?
  public static boolean InitializerListValues(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "InitializerListValues")) return false;
    boolean r;
    Marker m = enter_section_(b, l, _NONE_, INITIALIZER_LIST_VALUES, "<initializer list values>");
    r = InitializerListValue(b, l + 1);
    r = r && InitializerListValues_1(b, l + 1);
    exit_section_(b, l, m, r, false, null);
    return r;
  }

  // (COMMA InitializerListValues)?
  private static boolean InitializerListValues_1(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "InitializerListValues_1")) return false;
    InitializerListValues_1_0(b, l + 1);
    return true;
  }

  // COMMA InitializerListValues
  private static boolean InitializerListValues_1_0(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "InitializerListValues_1_0")) return false;
    boolean r;
    Marker m = enter_section_(b);
    r = consumeToken(b, COMMA);
    r = r && InitializerListValues(b, l + 1);
    exit_section_(b, m, null, r);
    return r;
  }

  /* ********************************************************** */
  // ForLoop | WhileLoop
  public static boolean LoopStmt(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "LoopStmt")) return false;
    if (!nextTokenIs(b, "<loop stmt>", DO, FOR)) return false;
    boolean r;
    Marker m = enter_section_(b, l, _NONE_, LOOP_STMT, "<loop stmt>");
    r = ForLoop(b, l + 1);
    if (!r) r = WhileLoop(b, l + 1);
    exit_section_(b, l, m, r, false, null);
    return r;
  }

  /* ********************************************************** */
  // MULT | DIV
  public static boolean MultOp(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "MultOp")) return false;
    if (!nextTokenIs(b, "<mult op>", DIV, MULT)) return false;
    boolean r;
    Marker m = enter_section_(b, l, _NONE_, MULT_OP, "<mult op>");
    r = consumeToken(b, MULT);
    if (!r) r = consumeToken(b, DIV);
    exit_section_(b, l, m, r, false, null);
    return r;
  }

  /* ********************************************************** */
  // Expr (COMMA NonEmptyArgumentsList)?
  public static boolean NonEmptyArgumentsList(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "NonEmptyArgumentsList")) return false;
    boolean r;
    Marker m = enter_section_(b, l, _NONE_, NON_EMPTY_ARGUMENTS_LIST, "<non empty arguments list>");
    r = Expr(b, l + 1);
    r = r && NonEmptyArgumentsList_1(b, l + 1);
    exit_section_(b, l, m, r, false, null);
    return r;
  }

  // (COMMA NonEmptyArgumentsList)?
  private static boolean NonEmptyArgumentsList_1(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "NonEmptyArgumentsList_1")) return false;
    NonEmptyArgumentsList_1_0(b, l + 1);
    return true;
  }

  // COMMA NonEmptyArgumentsList
  private static boolean NonEmptyArgumentsList_1_0(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "NonEmptyArgumentsList_1_0")) return false;
    boolean r;
    Marker m = enter_section_(b);
    r = consumeToken(b, COMMA);
    r = r && NonEmptyArgumentsList(b, l + 1);
    exit_section_(b, m, null, r);
    return r;
  }

  /* ********************************************************** */
  // VarnameOrArrayParam (NonEmptyParametersList)?
  public static boolean NonEmptyParametersList(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "NonEmptyParametersList")) return false;
    if (!nextTokenIs(b, IDENTIFIER)) return false;
    boolean r;
    Marker m = enter_section_(b);
    r = VarnameOrArrayParam(b, l + 1);
    r = r && NonEmptyParametersList_1(b, l + 1);
    exit_section_(b, m, NON_EMPTY_PARAMETERS_LIST, r);
    return r;
  }

  // (NonEmptyParametersList)?
  private static boolean NonEmptyParametersList_1(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "NonEmptyParametersList_1")) return false;
    NonEmptyParametersList_1_0(b, l + 1);
    return true;
  }

  // (NonEmptyParametersList)
  private static boolean NonEmptyParametersList_1_0(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "NonEmptyParametersList_1_0")) return false;
    boolean r;
    Marker m = enter_section_(b);
    r = NonEmptyParametersList(b, l + 1);
    exit_section_(b, m, null, r);
    return r;
  }

  /* ********************************************************** */
  // (Statement NonEmptyStatements?) | ExitStatement
  public static boolean NonEmptyStatements(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "NonEmptyStatements")) return false;
    boolean r;
    Marker m = enter_section_(b, l, _NONE_, NON_EMPTY_STATEMENTS, "<non empty statements>");
    r = NonEmptyStatements_0(b, l + 1);
    if (!r) r = ExitStatement(b, l + 1);
    exit_section_(b, l, m, r, false, null);
    return r;
  }

  // Statement NonEmptyStatements?
  private static boolean NonEmptyStatements_0(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "NonEmptyStatements_0")) return false;
    boolean r;
    Marker m = enter_section_(b);
    r = Statement(b, l + 1);
    r = r && NonEmptyStatements_0_1(b, l + 1);
    exit_section_(b, m, null, r);
    return r;
  }

  // NonEmptyStatements?
  private static boolean NonEmptyStatements_0_1(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "NonEmptyStatements_0_1")) return false;
    NonEmptyStatements(b, l + 1);
    return true;
  }

  /* ********************************************************** */
  // (VarnameOrArrayParam (COMMA NonEmptyParametersList)? )?
  public static boolean ParametersList(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "ParametersList")) return false;
    Marker m = enter_section_(b, l, _NONE_, PARAMETERS_LIST, "<parameters list>");
    ParametersList_0(b, l + 1);
    exit_section_(b, l, m, true, false, null);
    return true;
  }

  // VarnameOrArrayParam (COMMA NonEmptyParametersList)?
  private static boolean ParametersList_0(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "ParametersList_0")) return false;
    boolean r;
    Marker m = enter_section_(b);
    r = VarnameOrArrayParam(b, l + 1);
    r = r && ParametersList_0_1(b, l + 1);
    exit_section_(b, m, null, r);
    return r;
  }

  // (COMMA NonEmptyParametersList)?
  private static boolean ParametersList_0_1(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "ParametersList_0_1")) return false;
    ParametersList_0_1_0(b, l + 1);
    return true;
  }

  // COMMA NonEmptyParametersList
  private static boolean ParametersList_0_1_0(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "ParametersList_0_1_0")) return false;
    boolean r;
    Marker m = enter_section_(b);
    r = consumeToken(b, COMMA);
    r = r && NonEmptyParametersList(b, l + 1);
    exit_section_(b, m, null, r);
    return r;
  }

  /* ********************************************************** */
  // Statements LOOP PostLoopExpr
  public static boolean PostLoop(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "PostLoop")) return false;
    boolean r;
    Marker m = enter_section_(b, l, _NONE_, POST_LOOP, "<post loop>");
    r = Statements(b, l + 1);
    r = r && consumeToken(b, LOOP);
    r = r && PostLoopExpr(b, l + 1);
    exit_section_(b, l, m, r, false, null);
    return r;
  }

  /* ********************************************************** */
  // (WHILE Expr | UNTIL Expr)?
  public static boolean PostLoopExpr(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "PostLoopExpr")) return false;
    Marker m = enter_section_(b, l, _NONE_, POST_LOOP_EXPR, "<post loop expr>");
    PostLoopExpr_0(b, l + 1);
    exit_section_(b, l, m, true, false, null);
    return true;
  }

  // WHILE Expr | UNTIL Expr
  private static boolean PostLoopExpr_0(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "PostLoopExpr_0")) return false;
    boolean r;
    Marker m = enter_section_(b);
    r = PostLoopExpr_0_0(b, l + 1);
    if (!r) r = PostLoopExpr_0_1(b, l + 1);
    exit_section_(b, m, null, r);
    return r;
  }

  // WHILE Expr
  private static boolean PostLoopExpr_0_0(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "PostLoopExpr_0_0")) return false;
    boolean r;
    Marker m = enter_section_(b);
    r = consumeToken(b, WHILE);
    r = r && Expr(b, l + 1);
    exit_section_(b, m, null, r);
    return r;
  }

  // UNTIL Expr
  private static boolean PostLoopExpr_0_1(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "PostLoopExpr_0_1")) return false;
    boolean r;
    Marker m = enter_section_(b);
    r = consumeToken(b, UNTIL);
    r = r && Expr(b, l + 1);
    exit_section_(b, m, null, r);
    return r;
  }

  /* ********************************************************** */
  // FuncCallOrArrayIndex | Const | LBRACKET Expr RBRACKET | Varname
  public static boolean Power(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "Power")) return false;
    boolean r;
    Marker m = enter_section_(b, l, _NONE_, POWER, "<power>");
    r = FuncCallOrArrayIndex(b, l + 1);
    if (!r) r = Const(b, l + 1);
    if (!r) r = Power_2(b, l + 1);
    if (!r) r = Varname(b, l + 1);
    exit_section_(b, l, m, r, false, null);
    return r;
  }

  // LBRACKET Expr RBRACKET
  private static boolean Power_2(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "Power_2")) return false;
    boolean r;
    Marker m = enter_section_(b);
    r = consumeToken(b, LBRACKET);
    r = r && Expr(b, l + 1);
    r = r && consumeToken(b, RBRACKET);
    exit_section_(b, m, null, r);
    return r;
  }

  /* ********************************************************** */
  // (INCLUDE INCLUDE_PATH) | (INCLUDE STRING_CONST)
  public static boolean PragmaCommand(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "PragmaCommand")) return false;
    if (!nextTokenIs(b, INCLUDE)) return false;
    boolean r;
    Marker m = enter_section_(b);
    r = PragmaCommand_0(b, l + 1);
    if (!r) r = PragmaCommand_1(b, l + 1);
    exit_section_(b, m, PRAGMA_COMMAND, r);
    return r;
  }

  // INCLUDE INCLUDE_PATH
  private static boolean PragmaCommand_0(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "PragmaCommand_0")) return false;
    boolean r;
    Marker m = enter_section_(b);
    r = consumeTokens(b, 0, INCLUDE, INCLUDE_PATH);
    exit_section_(b, m, null, r);
    return r;
  }

  // INCLUDE STRING_CONST
  private static boolean PragmaCommand_1(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "PragmaCommand_1")) return false;
    boolean r;
    Marker m = enter_section_(b);
    r = consumeTokens(b, 0, INCLUDE, STRING_CONST);
    exit_section_(b, m, null, r);
    return r;
  }

  /* ********************************************************** */
  // Expr Statements LOOP
  public static boolean PreLoop(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "PreLoop")) return false;
    boolean r;
    Marker m = enter_section_(b, l, _NONE_, PRE_LOOP, "<pre loop>");
    r = Expr(b, l + 1);
    r = r && Statements(b, l + 1);
    r = r && consumeToken(b, LOOP);
    exit_section_(b, l, m, r, false, null);
    return r;
  }

  /* ********************************************************** */
  // WHILE PreLoop | UNTIL PreLoop | PostLoop
  public static boolean PreOrPostLoop(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "PreOrPostLoop")) return false;
    boolean r;
    Marker m = enter_section_(b, l, _NONE_, PRE_OR_POST_LOOP, "<pre or post loop>");
    r = PreOrPostLoop_0(b, l + 1);
    if (!r) r = PreOrPostLoop_1(b, l + 1);
    if (!r) r = PostLoop(b, l + 1);
    exit_section_(b, l, m, r, false, null);
    return r;
  }

  // WHILE PreLoop
  private static boolean PreOrPostLoop_0(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "PreOrPostLoop_0")) return false;
    boolean r;
    Marker m = enter_section_(b);
    r = consumeToken(b, WHILE);
    r = r && PreLoop(b, l + 1);
    exit_section_(b, m, null, r);
    return r;
  }

  // UNTIL PreLoop
  private static boolean PreOrPostLoop_1(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "PreOrPostLoop_1")) return false;
    boolean r;
    Marker m = enter_section_(b);
    r = consumeToken(b, UNTIL);
    r = r && PreLoop(b, l + 1);
    exit_section_(b, m, null, r);
    return r;
  }

  /* ********************************************************** */
  // IncludeCommand | PragmaCommand
  public static boolean PreprocessorCommand(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "PreprocessorCommand")) return false;
    if (!nextTokenIs(b, "<preprocessor command>", INCLUDE, PRAGMA)) return false;
    boolean r;
    Marker m = enter_section_(b, l, _NONE_, PREPROCESSOR_COMMAND, "<preprocessor command>");
    r = IncludeCommand(b, l + 1);
    if (!r) r = PragmaCommand(b, l + 1);
    exit_section_(b, l, m, r, false, null);
    return r;
  }

  /* ********************************************************** */
  // (GlobalSymbol|COMMENT)*
  static boolean Program(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "Program")) return false;
    while (true) {
      int c = current_position_(b);
      if (!Program_0(b, l + 1)) break;
      if (!empty_element_parsed_guard_(b, "Program", c)) break;
    }
    return true;
  }

  // GlobalSymbol|COMMENT
  private static boolean Program_0(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "Program_0")) return false;
    boolean r;
    r = GlobalSymbol(b, l + 1);
    if (!r) r = consumeToken(b, COMMENT);
    return r;
  }

  /* ********************************************************** */
  // VariableDecl | AssignStatement | FuncCallOrArrayIndex | FuncCall | LoopStmt | IfStatement
  public static boolean Statement(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "Statement")) return false;
    boolean r;
    Marker m = enter_section_(b, l, _NONE_, STATEMENT, "<statement>");
    r = VariableDecl(b, l + 1);
    if (!r) r = AssignStatement(b, l + 1);
    if (!r) r = FuncCallOrArrayIndex(b, l + 1);
    if (!r) r = FuncCall(b, l + 1);
    if (!r) r = LoopStmt(b, l + 1);
    if (!r) r = IfStatement(b, l + 1);
    exit_section_(b, l, m, r, false, null);
    return r;
  }

  /* ********************************************************** */
  // ((Statement NonEmptyStatements) | ExitStatement | Statement)?
  public static boolean Statements(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "Statements")) return false;
    Marker m = enter_section_(b, l, _NONE_, STATEMENTS, "<statements>");
    Statements_0(b, l + 1);
    exit_section_(b, l, m, true, false, null);
    return true;
  }

  // (Statement NonEmptyStatements) | ExitStatement | Statement
  private static boolean Statements_0(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "Statements_0")) return false;
    boolean r;
    Marker m = enter_section_(b);
    r = Statements_0_0(b, l + 1);
    if (!r) r = ExitStatement(b, l + 1);
    if (!r) r = Statement(b, l + 1);
    exit_section_(b, m, null, r);
    return r;
  }

  // Statement NonEmptyStatements
  private static boolean Statements_0_0(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "Statements_0_0")) return false;
    boolean r;
    Marker m = enter_section_(b);
    r = Statement(b, l + 1);
    r = r && NonEmptyStatements(b, l + 1);
    exit_section_(b, m, null, r);
    return r;
  }

  /* ********************************************************** */
  // DECLARE SubroutineProto
  public static boolean SubroutineDecl(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "SubroutineDecl")) return false;
    if (!nextTokenIs(b, DECLARE)) return false;
    boolean r;
    Marker m = enter_section_(b);
    r = consumeToken(b, DECLARE);
    r = r && SubroutineProto(b, l + 1);
    exit_section_(b, m, SUBROUTINE_DECL, r);
    return r;
  }

  /* ********************************************************** */
  // SubroutineProto Statements END SUB
  public static boolean SubroutineDef(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "SubroutineDef")) return false;
    if (!nextTokenIs(b, SUB)) return false;
    boolean r;
    Marker m = enter_section_(b);
    r = SubroutineProto(b, l + 1);
    r = r && Statements(b, l + 1);
    r = r && consumeTokens(b, 0, END, SUB);
    exit_section_(b, m, SUBROUTINE_DEF, r);
    return r;
  }

  /* ********************************************************** */
  // SUB IDENTIFIER LBRACKET ParametersList RBRACKET
  public static boolean SubroutineProto(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "SubroutineProto")) return false;
    if (!nextTokenIs(b, SUB)) return false;
    boolean r;
    Marker m = enter_section_(b);
    r = consumeTokens(b, 0, SUB, IDENTIFIER, LBRACKET);
    r = r && ParametersList(b, l + 1);
    r = r && consumeToken(b, RBRACKET);
    exit_section_(b, m, SUBROUTINE_PROTO, r);
    return r;
  }

  /* ********************************************************** */
  // Power (MultOp Term)?
  public static boolean Term(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "Term")) return false;
    boolean r;
    Marker m = enter_section_(b, l, _NONE_, TERM, "<term>");
    r = Power(b, l + 1);
    r = r && Term_1(b, l + 1);
    exit_section_(b, l, m, r, false, null);
    return r;
  }

  // (MultOp Term)?
  private static boolean Term_1(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "Term_1")) return false;
    Term_1_0(b, l + 1);
    return true;
  }

  // MultOp Term
  private static boolean Term_1_0(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "Term_1_0")) return false;
    boolean r;
    Marker m = enter_section_(b);
    r = MultOp(b, l + 1);
    r = r && Term(b, l + 1);
    exit_section_(b, m, null, r);
    return r;
  }

  /* ********************************************************** */
  // INT_TYPE | LONG_TYPE | FLOAT_TYPE | DOUBLE_TYPE | STRING_TYPE | AUTO_TYPE
  public static boolean Type(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "Type")) return false;
    boolean r;
    Marker m = enter_section_(b, l, _NONE_, TYPE, "<type>");
    r = consumeToken(b, INT_TYPE);
    if (!r) r = consumeToken(b, LONG_TYPE);
    if (!r) r = consumeToken(b, FLOAT_TYPE);
    if (!r) r = consumeToken(b, DOUBLE_TYPE);
    if (!r) r = consumeToken(b, STRING_TYPE);
    if (!r) r = consumeToken(b, AUTO_TYPE);
    exit_section_(b, l, m, r, false, null);
    return r;
  }

  /* ********************************************************** */
  // DIM VarnameOrArrayArg VariableInit
  public static boolean VariableDecl(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "VariableDecl")) return false;
    if (!nextTokenIs(b, DIM)) return false;
    boolean r;
    Marker m = enter_section_(b);
    r = consumeToken(b, DIM);
    r = r && VarnameOrArrayArg(b, l + 1);
    r = r && VariableInit(b, l + 1);
    exit_section_(b, m, VARIABLE_DECL, r);
    return r;
  }

  /* ********************************************************** */
  // (EQ Expr | EQ InitializerList)?
  public static boolean VariableInit(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "VariableInit")) return false;
    Marker m = enter_section_(b, l, _NONE_, VARIABLE_INIT, "<variable init>");
    VariableInit_0(b, l + 1);
    exit_section_(b, l, m, true, false, null);
    return true;
  }

  // EQ Expr | EQ InitializerList
  private static boolean VariableInit_0(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "VariableInit_0")) return false;
    boolean r;
    Marker m = enter_section_(b);
    r = VariableInit_0_0(b, l + 1);
    if (!r) r = VariableInit_0_1(b, l + 1);
    exit_section_(b, m, null, r);
    return r;
  }

  // EQ Expr
  private static boolean VariableInit_0_0(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "VariableInit_0_0")) return false;
    boolean r;
    Marker m = enter_section_(b);
    r = consumeToken(b, EQ);
    r = r && Expr(b, l + 1);
    exit_section_(b, m, null, r);
    return r;
  }

  // EQ InitializerList
  private static boolean VariableInit_0_1(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "VariableInit_0_1")) return false;
    boolean r;
    Marker m = enter_section_(b);
    r = consumeToken(b, EQ);
    r = r && InitializerList(b, l + 1);
    exit_section_(b, m, null, r);
    return r;
  }

  /* ********************************************************** */
  // IDENTIFIER Type
  public static boolean Varname(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "Varname")) return false;
    if (!nextTokenIs(b, IDENTIFIER)) return false;
    boolean r;
    Marker m = enter_section_(b);
    r = consumeToken(b, IDENTIFIER);
    r = r && Type(b, l + 1);
    exit_section_(b, m, VARNAME, r);
    return r;
  }

  /* ********************************************************** */
  // Varname (LBRACKET (NonEmptyArgumentsList | CommaList) RBRACKET)?
  public static boolean VarnameOrArrayArg(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "VarnameOrArrayArg")) return false;
    if (!nextTokenIs(b, IDENTIFIER)) return false;
    boolean r;
    Marker m = enter_section_(b);
    r = Varname(b, l + 1);
    r = r && VarnameOrArrayArg_1(b, l + 1);
    exit_section_(b, m, VARNAME_OR_ARRAY_ARG, r);
    return r;
  }

  // (LBRACKET (NonEmptyArgumentsList | CommaList) RBRACKET)?
  private static boolean VarnameOrArrayArg_1(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "VarnameOrArrayArg_1")) return false;
    VarnameOrArrayArg_1_0(b, l + 1);
    return true;
  }

  // LBRACKET (NonEmptyArgumentsList | CommaList) RBRACKET
  private static boolean VarnameOrArrayArg_1_0(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "VarnameOrArrayArg_1_0")) return false;
    boolean r;
    Marker m = enter_section_(b);
    r = consumeToken(b, LBRACKET);
    r = r && VarnameOrArrayArg_1_0_1(b, l + 1);
    r = r && consumeToken(b, RBRACKET);
    exit_section_(b, m, null, r);
    return r;
  }

  // NonEmptyArgumentsList | CommaList
  private static boolean VarnameOrArrayArg_1_0_1(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "VarnameOrArrayArg_1_0_1")) return false;
    boolean r;
    r = NonEmptyArgumentsList(b, l + 1);
    if (!r) r = CommaList(b, l + 1);
    return r;
  }

  /* ********************************************************** */
  // Varname (LBRACKET CommaList RBRACKET)?
  public static boolean VarnameOrArrayParam(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "VarnameOrArrayParam")) return false;
    if (!nextTokenIs(b, IDENTIFIER)) return false;
    boolean r;
    Marker m = enter_section_(b);
    r = Varname(b, l + 1);
    r = r && VarnameOrArrayParam_1(b, l + 1);
    exit_section_(b, m, VARNAME_OR_ARRAY_PARAM, r);
    return r;
  }

  // (LBRACKET CommaList RBRACKET)?
  private static boolean VarnameOrArrayParam_1(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "VarnameOrArrayParam_1")) return false;
    VarnameOrArrayParam_1_0(b, l + 1);
    return true;
  }

  // LBRACKET CommaList RBRACKET
  private static boolean VarnameOrArrayParam_1_0(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "VarnameOrArrayParam_1_0")) return false;
    boolean r;
    Marker m = enter_section_(b);
    r = consumeToken(b, LBRACKET);
    r = r && CommaList(b, l + 1);
    r = r && consumeToken(b, RBRACKET);
    exit_section_(b, m, null, r);
    return r;
  }

  /* ********************************************************** */
  // DO PreOrPostLoop
  public static boolean WhileLoop(PsiBuilder b, int l) {
    if (!recursion_guard_(b, l, "WhileLoop")) return false;
    if (!nextTokenIs(b, DO)) return false;
    boolean r;
    Marker m = enter_section_(b);
    r = consumeToken(b, DO);
    r = r && PreOrPostLoop(b, l + 1);
    exit_section_(b, m, WHILE_LOOP, r);
    return r;
  }

}
