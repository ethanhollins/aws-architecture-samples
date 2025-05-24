from typing import Callable
from aws_cdk import App


def topic(
    expected_topic: str,
) -> Callable[[Callable[[App], None]], Callable[[App], None]]:
    def decorator(register_fn: Callable[[App], None]) -> Callable[[App], None]:
        def wrapper(app: App):
            selected_topic = app.node.try_get_context("topic")
            if selected_topic is None or selected_topic == expected_topic:
                register_fn(app)

        return wrapper

    return decorator
