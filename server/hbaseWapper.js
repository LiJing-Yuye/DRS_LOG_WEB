const hbase = require('hbase')
client = hbase({ host: '10.206.178.201', port: 8080 })

module.exports = client
