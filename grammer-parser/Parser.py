import ASTNodeDefs as AST
class Lexer:
    def __init__(self, code):
        self.code = code
        self.position = 0
        self.current_char = self.code[self.position]
        self.tokens = []
    
    # Move to the next position in the code increment by one.
    def advance(self):
        self.position += 1
        if self.position >= len(self.code):
            self.current_char = None
        else:
            self.current_char = self.code[self.position]

    # If the current char is whitespace, move ahead.
    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    # Tokenize the identifier.
    def identifier(self):
        result = ''
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()
        return ('IDENTIFIER', result)
    

    # Tokenize numbers, including float handling
    def number(self):
        result = ''
        # TODO: Update this code to handle floating-point numbers

        #sets float to false as a default
        is_float=False
        #while loop runs through number looking for decimal point
        while self.current_char!=None and (self.current_char.isdigit() or self.current_char=="."):
            if self.current_char=='.':
                # more then one decimal point is not allowed
                if is_float:
                    raise ValueError("Invalid Float Literal")
                is_float=True
            result+=self.current_char
            self.advance()

        if is_float:
            return ('FNUMBER', float(result))
        else:
            return ('NUMBER', int(result))

    def token(self):
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            if self.current_char.isalpha():
                ident = self.identifier()
                if ident[1] == 'if':
                    return ('IF', 'if')
                elif ident[1] == 'else':
                    return ('ELSE', 'else')
                elif ident[1] == 'while':
                    return ('WHILE', 'while')
                elif ident[1] == 'int':
                    return ('INT', 'int')
                elif ident[1] == 'float':
                    return ('FLOAT', 'float')
                return ident  # Generic identifier
            if self.current_char.isdigit() or self.current_char == '.':
                return self.number()
            if self.current_char == '+':
                self.advance()
                return ('PLUS', '+')
            if self.current_char == '-':
                self.advance()
                return ('MINUS', '-')
            if self.current_char == '*':
                self.advance()
                return ('MULTIPLY', '*')
            if self.current_char == '/':
                self.advance()
                return ('DIVIDE', '/')
            if self.current_char == '=':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return ('EQ', '==')
                return ('EQUALS', '=')
            if self.current_char == '!':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return ('NEQ', '!=')
            if self.current_char == '<':
                self.advance()
                return ('LESS', '<')
            if self.current_char == '>':
                self.advance()
                return ('GREATER', '>')
            if self.current_char == '(':
                self.advance()
                return ('LPAREN', '(')
            if self.current_char == ')':
                self.advance()
                return ('RPAREN', ')')
            if self.current_char == ',':
                self.advance()
                return ('COMMA', ',')
            if self.current_char == ':':
                self.advance()
                return ('COLON', ':')
            # TODO: Implement handling for '{' and '}' tokens here (see `tokens.txt` for exact names)
            if self.current_char=="{":
                self.advance()
                return('LBRACE','{')
            if self.current_char=="}":
                self.advance()
                return("RBRACE","}")
            if self.current_char == '\n':
                self.advance()
                continue

            raise ValueError(f"Illegal character at position {self.position}: {self.current_char}")

        return ('EOF', None)

    # Collect all the tokens in a list.
    def tokenize(self):
        while True:
            token = self.token()
            self.tokens.append(token)
            if token[0] == 'EOF':
                break
        return self.tokens



import ASTNodeDefs as AST

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token = tokens.pop(0)
        # Use these to track the variables and their scope
        self.symbol_table = {'global': {}}
        self.scope_counter = 0
        self.scope_stack = ['global']
        self.messages = []

    def error(self, message):
        self.messages.append(message)
    
    def advance(self):
        if self.tokens:
            self.current_token = self.tokens.pop(0)

    # TODO: Implement logic to enter a new scope, add it to symbol table, and update `scope_stack`
    def enter_scope(self):
        self.scope_counter+=1                   #updates scope counter
        new_scope=f"scope_{self.scope_counter}" #creates new scope
        self.symbol_table[new_scope]={}         #puts new scope to symbol table
        self.scope_stack.append(new_scope)      #updates scope stack

    # TODO: Implement logic to exit the current scope, removing it from `scope_stack`
    def exit_scope(self):
        if len(self.scope_stack)>1: #ensures not last element
            self.scope_stack.pop()  

    # Return the current scope name
    def current_scope(self):
        return self.scope_stack[-1]

    # TODO: Check if a variable is already declared in the current scope; if so, log an error
    def checkVarDeclared(self, identifier):
        current_scope=self.current_scope()
        # checks if the variable is declared in the current scope
        if identifier in self.symbol_table[current_scope]:
            self.error(f"Variable {identifier} has already been declared in the current scope")

    # TODO: Check if a variable is declared in any accessible scope; if not, log an error
    def checkVarUse(self, identifier):
        for scope in reversed(self.scope_stack):
            # checks for variable in the current scope or enclosing
            if identifier in self.symbol_table[scope]:
                return
        self.error(f"Variable {identifier} has not been declared in the current or any enclosing scopes")

    # TODO: Check type mismatch between two entities; log an error if they do not match
    def checkTypeMatch2(self, vType, eType, var, exp):
        # checks if tyopes equal
        if vType!=eType:
            self.error(f"Type Mismatch between {vType} and {eType}")

    # TODO: Implement logic to add a variable to the current scope in `symbol_table`
    def add_variable(self, name, var_type):
        current_scope=self.current_scope()
        # if its already in the symbol table must check if its already been declared, which causes an error
        if name in self.symbol_table[current_scope]:
            self.checkVarDeclared(name)
        else:
            self.symbol_table[current_scope][name]=var_type


    # TODO: Retrieve the variable type from `symbol_table` if it exists
    def get_variable_type(self, name):

        #loops through looking for variable in symbol table
        for scope in reversed(self.scope_stack):
            if name in self.symbol_table[scope]:
                return self.symbol_table[scope][name]
        self.checkVarUse(name)
        return None

    def parse(self):
        return self.program()

    def program(self):
        statements = []
        while self.current_token[0] != 'EOF':
            statements.append(self.statement())
        return AST.Block(statements)

    # TODO: Modify the `statement` function to dispatch to declare statement
    def statement(self):
        if self.current_token[0] == 'IDENTIFIER':
            if self.peek() == 'EQUALS':
                return self.assign_stmt()
            elif self.peek() == 'LPAREN':
                return self.function_call()
            else:
                raise ValueError(f"Unexpected token after identifier: {self.current_token}")
        elif self.current_token[0] == 'IF':
            return self.if_stmt()
        elif self.current_token[0] == 'WHILE':
            return self.while_stmt()
        # float and int types go to decl
        elif self.current_token[0] in ['FLOAT','INT']:
            return self.decl_stmt()
        else:
            raise ValueError(f"Unexpected token: {self.current_token}")

    # TODO: Implement the declaration statement and handle adding the variable to the symbol table
    def decl_stmt(self):
        """
        Parses a declaration statement.
        Example:
        int x = 5
        float y = 3.5
        TODO: Implement logic to parse type, identifier, and initialization expression and also handle type checking
        """
        var_type=self.current_token[1]          # gets var type
        self.advance()
        var_name=self.current_token[1]          #gets var name
        self.advance()
        self.expect("EQUALS")  

        # put vars in symbols table
        self.add_variable(var_name, var_type)

        expression=self.expression()            #gets expression

        # make sure types match and does not evaluate if they are None because that is a seperate error
        if var_type!=expression.value_type and expression.value_type!=None and var_type!=None:
            self.checkTypeMatch2(var_type, expression.value_type, var_name, expression)
        
        
        return AST.Declaration(var_type, var_name, expression)

    # TODO: Parse assignment statements, handle type checking
    def assign_stmt(self):
        """
        Parses an assignment statement.
        Example:
        x = 10
        x = y + 5
        TODO: Implement logic to handle assignment, including type checking.
        """
        var_name=self.current_token[1]                  #gets var name
        var_type=self.get_variable_type(var_name)       #gets var type
        self.advance()
        self.expect('EQUALS')
        expression=self.expression()                    #gets expression

        # check the types and does not evaluate if they are None because that is a seperate error
        if var_type!=expression.value_type and expression.value_type!=None and var_type!=None:
            self.checkTypeMatch2(var_type,expression.value_type,var_name,expression)
        
        return AST.Assignment(var_name, expression)

    # TODO: Implement the logic to parse the if condition and blocks of code
    def if_stmt(self):
        """
        Parses an if-statement, with an optional else block.
        Example:
        if condition {
            # statements
        }
        else {
            # statements
        }
        TODO: Implement the logic to parse the if condition and blocks of code.
        """
        self.advance()                          #moves past 'IF
        condition=self.boolean_expression()     # gets the condition
        then_block=self.block()                 # gets the block
        else_block=None                         # sets else to None because not all ifs have an else
        if self.current_token[0]=='ELSE':       # checks for else block
            self.advance()
            else_block=self.block()             #gets else block
        return AST.IfStatement(condition, then_block, else_block)

    # TODO: Implement the logic to parse while loops with a condition and a block of statements
    def while_stmt(self):
        """
        Parses a while-statement.
        Example:
        while condition {
            # statements
        }
        TODO: Implement the logic to parse while loops with a condition and a block of statements.
        """
        self.advance()                          #moves past 'WHILE'
        condition=self.boolean_expression()     # gets condition
        block=self.block()                      # gets block
        return AST.WhileStatement(condition, block)
    # TODO: Implement logic to capture multiple statements as part of a block
    def block(self):
        """
        Parses a block of statements. A block is a collection of statements grouped by `{}`.
        Example:
        
        x = 5
        y = 10
        
        TODO: Implement logic to capture multiple statements as part of a block.
        """
        self.expect('LBRACE')                   # blocks should start with a brace
        self.enter_scope()                      # enters scope of block
        statements=[]
        # appends the statements to the list of block statements til closing brace
        while self.current_token[0] !='RBRACE': 
            statements.append(self.statement())
        self.exit_scope()
        self.expect("RBRACE")
        return AST.Block(statements)

    # TODO: Implement logic to parse binary operations (e.g., addition, subtraction) with correct precedence and type checking
    def expression(self):
        """
        Parses an expression. Handles operators like +, -, etc.
        Example:
        x + y - 5
        TODO: Implement logic to parse binary operations (e.g., addition, subtraction) with correct precedence and type checking.
        """
        left = self.term()
        while self.current_token[0] in ['PLUS', 'MINUS']:
            op = self.current_token[0]
            self.advance()
            right = self.term()

            self.checkTypeMatch2(left.value_type, right.value_type, left, right)
            left = AST.BinaryOperation(left, op, right, value_type=left.value_type)

        return left

    # TODO: Implement parsing for boolean expressions and check for type compatibility
    def boolean_expression(self):
        """
        Parses a boolean expression. These are comparisons like ==, !=, <, >.
        Example:
        x == 5
        TODO: Implement parsing for boolean expressions and check for type compatibility.
        """
        left=self.expression()

        # check if current token is boolean op
        if self.current_token[0] in ['NEQ', 'GREATER', 'EQ','LESS']:
            # current operator
            op=self.current_token
            self.advance()
            # parse the right side of the boolean expression
            right=self.expression()
            # ensures program does not throw a type error when the var is not declared
            if left.value_type!=None and right.value_type!=None:
                self.checkTypeMatch2(left.value_type, right.value_type, left, right)
            # returns ast of the expression
            return AST.BooleanExpression(left, op, right)
        return ValueError(f"Expected boolean operator but got {self.current_token}")

    # TODO: Implement parsing for multiplication and division and check for type compatibility
    def term(self):
        """
        Parses a term. A term consists of factors combined by * or /.
        Example:
        x * y / z
        TODO: Implement parsing for multiplication and division and check for type compatibility.
        """
        left=self.factor()
        # continue parsing is the term is a * or /
        while self.current_token[0] in ['DIVIDE','MULTIPLY']:
            # current operator
            op=self.current_token[0]
            self.advance()
            # parses the right side of the expression
            right=self.factor()
            #check types
            self.checkTypeMatch2(left.value_type,right.value_type,left,right)
            # create binary op of the left and right
            left=AST.BinaryOperation(left, op, right,value_type=left.value_type)

        return left

        
    def factor(self):
        if self.current_token[0] == 'NUMBER':
            # handle int
            num=self.current_token[1]
            self.advance()
            return AST.Factor(num, 'int')
        elif self.current_token[0] == 'FNUMBER':
            # handle float
            num=self.current_token[1]
            self.advance()
            return AST.Factor(num, 'float')
        elif self.current_token[0] == 'IDENTIFIER':
            # TODO: Ensure that you parse the identifier correctly, retrieve its type from the symbol table, and check if it has been declared in the current or any enclosing scopes.
            var_name=self.current_token[1]              #gets the variable name
            var_type=self.get_variable_type(var_name)   # gets variable type which within it checks if it has been declared
            self.advance()
            return AST.Factor(var_name, var_type)
        elif self.current_token[0] == 'LPAREN':
            self.advance()
            expr = self.expression()
            self.expect('RPAREN')
            return expr
        else:
            raise ValueError(f"Unexpected token in factor: {self.current_token}")

    def function_call(self):
        func_name = self.current_token[1]
        self.advance()
        self.expect('LPAREN')
        args = self.arg_list()
        self.expect('RPAREN')

        return AST.FunctionCall(func_name, args)

    def arg_list(self):
        """
        Parses a list of function arguments.
        Example:
        (x, y + 5)
        """
        args = []
        if self.current_token[0] != 'RPAREN':
            args.append(self.expression())
            while self.current_token[0] == 'COMMA':
                self.advance()
                args.append(self.expression())

        return args

    def expect(self, token_type):
        if self.current_token[0] == token_type:
            self.advance()
        else:
            raise ValueError(f"Expected token {token_type}, but got {self.current_token[0]}")

    def peek(self):
        return self.tokens[0][0] if self.tokens else None
