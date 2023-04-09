from collections.abc import Generator
from typing import TypeVar

ClassType = TypeVar("ClassType", bound=type)


def all_subclasses(cls: ClassType) -> Generator[ClassType, None, None]:
    for sub_cls in cls.__subclasses__():
        yield from all_subclasses(sub_cls)
        yield sub_cls


def all_non_abstract_sub_models(model_klass: ClassType) -> tuple[ClassType, ...]:
    return tuple(
        filter(
            lambda cls: not getattr(cls._meta, "abstract", None),
            all_subclasses(model_klass),
        )
    )
