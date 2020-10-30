const mssql = require('mssql')

var db = {}
db.sql = function(sql, config, callBack) {
    console.log(sql)
    new mssql.ConnectionPool(config)
        .connect()
        .then((pool) => {
            let ps = new mssql.PreparedStatement(pool)
            ps.prepare(sql, (err) => {
                if (err) {
                    callBack(err, [])
                    return
                }

                ps.execute('', (err, result) => {
                    if (err) {
                        callBack(err, [])
                        return
                    }

                    ps.unprepare((err) => {
                        if (err) {
                            return
                        }

                        callBack(err, result['recordset'])
                    })
                })
            })
        })
        .catch((err) => {
            return err
        })
}

db.sql_async = function(strsql, config) {
    console.log(strsql)
    return new Promise((resolve, reject) => {
        mssql
            .connect(config)
            .then(() => {
                new mssql.Request()
                    .query(strsql)
                    .then(function(recordset) {
                        resolve(recordset['recordset'])
                    })
                    .catch(function(err) {
                        reject(err)
                    })
            })
            .catch(function(err) {
                reject(err)
            })
    })
}

db.close = function() {
    mssql.close()
}
module.exports = db
