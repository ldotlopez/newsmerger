from __future__ import annotations

from pathlib import Path

import platformdirs
import pydantic
import yaml

from .consts import PACKAGE_NAME
from .models import SourceData


class CacheConfig(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")
    base_dir: Path = pydantic.Field(
        default_factory=lambda: platformdirs.user_cache_path(PACKAGE_NAME)
    )
    expiration: float = 60 * 60


class DatabaseConfig(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")
    uri: str = pydantic.Field(
        default_factory=lambda: (
            "sqlite:///" + platformdirs.user_data_dir(PACKAGE_NAME) + "/data.db"
        )
    )


class ProcessorConfigParams(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="allow")


class ProcessorConfig(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")
    name: str
    # Forwarded as kwargs to the Processor's __init__. `max_retries` and
    # `version` are recognized by BaseProcessor itself (override the
    # class-level MAX_RETRIES/VERSION); anything else is processor-specific
    # (e.g. a model name, a feed title).
    params: ProcessorConfigParams


class PipelineStepConfig(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")
    processor: str
    params: ProcessorConfigParams = pydantic.Field(
        default_factory=ProcessorConfigParams
    )


class PipelineConfig(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")
    name: str
    steps: list[PipelineStepConfig]

    @pydantic.field_validator("steps")
    @classmethod
    def validate_steps(
        cls, steps: list[PipelineStepConfig]
    ) -> list[PipelineStepConfig]:
        if not steps:
            raise ValueError("pipeline must contain at least one step")

        processor_names = [step.processor for step in steps]
        if len(processor_names) != len(set(processor_names)):
            raise ValueError("pipeline steps must not repeat a processor")
        return steps


class Config(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")
    sources: list[SourceData] = []
    processors: list[ProcessorConfig] = []
    pipelines: list[PipelineConfig] = []
    cache: CacheConfig = CacheConfig()
    db: DatabaseConfig = DatabaseConfig()

    @pydantic.model_validator(mode="after")
    def validate_pipelines(self) -> Config:
        processor_names = [processor.name for processor in self.processors]
        if len(processor_names) != len(set(processor_names)):
            raise ValueError("processor names must be unique")

        pipeline_names = [pipeline.name for pipeline in self.pipelines]
        if len(pipeline_names) != len(set(pipeline_names)):
            raise ValueError("pipeline names must be unique")

        configured_processors = set(processor_names)
        for pipeline in self.pipelines:
            unknown = {
                step.processor
                for step in pipeline.steps
                if step.processor not in configured_processors
            }
            if unknown:
                names = ", ".join(sorted(unknown))
                raise ValueError(
                    f"pipeline '{pipeline.name}' references unknown processor(s): {names}"
                )
        return self

    def get_pipeline(self, name: str) -> PipelineConfig:
        for pipeline in self.pipelines:
            if pipeline.name == name:
                return pipeline
        raise ValueError(f"pipeline '{name}' is not configured")

    @classmethod
    def from_file(cls, filepath: str | Path) -> Config:
        if isinstance(filepath, str):
            filepath = Path(filepath)

        return cls.from_text(filepath.read_text())

    @classmethod
    def from_text(cls, text: str) -> Config:
        data = yaml.load(text, yaml.Loader)
        return cls(**data)
