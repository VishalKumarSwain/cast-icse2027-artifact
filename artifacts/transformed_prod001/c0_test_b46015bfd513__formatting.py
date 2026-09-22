from dataclasses import dataclass, field
from typing import List


@dataclass
class FunctionCall(Expression):
    location: int
    function: str
    args: List[Expression] = field(default_factory=list)
    is_constructor: bool = False
    freevars: List[str] = field(default_factory=list)

    def postorder(self, visitor):
        result = []
        for arg in self.args:
            result.append(arg.postorder(visitor))
        return visitor(result) + visitor(self)

    def preorder(self, visitor):
        return visitor(self) + visitor(self.args)

    def visit(self, visitor):
        return self.preorder(visitor)

    def toJSON(self):
        return {
            "location": self.location,
            "function": self.function,
            "args": [arg.toJSON() for arg in self.args],
            "is_constructor": self.is_constructor,
            "freevars": self.freevars,
        }
