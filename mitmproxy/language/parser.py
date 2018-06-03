import ply.yacc as yacc

from mitmproxy import exceptions
from mitmproxy.language.lexer import CommandLanguageLexer


class CommandLanguageParser:
    tokens = CommandLanguageLexer.tokens  # it is required according to docs

    def __init__(self, command_manager):
        self.return_value = None
        self.command_manager = command_manager

    def p_command_line(self, p):
        """command_line : empty
                        | command_call"""
        p[0] = p[1]

    def p_command_call(self, p):
        """command_call : COMMAND argument_list"""
        print(p[:])
        p[0] = self.command_manager.call_strings(p[1], p[2])
        self.return_value = p[0]

    def p_argument_list(self, p):
        """argument_list : empty
                         | argument_list argument"""
        if len(p) == 2:
            p[0] = [] if p[1] is None else [p[1]]
        else:
            p[0] = p[1]
            p[0].append(p[2])

    def p_argument(self, p):
        """argument : PLAIN_STR
                    | QUOTED_STR
                    | array
                    | COMMAND"""
        p[0] = p[1]

    def p_array(self, p):
        """array : ARRAY"""
        p[0] = p[1].split(",")

    def p_empty(self, p):
        """empty :"""

    def p_error(self, p):
        if p is None:
            raise exceptions.CommandError("Syntax error at EOF")
        else:
            raise exceptions.CommandError(f"Syntax error at '{p.value}'")

    def build(self, **kwargs):
        self.parser = yacc.yacc(module=self,
                                errorlog=yacc.NullLogger(), **kwargs)


def create_parser(command_manager) -> yacc.LRParser:
    command_parser = CommandLanguageParser(command_manager)
    command_parser.build(debug=False, write_tables=False)
    return command_parser.parser
