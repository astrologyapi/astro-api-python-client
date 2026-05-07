"""SDK surface discovery and deterministic invocation planning."""

from __future__ import annotations

import inspect
from datetime import datetime
from typing import Any

from ..models import BirthData, NumeroData, PDFBranding
from ..namespaces import (
    ChineseNamespace,
    HoroscopesNamespace,
    KPNamespace,
    LalKitabNamespace,
    LocationNamespace,
    NumerologyNamespace,
    PDFNamespace,
    TarotNamespace,
    VedicNamespace,
    WesternNamespace,
    WesternTransitNamespace,
)
from .http_capture import serialize_value
from .models import InvocationPlan
from .test_data import (
    ScenarioBundle,
    birth_from_raw,
    branding_from_raw,
    numero_from_raw,
)

PATH_PARAMETER_NAMES = {
    "planet",
    "chart_id",
    "zodiac",
    "partner_zodiac",
    "maha_dasha",
    "antar_dasha",
    "pratyantar_dasha",
    "sookshma_dasha",
}


def build_module_registry(http_client: Any) -> dict[str, Any]:
    """Instantiate the namespace registry used by inventory and live runners."""
    pdf_namespace = PDFNamespace(http_client)
    return {
        "vedic": VedicNamespace(http_client),
        "western": WesternNamespace(http_client),
        "kp": KPNamespace(http_client),
        "lal_kitab": LalKitabNamespace(http_client),
        "horoscopes": HoroscopesNamespace(http_client),
        "numerology": NumerologyNamespace(http_client),
        "western_transit": WesternTransitNamespace(http_client),
        "tarot": TarotNamespace(http_client),
        "chinese": ChineseNamespace(http_client),
        "location": LocationNamespace(http_client),
        "pdf.vedic": pdf_namespace.vedic,
        "pdf.western": pdf_namespace.western,
    }


def _module_methods(module: Any) -> list[str]:
    return sorted(
        name
        for name, value in inspect.getmembers(module, predicate=callable)
        if not name.startswith("_")
    )


def _birth_for_name(scenarios: ScenarioBundle, raw: dict[str, Any]) -> BirthData:
    return birth_from_raw(raw)


def _value_for_parameter(
    module_name: str,
    method_name: str,
    parameter: inspect.Parameter,
    scenarios: ScenarioBundle,
) -> Any:
    """Map a method parameter to the canonical shared QA scenarios."""
    name = parameter.name
    annotation = parameter.annotation
    current_year = datetime.now().year

    if name == "male":
        return _birth_for_name(scenarios, scenarios.match["male"])
    if name == "female":
        return _birth_for_name(scenarios, scenarios.match["female"])
    if name == "person1":
        return _birth_for_name(scenarios, scenarios.couple["person1"])
    if name == "person2":
        return _birth_for_name(scenarios, scenarios.couple["person2"])
    if name == "branding" or annotation is PDFBranding:
        return branding_from_raw(scenarios.pdf_branding)
    if annotation is NumeroData:
        if "alternate" in method_name:
            return numero_from_raw(scenarios.numerology_secondary)
        return numero_from_raw(scenarios.numerology_primary)
    if annotation is BirthData or name == "data":
        return _birth_for_name(scenarios, scenarios.birth_primary)
    if name == "name":
        if module_name == "pdf.vedic" and method_name == "get_match_making":
            return scenarios.match.get("name")
        if module_name == "pdf.western" and method_name == "get_synastry":
            return scenarios.couple.get("name")
        return scenarios.birth_primary.get("name")
    if name == "partner_name":
        if module_name == "pdf.vedic":
            return scenarios.match.get("partner_name")
        return scenarios.couple.get("partner_name")
    if name == "place":
        if module_name == "pdf.vedic" and method_name == "get_match_making":
            return scenarios.match.get("male", {}).get("place") or scenarios.match.get("place")
        if module_name == "pdf.western" and method_name == "get_synastry":
            return scenarios.couple.get("person1", {}).get("place") or scenarios.couple.get("place")
        if module_name == "location":
            return scenarios.birth_primary.get("place")
        return scenarios.birth_primary.get("place")
    if name == "partner_place":
        if module_name == "pdf.vedic":
            return scenarios.match.get("female", {}).get("place")
        return scenarios.couple.get("person2", {}).get("place")
    if name == "full_name":
        return scenarios.birth_primary.get("name")
    if name == "gender":
        return scenarios.birth_primary.get("gender", "male")
    if name == "language":
        return "en"
    if name == "solar_year":
        return current_year
    if name == "varshaphal_year":
        return current_year
    if name == "year":
        if module_name == "western" and method_name.startswith("get_solar_return_"):
            return None
        if module_name == "location" and method_name == "get_timezone":
            return scenarios.birth_primary["year"]
        return current_year
    if name == "year_count":
        if module_name == "vedic" and method_name.startswith("get_varshaphal_"):
            return None
        return current_year - scenarios.birth_primary["year"]
    if name == "zodiac":
        return scenarios.zodiac["primary"]["zodiac"]
    if name == "partner_zodiac":
        return scenarios.zodiac["primary"]["partnerZodiac"]
    if name == "chart_id":
        return "D1"
    if name == "planet":
        return "sun"
    if name == "maha_dasha":
        if method_name == "get_sub_char_dasha":
            return scenarios.zodiac["primary"]["zodiac"].upper()
        return "MOON"
    if name == "antar_dasha":
        return "SATURN"
    if name == "pratyantar_dasha":
        return "MARS"
    if name == "sookshma_dasha":
        return "JUPITER"
    if name == "date":
        return scenarios.birth_primary["day"]
    if name == "max_rows":
        return 6
    if name == "day":
        return scenarios.birth_primary["day"]
    if name == "month":
        return scenarios.birth_primary["month"]
    if name == "hour":
        return scenarios.birth_primary["hour"]
    if name == "min":
        return scenarios.birth_primary["min"]
    if name == "lat":
        return scenarios.birth_primary["lat"]
    if name == "lon":
        return scenarios.birth_primary["lon"]
    if name == "tarot_id":
        return 5
    if name == "love":
        return 12
    if name == "career":
        return 23
    if name == "finance":
        return 45
    if name == "aspects":
        return True
    if name == "ayanamsha":
        return "LAHIRI"
    if name in {"ashtakoot", "papasyam", "dashakoot"}:
        return True
    if name == "timezone":
        return scenarios.birth_primary["tzone"]

    if parameter.default is not inspect._empty:
        return parameter.default

    raise ValueError(
        f"No invocation mapping for {module_name}.{method_name} parameter `{name}`"
    )


def _build_plan_for_method(
    module_name: str,
    method_name: str,
    method: Any,
    scenarios: ScenarioBundle,
) -> InvocationPlan:
    signature = inspect.signature(method)
    args: list[Any] = []
    kwargs: dict[str, Any] = {}
    path_values: dict[str, Any] = {}
    parameter_names: list[str] = []

    for parameter in signature.parameters.values():
        parameter_names.append(parameter.name)
        value = _value_for_parameter(module_name, method_name, parameter, scenarios)
        if parameter.name in PATH_PARAMETER_NAMES:
            path_values[parameter.name] = value

        if parameter.kind in (
            inspect.Parameter.POSITIONAL_ONLY,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
        ):
            args.append(value)
        elif parameter.kind is inspect.Parameter.KEYWORD_ONLY:
            kwargs[parameter.name] = value

    return InvocationPlan(
        target=f"{module_name}.{method_name}",
        module_name=module_name,
        method_name=method_name,
        args=args,
        kwargs=kwargs,
        path_values=path_values,
        parameter_names=parameter_names,
    )


def build_invocation_plans(scenarios: ScenarioBundle) -> list[InvocationPlan]:
    """Build one deterministic invocation plan per public SDK method."""
    registry = build_module_registry(http_client=object())
    plans: list[InvocationPlan] = []
    for module_name, module in registry.items():
        for method_name in _module_methods(module):
            method = getattr(module, method_name)
            plans.append(
                _build_plan_for_method(
                    module_name,
                    method_name,
                    method,
                    scenarios,
                )
            )
    return plans


def execute_plan(plan: InvocationPlan, registry: dict[str, Any]) -> Any:
    """Execute an invocation plan against a live or stub namespace registry."""
    method = getattr(registry[plan.module_name], plan.method_name)
    return method(*plan.args, **plan.kwargs)


def serialize_plan_args(plan: InvocationPlan) -> dict[str, Any]:
    """Serialize invocation args for debug output and request captures."""
    payload: dict[str, Any] = {}
    for index, value in enumerate(plan.args):
        key = plan.parameter_names[index]
        payload[key] = serialize_value(value)
    for key, value in plan.kwargs.items():
        payload[key] = serialize_value(value)
    return payload
