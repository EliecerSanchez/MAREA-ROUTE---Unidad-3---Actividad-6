"""Patron Command: acciones de navegacion encapsuladas con soporte de undo."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List, Optional

from .routing import RouteStrategy

if TYPE_CHECKING:
    from .facade import Navigator


class Command(ABC):
    """Interfaz comun para comandos de navegacion (execute / undo)."""

    label: str = "comando"

    @abstractmethod
    def execute(self) -> None:
        ...

    @abstractmethod
    def undo(self) -> None:
        ...


class ChangeDestinationCommand(Command):
    """Establece un nuevo origen/destino; al deshacer restaura el anterior."""

    label = "cambiar destino"

    def __init__(self, navigator: "Navigator", start: str, end: str):
        self._navigator = navigator
        self._start = start
        self._end = end
        self._prev_start = navigator.position
        self._prev_end = navigator.destination
        self._prev_route = navigator.route

    def execute(self) -> None:
        self._navigator.set_destination(self._start, self._end)

    def undo(self) -> None:
        self._navigator.restore(self._prev_start, self._prev_end, self._prev_route)


class RerouteCommand(Command):
    """Recalcula la ruta con una estrategia; al deshacer vuelve a la ruta anterior."""

    label = "replanificar ruta"

    def __init__(self, navigator: "Navigator", strategy: Optional[RouteStrategy] = None):
        self._navigator = navigator
        self._strategy = strategy
        self._prev_route = navigator.route
        self._prev_strategy = navigator.planner.strategy
        self._had_strategy_change = strategy is not None

    def execute(self) -> None:
        self._navigator.reroute(self._strategy)

    def undo(self) -> None:
        if self._had_strategy_change:
            self._navigator.planner.set_strategy(self._prev_strategy)
        self._navigator.set_route(self._prev_route, planner_flag=False)


class CommandHistory:
    """Pila de comandos ejecutados con soporte de deshacer."""

    def __init__(self) -> None:
        self._stack: List[Command] = []

    def execute(self, command: Command) -> None:
        command.execute()
        self._stack.append(command)

    def undo(self) -> Optional[Command]:
        if not self._stack:
            return None
        command = self._stack.pop()
        command.undo()
        return command

    @property
    def size(self) -> int:
        return len(self._stack)

    @property
    def can_undo(self) -> bool:
        return bool(self._stack)

    def __repr__(self) -> str:
        labels = [c.label for c in self._stack]
        return f"CommandHistory({labels})"