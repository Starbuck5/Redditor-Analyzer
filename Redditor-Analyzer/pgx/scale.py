import pygame

from typing import List


class scale:
    _resolution = []
    _global_scale = 1
    _global_offset = [0, 0]
    _mode = "manual"
    _modes = set(["none", "center", "full", "manual"])

    @staticmethod
    def get_mode() -> str:
        """Get the scaling mode."""
        return scale._mode

    @staticmethod
    def set_mode(mode: str) -> None:
        """Change the scaling mode."""
        if mode in scale._modes:
            if mode != scale._mode:
                scale._mode = mode
                scale.apply()
        else:
            raise ValueError(f"'{mode}' not a valid scaling mode: {scale._modes}")

    @staticmethod
    def apply() -> None:
        """Tell pgx to apply the current scaling mode."""
        mode = scale.get_mode()
        screen_size = pygame.display.get_surface().get_size()
        native_res = scale.get_resolution()

        if mode == "manual":
            return

        if mode == "none":
            scalar = 1
            adjustments = [0, 0]

        elif mode == "center":
            scalar = 1
            adjustments = [(screen_size[i] - native_res[i]) / 2 for i in range(2)]

        elif mode == "full":
            xandy = [screen_size[i] / native_res[i] for i in range(2)]
            scalar = min(xandy)

            xandy = [num / scalar for num in xandy]
            adjustments = [
                (xandy[i] - 1) / 2 * screen_size[i] / xandy[i] for i in range(2)
            ]

        scale.set_scalar(scalar)
        scale.set_offset(adjustments)

    @staticmethod
    def get_resolution() -> List[int]:
        """The resolution pgx considers the base resolution."""
        return scale._resolution

    @staticmethod
    def set_resolution(res: List[int]) -> None:
        """Change resolution pgx considers the base resolution."""
        scale._resolution = list(res)

    @staticmethod
    def get_scalar() -> float:
        """Global UI element scalar."""
        return scale._global_scale

    @staticmethod
    def set_scalar(scalar: float) -> None:
        """Change global UI element scalar."""
        if scalar <= 0.05:
            raise ValueError("pgx global scale has to be greater than 0.05")
        scale._global_scale = scalar

    @staticmethod
    def get_offset() -> List[int]:
        """Global UI element position offset."""
        return scale._global_offset

    @staticmethod
    def set_offset(offset: List[int]) -> None:
        """Change global UI element position offset."""
        scale._global_offset = list(offset)
