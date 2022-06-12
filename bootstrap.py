import os
import psycopg2

def events(conn):
    eventlist = [
        {"eventid": 1, "eventname": "IPL", "startdate": "01/05/2022", "enddate": "15/06/2022"},
        {"eventid": 2, "eventname": "IFL", "startdate": "15/05/2022", "enddate": "20/06/2022"}
    ]
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE events (eventid integer, eventname varchar, startdate varchar, enddate varchar);"
    )
    for event in eventlist:
        print("INSERT INTO events (eventid, eventname, startdate, enddate) values ({}, {}, {}, {});".format(
                event["eventid"],
                event["eventname"],
                event["startdate"],
                event["enddate"]
            )
        )
        cursor.execute(
            "INSERT INTO events (eventid, eventname, startdate, enddate) values (%s, %s, %s, %s);", (
                event["eventid"],
                event["eventname"],
                event["startdate"],
                event["enddate"],
            )
        )
    conn.commit()
    cursor.close()


def participants(conn):
    participantlist = [
        {"eventid": 1, "pname": "Delhi Capitals"},
        {"eventid": 1, "pname": "Punjab Kings"},
        {"eventid": 1, "pname": "Chennai Super Kings"},
        {"eventid": 1, "pname": "Gujarat Titans"},
        {"eventid": 2, "pname": "Bucks"},
        {"eventid": 2, "pname": "Storm"},
        {"eventid": 2, "pname": "Panthers"},
        {"eventid": 2, "pname": "Columbus Wild Dogs"}
    ]
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE participants (eventid integer, pname varchar);"
    )
    for participant in participantlist:
        print("INSERT INTO participants (eventid, pname) values ({}, {})".format(
            participant["eventid"], participant["pname"]
        ))
        cursor.execute(
            "INSERT INTO participants (eventid, pname) values (%s, %s)",
            (participant["eventid"], participant["pname"])
        )
    conn.commit()
    cursor.close()

if __name__=="__main__":
    conn = psycopg2.connect(
        user=os.environ.get("DB_USER", "postgres"),
        password=os.environ.get("DB_PASSWORD", "postgres"),
        dbname=os.environ.get("DB_NAME", "eventsapp"),
        host=os.environ.get("DB_HOST", "localhost")
    )
    events(conn)
    participants(conn)
    conn.close()