
from flask import Flask, request, jsonify
from jsonschema import validate,Draft7Validator
from jsonschema.exceptions import ValidationError
from logging.config import dictConfig
import json
import os

from parsers import base_parser
from process_document import process_document


dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})


app = Flask('app')
schema_file='schemas/config_json.schema'


@app.route("/parse", methods=["POST"])
def parse_endpoint():
    app.logger.info('Processing request')

    # Load JSON schema file used for validation of inbound requests
    try:
        with open(schema_file) as json_file:
            json_schema = json.load(json_file)
    except:
        raise Exception('Error loading local application schema definition: ' + schema_file)

    # set input / output based on headers
    if 's3_input_file' in request.headers:
        input_file = request.headers['s3_input_file']
        input_type = 's3'
    elif 'local_input_file' in request.headers:
        input_file = request.headers['local_input_file']
        input_type = 'local'
    else:
        return jsonify({"message": "ERROR: either s3_input_file or local_input_file is required as a request header, please check your configuration"}), 400

    # set the output type based on the headers
    if 's3_output_path' in request.headers:
        output_path = request.headers['s3_output_path']
        output_type = 's3'
    elif 'local_output_path' in request.headers:
        output_path = request.headers['local_output_path']
        output_type = 'local'
    else:
        return jsonify({"message": "ERROR: either s3_output_path or local_output_path is required as a request header, please check your configuration"}), 400

    # set output format from the headers but default to JSON
    if 'output_format' in request.headers:
        output_format = request.headers['output_format']
    else:
        output_format = 'json'


    # set the schema based on request body JSON
    parse_config = request.json

    # validate request JSON against the application schema
    res, errors = validate_schema(schema=json_schema,json=parse_config)

    # If errors exist return to client
    if res == False:
        status = 400
        response = jsonify({
            'message': 'Sent schema JSON was invalid!',
            'errors': errors
        })

        response.status_code = status
        return response
    
    else:


        # process message using parameters
        success, output_path =  process_document(input_file, input_type, output_path, output_type, output_format, parse_config)


        if success:
            app.logger.info('Processing completed')
            return jsonify({"success": "Successfully parsed file " + input_file,
                            "output_location":  output_path} )

        else:
            app.logger.error('Processing failed')
            return jsonify({"error": "Error parsing file " + input_file})






def validate_schema(schema,json):
    validator = Draft7Validator(schema)
    
    error_list = [error.message for error in validator.iter_errors(json)]
    if error_list:
        return False, error_list
    else:
        return True, []


@app.errorhandler(ValidationError)
def validation_exception_handler(error):
    
    status = 400
    response = jsonify({
        'message': 'Sent schema JSON was invalid!',
        'errors': str(error.message) +  "path: " + str(error.relative_path) + str(error.relative_schema_path) + str(error.instance) })

    response.status_code = status
    return response



@app.errorhandler(base_parser.ParsingException)
def parsing_exception_handler(error):

    status = 500
    response = jsonify({
        'status': status,
        'message': 'Parsing Error',
        'errors': str(error.message)})

    response.status_code = status
    return response




if __name__ == "__main__":
    if "FLASK_DEBUG" in os.environ:
        app.run(debug=True, host="0.0.0.0")
    else:
         app.run(debug=False, host="0.0.0.0")