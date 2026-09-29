from flask import Flask, jsonify, request

app = Flask(__name__)


# Simulated data
class Event:
    def __init__(self, id, title):
        self.id = id
        self.title = title

    def to_dict(self):
        return {"id": self.id, "title": self.title}


events = [
    Event(1, "Tech Meetup"),
    Event(2, "Python Workshop")
]


def _get(item, field):
    """Read a field from an Event object or a dict."""
    return item[field] if isinstance(item, dict) else getattr(item, field)


def find_event(event_id):
    """Return the event with the given id, or None if it doesn't exist."""
    return next((e for e in events if _get(e, "id") == event_id), None)


def get_valid_title():
    """
    Read and validate 'title' from the JSON body.
    Returns (title, error_response). Exactly one of them is None.
    """
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return None, (jsonify({"error": "Request body must be valid JSON"}), 400)

    title = data.get("title")
    if not isinstance(title, str) or not title.strip():
        return None, (jsonify({"error": "'title' is required and must be a non-empty string"}), 400)

    return title.strip(), None


# POST /events - Create a new event from JSON input
@app.route("/events", methods=["POST"])
def create_event():
    title, error = get_valid_title()
    if error:
        return error

    new_id = max((_get(e, "id") for e in events), default=0) + 1
    event = Event(new_id, title)
    events.append(event)

    return jsonify(event.to_dict()), 201


# PATCH /events/<id> - Update the title of an event
@app.route("/events/<int:event_id>", methods=["PATCH"])
def update_event(event_id):
    event = find_event(event_id)
    if event is None:
        return jsonify({"error": f"Event with id {event_id} not found"}), 404

    title, error = get_valid_title()
    if error:
        return error

    if isinstance(event, dict):
        event["title"] = title
        return jsonify(event), 200

    event.title = title
    return jsonify(event.to_dict()), 200


# DELETE /events/<id> - Remove an event from the list
@app.route("/events/<int:event_id>", methods=["DELETE"])
def delete_event(event_id):
    event = find_event(event_id)
    if event is None:
        return jsonify({"error": f"Event with id {event_id} not found"}), 404

    events.remove(event)
    return "", 204


if __name__ == "__main__":
    app.run(debug=True)
