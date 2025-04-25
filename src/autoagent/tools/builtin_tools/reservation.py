# autoagent/tools/builtin_tools/reservation.py

from ..base import BaseTool, ToolInput, ToolOutput
from ..registry import register_tool
from pydantic import Field

class ReservationInput(ToolInput):
    date:       str = Field(..., description="YYYY-MM-DD")
    time:       str = Field(..., description="HH:MM")
    party_size: int = Field(..., description="Number of guests")

class ReservationOutput(ToolOutput):
    confirmation_id: str = Field(..., description="Reservation confirmation code")
    status:          str = Field(..., description="e.g. confirmed, pending")

@register_tool
class ReservationTool(BaseTool):
    name = "reservation"
    description = "Create a reservation for a given date, time, and party size."
    input_model = ReservationInput
    output_model = ReservationOutput

    def execute(self, input: ReservationInput) -> ReservationOutput:
        # TODO: hook into your real reservation backend
        return ReservationOutput(confirmation_id="RES-123456", status="confirmed")
