from flask import Flask
import models
import json

app = Flask(__name__)

@app.route('/v1/recent')
def recent():
    evs = models.Event.query.order_by(models.Event.time.desc()).limit(10).all()
    resp_list = []
    for ev in evs:
        resp_list.append({
            'id': ev.id,
            'type': {
                'id': ev.type.id,
                'name': ev.type.name,
                'source': {
                    'id': ev.type.source.id,
                    'name': ev.type.source.name,
                }
            },
            'time': str(ev.time),
            'properties': json.loads(ev.properties)
        })
    return json.dumps(resp_list)

if __name__ == '__main__':
    app.run(debug=True)

