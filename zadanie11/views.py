from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
import psycopg2
import json


def home_view(request):
    return HttpResponse('Hello there')


def uptime_view(request):
    conn = psycopg2.connect(host="fiit-dbs-xhankova-db.postgres.database.azure.com", dbname="postgres",
                            user="xhankova@fiit-dbs-xhankova-db", password="1Neviemco123", sslmode="require")
    cur = conn.cursor()
    cur.execute("SELECT date_trunc('second', current_timestamp -pg_postmaster_start_time()) as uptime")
    time = cur.fetchone()

    konvertuj_na_string = ' '.join(['\'{}\''.format(x) for x in time])
    konvertuj_na_string = konvertuj_na_string.replace(',', '')

    cur.close()
    conn.close()

    vysledok_konvertovany_na_tuple = eval(konvertuj_na_string)

    prvy_slovnik = {
        "uptime": vysledok_konvertovany_na_tuple
    }

    druhy_slovnik = {
        "pgsql": prvy_slovnik
    }

    json_object = json.dumps(druhy_slovnik)
    print(time)

    return HttpResponse(json_object, content_type="application/json")
