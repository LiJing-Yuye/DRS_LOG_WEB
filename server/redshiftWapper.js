var Redshift = require('node-redshift')

var client = {
    user: 'druser',
    database: 'fp2fullbeta',
    password: 'RedshiftReadOnlyTrendmac8.6dr',
    port: '3389',
    host:
        'fp2-redshift-cluster.c2nwpm4iszlv.ap-northeast-1.redshift.amazonaws.com',
}

const sql = 'select * from fp2fullbeta.y20m07.device_results limit 1'
var redshift = new Redshift(client, { rawConnection: true })

// using callbacks
// redshift.connect(function(err){ //create connection manually
//   if(err) throw err;
//   else{
//     redshift.query('SELECT * FROM "Tags"', {raw: true}, function(err, data){ //query redshift
//       if(err) throw err;
//       else{
//         console.log(data);

//         redshift.close();
//       }
//     });
//   }
// });

// using promises
// redshift.connect(function(err){ //create connection manually
//   if(err) throw err;
//   else{

//     redshift.query('SELECT * FROM "Tags"', {raw: true})
//     .then(function(data){ //query redshift
//       console.log(data);

//       redshift.close();
//     }, function(err){
//       throw err;
//     });
//   }
// });

// you can also skip connecting and closing manually by using the rawQuery function which creates a new redshift instance temporarily,
// connects to your db, makes a query, returns the data and disconnects from the database in one operation
redshift
    .rawQuery(sql, { raw: true })
    .then(function(data) {
        console.log(data)
    })
    .catch(function(err) {
        console.log(err)
    })

console.log('hhh')
while (true) {}
