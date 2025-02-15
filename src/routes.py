from flask import Blueprint, request, jsonify, send_file
# from helpers import  get_func_name
# from tasks import *
# routes = Blueprint("routes", __name__)
# import json

# @routes.route("/run", methods=["GET", "POST"])
# def run():
#     task = request.args.get("task")
#     try:
#         res = get_func_name(task)
#         func_name = res["func_name"]
#         args = res.get("arguments", [])
#         print("FUNCTION NAME : ", func_name)
#         print("ARGUMENTS : ", (args))
#         merged_args = {}
#         for d in args:
#             merged_args.update(d)
#         # merged_args = str(merged_args)
#         print("MERGED ARGUMENTS : ",merged_args)
#         try:
#             if merged_args:
#                 # args = json.loads(args)
#                 # print("DB CONFIG : ", args[0])
#                 # if 'db_path' in args[0].keys():
#                 # # Extract values from the dictionaries
#                 #         db_config = args[0]  # First dictionary with db_path and db_type
#                 #         query = args[1]['query']  # Second dictionary with query
#                 #         generated_func = globals()[func_name](
#                 #             db_path=db_config['db_path'],
#                 #             db_type=db_config['db_type'],
#                 #             query=query
#                 #         )
#                 # else:
#                 generated_func = globals()[func_name](**list(merged_args))

#             else:
#                 generated_func = globals()[func_name]()
#             print(generated_func)
#             res = f"{func_name} executed successfully"
#         except Exception as e:
#             res = None
#             print("error executing function : ", e)
#     except Exception as e:
#         res = None
#         print("error retrieving data from API Call : ", e)
#     return jsonify(res)
from helpers import get_func_name
from tasks import *  # Assuming the functions are defined here

routes = Blueprint("routes", __name__)

@routes.route("/run", methods=["GET", "POST"])
def run():
    task = request.args.get("task")

    try:
        # Retrieve function name and arguments
        res = get_func_name(task)
        func_name = res["func_name"]
        args = res.get("arguments", [])

        print("FUNCTION NAME: ", func_name)
        print("ARGUMENTS: ", args)

        # Merge the argument dictionaries into one
        merged_args = {}
        for d in args:
            if isinstance(d, dict):
                merged_args.update(d)

        print("MERGED ARGUMENTS: ", merged_args)

        # Attempt to call the function with the merged arguments
        try:
            if merged_args:
                # Dynamically call the function with **merged_args
                generated_func = globals()[func_name](**merged_args)
            else:
                # Call the function without arguments
                generated_func = globals()[func_name]()

            print(generated_func)
            res = f"{func_name} executed successfully"

        except Exception as e:
            res = None
            print("Error executing function: ", e)

    except Exception as e:
        res = None
        print("Error retrieving data from API call: ", e)

    return jsonify(res)
