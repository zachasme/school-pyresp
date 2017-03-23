# Message serializer for translating tuple space requests into jRESP JSON

ACTUAL_TYPE = 'org.cmg.jresp.knowledge.ActualTemplateField'
FORMAL_TYPE = 'org.cmg.jresp.knowledge.FormalTemplateField'

JAVATYPES = {
    str: 'java.lang.String',
    int: 'java.lang.Integer',
    float: 'java.lang.Double',
    tuple: 'org.cmg.jresp.knowledge.Tuple',
}
PYTHONTYPES = {
    'java.lang.String': str,
    'java.lang.Integer': int,
    'java.lang.Double': float,
    'org.cmg.jresp.knowledge.Tuple': tuple,
}


def dump_tuple(tuple_):
    """python to java-compatible dict

    ("foo", "baz", (1, "foo", 2), "bar")
    ->
    [{type:"javastring", value:"foo"}]
    """
    def generator():
        for item in tuple_:
            if isinstance(item, tuple):
                # recursively dump tuple
                value = dump_tuple(item)
            else:
                value = item
            yield {'type': JAVATYPES[type(item)], 'value': value}

    return list(generator())


def load_tuple(tuple_):
    """Convert to python tuple
    [{ 'type': 'java.lang.String', 'value': "foo" }]
    ->
    "foo"
    """
    def generator():
        for item in tuple_:
            type_ = item['type']
            value = item['value']
            if type_ == 'org.cmg.jresp.knowledge.Tuple':
                yield load_tuple(value)
            else:
                yield PYTHONTYPES[type_](value)

    return tuple(generator())


def load_template(tuple_):
    """java TEMPLATE list to python-compatible

    [{type:'FORMAL',value:{type:"javastring"}}]
    ->
    (str)
    """
    def generator():
        for item in tuple_:
            type_ = item['type']
            value = item['value']
            if type_ == FORMAL_TYPE:
                yield PYTHONTYPES[value['type']]
            else:
                yield value['value']
    return tuple(generator())


def dump_template(tuple_):
    """python to java-compatible TEMPLATE dict

    (str, "foo", (1, int, float, "bar"))
    ->
    [{type:'FORMAL',value:{type:"javastring"}}]
    """
    def generator():
        for item in tuple_:
            type_ = FORMAL_TYPE if isinstance(item, type) else ACTUAL_TYPE
            if type_ == FORMAL_TYPE:
                value = {'type': JAVATYPES[item]}
            elif isinstance(item, tuple):
                raise Exception("jResp does not support nested templates")
            else:
                value = dump_tuple([item])[0]
            yield {'type': type_, 'value': value}

    return list(generator())
