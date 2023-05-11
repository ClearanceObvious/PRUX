from nodes import NodeType, Node
from ttoken import TokenType

KEYWORDS = ['let', 'return', 'if', 'else']
BOOL_VAL = ['true', 'false']
NULL_VAL = 'null'

def dump_ast(obj, indent=0, indent_level=0):
    """
    Dump an object into a text format.

    Args:
        obj: The object to dump.
        indent (int, optional): The number of spaces to indent each line of output by.
            Defaults to 0.
        indent_level (int, optional): The level of indentation of the opening parentheses.
            Defaults to 0.

    Returns:
        str: The text format of the object.
    """
    # Get the object's class name.
    class_name = obj.__class__.__name__

    # Check if the class is an Enum.
    is_enum = False

    # Check if the class is a NodeType or a TokenType.
    is_nodetype = isinstance(obj, NodeType)
    is_tokentype = isinstance(obj, TokenType)
    
    # Check if the class is a subclass of Node.
    is_node = issubclass(obj.__class__, Node)

    # Initialize the output string.
    output = ""

    if is_nodetype or is_tokentype:
        output = obj.name
    else:
        output = f"{class_name}("

        # Get the object's attributes.
        attributes = []
        if isinstance(obj, list):
            for i, item in enumerate(obj):
                attributes.append(f"[{i}]={dump_ast(item, indent + 4, indent_level + 1)}")
        else:
            for attr_name in dir(obj):
                if not attr_name.startswith("__") and not callable(getattr(obj, attr_name)):
                    attr_value = getattr(obj, attr_name)
                    if isinstance(attr_value, (int, float, str)):
                        attributes.append(f"{attr_name}={repr(attr_value)}")
                    else:
                        if is_enum and attr_name == "_name_":
                            attributes.append(f"{obj._name_}")
                        else:
                            attributes.append(f"{attr_name}={dump_ast(attr_value, indent + 4, indent_level + 1)}")

        # Add the attributes to the output string.
        if len(attributes) > 0:
            output += "\n" + "\n".join([f"{' ' * (indent + 4)}{attr}," for attr in attributes]) + "\n" + " " * (indent_level * 4) + ")"
        else:
            output += ")"

    return output

def convert(val: Node):
    if val.type == NodeType.NumberNode:
        return float(val.value)
    elif val.type == NodeType.StringNode:
        return str(val.value)
    elif val.type == NodeType.BooleanNode:
        return bool(val.value)
    elif val.type == NodeType.NullNode:
        return 'null'
