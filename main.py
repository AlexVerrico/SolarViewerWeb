import datetime
import io

import flask
import sqlite3
from matplotlib import pyplot as plt

from flask import request, Response
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

import config
from monitored_fields import monitored_fields

db_file = config.SQLITE_DB_PATH

app = flask.Flask(__name__)
@app.route('/')
def index():
    return flask.render_template('home.jinja', monitored_fields=monitored_fields)


@app.route('/data_viewer/<string:data_type>')
def data_viewer(data_type):
    now = datetime.datetime.utcnow().timestamp()
    limit = now - 24 * 60 * 60
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute(f"""SELECT * FROM main.inverter_records WHERE timestamp > {limit} AND data_type = '{data_type}' ORDER BY timestamp ASC""")
        data = cursor.fetchall()
    return flask.render_template('data_viewer.jinja', data_type=data_type, data=data, now=now)


@app.route('/graph/<string:data_type>')
def graph(data_type):
    if monitored_fields[data_type].get('graphable', False) is not True:
        return flask.abort(400)
    now = datetime.datetime.utcnow().timestamp()
    start_timestamp = request.args.get('start_timestamp', now - 24 * 60 * 60)
    end_timestamp = request.args.get('end_timestamp', now)
    granularity = request.args.get('granularity', 30 * 60)

    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute(f"""SELECT * FROM main.inverter_records WHERE timestamp > {start_timestamp} AND timestamp < {end_timestamp} AND data_type = '{data_type}' ORDER BY timestamp ASC""")
        data = cursor.fetchall()

    def transform_date(timestamp):
        x = datetime.datetime.fromtimestamp(timestamp) + datetime.timedelta(hours=10)
        y = x.isoformat().split('T')[1].rsplit(':', 1)[0]
        return y

    output = [
        (data[0][0], data[0][1], data[0][2], transform_date(data[0][0])),
    ]
    for row in data:
        if row[0] > output[-1][0] + granularity:
            output.append((row[0], row[1], row[2], transform_date(row[0])))


    fig = plt.figure(dpi=128, figsize=(16, 9))
    plt.title(data_type, fontsize=24)
    plt.plot([row[3] for row in output], [row[2] for row in output])
    for row in output:
        plt.annotate(xy=(transform_date(row[0]), row[2]), text=row[2])
    plt.ylim(monitored_fields[data_type]['limits']['min'], monitored_fields[data_type]['limits']['max'])
    plt.xlabel('Time', fontsize=16)
    plt.ylabel('Value', fontsize=16)
    plt.tick_params(axis='both', which='major', labelsize=6)
    plt.legend()

    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')



with sqlite3.connect(db_file) as _conn:
    _cursor = _conn.cursor()
    _cursor.execute("""SELECT * FROM main.db_version LIMIT 1""")
    version = _cursor.fetchone()[0]
    if version != 2:
        print(f'Invalid DB version {version}')
        exit(1)


if __name__ == '__main__':
    app.run(debug=config.SERVER_DEBUG, host=config.SERVER_HOST, port=config.SERVER_PORT)
