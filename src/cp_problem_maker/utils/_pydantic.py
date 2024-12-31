import json
from pathlib import Path
from typing import Any, Mapping, TypeGuard, TypeVar

import tomllib
import yaml
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def read_file_as_dict(file_path: Path) -> dict[str, Any]:
    """Read a file and return its content as a dictionary.

    Supported file types are .toml, .yaml, and .json.

    Args:
        file_path (Path): Path to the file to read
    Returns:
        dict[str, Any]: Content of the file as a dictionary
    """
    with file_path.open(mode="rb") as fp:
        if file_path.suffix == ".toml":
            return tomllib.load(fp)
        elif file_path.suffix == ".yaml":
            return yaml.safe_load(fp)  # type: ignore
        elif file_path.suffix == ".json":
            return json.load(fp)  # type: ignore
        else:
            raise ValueError(f"Unsupported file type for file {file_path}")


def load_model_from_file(model: type[T], file_path: Path, *, strict: bool) -> T:
    """Load a file into a model.

    Args:
        model (type[T]): Model to load the file into
        file_path (Path): Path to the file to load
        strict (bool): Whether to strictly validate the model
    Returns:
        T: Model loaded from the file
    """
    return model.model_validate(read_file_as_dict(file_path), strict=strict)


def load_model_from_object(
    model: type[T], obj: Mapping[str, Any], *, strict: bool
) -> T:
    """Load an object into a model.

    Args:
        model (type[T]): Model to load the object into
        obj (Mapping[str, Any]): Object to load
        strict (bool): Whether to strictly validate the model
    Returns:
        T: Model loaded from the object
    """
    return model.model_validate(obj, strict=strict)


def load_model(model: type[T], src: Any, *, strict: bool) -> T:
    """Load a source into a model.

    Supported source types are Path, str, and Mapping.

    Args:
        model (type[T]): Model to load the source into
        src (Any): Source to load
        strict (bool): Whether to strictly validate the model
    Returns:
        T: Model loaded from the source
    """
    if isinstance(src, Path):
        return load_model_from_file(model, src, strict=strict)
    elif isinstance(src, Mapping):
        return load_model_from_object(model, src, strict=strict)
    else:
        raise ValueError(
            f"Unsupported source type {type(src)}. Must be Path, str, or Mapping"
        )


def update_model(model: BaseModel, update_dict: dict[str, Any]) -> None:
    """Update a model with a dictionary.

    Note that this function modifies the model in place.

    Args:
        model (BaseModel): Model to update
        update_dict (dict[str, Any]): Dictionary to update the model with
    """
    for key, value in update_dict.items():
        curr_value = getattr(model, key)
        if isinstance(curr_value, BaseModel):
            update_model(curr_value, value)
        else:
            setattr(model, key, value)


class ModelAttributeAccessor:
    """Utility class to access nested attributes of a model."""

    @staticmethod
    def _is_branch(node: Any) -> TypeGuard[BaseModel]:
        return isinstance(node, BaseModel)

    @staticmethod
    def _is_leaf(node: Any) -> bool:
        return not ModelAttributeAccessor._is_branch(node)

    @staticmethod
    def get_attr(model: BaseModel, keys: list[str]) -> Any:
        """Get a nested attribute of a model.

        Args:
            model (BaseModel):
                Model to get the attribute from
            keys (list[str]):
                List of keys to get the attribute.
        Returns:
            Any: Attribute of the model
        Raises:
            AttributeError: If the attribute is not found
        Examples:
            >>> model = Model(a=Model(b=Model(c=1)))
            >>> ModelAttributeAccessor.get_attr(model, ["a", "b", "c"])
            1
        """
        model_type = type(model)
        for i, key in enumerate(keys):
            if ModelAttributeAccessor._is_leaf(model):
                leaf_type = type(model)
                path = ".".join(keys[:i])
                raise AttributeError(f"'{model_type}.{path}' is of type '{leaf_type}'.")
            model = getattr(model, key)
        return model
