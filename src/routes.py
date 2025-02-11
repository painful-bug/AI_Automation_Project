from flask import Blueprint, request, jsonify, send_file
from helpers import  get_func_name
from tasks import *
routes = Blueprint("routes", __name__)


@routes.route("/run", methods=["GET", "POST"])
def run():
    task = request.args.get("task")
    try:
        res = get_func_name(task)
        func_name = res["func_name"]
        args = res.get("arguments", [])
        print("ARGUMENTS : ", args)
        try:
            if args:
                generated_func = globals()[func_name](*args)
            else:
                generated_func = globals()[func_name]()
            print(generated_func)
            res = f"{func_name} executed successfully"
        except Exception as e:
            res = None
            print("error executing function : ", e)
    except Exception as e:
        res = None
        print("error retrieving data from API Call : ", e)
    return jsonify(res)
