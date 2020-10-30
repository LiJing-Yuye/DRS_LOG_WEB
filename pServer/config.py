DB_CONFIG = {
    "RedShift": {
        "Prod": {
            "dbname": "fp2fullprod",
            "host": "fp2-redshift-cluster.c2nwpm4iszlv.ap-northeast-1.redshift.amazonaws.com",
            "user": "dradmin",
            "pwd": "TrendRedshiftPWDmac8.6#1..",
            "port": "3389"
        },
        "Beta": {
            "dbname": "fp2fullbeta",
            "host": "fp2-redshift-cluster.c2nwpm4iszlv.ap-northeast-1.redshift.amazonaws.com",
            "user": "dradmin",
            "pwd": "TrendRedshiftPWDmac8.6#1..",
            "port": "3389"
        }

    },
    "Athena": {
        "Prod": {
            "profile_name": "Athena-Prod",
            "bucket": 'fp2-athena',
            "bucket_path": "test",
            "database": "fp2_prod_last_month_raw_log",
            "table_name": "drs2_core_prod_stream"
        },
        "Beta": {
            "profile_name": "Athena-Beta",
            "bucket": 'drs-athena-results',
            "bucket_path": "test",
            "database": "fp2_beta_last_month_raw_log",
            "table_name": "drs2_core_beta_stream"
        }

    }
}
