#!/usr/bin/python

import sys

print_int = """void print(int value) {
    char temp_str[11];
    itoa (value, temp_str, 10); 
    print_message(temp_str);
}"""

print_str = """void print(char *value) {
   print_message(value);
}"""


program_template = """\
#include "dal.h"

%DECLARATIONS%

void setup()
{
    microbug_setup();
}

void loop()
{
    %STATEMENTS%;
}

int main(void)
{
        init();

#if defined(USBCON)
        USBDevice.attach();
#endif
        setup(); // Switches on "eyes", and switches to bootloader if required

set_eye('L', LOW);  // Switch off eyes if bootloader not required
set_eye('R', LOW);
        for (;;) {
                loop();
                if (serialEventRun) serialEventRun();
        }
        return 0;
}


"""

class CodeGenerator(object):
    def __init__(self):
        self.need_print_str = False
        self.need_print_int = False
        self.declarations = []

    def program(self, statementlist):
        statement_lines = self.statementlist(statementlist)
        declarations= []
        if self.need_print_str:
            self.declarations.append(print_str)
        if self.need_print_int:
            self.declarations.append(print_int)

        program_lines = program_template
        program_lines = program_lines.replace("%STATEMENTS%", ";\n".join(statement_lines))
        program_lines = program_lines.replace("%DECLARATIONS%", "\n".join(self.declarations))
        return program_lines

    def statementlist(self, statementlist):
        assert statementlist[0] == "statementlist"
        lines = []
        for statement in statementlist[1]:
            statement_lines = self.statement(statement)
            lines.append(statement_lines)
        return lines

    def statement(self, statement):
        assert statement[0] == "statement"
        the_statement = statement[1]
        if the_statement[0] == "expression":
            gen_result = self.expression(the_statement)
            try:
                expression_type, expression_fragment = gen_result
            except ValueError:
                print repr(gen_result),gen_result.__class__
                raise
            return expression_fragment

        if the_statement[0] == "print_statement":
            print_statement_lines = self.print_statement(the_statement)
            return print_statement_lines

        if the_statement[0] == "forever_statement":
            return self.forever_statement(the_statement)

        return "//TBD (statement) " + the_statement[0]

    def forever_statement(self, forever_statement):
        assert forever_statement[0] == "forever_statement"
        the_statement = forever_statement[1]
        body_lines = ""
        if the_statement[0] == "statementlist":
            body_lines = self.statementlist(the_statement)

        return "while(1) {// Forever\n"+";\n".join(body_lines)+";"+ "\n}\n"

    def print_statement(self, print_statement):
        assert print_statement[0] == "print_statement"
        what_to_print = print_statement[1]

        if what_to_print[0] == "expression":
            gen_result = self.expression(what_to_print)
            (expression_type, expression_fragment) = gen_result
            if expression_type == "string":
                self.need_print_str = True

            if expression_type == "int":
                self.need_print_int = True

            print_template = 'print(%WHAT%)'
            return print_template.replace("%WHAT%", expression_fragment)

        return "// TBD print_statemnt " + repr(what_to_print)

    def expression(self, expression):
        assert expression[0] == "expression"
        the_expression = expression[1]
        if the_expression[0] == "literalvalue":
            (literalvalue_type, literalvalue_fragment) = self.literalvalue(the_expression)
            return (literalvalue_type, literalvalue_fragment)

        if the_expression[0] == "expression":
            gen_result = self.expression(the_expression)
            expression_type, expression_fragment = gen_result
            return expression_type, expression_fragment

        if the_expression[0] == "func_call":
            sys.stderr.write("AHA\n")
            sys.stderr.flush()
            gen_result = self.func_call(the_expression)
            func_type, expression_fragment = gen_result
            return func_type, expression_fragment

        sys.stderr.write("TBD::\n")
        sys.stderr.flush()
        sys.stderr.write(repr(expression))
        sys.stderr.flush()
        return ("tbd", repr(expression))

    def func_call(self, func_call):
        
        # ['func_call', 'scroll_string', ['expr_list', ['expression', ['literalvalue', ['string', 'HELLO WORLD']]]]]

        assert func_call[0] == "func_call"
        sys.stderr.write( repr(func_call) )
        sys.stderr.write("\n")
        sys.stderr.flush()
        function_name = func_call[1]
        function_arglist = func_call[2]
        gen_function_arglist = self.expr_list(function_arglist)
        gen_function_arglist_ = ",".join(gen_function_arglist)
        assert function_arglist[0] == "expr_list"
        function_call = function_name + '("HELLO WORLD")'
        function_call = function_name + "( " + gen_function_arglist_ + " )"
        return ("void", function_call)

    def expr_list(self, expr_list):
        assert expr_list[0] == "expr_list"
        list_result = []
        for item in expr_list[1:]:
            if item[0] == "expression":
                gen_result = self.expression(item)
                expression_type, expression_fragment = gen_result
                list_result.append( expression_fragment )
            if item[0] == "expr_list":
                cdr_list = self.expr_list(item)
                list_result = list_result+cdr_list

        return list_result

    def literalvalue(self, literalvalue):
        assert literalvalue[0] == "literalvalue"
        the_literalvalue = literalvalue[1]

        if the_literalvalue[0] == "number":
            # Generated C code for a literal integer  #FIXME, integer size
            # Note that this should be a string!
            return ( "int", str( the_literalvalue[1] ) )

        if the_literalvalue[0] == "string":
            # Generated C code for a literal string
            # FIXME: Do we want to be able to auto flash things?
            # FIXME: Do we want these as predeclared constants?
            py_string = the_literalvalue[1]

            x = repr(py_string)
            x = '"' + x[1:-1] + '"'

            return ("string", x)
            # literalvalue_fragment = self.literalvalue(the_expression)
            # return literalvalue_fragment

        return ("tbd", "//TBD (expression)")


def gen_code(AST):
    cg = CodeGenerator()
    print repr(AST)
    AST[0] = "program"
    program = cg.program(AST[1])
    return program
