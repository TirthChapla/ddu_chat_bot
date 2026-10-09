"""Backend package.

The application is imported lazily so ``python -m backend.main`` does not
execute ``backend.main`` once as package initialization and again as
``__main__``.
"""

__all__ = ["app"]


def __getattr__(name):
	if name == "app":
		from .main import app

		return app
	raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
