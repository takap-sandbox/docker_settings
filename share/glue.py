import sys
import json
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions

job_params = [
    'JOB_NAME',
]

args = getResolvedOptions(sys.argv, job_params)

# ローカルs3を対象にするため、hadoopにendpointの設定を行う
sc = SparkContext()
sc._jsc.hadoopConfiguration().set("fs.s3a.endpoint", "http://localstack:4572")
sc._jsc.hadoopConfiguration().set("fs.s3a.path.style.access", "true")
sc._jsc.hadoopConfiguration().set("fs.s3a.signing-algorithm", "S3SignerType")

glue_context = GlueContext(sc)
spark = glue_context.spark_session
job = Job(glue_context)
job.init(args['JOB_NAME'], args)

dyf = glue_context.create_dynamic_frame.from_options(
    connection_type="s3",
    connection_options={
        "paths": ["s3a://test-csv/"]
    },
    format="csv",
    format_options={
        "withHeader": True
    },
)

# ここでdyfに対して何かしら処理をする

glue_context.write_dynamic_frame.from_options(
    frame=dyf,
    connection_type="s3",
    connection_options={
        "path": "s3a://test-csv/write/"
    },
    format='csv'
)

job.commit()