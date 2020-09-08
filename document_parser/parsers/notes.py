input = FileInput()


input.read_s3_file("s3://safari-dev-assets/glue/jobs/scripts/safari-jb-enriched-matching-input-P-GENERIC.py")
input.read_local_file('test')



apt install python3-tk ghostscript