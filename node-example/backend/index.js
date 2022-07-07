const express = require('express')
const {Pool, Client} = require('pg')

const app = express()

const pool = new Pool({
    user: process.env.DB_USER || 'postgres',
    host: process.env.DB_HOST || 'localhost',
    database: process.env.DB_NAME || 'eventsapp',
    password: process.env.DB_PASSWORD || 'postgres',
    port: process.env.DB_PORT || 5432
})

app.get('/health', (req, res) => {
    console.log(`Request received on ${req.path}`)
    return res.status(200).send({
        success: "true",
        message: "Service Healthy"
    })
});


app.get('/api/events', (req, res) => {
    console.log(`Request received on ${req.path}`)
    const query = 'SELECT * from events;'
    console.log(`SQL Query: ${query}`)
    let events = []
    pool.query(query, (err, result) => {
        if (err) {
            console.error(`Error querying database: ${err}`)
        }
        // const events = []
        for (let row of result.rows) {
            var event = {
                'eventid': row.eventid,
                'eventname': row.eventname
            }
            events.push(event);
            console.log(event)
        }
        console.log(events)
        return res.status(200).json({
            events: events,
            success: 'true'
        })
    })
    // console.log(events)
    // return res.status(200).json({
    //     events: events,
    //     success: 'true'
    // })
})


app.get('/api/event/:id', (req, res) => {
    console.log(`Request received on ${req.path}`)
    const query = `SELECT * from events where eventid = ${req.params.id};`
    console.log(`SQL Query: ${query}`)
    pool.query(query, (err, result) => {
        if (err) {
            console.error(`Error querying database: ${err}`)
        }
        // console.log(result)
        for (let row of result.rows) {
            // console.log(row)
            var eventdetail = {
                'eventname': row.eventname,
                'startdate': row.startdate,
                'enddate': row.enddate
            }
            console.log(eventdetail)
        }
        return res.status(200).json({
            success: 'true',
            eventdetails: eventdetail
        })
    })
})


app.get('/api/event/:id/participants', (req, res) => {
    console.log(`Request received on ${req.path}`)
    const query = `SELECT pname from participants where eventid = ${req.params.id};`
    console.log(`SQL Query: ${query}`)
    pool.query(query, (err, result) => {
        if (err){
            console.error(`Error querying database: ${err}`)
        }
        var participants = []
        for (let row of result.rows) {
            console.log(row)
            participants.push(row.pname)
        }
        return res.status(200).json({
            success: 'true',
            participants: participants
        })
    })
})


app.listen(3000, () => {
    console.log('Sample App - listening on port 3000')
})