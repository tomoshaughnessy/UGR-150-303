from pyparsing import Literal,CaselessLiteral,Word,Combine,Group,Optional,ZeroOrMore,Forward,nums,alphas

import math
import operator

exprStack = []

def pushFirst( strg, loc, toks ):
        exprStack.append( toks[0] )
def pushUMinus( strg, loc, toks ):
    if toks and toks[0]=='-':
        exprStack.append( 'unary -' )
        #~ exprStack.append( '-1' )
        #~ exprStack.append( '*' )

bnf = None
def BNF():
    """
    expop   :: '^'
    multop  :: '*' | '/'
    addop   :: '+' | '-'
    integer :: ['+' | '-'] '0'..'9'+
    atom    :: PI | E | real | fn '(' expr ')' | expr ')'
    factor  :: atom [ expop factor ]*
    term    :: factor [ multop factor ]*
    expr    :: term [ addop term ]*
    """
    global bnf
    if not bnf:
        point   = Literal( "." )                                        # Literals are one char
        e       = CaselessLiteral( "E" )
        fnumber = Combine( Word( "+-"+nums, nums) +
                    Optional( point + Optional( Word ( nums ) ) ) +
                    Optional( e + Word("+-"+nums, nums ) ) )
        ident = Word(alphas, alphas+nums+"_$")

        plus    = Literal( "+" )
        minus   = Literal( "-" )
        mult    = Literal( "*" )
        div     = Literal( "/" )
        lpar    = Literal( "(" ).suppress()                             # Doesn't add parenthesis to the parse tree
        rpar    = Literal( ")" ).suppress()
        addop   = plus | minus
        multop  = mult | div
        expop   = Literal( "^" )
        pi      = CaselessLiteral( "PI" )

        expr    = Forward()
        atom    = (Optional("-") + ( pi | e | fnumber | ident + lpar + expr + rpar ).setParseAction( pushFirst ) | ( lpar + expr.suppress() + rpar )).setParseAction(pushUMinus)

        factor = Forward()
        factor << atom + ZeroOrMore( ( expop + factor ).setParseAction( pushFirst ) )

        term = factor + ZeroOrMore ( ( multop + factor ).setParseAction( pushFirst ) )
        expr << term + ZeroOrMore ( ( addop + term ).setParseAction( pushFirst ) )
        bnf = expr
    return bnf

epsilon = 1e-12
opn = {
        "+" :   operator.add,
        "-" :   operator.sub,
        "*" :   operator.mul,
        "/" :   operator.truediv,
        "^" :   operator.pow
        }
fn = {
        "sin"   : math.sin,
        "cos"   : math.cos,
        "tan"   : math.tan,
        "abs"   : abs,
        "trunc" : lambda a: int(a),
        "round" : round,
        "sgn"   : lambda a: abs(a)>epsilon and cmp(a,0) or 0
        }
def evaluateStack( s ):
    op = s.pop()
    if op == 'unary -':
        return -evaluateStack( s )
    if op in "+-*/^":
        op2 = evaluateStack( s )
        op1 = evaluateStack( s )
        return opn[op]( op1, op2 )
    elif op == "PI":
        return math.pi # 3.1415
    elif op == "E":
        return math.e
    elif op in fn:
        return fn[op]( evaluateStack( s ) )
    elif op[0].isalpha():
        return 0
    else:
        return float( op )

if __name__ == "__main__":
    
    def test( s, expVal ):
        global exprStack
        exprStack = []
        results = BNF().parseString( s )
        val = evaluateStack( exprStack[:] )
        if val == expVal:
            print s, "=", val, results, "=>", exprStack
        else:
            print s+"!!!", val, "!=", expVal, results, "=>", exprStack

    test( "PI*PI/10", math.pi*math.pi/10  )

