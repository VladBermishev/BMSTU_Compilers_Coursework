// Generated by JFlex 1.9.2 http://jflex.de/  (tweaked for IntelliJ platform)
// source: Basic.flex

package org.intellij.sdk.language;
import com.intellij.lexer.FlexLexer;
import com.intellij.psi.tree.IElementType;
import org.intellij.sdk.language.psi.BasicTypes;
import com.intellij.psi.TokenType;


class BasicLexer implements FlexLexer {

  /** This character denotes the end of file */
  public static final int YYEOF = -1;

  /** initial size of the lookahead buffer */
  private static final int ZZ_BUFFERSIZE = 16384;

  /** lexical states */
  public static final int YYINITIAL = 0;
  public static final int INCLUDE = 2;

  /**
   * ZZ_LEXSTATE[l] is the state in the DFA for the lexical state l
   * ZZ_LEXSTATE[l+1] is the state in the DFA for the lexical state l
   *                  at the beginning of a line
   * l is of the form l = 2*k, k a non negative integer
   */
  private static final int ZZ_LEXSTATE[] = {
     0,  0,  1, 1
  };

  /**
   * Top-level table for translating characters to character classes
   */
  private static final int [] ZZ_CMAP_TOP = zzUnpackcmap_top();

  private static final String ZZ_CMAP_TOP_PACKED_0 =
    "\1\0\1\u0100\36\u0200\1\u0300\u10df\u0200";

  private static int [] zzUnpackcmap_top() {
    int [] result = new int[4352];
    int offset = 0;
    offset = zzUnpackcmap_top(ZZ_CMAP_TOP_PACKED_0, offset, result);
    return result;
  }

  private static int zzUnpackcmap_top(String packed, int offset, int [] result) {
    int i = 0;       /* index in packed string  */
    int j = offset;  /* index in unpacked array */
    int l = packed.length();
    while (i < l) {
      int count = packed.charAt(i++);
      int value = packed.charAt(i++);
      do result[j++] = value; while (--count > 0);
    }
    return j;
  }


  /**
   * Second-level tables for translating characters to character classes
   */
  private static final int [] ZZ_CMAP_BLOCKS = zzUnpackcmap_blocks();

  private static final String ZZ_CMAP_BLOCKS_PACKED_0 =
    "\11\0\1\1\1\2\2\1\1\2\22\0\1\1\1\3"+
    "\1\4\1\5\1\6\1\7\1\10\1\11\1\12\1\13"+
    "\1\14\1\15\1\16\1\17\1\20\1\21\12\22\2\0"+
    "\1\23\1\24\1\25\1\0\1\26\1\27\1\30\1\31"+
    "\1\32\1\33\1\34\1\35\1\36\1\37\2\40\1\41"+
    "\1\42\1\43\1\44\1\45\1\40\1\46\1\47\1\50"+
    "\1\51\1\40\1\52\1\53\2\40\4\0\1\40\1\0"+
    "\1\27\1\30\1\31\1\32\1\33\1\34\1\35\1\36"+
    "\1\37\2\40\1\41\1\42\1\43\1\44\1\45\1\40"+
    "\1\46\1\47\1\50\1\51\1\40\1\52\1\53\2\40"+
    "\1\54\1\0\1\55\7\0\1\1\252\0\2\56\115\0"+
    "\1\57\u01a8\0\2\1\326\0";

  private static int [] zzUnpackcmap_blocks() {
    int [] result = new int[1024];
    int offset = 0;
    offset = zzUnpackcmap_blocks(ZZ_CMAP_BLOCKS_PACKED_0, offset, result);
    return result;
  }

  private static int zzUnpackcmap_blocks(String packed, int offset, int [] result) {
    int i = 0;       /* index in packed string  */
    int j = offset;  /* index in unpacked array */
    int l = packed.length();
    while (i < l) {
      int count = packed.charAt(i++);
      int value = packed.charAt(i++);
      do result[j++] = value; while (--count > 0);
    }
    return j;
  }

  /**
   * Translates DFA states to action switch labels.
   */
  private static final int [] ZZ_ACTION = zzUnpackAction();

  private static final String ZZ_ACTION_PACKED_0 =
    "\2\0\1\1\1\2\1\3\1\1\1\4\1\5\1\6"+
    "\1\7\1\10\1\11\1\12\1\13\1\14\1\15\1\16"+
    "\1\17\1\20\1\21\1\22\1\23\1\24\14\25\1\26"+
    "\1\27\2\1\1\30\1\1\1\0\1\31\2\0\1\32"+
    "\1\33\1\34\1\35\2\25\1\36\1\0\5\25\1\37"+
    "\5\25\1\40\2\25\1\37\2\0\1\41\3\0\1\25"+
    "\2\42\1\25\1\0\1\43\1\25\1\0\1\44\4\25"+
    "\1\0\1\45\3\25\1\0\1\45\3\0\1\32\1\25"+
    "\2\46\2\47\1\25\1\50\1\51\1\25\1\0\1\52"+
    "\1\25\1\0\1\25\3\0\2\25\2\53\2\54\2\55"+
    "\2\0\2\25\2\0\1\56\1\57\1\25\1\0\1\60"+
    "\2\61";

  private static int [] zzUnpackAction() {
    int [] result = new int[136];
    int offset = 0;
    offset = zzUnpackAction(ZZ_ACTION_PACKED_0, offset, result);
    return result;
  }

  private static int zzUnpackAction(String packed, int offset, int [] result) {
    int i = 0;       /* index in packed string  */
    int j = offset;  /* index in unpacked array */
    int l = packed.length();
    while (i < l) {
      int count = packed.charAt(i++);
      int value = packed.charAt(i++);
      do result[j++] = value; while (--count > 0);
    }
    return j;
  }


  /**
   * Translates a state to a row index in the transition table
   */
  private static final int [] ZZ_ROWMAP = zzUnpackRowMap();

  private static final String ZZ_ROWMAP_PACKED_0 =
    "\0\0\0\60\0\140\0\220\0\140\0\300\0\360\0\140"+
    "\0\140\0\140\0\u0120\0\140\0\140\0\140\0\140\0\140"+
    "\0\140\0\140\0\u0150\0\u0180\0\140\0\u01b0\0\140\0\u01e0"+
    "\0\u0210\0\u0240\0\u0270\0\u02a0\0\u02d0\0\u0300\0\u0330\0\u0360"+
    "\0\u0390\0\u03c0\0\u03f0\0\140\0\140\0\u0420\0\u0450\0\u0480"+
    "\0\u04b0\0\300\0\140\0\u04e0\0\u0510\0\u0540\0\140\0\140"+
    "\0\140\0\u0570\0\u05a0\0\u01e0\0\u05d0\0\u0600\0\u0630\0\u0660"+
    "\0\u0690\0\u06c0\0\u01e0\0\u06f0\0\u0720\0\u0750\0\u0780\0\u07b0"+
    "\0\u01e0\0\u07e0\0\u0810\0\140\0\u0840\0\u04b0\0\140\0\u0870"+
    "\0\u08a0\0\u08d0\0\u0900\0\u01e0\0\140\0\u0930\0\u0960\0\u01e0"+
    "\0\u0990\0\u09c0\0\u01e0\0\u09f0\0\u0a20\0\u0a50\0\u0a80\0\u0ab0"+
    "\0\u01e0\0\u0ae0\0\u0b10\0\u0b40\0\u0b70\0\140\0\u0ba0\0\u0bd0"+
    "\0\u0c00\0\u0c00\0\u0c30\0\u01e0\0\140\0\u01e0\0\140\0\u0c60"+
    "\0\u01e0\0\u01e0\0\u0c90\0\u0cc0\0\u01e0\0\u0cf0\0\u0d20\0\u0d50"+
    "\0\u0d80\0\u0db0\0\u0de0\0\u0e10\0\u0e40\0\u01e0\0\140\0\u01e0"+
    "\0\140\0\u01e0\0\140\0\u0e70\0\u0ea0\0\u0ed0\0\u0f00\0\u0f30"+
    "\0\u0f60\0\140\0\u01e0\0\u0f90\0\u0fc0\0\140\0\u01e0\0\140";

  private static int [] zzUnpackRowMap() {
    int [] result = new int[136];
    int offset = 0;
    offset = zzUnpackRowMap(ZZ_ROWMAP_PACKED_0, offset, result);
    return result;
  }

  private static int zzUnpackRowMap(String packed, int offset, int [] result) {
    int i = 0;  /* index in packed string  */
    int j = offset;  /* index in unpacked array */
    int l = packed.length() - 1;
    while (i < l) {
      int high = packed.charAt(i++) << 16;
      result[j++] = high | packed.charAt(i++);
    }
    return j;
  }

  /**
   * The transition table of the DFA
   */
  private static final int [] ZZ_TRANS = zzUnpacktrans();

  private static final String ZZ_TRANS_PACKED_0 =
    "\1\3\2\4\1\5\1\6\1\7\1\10\1\11\1\12"+
    "\1\13\1\14\1\15\1\16\1\17\1\20\1\21\1\3"+
    "\1\22\1\23\1\24\1\25\1\26\1\27\3\30\1\31"+
    "\1\32\1\33\2\30\1\34\1\30\1\35\1\30\1\36"+
    "\1\30\1\37\1\30\1\40\1\41\1\42\1\43\1\30"+
    "\1\44\1\45\1\46\1\47\1\3\2\50\20\3\1\51"+
    "\34\3\61\0\2\4\55\0\4\52\1\53\53\52\37\0"+
    "\1\54\5\0\1\55\10\0\1\54\1\0\2\13\1\0"+
    "\55\13\20\0\1\56\1\0\1\23\61\0\1\57\1\60"+
    "\56\0\1\61\55\0\1\30\4\0\25\30\26\0\1\30"+
    "\4\0\4\30\1\62\3\30\1\63\4\30\1\64\7\30"+
    "\2\0\1\65\23\0\1\30\4\0\12\30\1\66\1\30"+
    "\1\67\7\30\1\70\26\0\1\30\4\0\15\30\1\71"+
    "\4\30\1\72\2\30\26\0\1\30\4\0\5\30\1\73"+
    "\17\30\26\0\1\30\4\0\15\30\1\74\7\30\26\0"+
    "\1\30\4\0\4\30\1\75\20\30\26\0\1\30\4\0"+
    "\17\30\1\76\5\30\26\0\1\30\4\0\22\30\1\77"+
    "\2\30\26\0\1\30\4\0\7\30\1\100\5\30\1\101"+
    "\7\30\26\0\1\30\4\0\14\30\1\102\10\30\26\0"+
    "\1\30\4\0\7\30\1\103\15\30\40\0\1\104\74\0"+
    "\1\105\7\0\2\50\55\0\25\106\1\107\32\106\43\0"+
    "\1\110\62\0\1\111\33\0\1\56\10\0\1\112\46\0"+
    "\1\30\4\0\2\30\1\113\22\30\26\0\1\30\4\0"+
    "\13\30\1\114\11\30\46\0\1\115\37\0\1\30\4\0"+
    "\20\30\1\116\4\30\3\0\1\117\22\0\1\30\4\0"+
    "\3\30\1\120\21\30\26\0\1\30\4\0\10\30\1\121"+
    "\14\30\2\0\1\122\23\0\1\30\4\0\17\30\1\123"+
    "\5\30\26\0\1\30\4\0\14\30\1\124\10\30\26\0"+
    "\1\30\4\0\15\30\1\125\7\30\26\0\1\30\4\0"+
    "\24\30\1\126\26\0\1\30\4\0\10\30\1\127\14\30"+
    "\2\0\1\130\23\0\1\30\4\0\1\30\1\131\23\30"+
    "\26\0\1\30\4\0\4\30\1\132\20\30\26\0\1\30"+
    "\4\0\21\30\1\133\3\30\26\0\1\30\4\0\10\30"+
    "\1\134\14\30\2\0\1\135\31\0\1\136\60\0\1\137"+
    "\55\0\1\140\45\0\1\141\1\0\1\141\2\0\1\142"+
    "\57\0\1\30\4\0\12\30\1\143\12\30\26\0\1\30"+
    "\4\0\4\30\1\144\20\30\37\0\1\145\46\0\1\30"+
    "\4\0\21\30\1\146\3\30\54\0\1\147\31\0\1\30"+
    "\4\0\2\30\1\150\22\30\26\0\1\30\4\0\16\30"+
    "\1\151\6\30\26\0\1\30\4\0\21\30\1\152\3\30"+
    "\26\0\1\30\4\0\14\30\1\153\10\30\47\0\1\154"+
    "\36\0\1\30\4\0\14\30\1\155\10\30\26\0\1\30"+
    "\4\0\10\30\1\156\14\30\2\0\1\157\23\0\1\30"+
    "\4\0\12\30\1\160\12\30\45\0\1\161\57\0\1\162"+
    "\53\0\1\163\44\0\1\142\57\0\1\30\4\0\1\164"+
    "\24\30\26\0\1\30\4\0\21\30\1\165\3\30\26\0"+
    "\1\30\4\0\21\30\1\166\3\30\54\0\1\167\31\0"+
    "\1\30\4\0\12\30\1\170\12\30\45\0\1\171\40\0"+
    "\1\30\4\0\4\30\1\172\20\30\37\0\1\173\75\0"+
    "\1\174\50\0\1\175\37\0\1\30\4\0\17\30\1\176"+
    "\5\30\26\0\1\30\4\0\10\30\1\177\14\30\2\0"+
    "\1\200\33\0\1\201\54\0\1\202\52\0\1\30\4\0"+
    "\4\30\1\203\20\30\26\0\1\30\4\0\15\30\1\204"+
    "\7\30\50\0\1\205\46\0\1\206\46\0\1\30\4\0"+
    "\14\30\1\207\10\30\47\0\1\210\14\0";

  private static int [] zzUnpacktrans() {
    int [] result = new int[4080];
    int offset = 0;
    offset = zzUnpacktrans(ZZ_TRANS_PACKED_0, offset, result);
    return result;
  }

  private static int zzUnpacktrans(String packed, int offset, int [] result) {
    int i = 0;       /* index in packed string  */
    int j = offset;  /* index in unpacked array */
    int l = packed.length();
    while (i < l) {
      int count = packed.charAt(i++);
      int value = packed.charAt(i++);
      value--;
      do result[j++] = value; while (--count > 0);
    }
    return j;
  }


  /* error codes */
  private static final int ZZ_UNKNOWN_ERROR = 0;
  private static final int ZZ_NO_MATCH = 1;
  private static final int ZZ_PUSHBACK_2BIG = 2;

  /* error messages for the codes above */
  private static final String[] ZZ_ERROR_MSG = {
    "Unknown internal scanner error",
    "Error: could not match input",
    "Error: pushback value was too large"
  };

  /**
   * ZZ_ATTRIBUTE[aState] contains the attributes of state {@code aState}
   */
  private static final int [] ZZ_ATTRIBUTE = zzUnpackAttribute();

  private static final String ZZ_ATTRIBUTE_PACKED_0 =
    "\2\0\1\11\1\1\1\11\2\1\3\11\1\1\7\11"+
    "\2\1\1\11\1\1\1\11\14\1\2\11\4\1\1\0"+
    "\1\11\2\0\1\1\3\11\3\1\1\0\16\1\1\11"+
    "\2\0\1\11\3\0\2\1\1\11\1\1\1\0\2\1"+
    "\1\0\5\1\1\0\4\1\1\0\1\11\3\0\3\1"+
    "\1\11\1\1\1\11\4\1\1\0\2\1\1\0\1\1"+
    "\3\0\3\1\1\11\1\1\1\11\1\1\1\11\2\0"+
    "\2\1\2\0\1\11\2\1\1\0\1\11\1\1\1\11";

  private static int [] zzUnpackAttribute() {
    int [] result = new int[136];
    int offset = 0;
    offset = zzUnpackAttribute(ZZ_ATTRIBUTE_PACKED_0, offset, result);
    return result;
  }

  private static int zzUnpackAttribute(String packed, int offset, int [] result) {
    int i = 0;       /* index in packed string  */
    int j = offset;  /* index in unpacked array */
    int l = packed.length();
    while (i < l) {
      int count = packed.charAt(i++);
      int value = packed.charAt(i++);
      do result[j++] = value; while (--count > 0);
    }
    return j;
  }

  /** the input device */
  private java.io.Reader zzReader;

  /** the current state of the DFA */
  private int zzState;

  /** the current lexical state */
  private int zzLexicalState = YYINITIAL;

  /** this buffer contains the current text to be matched and is
      the source of the yytext() string */
  private CharSequence zzBuffer = "";

  /** the textposition at the last accepting state */
  private int zzMarkedPos;

  /** the current text position in the buffer */
  private int zzCurrentPos;

  /** startRead marks the beginning of the yytext() string in the buffer */
  private int zzStartRead;

  /** endRead marks the last character in the buffer, that has been read
      from input */
  private int zzEndRead;

  /** zzAtEOF == true <=> the scanner is at the EOF */
  private boolean zzAtEOF;

  /** Number of newlines encountered up to the start of the matched text. */
  @SuppressWarnings("unused")
  private int yyline;

  /** Number of characters from the last newline up to the start of the matched text. */
  @SuppressWarnings("unused")
  protected int yycolumn;

  /** Number of characters up to the start of the matched text. */
  @SuppressWarnings("unused")
  private long yychar;

  /** Whether the scanner is currently at the beginning of a line. */
  @SuppressWarnings("unused")
  private boolean zzAtBOL = true;

  /** Whether the user-EOF-code has already been executed. */
  private boolean zzEOFDone;


  /**
   * Creates a new scanner
   *
   * @param   in  the java.io.Reader to read input from.
   */
  BasicLexer(java.io.Reader in) {
    this.zzReader = in;
  }


  /** Returns the maximum size of the scanner buffer, which limits the size of tokens. */
  private int zzMaxBufferLen() {
    return Integer.MAX_VALUE;
  }

  /**  Whether the scanner buffer can grow to accommodate a larger token. */
  private boolean zzCanGrow() {
    return true;
  }

  /**
   * Translates raw input code points to DFA table row
   */
  private static int zzCMap(int input) {
    int offset = input & 255;
    return offset == input ? ZZ_CMAP_BLOCKS[offset] : ZZ_CMAP_BLOCKS[ZZ_CMAP_TOP[input >> 8] | offset];
  }

  public final int getTokenStart() {
    return zzStartRead;
  }

  public final int getTokenEnd() {
    return getTokenStart() + yylength();
  }

  public void reset(CharSequence buffer, int start, int end, int initialState) {
    zzBuffer = buffer;
    zzCurrentPos = zzMarkedPos = zzStartRead = start;
    zzAtEOF  = false;
    zzAtBOL = true;
    zzEndRead = end;
    yybegin(initialState);
  }

  /**
   * Refills the input buffer.
   *
   * @return      {@code false}, iff there was new input.
   *
   * @exception   java.io.IOException  if any I/O-Error occurs
   */
  private boolean zzRefill() throws java.io.IOException {
    return true;
  }


  /**
   * Returns the current lexical state.
   */
  public final int yystate() {
    return zzLexicalState;
  }


  /**
   * Enters a new lexical state
   *
   * @param newState the new lexical state
   */
  public final void yybegin(int newState) {
    zzLexicalState = newState;
  }


  /**
   * Returns the text matched by the current regular expression.
   */
  public final CharSequence yytext() {
    return zzBuffer.subSequence(zzStartRead, zzMarkedPos);
  }


  /**
   * Returns the character at position {@code pos} from the
   * matched text.
   *
   * It is equivalent to yytext().charAt(pos), but faster
   *
   * @param pos the position of the character to fetch.
   *            A value from 0 to yylength()-1.
   *
   * @return the character at position pos
   */
  public final char yycharat(int pos) {
    return zzBuffer.charAt(zzStartRead+pos);
  }


  /**
   * Returns the length of the matched text region.
   */
  public final int yylength() {
    return zzMarkedPos-zzStartRead;
  }


  /**
   * Reports an error that occurred while scanning.
   *
   * In a wellformed scanner (no or only correct usage of
   * yypushback(int) and a match-all fallback rule) this method
   * will only be called with things that "Can't Possibly Happen".
   * If this method is called, something is seriously wrong
   * (e.g. a JFlex bug producing a faulty scanner etc.).
   *
   * Usual syntax/scanner level error handling should be done
   * in error fallback rules.
   *
   * @param   errorCode  the code of the errormessage to display
   */
  private void zzScanError(int errorCode) {
    String message;
    try {
      message = ZZ_ERROR_MSG[errorCode];
    }
    catch (ArrayIndexOutOfBoundsException e) {
      message = ZZ_ERROR_MSG[ZZ_UNKNOWN_ERROR];
    }

    throw new Error(message);
  }


  /**
   * Pushes the specified amount of characters back into the input stream.
   *
   * They will be read again by then next call of the scanning method
   *
   * @param number  the number of characters to be read again.
   *                This number must not be greater than yylength()!
   */
  public void yypushback(int number)  {
    if ( number > yylength() )
      zzScanError(ZZ_PUSHBACK_2BIG);

    zzMarkedPos -= number;
  }


  /**
   * Contains user EOF-code, which will be executed exactly once,
   * when the end of file is reached
   */
  private void zzDoEOF() {
    if (!zzEOFDone) {
      zzEOFDone = true;
    
    }
  }


  /**
   * Resumes scanning until the next regular expression is matched,
   * the end of input is encountered or an I/O-Error occurs.
   *
   * @return      the next token
   * @exception   java.io.IOException  if any I/O-Error occurs
   */
  public IElementType advance() throws java.io.IOException
  {
    int zzInput;
    int zzAction;

    // cached fields:
    int zzCurrentPosL;
    int zzMarkedPosL;
    int zzEndReadL = zzEndRead;
    CharSequence zzBufferL = zzBuffer;

    int [] zzTransL = ZZ_TRANS;
    int [] zzRowMapL = ZZ_ROWMAP;
    int [] zzAttrL = ZZ_ATTRIBUTE;

    while (true) {
      zzMarkedPosL = zzMarkedPos;

      zzAction = -1;

      zzCurrentPosL = zzCurrentPos = zzStartRead = zzMarkedPosL;

      zzState = ZZ_LEXSTATE[zzLexicalState];

      // set up zzAction for empty match case:
      int zzAttributes = zzAttrL[zzState];
      if ( (zzAttributes & 1) == 1 ) {
        zzAction = zzState;
      }


      zzForAction: {
        while (true) {

          if (zzCurrentPosL < zzEndReadL) {
            zzInput = Character.codePointAt(zzBufferL, zzCurrentPosL);
            zzCurrentPosL += Character.charCount(zzInput);
          }
          else if (zzAtEOF) {
            zzInput = YYEOF;
            break zzForAction;
          }
          else {
            // store back cached positions
            zzCurrentPos  = zzCurrentPosL;
            zzMarkedPos   = zzMarkedPosL;
            boolean eof = zzRefill();
            // get translated positions and possibly new buffer
            zzCurrentPosL  = zzCurrentPos;
            zzMarkedPosL   = zzMarkedPos;
            zzBufferL      = zzBuffer;
            zzEndReadL     = zzEndRead;
            if (eof) {
              zzInput = YYEOF;
              break zzForAction;
            }
            else {
              zzInput = Character.codePointAt(zzBufferL, zzCurrentPosL);
              zzCurrentPosL += Character.charCount(zzInput);
            }
          }
          int zzNext = zzTransL[ zzRowMapL[zzState] + zzCMap(zzInput) ];
          if (zzNext == -1) break zzForAction;
          zzState = zzNext;

          zzAttributes = zzAttrL[zzState];
          if ( (zzAttributes & 1) == 1 ) {
            zzAction = zzState;
            zzMarkedPosL = zzCurrentPosL;
            if ( (zzAttributes & 8) == 8 ) break zzForAction;
          }

        }
      }

      // store back cached position
      zzMarkedPos = zzMarkedPosL;

      if (zzInput == YYEOF && zzStartRead == zzCurrentPos) {
        zzAtEOF = true;
            zzDoEOF();
        return null;
      }
      else {
        switch (zzAction < 0 ? zzAction : ZZ_ACTION[zzAction]) {
          case 1:
            { return TokenType.BAD_CHARACTER;
            }
          // fall through
          case 50: break;
          case 2:
            { yybegin(YYINITIAL); return TokenType.WHITE_SPACE;
            }
          // fall through
          case 51: break;
          case 3:
            { yybegin(YYINITIAL); return BasicTypes.FLOAT_TYPE;
            }
          // fall through
          case 52: break;
          case 4:
            { yybegin(YYINITIAL); return BasicTypes.DOUBLE_TYPE;
            }
          // fall through
          case 53: break;
          case 5:
            { yybegin(YYINITIAL); return BasicTypes.STRING_TYPE;
            }
          // fall through
          case 54: break;
          case 6:
            { yybegin(YYINITIAL); return BasicTypes.INT_TYPE;
            }
          // fall through
          case 55: break;
          case 7:
            { yybegin(YYINITIAL); return BasicTypes.LONG_TYPE;
            }
          // fall through
          case 56: break;
          case 8:
            { yybegin(YYINITIAL); return BasicTypes.COMMENT;
            }
          // fall through
          case 57: break;
          case 9:
            { yybegin(YYINITIAL); return BasicTypes.LBRACKET;
            }
          // fall through
          case 58: break;
          case 10:
            { yybegin(YYINITIAL); return BasicTypes.RBRACKET;
            }
          // fall through
          case 59: break;
          case 11:
            { yybegin(YYINITIAL); return BasicTypes.MULT;
            }
          // fall through
          case 60: break;
          case 12:
            { yybegin(YYINITIAL); return BasicTypes.PLUS;
            }
          // fall through
          case 61: break;
          case 13:
            { yybegin(YYINITIAL); return BasicTypes.COMMA;
            }
          // fall through
          case 62: break;
          case 14:
            { yybegin(YYINITIAL); return BasicTypes.MINUS;
            }
          // fall through
          case 63: break;
          case 15:
            { yybegin(YYINITIAL); return BasicTypes.DIV;
            }
          // fall through
          case 64: break;
          case 16:
            { yybegin(YYINITIAL); return BasicTypes.INT_CONST;
            }
          // fall through
          case 65: break;
          case 17:
            { yybegin(YYINITIAL); return BasicTypes.LT;
            }
          // fall through
          case 66: break;
          case 18:
            { yybegin(YYINITIAL); return BasicTypes.EQ;
            }
          // fall through
          case 67: break;
          case 19:
            { yybegin(YYINITIAL); return BasicTypes.GT;
            }
          // fall through
          case 68: break;
          case 20:
            { yybegin(YYINITIAL); return BasicTypes.AUTO_TYPE;
            }
          // fall through
          case 69: break;
          case 21:
            { yybegin(YYINITIAL); return BasicTypes.IDENTIFIER;
            }
          // fall through
          case 70: break;
          case 22:
            { yybegin(YYINITIAL); return BasicTypes.LCBRACKET;
            }
          // fall through
          case 71: break;
          case 23:
            { yybegin(YYINITIAL); return BasicTypes.RCBRACKET;
            }
          // fall through
          case 72: break;
          case 24:
            { yybegin(INCLUDE); return TokenType.WHITE_SPACE;
            }
          // fall through
          case 73: break;
          case 25:
            { yybegin(YYINITIAL); return BasicTypes.STRING_CONST;
            }
          // fall through
          case 74: break;
          case 26:
            { yybegin(YYINITIAL); return BasicTypes.REAL_CONST;
            }
          // fall through
          case 75: break;
          case 27:
            { yybegin(YYINITIAL); return BasicTypes.LE;
            }
          // fall through
          case 76: break;
          case 28:
            { yybegin(YYINITIAL); return BasicTypes.NE;
            }
          // fall through
          case 77: break;
          case 29:
            { yybegin(YYINITIAL); return BasicTypes.GE;
            }
          // fall through
          case 78: break;
          case 30:
            { yybegin(YYINITIAL); return BasicTypes.DO;
            }
          // fall through
          case 79: break;
          case 31:
            { yybegin(YYINITIAL); return BasicTypes.IF;
            }
          // fall through
          case 80: break;
          case 32:
            { yybegin(YYINITIAL); return BasicTypes.TO;
            }
          // fall through
          case 81: break;
          case 33:
            { yybegin(YYINITIAL); return BasicTypes.INCLUDE_PATH;
            }
          // fall through
          case 82: break;
          case 34:
            { yybegin(YYINITIAL); return BasicTypes.DIM;
            }
          // fall through
          case 83: break;
          case 35:
            { yybegin(YYINITIAL); return BasicTypes.END;
            }
          // fall through
          case 84: break;
          case 36:
            { yybegin(YYINITIAL); return BasicTypes.FOR;
            }
          // fall through
          case 85: break;
          case 37:
            { yybegin(YYINITIAL); return BasicTypes.SUB;
            }
          // fall through
          case 86: break;
          case 38:
            { yybegin(YYINITIAL); return BasicTypes.ELSE;
            }
          // fall through
          case 87: break;
          case 39:
            { yybegin(YYINITIAL); return BasicTypes.EXIT;
            }
          // fall through
          case 88: break;
          case 40:
            { yybegin(YYINITIAL); return BasicTypes.LOOP;
            }
          // fall through
          case 89: break;
          case 41:
            { yybegin(YYINITIAL); return BasicTypes.NEXT;
            }
          // fall through
          case 90: break;
          case 42:
            { yybegin(YYINITIAL); return BasicTypes.THEN;
            }
          // fall through
          case 91: break;
          case 43:
            { yybegin(YYINITIAL); return BasicTypes.PRINT;
            }
          // fall through
          case 92: break;
          case 44:
            { yybegin(YYINITIAL); return BasicTypes.UNTIL;
            }
          // fall through
          case 93: break;
          case 45:
            { yybegin(YYINITIAL); return BasicTypes.WHILE;
            }
          // fall through
          case 94: break;
          case 46:
            { yybegin(YYINITIAL); return BasicTypes.PRAGMA;
            }
          // fall through
          case 95: break;
          case 47:
            { yybegin(YYINITIAL); return BasicTypes.DECLARE;
            }
          // fall through
          case 96: break;
          case 48:
            { yybegin(INCLUDE); return BasicTypes.INCLUDE;
            }
          // fall through
          case 97: break;
          case 49:
            { yybegin(YYINITIAL); return BasicTypes.FUNCTION;
            }
          // fall through
          case 98: break;
          default:
            zzScanError(ZZ_NO_MATCH);
          }
      }
    }
  }


}
