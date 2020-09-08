# DocumentParser
Aston University Final Project - Document Parsing Microservice

Requirements to run the code locally:
- Python 3.6
- Pip
- Packages outlined in the requirements.txt

Requirements to run the parsing pipeline using Docker:
- Docker
- Docker Compose (optional if using the compose file)


### Docker build command
From the root of the repo execute the following command
```docker build -f docker/Dockerfile -t document_parser .```


### Starting the container
Change directory to the docker directory and run `docker-compose up -d`

Application logs can then be accessed by running `docker logs -f docker_dp_1`

Debug mode can be enabled by setting the `FLASK_DEBUG` environment variable to any value


### API Header Options
    - output_format: currently only `json` is supported as a valid output format

    - local_output_path
    - local_input_file
    or 
    - s3_input_file
    - s3_output_path


#### Using AWS S3
In order to utilise the S3 read/write capabilities of the document parser AWS credentials with the correct IAM access need to be made available to the container.

- The `docker-compose.yml` contains placeholders for access keys
- Requests to the API must use the relevant s3 request headers:

    ```
    s3_input_file: s3://a_bucket/a.pdf
    s3_output_path: s3://a_bucket/output_files/
    ```




### Using the sample PDF

- accompanying files are available in the `sample_pdf` directory]
- `sample.pdf` is a PDF file containing a table as well as text data
- `sample_annotated.pdf` is an example of annotations that can be included on the PDF file. annotation comments must be key/value pairs in the form `key : value` on their unique line
- Running the `annotation_extractor.py` script with the sample annotated PDF will produce some text (`sample_extracted_annotations`) that can then be used to start building the JSON schema files like the example `sample_schema.json`.
  This schema defines a table with headings and a text element to be extracted
- To run this schema and file with the docker-compose file the following steps are required:
    - copy the PDF file to the `input` directory inside the `docker` top-level directory
    - Run the CURL command from a terminal, ensuring the JSON schema is updated if appropriate:
        ```
        curl --location --request POST 'http://localhost:5000/parse' \
        --header 'Content-Type: application/json' \
        --header 'local_input_file: sample.pdf' \
        --header 'output_format: json' \
        --header 'local_output_path: /app/output_files/' \
        --data-raw '{
            "type": "pdf",
            "schema_name": "Sample PDF Schema",
            "tables": [
                {
                    "id": "fuel_savings",
                    "type": "lattice",
                    "fields": ["cycle_name","KI","distance_mi","improved_speed","decreased_acce","eliminate_stops","decreased_idle"],
                    "sections": [
                        {
                            "pages": "1",
                            "header": "Y",
                            "table_region": "102.26399993896484,242.67901611328125,506.46600341796875,108.1519775390625"
                        }
                    ]
                }
            ],
            "text": [
                {
                    "id": "doc_title",
                    "type": "area",
                    "sections": [
                        {
                            "pages": "1",
                            "text_region": "44.66379928588867,766.3179931640625,554.9019775390625,680.2269897460938"
                        }
                    ]
                }
            ]
        }'
        ```
    - The request should return the following response:
        ```
        {"output_location":"/app/output_files/","success":"Successfully parsed file sample.pdf"}
        ```
    - Output JSON files should be available in the `output` directory