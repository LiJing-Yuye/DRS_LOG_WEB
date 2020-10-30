import boto3
import pandas as pd
import base64
import io
import zipfile
import time


def unzip_string(buf):
    buf = base64.b64decode(buf)
    in_ = io.BytesIO()
    in_.write(buf)
    in_.seek(0)
    with zipfile.ZipFile(file=in_) as zf:
        filename = zf.namelist()[0]
        result = zf.read(filename)

    final_result = None
    try:
        final_result = result.decode("utf-8")
    except:
        final_result = str(result)
    return final_result


class AthenaWrapper():
    def __init__(self, profile_name="Athena", bucket="drs-athena-results", path="test"):
        session = boto3.Session(profile_name=profile_name)
        self.output_bucket = bucket
        self.bucket_path = path
        self.athena = session.client('athena')
        self.s3 = session.client('s3')

    def get_s3_file(self, key):
        print("Get S3 File, Key: [{}]".format(key))
        obj = self.s3.get_object(Bucket=self.output_bucket, Key=key)['Body'].read().decode("utf-8")
        df = pd.read_csv(io.StringIO(obj))
        return df

    def exec_query(self, sql, database):
        response = self.athena.start_query_execution(
            QueryString=sql,
            QueryExecutionContext={
                'Database': database
            },
            ResultConfiguration={
                'OutputLocation': 's3://{}/{}'.format(self.output_bucket, self.bucket_path)
            },
            WorkGroup='primary')

        execution_id = response['QueryExecutionId']
        if execution_id:
            while True:
                stats = self.athena.get_query_execution(QueryExecutionId=execution_id)
                status = stats['QueryExecution']['Status']['State']
                if status in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
                    break
                time.sleep(0.2)  # 200ms

            if status == 'SUCCEEDED':
                return self.get_s3_file('{}/{}.csv'.format(self.bucket_path, execution_id))
            if status == 'FAILED':
                raise Exception(stats['QueryExecution']['Status']['StateChangeReason'])


if __name__ == '__main__':
    SQL = """SELECT raw_log_base64_zip FROM drs2_core_prod_stream  WHERE
                year = 2020 AND month = 9 AND day = 5 AND hour= 10
                AND req_env is NOT null
                AND req_env.s_guid = '69a888e2-bf71-474b-834f-5ccd806b65c9'
                limit 1
            """

    ATHENA_CONFIG = {
        "database": "fp2_prod_last_month_raw_log",
        "staging-s3": "s3://drs-athena-results/"
    }

    at = AthenaWrapper("Athena-Prod", "fp2-athena", "query-results")
    # at.get_s3_file('89cd34bc-79f4-4609-9cd2-516ac9a3b1be.csv')
    print(at.exec_query(SQL, ATHENA_CONFIG.get("database")))
