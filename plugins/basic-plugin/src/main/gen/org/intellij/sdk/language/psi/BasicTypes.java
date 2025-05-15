// This is a generated file. Not intended for manual editing.
package org.intellij.sdk.language.psi;

import com.intellij.psi.tree.IElementType;
import com.intellij.psi.PsiElement;
import com.intellij.lang.ASTNode;
import org.intellij.sdk.language.psi.impl.*;

public interface BasicTypes {

  IElementType ADD_OP = new BasicElementType("ADD_OP");
  IElementType ARGUMENTS_LIST = new BasicElementType("ARGUMENTS_LIST");
  IElementType ARITHM_EXPR = new BasicElementType("ARITHM_EXPR");
  IElementType ASSIGN_STATEMENT = new BasicElementType("ASSIGN_STATEMENT");
  IElementType CMP_OP = new BasicElementType("CMP_OP");
  IElementType COMMA_LIST = new BasicElementType("COMMA_LIST");
  IElementType CONST = new BasicElementType("CONST");
  IElementType ELSE_STATEMENT = new BasicElementType("ELSE_STATEMENT");
  IElementType EXIT_STATEMENT = new BasicElementType("EXIT_STATEMENT");
  IElementType EXPR = new BasicElementType("EXPR");
  IElementType FOR_LOOP = new BasicElementType("FOR_LOOP");
  IElementType FUNCTION_DECL = new BasicElementType("FUNCTION_DECL");
  IElementType FUNCTION_DEF = new BasicElementType("FUNCTION_DEF");
  IElementType FUNCTION_PROTO = new BasicElementType("FUNCTION_PROTO");
  IElementType FUNC_CALL = new BasicElementType("FUNC_CALL");
  IElementType FUNC_CALL_OR_ARRAY_INDEX = new BasicElementType("FUNC_CALL_OR_ARRAY_INDEX");
  IElementType GLOBAL_SYMBOL = new BasicElementType("GLOBAL_SYMBOL");
  IElementType IF_STATEMENT = new BasicElementType("IF_STATEMENT");
  IElementType INCLUDE_COMMAND = new BasicElementType("INCLUDE_COMMAND");
  IElementType INITIALIZER_LIST = new BasicElementType("INITIALIZER_LIST");
  IElementType INITIALIZER_LIST_VALUE = new BasicElementType("INITIALIZER_LIST_VALUE");
  IElementType INITIALIZER_LIST_VALUES = new BasicElementType("INITIALIZER_LIST_VALUES");
  IElementType LOOP_STMT = new BasicElementType("LOOP_STMT");
  IElementType MULT_OP = new BasicElementType("MULT_OP");
  IElementType NON_EMPTY_ARGUMENTS_LIST = new BasicElementType("NON_EMPTY_ARGUMENTS_LIST");
  IElementType NON_EMPTY_PARAMETERS_LIST = new BasicElementType("NON_EMPTY_PARAMETERS_LIST");
  IElementType NON_EMPTY_STATEMENTS = new BasicElementType("NON_EMPTY_STATEMENTS");
  IElementType PARAMETERS_LIST = new BasicElementType("PARAMETERS_LIST");
  IElementType POST_LOOP = new BasicElementType("POST_LOOP");
  IElementType POST_LOOP_EXPR = new BasicElementType("POST_LOOP_EXPR");
  IElementType POWER = new BasicElementType("POWER");
  IElementType PRAGMA_COMMAND = new BasicElementType("PRAGMA_COMMAND");
  IElementType PREPROCESSOR_COMMAND = new BasicElementType("PREPROCESSOR_COMMAND");
  IElementType PRE_LOOP = new BasicElementType("PRE_LOOP");
  IElementType PRE_OR_POST_LOOP = new BasicElementType("PRE_OR_POST_LOOP");
  IElementType STATEMENT = new BasicElementType("STATEMENT");
  IElementType STATEMENTS = new BasicElementType("STATEMENTS");
  IElementType SUBROUTINE_DECL = new BasicElementType("SUBROUTINE_DECL");
  IElementType SUBROUTINE_DEF = new BasicElementType("SUBROUTINE_DEF");
  IElementType SUBROUTINE_PROTO = new BasicElementType("SUBROUTINE_PROTO");
  IElementType TERM = new BasicElementType("TERM");
  IElementType TYPE = new BasicElementType("TYPE");
  IElementType VARIABLE_DECL = new BasicElementType("VARIABLE_DECL");
  IElementType VARIABLE_INIT = new BasicElementType("VARIABLE_INIT");
  IElementType VARNAME = new BasicElementType("VARNAME");
  IElementType VARNAME_OR_ARRAY_ARG = new BasicElementType("VARNAME_OR_ARRAY_ARG");
  IElementType VARNAME_OR_ARRAY_PARAM = new BasicElementType("VARNAME_OR_ARRAY_PARAM");
  IElementType WHILE_LOOP = new BasicElementType("WHILE_LOOP");

  IElementType COMMA = new BasicTokenType("COMMA");
  IElementType COMMENT = new BasicTokenType("COMMENT");
  IElementType DECLARE = new BasicTokenType("DECLARE");
  IElementType DIM = new BasicTokenType("DIM");
  IElementType DIV = new BasicTokenType("DIV");
  IElementType DO = new BasicTokenType("DO");
  IElementType DOUBLE_TYPE = new BasicTokenType("DOUBLE_TYPE");
  IElementType ELSE = new BasicTokenType("ELSE");
  IElementType END = new BasicTokenType("END");
  IElementType EQ = new BasicTokenType("EQ");
  IElementType EXIT = new BasicTokenType("EXIT");
  IElementType FLOAT_TYPE = new BasicTokenType("FLOAT_TYPE");
  IElementType FOR = new BasicTokenType("FOR");
  IElementType FUNCTION = new BasicTokenType("FUNCTION");
  IElementType GE = new BasicTokenType("GE");
  IElementType GT = new BasicTokenType("GT");
  IElementType IDENTIFIER = new BasicTokenType("IDENTIFIER");
  IElementType IF = new BasicTokenType("IF");
  IElementType INCLUDE = new BasicTokenType("INCLUDE");
  IElementType INCLUDE_PATH = new BasicTokenType("INCLUDE_PATH");
  IElementType INT_CONST = new BasicTokenType("INT_CONST");
  IElementType INT_TYPE = new BasicTokenType("INT_TYPE");
  IElementType LBRACKET = new BasicTokenType("LBRACKET");
  IElementType LCBRACKET = new BasicTokenType("LCBRACKET");
  IElementType LE = new BasicTokenType("LE");
  IElementType LONG_TYPE = new BasicTokenType("LONG_TYPE");
  IElementType LOOP = new BasicTokenType("LOOP");
  IElementType LT = new BasicTokenType("LT");
  IElementType MINUS = new BasicTokenType("MINUS");
  IElementType MULT = new BasicTokenType("MULT");
  IElementType NE = new BasicTokenType("NE");
  IElementType NEXT = new BasicTokenType("NEXT");
  IElementType PLUS = new BasicTokenType("PLUS");
  IElementType PRAGMA = new BasicTokenType("PRAGMA");
  IElementType PRINT = new BasicTokenType("PRINT");
  IElementType RBRACKET = new BasicTokenType("RBRACKET");
  IElementType RCBRACKET = new BasicTokenType("RCBRACKET");
  IElementType REAL_CONST = new BasicTokenType("REAL_CONST");
  IElementType STRING_CONST = new BasicTokenType("STRING_CONST");
  IElementType STRING_TYPE = new BasicTokenType("STRING_TYPE");
  IElementType SUB = new BasicTokenType("SUB");
  IElementType THEN = new BasicTokenType("THEN");
  IElementType TO = new BasicTokenType("TO");
  IElementType UNTIL = new BasicTokenType("UNTIL");
  IElementType WHILE = new BasicTokenType("WHILE");

  class Factory {
    public static PsiElement createElement(ASTNode node) {
      IElementType type = node.getElementType();
      if (type == ADD_OP) {
        return new BasicAddOpImpl(node);
      }
      else if (type == ARGUMENTS_LIST) {
        return new BasicArgumentsListImpl(node);
      }
      else if (type == ARITHM_EXPR) {
        return new BasicArithmExprImpl(node);
      }
      else if (type == ASSIGN_STATEMENT) {
        return new BasicAssignStatementImpl(node);
      }
      else if (type == CMP_OP) {
        return new BasicCmpOpImpl(node);
      }
      else if (type == COMMA_LIST) {
        return new BasicCommaListImpl(node);
      }
      else if (type == CONST) {
        return new BasicConstImpl(node);
      }
      else if (type == ELSE_STATEMENT) {
        return new BasicElseStatementImpl(node);
      }
      else if (type == EXIT_STATEMENT) {
        return new BasicExitStatementImpl(node);
      }
      else if (type == EXPR) {
        return new BasicExprImpl(node);
      }
      else if (type == FOR_LOOP) {
        return new BasicForLoopImpl(node);
      }
      else if (type == FUNCTION_DECL) {
        return new BasicFunctionDeclImpl(node);
      }
      else if (type == FUNCTION_DEF) {
        return new BasicFunctionDefImpl(node);
      }
      else if (type == FUNCTION_PROTO) {
        return new BasicFunctionProtoImpl(node);
      }
      else if (type == FUNC_CALL) {
        return new BasicFuncCallImpl(node);
      }
      else if (type == FUNC_CALL_OR_ARRAY_INDEX) {
        return new BasicFuncCallOrArrayIndexImpl(node);
      }
      else if (type == GLOBAL_SYMBOL) {
        return new BasicGlobalSymbolImpl(node);
      }
      else if (type == IF_STATEMENT) {
        return new BasicIfStatementImpl(node);
      }
      else if (type == INCLUDE_COMMAND) {
        return new BasicIncludeCommandImpl(node);
      }
      else if (type == INITIALIZER_LIST) {
        return new BasicInitializerListImpl(node);
      }
      else if (type == INITIALIZER_LIST_VALUE) {
        return new BasicInitializerListValueImpl(node);
      }
      else if (type == INITIALIZER_LIST_VALUES) {
        return new BasicInitializerListValuesImpl(node);
      }
      else if (type == LOOP_STMT) {
        return new BasicLoopStmtImpl(node);
      }
      else if (type == MULT_OP) {
        return new BasicMultOpImpl(node);
      }
      else if (type == NON_EMPTY_ARGUMENTS_LIST) {
        return new BasicNonEmptyArgumentsListImpl(node);
      }
      else if (type == NON_EMPTY_PARAMETERS_LIST) {
        return new BasicNonEmptyParametersListImpl(node);
      }
      else if (type == NON_EMPTY_STATEMENTS) {
        return new BasicNonEmptyStatementsImpl(node);
      }
      else if (type == PARAMETERS_LIST) {
        return new BasicParametersListImpl(node);
      }
      else if (type == POST_LOOP) {
        return new BasicPostLoopImpl(node);
      }
      else if (type == POST_LOOP_EXPR) {
        return new BasicPostLoopExprImpl(node);
      }
      else if (type == POWER) {
        return new BasicPowerImpl(node);
      }
      else if (type == PRAGMA_COMMAND) {
        return new BasicPragmaCommandImpl(node);
      }
      else if (type == PREPROCESSOR_COMMAND) {
        return new BasicPreprocessorCommandImpl(node);
      }
      else if (type == PRE_LOOP) {
        return new BasicPreLoopImpl(node);
      }
      else if (type == PRE_OR_POST_LOOP) {
        return new BasicPreOrPostLoopImpl(node);
      }
      else if (type == STATEMENT) {
        return new BasicStatementImpl(node);
      }
      else if (type == STATEMENTS) {
        return new BasicStatementsImpl(node);
      }
      else if (type == SUBROUTINE_DECL) {
        return new BasicSubroutineDeclImpl(node);
      }
      else if (type == SUBROUTINE_DEF) {
        return new BasicSubroutineDefImpl(node);
      }
      else if (type == SUBROUTINE_PROTO) {
        return new BasicSubroutineProtoImpl(node);
      }
      else if (type == TERM) {
        return new BasicTermImpl(node);
      }
      else if (type == TYPE) {
        return new BasicTypeImpl(node);
      }
      else if (type == VARIABLE_DECL) {
        return new BasicVariableDeclImpl(node);
      }
      else if (type == VARIABLE_INIT) {
        return new BasicVariableInitImpl(node);
      }
      else if (type == VARNAME) {
        return new BasicVarnameImpl(node);
      }
      else if (type == VARNAME_OR_ARRAY_ARG) {
        return new BasicVarnameOrArrayArgImpl(node);
      }
      else if (type == VARNAME_OR_ARRAY_PARAM) {
        return new BasicVarnameOrArrayParamImpl(node);
      }
      else if (type == WHILE_LOOP) {
        return new BasicWhileLoopImpl(node);
      }
      throw new AssertionError("Unknown element type: " + type);
    }
  }
}
