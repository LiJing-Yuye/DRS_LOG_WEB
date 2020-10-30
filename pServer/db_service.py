from utils.RedshiftWrapper import RedShiftWrapper
from utils.AthenaWrapper import AthenaWrapper, unzip_string
from config import DB_CONFIG
import traceback
from datetime import datetime, timedelta

REDSHIFT_CONFIG = DB_CONFIG['RedShift']
ATHENA_CONFIG = DB_CONFIG['Athena']

IDENTITY_NAME_MAPPING = {}


def set_identity_name():
    global IDENTITY_NAME_MAPPING

    sql = "select * from public.identify_from_name"

    try:
        name_list = RedShiftWrapper.query_with_sql(sql, REDSHIFT_CONFIG['Beta'])
        for name in name_list:
            IDENTITY_NAME_MAPPING[name['id']] = name['identify_from_name']
    except:
        raise Exception(traceback.format_exc())


def get_all_table(server):
    table_list = []
    sql = "select distinct(schemaname) from pg_tables where schemaname like 'y%m%'"

    try:
        tables = RedShiftWrapper.query_with_sql(sql, REDSHIFT_CONFIG[server])
        for table in tables:
            table_list.append(table['schemaname'])
    except:
        raise Exception(traceback.format_exc())

    return table_list


def get_device_results(server, condition, table_name, data, order='desc'):
    result = []
    if order != 'desc':
        order = 'asc'

    sql = "SELECT * FROM {}.device_results where 1 = 1 {} order by log_date {} limit 1000".format(table_name,
                                                                                                  condition, order)

    print(sql)
    print(data)
    try:
        r_list = RedShiftWrapper.query_with_sql(sql, REDSHIFT_CONFIG[server], data)
        for device_result in r_list:
            obj = {}

            for item in device_result:
                if item == 'log_date' or item == 'id':
                    obj[item] = str(device_result[item])
                    continue
                obj[item] = device_result[item]
            result.append(obj)
    except:
        raise Exception(traceback.format_exc())

    return result


def get_type_from(document, month, server):
    if not IDENTITY_NAME_MAPPING:
        set_identity_name()

    type_list = ['category', 'brand', 'model']
    for type in type_list:
        sql = "select identify_from_name_id from {}.{}_from where device_result_id = %(DEVICE_RESULT_ID)s".format(month,
                                                                                                                  type)
        data = {"DEVICE_RESULT_ID": document["id"]}

        type_from_list = []
        try:
            id_list = RedShiftWrapper.query_with_sql(sql, REDSHIFT_CONFIG[server], data)
            for item in id_list:
                type_from_list.append(IDENTITY_NAME_MAPPING.get(item["identify_from_name_id"]))
        except:
            raise Exception(traceback.format_exc())

        document['{}_from'.format(type)] = ', '.join(type_from_list)


def get_ids_from(document, month, server):
    type_map = {
        'category': {
            'q_name': 'category_id',
            's_name': 'category_id',
            'from_list': set()
        },
        'model': {
            'q_name': 'dev_model',
            's_name': 'model',
            'from_list': set()
        },
        'brand': {
            'q_name': 'dev_brand',
            's_name': 'brand',
            'from_list': set()
        },
    }

    sql = "select * from {}.pattern_info where device_result_id = %(DEVICE_RESULT_ID)s".format(month)
    data = {"DEVICE_RESULT_ID": document["id"]}
    result_list = RedShiftWrapper.query_with_sql(sql, REDSHIFT_CONFIG[server], data)
    for item in result_list:
        for type in type_map:
            q_name = type_map[type]['q_name']
            s_name = type_map[type]['s_name']
            if document[q_name] and document[q_name] == item[s_name]:
                type_map[type]['from_list'].add(item['pattern_id'])

    for type in type_map:
        document['{}_from_ids'.format(type)] = ", ".join(type_map[type]['from_list'])


def get_log_partition(s3_file_id, server):
    sql = "select created_date from public.s3_file_info where id = %(ID)s"
    data = {"ID": s3_file_id}
    result_list = RedShiftWrapper.query_with_sql(sql, REDSHIFT_CONFIG[server], data)
    if result_list:
        return result_list[0]['created_date']
    else:
        return None


def query_log(s3_file_id, server, s_guid):
    at = AthenaWrapper(ATHENA_CONFIG[server]["profile_name"], ATHENA_CONFIG[server]["bucket"],
                       ATHENA_CONFIG[server]["bucket_path"])

    log_time = get_log_partition(s3_file_id, server)

    table_name = ATHENA_CONFIG[server].get("table_name")
    SQL = """SELECT raw_log_base64_zip FROM {}  WHERE 
                year = {} AND month = {} AND day = {} AND hour= {}
                AND req_env is NOT null
                AND req_env.s_guid = '{}'
                limit 1
            """.format(table_name,
                       log_time.year, log_time.month, log_time.day, log_time.hour,
                       s_guid)

    print(SQL)

    file_content = at.exec_query(SQL, ATHENA_CONFIG[server].get("database"))
    if not file_content.empty:
        return unzip_string(file_content['raw_log_base64_zip'][0])


def ttest_get_device_results():
    import json
    table_name = "y20m07"
    condition = "and c_guid = %(C_GUID)s"
    data = {'C_GUID': 'DFBB489C-D1C9-466E-A2D4-7B7B72F381E4'}
    result = get_device_results('Beta', condition, table_name, data)
    print(json.dumps(result, indent=4))
    pass


def ttest_get_type_from():
    set_identity_name()
    document = {"id": 2020070000000000002}
    month = 'y20m07'
    server = 'Beta'
    get_type_from(document, month, server)
    print(document)


def ttest_get_ids_from():
    import json

    document = {
        "id": 2020070000000177200,
        'dev_brand': 'Huawei',
        'dev_model': "HUAWEI_Mate_30",
        'category_id': 769
    }
    month = 'y20m07'
    server = 'Beta'
    get_ids_from(document, month, server)
    print(json.dumps(document, indent=4))


if __name__ == '__main__':
    # ttest_get_ids_from()

    # ttest_get_device_results()


    # condition = "2 = 2"
    # table_name = "y20m03"
    # condition = "and log_date > %(START_TIME)s and log_date < %(END_TIME)s"
    # data = {"START_TIME": '2020-03-06 09', "END_TIME": "2020-03-06 10"}
    # result = get_device_results('Beta', condition, table_name, data)
    # print(json.dumps(result, indent=4))

    sql = "SELECT * FROM y20m08.device_results where dev_mac='00:0A:D5:01:84:7B';"
    sql = "SELECT * FROM y20m10.device_results where 1 = 1  and log_date > '2020-10-30' and log_date < '2020-10-31' and dev_mac = '22:EA:EF:92:F4:95' and c_guid = 'GUID_SDK_AUTOMATION' "

    sql = "SELECT * FROM y20m10.device_results where 1 = 1  and log_date > %(START_TIME)s and log_date < %(END_TIME)s and dev_mac = %(DEV_MAC)s and c_guid = %(C_GUID)s  order by log_date desc limit 1000"
    data = {'START_TIME': '2020-10-30', 'END_TIME': '2020-10-31', 'DEV_MAC': '22:EA:EF:92:F4:95', 'C_GUID': 'GUID_SDK_AUTOMATION'}

    r_list = RedShiftWrapper.query_with_sql(sql, REDSHIFT_CONFIG['Beta'], data)
    result = []
    for device_result in r_list:
        obj = {}

        for item in device_result:
            if item == 'log_date' or item == 'id':
                obj[item] = str(device_result[item])
                continue
            obj[item] = device_result[item]
        result.append(obj)
