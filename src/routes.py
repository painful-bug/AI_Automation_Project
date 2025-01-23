from flask import Blueprint, request, jsonify, send_file
from app.helpers import execute_task

routes = Blueprint("routes", __name__)


@routes.route("/run", methods=["GET", "POST"])
def run():
    task = request.args.get("task")
    try:
        res = execute_task(task)
    except Exception as e:
        res = None
        print("error : ", e)
    return jsonify(res)
