# state.py
import db


def get_current_state():
    topic, step = db.get_latest_state()
    return {
        "topic": topic,
        "step": step
    }


def advance_state(content):
    state = get_current_state()
    db.save_learning_state(
        topic=state["topic"],
        step=state["step"] + 1,
        content=content
    )
