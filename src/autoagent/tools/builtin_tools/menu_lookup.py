# autoagent/tools/builtin_tools/menu_lookup.py

from ..base import BaseTool, ToolInput, ToolOutput
from ..registry import register_tool
from pydantic import Field

class MenuLookupInput(ToolInput):
    restaurant_id: str = Field(..., description="Restaurant unique ID")
    item_name:     str = Field(..., description="Menu item to look up")

class MenuLookupOutput(ToolOutput):
    item_name: str   = Field(..., description="Name of the item")
    price:     float = Field(..., description="Item price")
    available: bool  = Field(..., description="Is the item available?")

@register_tool
class MenuLookupTool(BaseTool):
    name = "menu_lookup"
    description = "Lookup a menu item’s price and availability."
    version = "1.1.0"
    tags = ["menu", "price", "inventory"]
    categories = ["food_ordering", "builtin"]

    input_model = MenuLookupInput
    output_model = MenuLookupOutput

    def execute(self, input: MenuLookupInput) -> MenuLookupOutput:
        # TODO: replace stub with real DB/API call
        # Example of batch support:
        if isinstance(input.item_name, list):
            # handle batch of item names
            outputs = []
            for item in input.item_name:
                stub = {"item_name": item, "price": 12.99, "available": True}
                outputs.append(MenuLookupOutput(**stub))
            # return first for single-run, or list in batch context
            return outputs  # note: agents must handle list outputs in batch mode

        stub = {"item_name": input.item_name, "price": 12.99, "available": True}
        return MenuLookupOutput(**stub)
