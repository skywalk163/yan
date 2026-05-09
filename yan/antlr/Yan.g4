grammar Yan;

// ============ 词法规则 ============
// 注意：ANTLR 会按照规则在文件中的顺序进行匹配
// 关键字必须放在 ID 之前

// 关键字
IF: '若';
THEN: '则';
ELSE: '否则';
DEFINE: '定';
FUNC: '函';
TRUE: '真';
FALSE: '假';
NIL: '空';
FOREACH: '遍历';
IN: '于';
WHILE: '当';
DENGYU: '等于';

// 内置动词
PRINT: '印';
ADD: '加';
SUB: '减';
MUL: '乘';
DIV: '除';
MOD: '模';
POW: '幂';
ABS: '绝对';
NEG: '负';
GT: '大';
LT: '小';
EQ: '等';
NE: '不等';
AND: '且';
OR: '或';
NOT: '非';
HEAD: '首';
TAIL: '余';
APPEND: '入';
LEN: '长';
CONCAT: '连';
CONTAINS: '含';
MAP: '皆';
FILTER: '只';
REDUCE: '归';

// 操作符
EQUALS: '=';
DOT: '。';
SEMI: '；';
COMMA: '，';
COLON: '：';
QUOTE: '\'';

// 数学表达式
MATH: '$(' ~')'* ')';

// Python 代码块
PYTHON: '{{' .*? '}}';

// 字符串
STRING: '"' ~'"'* '"';

// 数字（独立出现）
NUMBER: [0-9]+ ('.' [0-9]+)?;

// 标识符（汉字序列或拉丁字母，可以包含数字）
// 注意：这个规则必须在所有关键字之后
ID: [\u4e00-\u9fa5]+ [0-9]* | [a-zA-Z_][a-zA-Z0-9_]*;

// 跳过空白字符
WS: [ \t\r\n]+ -> skip;

// 注释
COMMENT: '--' ~[\r\n]* -> skip;

// ============ 语法规则 ============

program: statement* EOF;

statement
    : defineStmt
    | exprStmt
    | DOT
    | SEMI
    ;

defineStmt
    : DEFINE ID EQUALS value          # DefineWithKeyword
    | ID EQUALS value                 # DefineWithoutKeyword
    | ID DENGYU value                 # DefineWithDengyu
    ;

value
    : lambda
    | expression
    ;

lambda
    : FUNC ID* COLON block            # LambdaWithBlock
    | FUNC ID* expression             # LambdaWithExpr
    | ID ID* COLON block              # LambdaIdWithBlock
    | ID ID* expression               # LambdaIdWithExpr
    ;

block
    : statement+ DOT
    ;

exprStmt
    : expression
    ;

// 表达式（条件表达式优先级最低）
expression
    : IF expr THEN thenBranch elseBranch?  # IfExpr
    | FOREACH ID IN expr COLON block        # ForeachExpr
    | WHILE expr COLON block                # WhileExpr
    | pipeline                              # PipelineExpr
    ;

thenBranch
    : COLON block
    | expr
    ;

elseBranch
    : ELSE COLON block
    | ELSE expr
    ;

// 管道
pipeline
    : expr (COMMA expr)*
    ;

// 表达式（动词调用或中缀表达式）
expr
    : verbCall                              # VerbCallExpr
    | infixExpr                             # InfixExprAlt
    ;

// 动词调用（前缀动词）
verbCall
    : (PRINT | ADD | SUB | MUL | DIV | MOD | POW | ABS | NEG | GT | LT | EQ | NE | AND | OR | NOT | HEAD | TAIL | APPEND | LEN | CONCAT | CONTAINS | MAP | FILTER | REDUCE) expr*
    ;

// 中缀表达式
infixExpr
    : atom ((PRINT | ADD | SUB | MUL | DIV | MOD | POW | ABS | NEG | GT | LT | EQ | NE | AND | OR | NOT | HEAD | TAIL | APPEND | LEN | CONCAT | CONTAINS | MAP | FILTER | REDUCE | ID) expr)*
    ;

atom
    : NUMBER                              # NumberAtom
    | STRING                              # StringAtom
    | TRUE                                # TrueAtom
    | FALSE                               # FalseAtom
    | NIL                                 # NilAtom
    | MATH                                # MathAtom
    | PYTHON                              # PythonAtom
    | QUOTE expr                          # QuoteAtom
    | ID                                  # IdAtom
    ;
