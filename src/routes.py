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
from agent import AIAgent
import os
from transcriber import transcriber

agent = AIAgent()
routes = Blueprint("routes", __name__)

# @routes.route("/run", methods=["GET", "POST"])
# def run():
#     task = request.args.get("task")

#     try:
#         # Retrieve function name and arguments
#         res = get_func_name(task)
#         func_name = res["func_name"]
#         args = res.get("arguments", [])

#         print("FUNCTION NAME: ", func_name)
#         print("ARGUMENTS: ", args)

#         # Merge the argument dictionaries into one
#         merged_args = {}
#         for d in args:
#             if isinstance(d, dict):
#                 merged_args.update(d)

#         print("MERGED ARGUMENTS: ", merged_args)

#         # Attempt to call the function with the merged arguments
#         try:
#             if merged_args:
#                 # Dynamically call the function with **merged_args
#                 print("CALLING FUNCTION WITH MERGED ARGUMENTS")
#                 generated_func = globals()[func_name](**merged_args)
#             elif args:
#                 print("CALLING FUNCTION WITH ARGUMENTS")
#                 generated_func = globals()[func_name](*args)
#             else:
#                 # Call the function without arguments
#                 print("CALLING FUNCTION WITHOUT ARGUMENTS")
#                 generated_func = globals()[func_name]()

#             print(generated_func)
#             res = f"{func_name} executed successfully"

#         except Exception as e:
#             res = None
#             print("Error executing function: ", e)

#     except Exception as e:
#         res = None
#         print("Error retrieving data from API call: ", e)
#         print("SENDIN G TO AGENT")

#         return jsonify(res)

def run_agent(task):
    try:
        check_audio_payload = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "system", "content": """You are given a task {{task}}.Check if the task requires audio transcription If yes, return this python dictionary : {"is_audio": true, "file_path": "{{relative path of the audio file}}"}; otherwise, return {"is_audio": false, "file_path": null}."""}, {"role": "user", "content": task}]
        }
        d = request_ai_proxy(payload=check_audio_payload)
        print(" D: ", d)
        d = json.loads(d)
        is_audio_file, audio_file_path = d.values()
        print("IS_AUDIO_FILE : ", is_audio_file)
        print("AUDIO FILE PATH : ", audio_file_path)
        if bool(is_audio_file) and audio_file_path is not None:
            transcriber(audio_file_path)
        else:
            print("Task does not require audio transcription. Running the normal agent!")
            result = agent.run_task(task)
            print(result)
    except Exception as e:
        print(f"An error occurred: {str(e)}")

@routes.route("/run", methods=["GET", "POST"])
def run():
    task = request.args.get("task")
    res = None  # Initialize response variable

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
                print("CALLING FUNCTION WITH MERGED ARGUMENTS")
                generated_func = globals()[func_name](**merged_args)
            elif args:
                print("CALLING FUNCTION WITH ARGUMENTS")
                generated_func = globals()[func_name](*args)
            else:
                # Call the function without arguments
                print("CALLING FUNCTION WITHOUT ARGUMENTS")
                generated_func = globals()[func_name]()

            output = generated_func
            if output:
                print(output)
                res = output
            else:
                res = f"{func_name} executed successfully"

        except Exception as e:
            res = f"Error executing function: {str(e)}"
            print(res)

    except Exception as e:
        res = f"Error retrieving data from API call: {str(e)}"
        print(res)
        print("SENDING TO AGENT")
        res = run_agent(task)

    # Always return a JSON response
    return jsonify({"result": res})

@routes.route("/read", methods=["GET", "POST"])
def read():
    path = request.args.get("path")
    if os.path.exists(path):
        with open(path, "r") as f:
            content = f.read()
            return content
    else:
        return "File does not exist", 404