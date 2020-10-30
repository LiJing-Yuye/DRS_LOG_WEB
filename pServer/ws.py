from flask import Flask, jsonify, request
from db_service import *
from datetime import datetime, timedelta
import time

app = Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    return jsonify({'version': '1.0.0'})


@app.route('/api/month', methods=['GET'])
def api_month():
    default_result = {
        "code": '0',
        "data": [],
        "msg": '',
    }

    try:
        default_result['data'] = get_all_table('Beta')
    except Exception as e:
        default_result['code'] = 1
        default_result['msg'] = str(e)
    finally:
        pass

    return jsonify(default_result)


@app.route('/api/log', methods=['POST'])
def api_log():
    default_result = {
        "code": '0',
        "data": [],
        "msg": '',
    }

    body = request.get_json()
    server = body.get('server')
    month = body.get('month')
    date = body.get('date')
    order = body.get('log_date')
    protocol = body.get('protocol')

    need_filter = False

    condition = ""
    para_query = {}
    table_list = []
    if date:
        start_date = date[:10]
        end_date = datetime.strptime(start_date, '%Y-%M-%d') + timedelta(days=1)
        end_date = end_date.strftime('%Y-%M-%d')
        condition += " and log_date > %(START_TIME)s and log_date < %(END_TIME)s"
        para_query["START_TIME"] = start_date
        para_query["END_TIME"] = end_date
        table_list = ['y{}m{}'.format(date[2:4], date[5:7])]
    else:
        if month == 'ALL':
            all_month = get_all_table(server)
            if order == 'desc':
                all_month.reverse()
            table_list.extend(all_month)
        else:
            table_list.append(month)

    query = body.get('query')
    if query:
        if str(query).find(":") != -1:
            condition += " and dev_mac = %(DEV_MAC)s "
            para_query['DEV_MAC'] = query.upper()
        else:
            condition += "and id = %(ID)s"
            para_query['ID'] = query

    if protocol:
        condition += " and req_url = %(PROTOCOL)s "
        para_query['PROTOCOL'] = protocol

    c_query = body.get('c_query')
    if c_query:
        need_filter = True
        if month == 'ALL' and not date:
            default_result['code'] = 1
            default_result['msg'] = "When query devices by c_guid, must select month/date !!!"
            return jsonify(default_result)

        if str(c_query).find(":") != -1:
            condition += " and gw_mac = %(GW_MAC)s "
            para_query['GW_MAC'] = c_query
        else:
            condition += "and c_guid = %(C_GUID)s "
            para_query['C_GUID'] = c_query

    if not query and not c_query:
        default_result['code'] = 1
        default_result['msg'] = "No query condition !!! "
        return jsonify(default_result)

    for table_name in table_list:
        try:
            devices = get_device_results(server, condition, table_name, para_query, order)
            for device in devices:
                device['month'] = table_name
                device['server'] = server

            if need_filter:
                devices_map = {}
                for device in devices:
                    if device['dev_mac'] not in devices_map:
                        devices_map[device['dev_mac']] = device
                    else:
                        if device['log_date'] > devices_map[device['dev_mac']]['log_date']:
                            devices_map[device['dev_mac']] = device

                devices = list(devices_map.values())

            default_result['data'].extend(devices)
        except Exception as e:
            default_result['code'] = 1
            default_result['msg'] = str(e)

        if len(default_result['data']) > 1000:
            break

    return jsonify(default_result)


@app.route('/api/download', methods=['POST'])
def api_download():
    default_result = {
        "code": '0',
        "data": [],
        "msg": '',
    }

    body = request.get_json()
    s_guid = body.get('s_guid')
    s3_file_id = body.get('s3_file_id')
    server = body.get('server')

    try:
        content = query_log(s3_file_id, server, s_guid)
        default_result["data"] = [content]
    except Exception as e:
            default_result['code'] = 1
            default_result['msg'] = str(e)

    return jsonify(default_result)


@app.route('/api/from', methods=['POST'])
def api_from():
    default_result = {
        "code": '0',
        "data": [],
        "msg": '',
    }

    document = request.get_json()
    month = document.get('month')
    server = document.get('server')

    get_type_from(document, month, server)
    get_ids_from(document, month, server)
    default_result['data'].append(document)

    return jsonify(default_result)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
