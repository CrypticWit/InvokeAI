from typing import Union

from pydantic import BaseModel, Field, field_validator, model_validator

from invokeai.app.invocations.baseinvocation import (
    BaseInvocation,
    BaseInvocationOutput,
    invocation,
    invocation_output,
)
from invokeai.app.invocations.controlnet_image_processors import CONTROLNET_RESIZE_VALUES
from invokeai.app.invocations.fields import FieldDescriptions, ImageField, Input, InputField, OutputField
from invokeai.app.invocations.model import ModelField
from invokeai.app.invocations.util import validate_begin_end_step, validate_weights
from invokeai.app.services.shared.invocation_context import InvocationContext


class T2IAdapterField(BaseModel):
    image: ImageField = Field(description="The T2I-Adapter image prompt.")
    t2i_adapter_model: ModelField = Field(description="The T2I-Adapter model to use.")
    weight: Union[float, list[float]] = Field(default=1, description="The weight given to the T2I-Adapter")
    begin_step_percent: float = Field(
        default=0, ge=0, le=1, description="When the T2I-Adapter is first applied (% of total steps)"
    )
    end_step_percent: float = Field(
        default=1, ge=0, le=1, description="When the T2I-Adapter is last applied (% of total steps)"
    )
    resize_mode: CONTROLNET_RESIZE_VALUES = Field(default="just_resize", description="The resize mode to use")

    @field_validator("weight")
    @classmethod
    def validate_ip_adapter_weight(cls, v):
        validate_weights(v)
        return v

    @model_validator(mode="after")
    def validate_begin_end_step_percent(self):
        validate_begin_end_step(self.begin_step_percent, self.end_step_percent)
        return self


@invocation_output("t2i_adapter_output")
class T2IAdapterOutput(BaseInvocationOutput):
    t2i_adapter: T2IAdapterField = OutputField(description=FieldDescriptions.t2i_adapter, title="T2I Adapter")


@invocation(
    "t2i_adapter", title="T2I-Adapter", tags=["t2i_adapter", "control"], category="t2i_adapter", version="1.0.1"
)
class T2IAdapterInvocation(BaseInvocation):
    """Collects T2I-Adapter info to pass to other nodes."""

    # Inputs
    image: ImageField = InputField(description="The IP-Adapter image prompt.")
    t2i_adapter_model: ModelField = InputField(
        description="The T2I-Adapter model.",
        title="T2I-Adapter Model",
        input=Input.Direct,
        ui_order=-1,
    )
    weight: Union[float, list[float]] = InputField(
        default=1, ge=0, description="The weight given to the T2I-Adapter", title="Weight"
    )
    begin_step_percent: float = InputField(
        default=0, ge=0, le=1, description="When the T2I-Adapter is first applied (% of total steps)"
    )
    end_step_percent: float = InputField(
        default=1, ge=0, le=1, description="When the T2I-Adapter is last applied (% of total steps)"
    )
    resize_mode: CONTROLNET_RESIZE_VALUES = InputField(
        default="just_resize",
        description="The resize mode applied to the T2I-Adapter input image so that it matches the target output size.",
    )

    @field_validator("weight")
    @classmethod
    def validate_ip_adapter_weight(cls, v):
        validate_weights(v)
        return v

    @model_validator(mode="after")
    def validate_begin_end_step_percent(self):
        validate_begin_end_step(self.begin_step_percent, self.end_step_percent)
        return self

    def invoke(self, context: InvocationContext) -> T2IAdapterOutput:
        return T2IAdapterOutput(
            t2i_adapter=T2IAdapterField(
                image=self.image,
                t2i_adapter_model=self.t2i_adapter_model,
                weight=self.weight,
                begin_step_percent=self.begin_step_percent,
                end_step_percent=self.end_step_percent,
                resize_mode=self.resize_mode,
            )
        )
