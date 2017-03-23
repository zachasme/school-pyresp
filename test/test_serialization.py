from pyresp.jresp import serialization

TUPLES = [
    [
        ("foo", 1),
        [{
            "type": "java.lang.String",
            "value": "foo"
        }, {
            "type": "java.lang.Integer",
            "value": 1
        }]
    ],
    [
        ("foo", ("bar", "baz")),
        [{
            "type": "java.lang.String",
            "value": "foo"
        }, {
            "type": "org.cmg.jresp.knowledge.Tuple",
            "value": [{
                "type": "java.lang.String",
                "value": "bar"
            }, {
                "type": "java.lang.String",
                "value": "baz"
            }]
        }],
    ]
]
PATTERNS = [
    [
        ("foo", 1),
        [{
            "type": "org.cmg.jresp.knowledge.ActualTemplateField",
            "value": {
                "type": "java.lang.String",
                "value": "foo"
            }
        }, {
            "type": "org.cmg.jresp.knowledge.ActualTemplateField",
            "value": {
                "type": "java.lang.Integer",
                "value": 1
            }
        }]
    ],
    [
        ("foo", str, 1, int),
        [{
            "type": "org.cmg.jresp.knowledge.ActualTemplateField",
            "value": {
                "type": "java.lang.String",
                "value": "foo"
            }
        }, {
            "type": "org.cmg.jresp.knowledge.FormalTemplateField",
            "value": {
                "type": "java.lang.String",
            }
        }, {
            "type": "org.cmg.jresp.knowledge.ActualTemplateField",
            "value": {
                "type": "java.lang.Integer",
                "value": 1
            }
        }, {
            "type": "org.cmg.jresp.knowledge.FormalTemplateField",
            "value": {
                "type": "java.lang.Integer",
            }
        }]
    ]
]


def test_tuples():
    """yup
    """
    for (python, java) in TUPLES:
        assert serialization.load_tuple(java) == python
        assert serialization.dump_tuple(python) == java


def test_patterns():
    """yup
    """
    for (python, java) in PATTERNS:
        assert serialization.load_template(java) == python
        assert serialization.dump_template(python) == java
