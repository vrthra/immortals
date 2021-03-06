import timeout_decorator
# std
import sys
import unittest

# vendor
import microjson


T_PARSE_DICTS = [
    ('{}', {}),
    ('{"a":1}', {"a":1}),
    ('{"abcdef": "ghijkl"}', {'abcdef': 'ghijkl'}),

    # whitespace tests
    ('\t{\n\r\t }\r\n', {}),
    (' \t{ "a"\n:\t"b"\n\t}  ', {"a":"b"})
    ]

T_PARSE_STRS = [
    ('', None),

    ('"foo bar baz"', 'foo bar baz'),
    ('"abc\\"def\\"ghi"', 'abc"def"ghi'),

    # escaped whitespace
    ('"\\n\\tindent\\r\\n"', '\n\tindent\r\n'),

    # escaped ascii, weird but need to test to cover possible cases
    ('"\\ \\x\\y\\z\\ "', ' xyz '),

    # escaped unicode 
    #('"\u0124\u0113\u013a\u013e\u014d"', u"\u0124\u0113\u013a\u013e\u014d"),
    #('"\u201chello\u201d"', u"\u201chello\u201d"),

    # bare utf-8 
    ('"\xc6\x91"', u"\u0191"),
    ('"\xc4\x91"', u"\u0111"),

    # mixed utf-8 and escaped unicode
    #('"a\xc6\x91b\u0191c\u2018"', u"a\u0191b\u0191c\u2018"),
    ]

# utf-8 encoded ucs-4 test case
if sys.maxunicode == 1114111:
    T_PARSE_STRS += [
        # pure utf-8 char > 16-bits. not asci-encodable in json.
        ('"\xf0\x90\x82\x82"', U"\U00010082")
    ]

# test range of 16-bit characters > 0x7F

T_PARSE_UNICODE = [('"%s"' % c, c) for c in 
        (chr(i) for i in range(0x80, 0x10000))
    ]

T_PARSE_LISTS = [
    ('[]', []),
    ('[1,2,3]', [1,2,3]),
    ('[[1,2],["a","b"]]', [[1,2],["a","b"]]),

    # whitespace tests
    ('\t\n[\r\n \t]\n', []),
    ('  [\n\t1,\t2 ] \t', [1,2])

    ]

T_PARSE_INTS = [
    ('0', 0),
    ('-1', -1),
    ('123', 123), 
    ('-2147483648', -2147483648),
    ('2147483648', 2147483648),
    ('4294967296', 4294967296),
    ('9223372036854775808', 9223372036854775808),
    ('18446744073709551616', 18446744073709551616)
    ]

T_PARSE_FLOATS = [
    ('.1', 0.1),
    ('-.1', -0.1),
    ('1.0', 1.0),
    ('-1.0', -1.0),
    ('3.14159', 3.14159),
    ('-3.14159', -3.14159),
    ('1E1', 1E1),
    ('-1E2', -1E2),
    ('-1E-2', -1E-2),
    ('12E-2', 12E-2),
    ('1.8446744073709552e19', 1.8446744073709552e19)
    ]

T_PARSE_FIXED = [('true', True), ('false', False), ('null', None)]

T_PARSE_MALFORMED = [
    'wegouhweg',    # naked char data
    '["abcdef]',    # string missing trailing '"'
    '["a","b"',     # list missing trailing ']'
    '{"a:"b"}',     # key missing trailing '"'
    '{"a":13',      # dict missing trailing '}'
    '{123: 456}',   # object keys must be quoted
    '[nulx]',       # null?
    '[trux]',       # true?
    "[12, ]",       # incomplete list
    "[123",         # truncated list
    "[1, , ,]",     # list with empty slots
    "[1, , ",       # truncated list with empty slots
    "[#",           # list with illegal chars
    "[1, 2\n#",     # list with illegal chars
    '{"abc"}',      # incomplete dict
    '{"abc"',       # truncated dict
    '{"abc":',      # truncated dict with missing value
    '{',            # truncated dict
    '{,}',          # dict with empty slots
    #u'[]',          # input must be a str
    #'{"a":1"b":2}'  # missing comma
    ]



class TestMicrojsonParse(unittest.TestCase):

    def _run_cases(self, cases):
        for js, py in cases:
            r = microjson.from_json(js)
            self.assertEqual(r, py)

    @timeout_decorator.timeout(10)
    def test_dict(self):
        self._run_cases(T_PARSE_DICTS)

    @timeout_decorator.timeout(10)
    def test_list(self):
        self._run_cases(T_PARSE_LISTS)

    @timeout_decorator.timeout(10)
    def test_string(self):
        self._run_cases(T_PARSE_STRS)

    #def test_unicode(self):
    #    self._run_cases(T_PARSE_UNICODE)

    @timeout_decorator.timeout(10)
    def test_integer(self):
        self._run_cases(T_PARSE_INTS)
    
    @timeout_decorator.timeout(10)
    def test_floats(self):
        self._run_cases(T_PARSE_FLOATS)

    @timeout_decorator.timeout(10)
    def test_null_and_bool(self):
        self._run_cases(T_PARSE_FIXED)

    @timeout_decorator.timeout(10)
    def test_malformed(self):
        "assert a JSONError is raised for these cases"
        for js in T_PARSE_MALFORMED:
            self.assertRaises(microjson.JSONError, microjson.from_json, js)

#    @timeout_decorator.timeout(10)
#    def test_aliases(self):
#        data = "abc"
#        json = '"abc"'
#        r = microjson.decode(json)
#        self.assertEqual(r, data)
#        r = microjson.encode(data)
#        self.assertEqual(r, json)


#T_EMIT_VALID = [
#    #(u"\"\n\t\u2018hi\u2019", '"\\\"\\n\\t\u2018hi\u2019"'),
#    #(u"se\u00f1or", '"se\u00f1or"'),
#    (["foo", "bar"], '["foo","bar"]'),
#    (3.14159, "3.14159"),
#    (10e20, "1e+21"),
#    (-100, "-100"),
#    (0x351, "849"),
#    ({"a":1,"b":[1,2,3]}, '{"a":1,"b":[1,2,3]}'),
#    ((None, True, False), "[null,true,false]"),
#
#    # non-string keys are cast to str
#    ({1: 2}, '{"1":2}'),
#
#    ]
#
#T_EMIT_INVALID = [
#    float('inf'),
#    float('-inf'),
#    float('nan'),
#    ]
#
#
#class TestMicrojsonEmit(unittest.TestCase):
#
#    def _run_cases(self, cases):
#        for py, js in cases:
#            r = microjson.to_json(py)
#            self.assertEqual(r, js)
#
#    @timeout_decorator.timeout(10)
#    def test_valid(self):
#        self._run_cases(T_EMIT_VALID)
#
#    @timeout_decorator.timeout(10)
#    def test_invalid(self):
#        for py in T_EMIT_INVALID:
#            self.assertRaises(microjson.JSONError, microjson.to_json, py)
#
#    @timeout_decorator.timeout(10)
#    def test_string_object(self):
#        class Bag:
#            pass
#        cases = [
#            ("hello", '"hello"'),
#            (u"\u2018hi\u2019", r'"\u2018hi\u2019"')
#            ]
#        for py, js in cases:
#            for meth in ('__str__', '__unicode__'):
#                obj = Bag()
#                setattr(obj, meth, lambda: py)
#                r = microjson.to_json(obj)
#                self.assertEqual(r, js)

def main():
    unittest.main()


if __name__ == "__main__":
    main()
        
