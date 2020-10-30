const express = require('express')
const bodyParser = require('body-parser')
const config = require('./config')
const db = require('./sqlserver')
const hbaseClient = require('./hbaseWapper')
const app = express()
const utils = require('./utils')
const port = 3000

async function GetIndentityName(id) {
    let result = await db.sql_async(
        `select * from identify_from_name where id = ${id}`,
        config['Prod']
    )
    return result[0]['identify_from_name']
}

async function GetTypeFrom(document, month, config) {
    const typeList = ['category', 'brand', 'model']
    for (var index in typeList) {
        let type = typeList[index]
        let resultList = await db.sql_async(
            `select * from ${type}_from_${month} where device_result_id = ${document.id}`,
            config
        )
        let typeFromList = []
        for (var resultIndex in resultList) {
            let item = resultList[resultIndex]
            const name = await GetIndentityName(item.identify_from_name_id)
            typeFromList.push(name)
        }

        document[`${type}_from`] = typeFromList.join(', ')
    }
    return
}

async function GetIDsFrom(document, month, config) {
    const typeMap = {
        category: 'category_id',
        model: 'dev_model',
    }

    let sql = `select * from pattern_ids_${month} where device_result_id = ${document.id}`
    let resultList = await db.sql_async(sql, config)
    let typeFromList = {
        category: new Set(),
        model: new Set(),
    }
    for (var resultIndex in resultList) {
        for (var type in typeMap) {
            let item = resultList[resultIndex]
            if (
                document[typeMap[type]] &&
                item[type] === document[typeMap[type]]
            ) {
                typeFromList[type].add(item['pattern_id'])
            }
        }
    }

    console.log(typeFromList)

    for (var type2 in typeMap) {
        document[`${type2}_from_ids`] = Array.from(typeFromList[type2]).join(
            ', '
        )
    }

    return
}

const checkPostData = function(postBody) {
    const regMap = {
        id: /^[0-9a-zA-Z][0-9a-zA-Z-|_]+[0-9a-zA-Z]$/,
        query: /^[0-9a-zA-Z:]+$/,
        server: /^(Prod)|(Beta)$/,
        month: /^([0-9]+)|(ALL)$/,
        log_date: /^(desc|asc)$/,
        date: /^[0-9T/.:-]+Z$/,
        category_id: /^[0-9]+$/,
    }

    for (var key in regMap) {
        if (postBody[key]) {
            if (!regMap[key].test(postBody[key])) {
                return false
            }
        }
    }

    return true
}

app.use(require('cors')())
app.use(bodyParser.urlencoded({ extended: true }))
app.use(bodyParser.json())

app.get('/', async (req, res) => {
    res.send('Hello World!')
})

app.get('/api/month', async (req, res) => {
    let fresult = {
        code: '0',
        data: [],
        msg: '',
    }

    let tables = await db
        .sql_async(
            `select name from sysobjects 
                where  xtype='u' and name like 'device_results_%'
                order by name desc`,
            config['Beta']
        )
        .catch((err) => {
            fresult['code'] = 1
            fresult['msg'] = JSON.stringify(err, null, 4)
            res.send(fresult)
            return
        })

    if (tables) {
        tables.forEach((item) => {
            fresult['data'].push(item['name'].replace('device_results_', ''))
        })
    }

    db.close()
    res.send(fresult)
})

app.post('/api/from', async (req, res) => {
    let fresult = {
        code: '0',
        data: [],
        msg: '',
    }

    if (!checkPostData(req.body)) {
        fresult['code'] = 1
        fresult['msg'] = 'Illegal data'
        res.send(fresult)
        return
    }

    const document = req.body
    const month = document['month']
    const server = document['server']

    await GetTypeFrom(document, month, config[server])
    await GetIDsFrom(document, month, config[server])
    fresult['data'] = fresult['data'].concat(document)

    db.close()
    res.send(fresult)
})

app.post('/api/log', async (req, res) => {
    let fresult = {
        code: '0',
        data: [],
        msg: '',
    }

    if (!checkPostData(req.body)) {
        fresult['code'] = 1
        fresult['msg'] = 'Illegal data'
        res.send(fresult)
        return
    }

    const server = req.body['server']
    const date = req.body['date']

    let table_list = []
    if (date) {
        const dmonth = date.substr(2, 2) + date.substr(5, 2)
        table_list = [`device_results_${dmonth}`]
    } else if (req.body['month'] === 'ALL') {
        let tables = await db
            .sql_async(
                `select name from sysobjects 
                where  xtype='u' and name like 'device_results_%'
                order by name ${req.body['log_date']}`,
                config[server]
            )
            .catch((err) => {
                fresult['code'] = 1
                fresult['msg'] = JSON.stringify(err, null, 4)
                res.send(fresult)
                return
            })
        if (tables) {
            tables.forEach((item) => {
                table_list.push(item['name'])
            })
        }
    } else {
        table_list = [`device_results_${req.body['month']}`]
    }

    for (var index in table_list) {
        let table = table_list[index]
        let month = table.substring(table.length - 4)
        let query_sql = ''
        if (req.body['query'].indexOf(':') != -1) {
            query_sql = `and dev_mac = '${req.body['query']}'`
        } else {
            query_sql = `and id = ${req.body['query']}`
        }

        if (date) {
            const startDate = date
            const endDate = utils.getNextDay(date)
            query_sql += ` and log_date > '${startDate}' and log_date < '${endDate}'`
        }

        let result = await db
            .sql_async(
                `SELECT top(1000) * FROM ${table} where 1 = 1 ${query_sql} order by log_date ${req.body['log_date']}`,
                config[server]
            )
            .catch((err) => {
                fresult['code'] = 1
                fresult['msg'] = JSON.stringify(err, null, 4)
            })

        if (result) {
            result.forEach((item) => {
                item['month'] = month
                item['server'] = server
            })
        }

        if (result) {
            fresult['data'] = fresult['data'].concat(result)
        }

        if (fresult['data'].length > 1000) {
            break
        }
    }

    db.close()
    res.send(fresult)
})

app.post('/api/download', async (req, res) => {
    let fresult = {
        code: '0',
        data: [],
        msg: '',
    }

    if (!checkPostData(req.body)) {
        fresult['code'] = 1
        fresult['msg'] = 'Illegal data'
        res.send(fresult)
        return
    }

    const log_key = req.body['id']
    const month = req.body['month']
    const server = req.body['server']

    let tablename
    if (server === 'Prod') {
        tablename = 'prod_devices_' + month
    } else {
        tablename = 'beta_devices_' + month
    }

    let row = hbaseClient.table(tablename).row(log_key)
    row.get(['f:log_content'], (err, value) => {
        if (err) {
            fresult['code'] = 1
            fresult['msg'] = JSON.stringify(err)
        }

        fresult['data'] = value
        res.send(fresult)
    })
})

app.post('/api/pwd', async (req, res) => {
    let fresult = {
        code: '0',
        data: [],
        msg: '',
    }

    if (!checkPostData(req.body)) {
        fresult['code'] = 1
        fresult['msg'] = 'Illegal data'
        res.send(fresult)
        return
    }

    const log_key = req.body['id']
    const month = req.body['month']
    const server = req.body['server']

    let tablename
    if (server === 'Prod') {
        tablename = 'prod_web_console_password_' + month
    } else {
        tablename = 'beta_web_console_password_' + month
    }

    let row = hbaseClient.table(tablename).row(log_key)
    row.get(['f:log_content'], (err, value) => {
        if (err) {
            fresult['code'] = 1
            fresult['msg'] = JSON.stringify(err)
        }

        fresult['data'] = value
        res.send(fresult)
    })
})

app.listen(port, () => console.log(`http://localhost:${port}`))
