from django.http import HttpResponse
import psycopg2
import json
import datetime
from django.views.decorators.csrf import csrf_exempt



def home_view(request):
    return HttpResponse('Hello there')

def myconverter(o):
    if isinstance(o, datetime.date):
        return o.__str__()

@csrf_exempt
def metoda_post(request):
    conn = psycopg2.connect(host="fiit-dbs-xhankova-db.postgres.database.azure.com", dbname="dbs2021",
                            user="xhankova@fiit-dbs-xhankova-db", password="1Neviemco123", sslmode="require")
    cur = conn.cursor()

    body = request.body
    body_v_json = json.loads(body)
    chyby = []
    tohtorocny_datum = 0

    mam_br_court = 0
    mam_kind_name = 0
    mam_cin = 0
    mam_registration_date = 0
    mam_corporate_body_name = 0
    mam_br_section = 0
    mam_br_insertion = 0
    mam_text = 0
    mam_street = 0
    mam_postal_code = 0
    mam_city = 0
    address_line = ''

    for kluc in body_v_json:
        if kluc == 'br_court_name':
            mam_br_court = 1
            br_court = body_v_json[kluc]
            spravny_vystup = {
                "br_court_name": body_v_json[kluc]
            }

        elif kluc == 'kind_name':
            mam_kind_name = 1
            kind = body_v_json[kluc]
            spravny_vystup['kind_name'] = kind

        elif kluc == 'cin':
            mam_cin = 1
            cislo_cin = body_v_json[kluc]
            spravny_vystup['cin'] = cislo_cin
            if isinstance(body_v_json[kluc], int) == False:
                chyba = {
                    "field": kluc,
                    "reasons": "not_number"
                }
                chyby.append(chyba)

        elif kluc == 'registration_date':
            mam_registration_date = 1
            registration_date = body_v_json[kluc]
            spravny_vystup['registration_date'] = body_v_json[kluc]
            registration_date = str(registration_date)
            if registration_date[0] == '2':
                if registration_date[1] == '0':
                    if registration_date[2] == '2':
                        if registration_date[3] == '1':
                            tohtorocny_datum = 1



        elif kluc == 'corporate_body_name':
            mam_corporate_body_name = 1
            spravny_vystup['corporate_body_name'] = body_v_json[kluc]
            corporate = body_v_json[kluc]

        elif kluc == 'br_section':
            mam_br_section = 1
            section = body_v_json[kluc]
            spravny_vystup['br_section'] = body_v_json[kluc]

        elif kluc == 'br_insertion':
            mam_br_insertion = 1
            insertion = body_v_json[kluc]
            spravny_vystup['br_insertion'] = body_v_json[kluc]

        elif kluc == 'text':
            mam_text = 1
            zadany_text = body_v_json[kluc]
            spravny_vystup['text'] = body_v_json[kluc]

        elif kluc == 'street':
            mam_street = 1
            address_line = body_v_json[kluc]
            ulica = body_v_json[kluc]
            spravny_vystup['street'] = body_v_json[kluc]

        elif kluc == 'postal_code':
            mam_postal_code = 1
            address_line = address_line + ", " + str(body_v_json[kluc])
            postove_cislo = body_v_json[kluc]
            spravny_vystup['postal_code'] = body_v_json[kluc]

        elif kluc == 'city':
            mam_city = 1
            address_line = address_line + " " + str(body_v_json[kluc])
            mesto = body_v_json[kluc]
            spravny_vystup['city'] = body_v_json[kluc]
            spravny_vystup['address_line'] = address_line

    if(mam_br_court == 0):
        chybajuci_br_court = {
            "field": "br_court_name",
            "reasons": ["required"]
        }
        chyby.append(chybajuci_br_court)

    if(mam_kind_name == 0):
        chybajuce_kind_name = {
            "field": "kind_name",
            "reasons": ["required"]
        }
        chyby.append(chybajuce_kind_name)

    if(mam_cin == 0):
        chybajuci_cin = {
            "field": "cin",
            "reasons": ["required"]
        }
        chyby.append(chybajuci_cin)

    if (tohtorocny_datum == 0):
        zly_datum = {
            "field": "registration_date",
            "reasons": ["invalid_range"]
        }
        chyby.append(zly_datum)

    if(mam_registration_date == 0):
        chybajuci_registration_date = {
            "field": "registration_date",
            "reasons": ["required"]
        }
        chyby.append(chybajuci_registration_date)

    if(mam_corporate_body_name == 0):
        chybajuce_corporate_body_name = {
            "field": "corporate_body_name",
            "reasons": ["required"]
        }
        chyby.append(chybajuce_corporate_body_name)

    if(mam_br_section == 0):
        chybajuci_br_section = {
            "field": "br_section",
            "reasons": ["required"]
        }
        chyby.append(chybajuci_br_section)

    if(mam_br_insertion == 0):
        chybajuci_br_insertion = {
            "field": "br_insertion",
            "reasons": ["required"]
        }
        chyby.append(chybajuci_br_insertion)

    if(mam_text == 0):
        chybajuci_text = {
            "field": "text",
            "reasons": ["required"]
        }
        chyby.append(chybajuci_text)

    if(mam_street == 0):
        chybajuca_street = {
            "field": "street",
            "reasons": ["required"]
        }
        chyby.append(chybajuca_street)

    if(mam_postal_code == 0):
        chybajuci_postal_code = {
            "field": "postal_code",
            "reasons": ["required"]
        }
        chyby.append(chybajuci_postal_code)

    if(mam_city == 0):
        chybajuce_mesto = {
            "field": "city",
            "reasons": ["required"]
        }
        chyby.append(chybajuce_mesto)


    if chyby:
        chyby_na_vstupe = {
            "errors": chyby
        };

        json_object = json.dumps(chyby_na_vstupe, ensure_ascii=False, indent=4, separators=(',', ':'))
        return HttpResponse(json_object, status=422, content_type="application/json")

    if not chyby:
        cur.execute("""INSERT INTO ov.or_podanie_issues (id, bulletin_issue_id, raw_issue_id, br_mark, br_court_code, br_court_name,
        kind_code, kind_name, cin, registration_date, corporate_body_name, br_section,
        br_insertion, text, created_at, updated_at, address_line, street, postal_code, city) 
        VALUES (DEFAULT , 2593, 2455864, '-', '-', (%s), '-', (%s), (%s), (%s),  
        (%s), (%s), (%s), (%s), now(), now(), (%s), (%s), (%s), (%s));""",
        (br_court, kind, cislo_cin, registration_date, corporate, section, insertion, zadany_text, address_line, ulica,
                     postove_cislo, mesto))

        conn.commit()

        cur.execute("SELECT id FROM ov.or_podanie_issues ORDER BY id DESC LIMIT 1")
        idecko = cur.fetchone()
        spravny_vystup['id'] = idecko[0]

        json_object = json.dumps(spravny_vystup, ensure_ascii=False, indent=4, separators=(',', ':'))

        cur.execute("SELECT number FROM ov.bulletin_issues ORDER BY id DESC LIMIT 1")
        number = cur.fetchone()
        cislo_zvysene_o_jedno = number[0] + 1

        cur.execute("""INSERT INTO ov.bulletin_issues (id, year, number, published_at, created_at, updated_at)
        VALUES (DEFAULT, 2021, (%s), now(), now(), now());""", [cislo_zvysene_o_jedno])

        conn.commit()

        cur.execute("""INSERT INTO ov.raw_issues (id, bulletin_issue_id, file_name, content, created_at, updated_at)
        VALUES (DEFAULT, 2594, '-', '-', now(), now());""")

        conn.commit()

        return HttpResponse(body, status=201, content_type="application/json")


@csrf_exempt
def vymaz(request, cislo_id):

    conn = psycopg2.connect(host="fiit-dbs-xhankova-db.postgres.database.azure.com", dbname="dbs2021",
                            user="xhankova@fiit-dbs-xhankova-db", password="1Neviemco123", sslmode="require")
    cur = conn.cursor()
    cur.execute("DELETE FROM ov.or_podanie_issues WHERE id = %s", [cislo_id])
    rows_deleted = cur.rowcount
    conn.commit()

    if rows_deleted > 0:
        return HttpResponse(status=204, content_type="application/json")

    else:
        zaznam_neexistuje = {
            "message": "Záznam neexistuje"
        };

        error = {
            "error": zaznam_neexistuje
        };

        json_object = json.dumps(error, ensure_ascii=False, indent=4, separators=(',', ':'))

        return HttpResponse(json_object, status=404, content_type="application/json")

@csrf_exempt
def submissions(request):
    conn = psycopg2.connect(host="fiit-dbs-xhankova-db.postgres.database.azure.com", dbname="dbs2021",
                            user="xhankova@fiit-dbs-xhankova-db", password="1Neviemco123", sslmode="require")
    cur = conn.cursor()

    if request.method == 'GET':
        query = request.GET.get('query')
        registration_date_gte = request.GET.get('registration_date_gte')

        order_type = request.GET.get('order_type')
        if order_type is None:
           order_type = "DESC"

        order_by = request.GET.get('order_by')
        if order_by is None:
           order_by = "id"
        registration_date_lte = request.GET.get('registration_date_lte')

        page = request.GET.get('page')
        if page is None:
           page = 1
        elif int(page) <= 0:
             page = 1

        per_page = request.GET.get('per_page')
        if per_page is None:
             per_page = 10

        elif int(per_page) <= 0:
             per_page = 10


        pocet_vysledkov = 0

        per_page = str(per_page)

        zaznamy = []
        cislo_stranky = str((int(page) - 1) * int(per_page))
        parameters = [query, order_by, order_type, registration_date_gte, registration_date_lte, page, per_page]
        ofset = str((int(page) - 1) * int(per_page))

        if query is None and registration_date_gte is None and registration_date_lte is None:

           cur.execute(
                  "SELECT id, br_court_name, kind_name, cin, registration_date, corporate_body_name, br_section, text, street,"
                    "postal_code, city FROM ov.or_podanie_issues ORDER BY " + order_by + " " +
                    order_type + " nulls last LIMIT " + per_page + " OFFSET " + str((int(page) - 1) * int(per_page)) + ";")

           time = cur.fetchall()
           cur = conn.cursor()

           cur.execute("SELECT COUNT(id) FROM ov.or_podanie_issues")

           pocet_vysledkov = cur.fetchone()

        elif registration_date_gte is None and registration_date_lte is None:
                cur.execute(
                    "SELECT id, br_court_name, kind_name, cin, registration_date, corporate_body_name, br_section, text, street,"
                    "postal_code, city FROM ov.or_podanie_issues WHERE CAST(corporate_body_name AS text) LIKE ('%" + str(
                        query) +
                    "%')  OR CAST(cin AS text) LIKE '%"+ str(query) +"%'  OR CAST(city AS text) LIKE '%" + str(query) +
                    "%' ORDER BY " + str(order_by) + " " + str(order_type) + " nulls last LIMIT " + per_page + " OFFSET " +
                    str((int(page) - 1) * int(per_page)) + ";")

                time = cur.fetchall()

                cur = conn.cursor()
                cur.execute("SELECT COUNT(id) FROM ov.or_podanie_issues WHERE CAST(corporate_body_name AS text) LIKE '%" + str(query) +
                    "%'  OR CAST(cin AS text) LIKE '%"+ str(query) +"%' OR CAST(city AS text) LIKE '%" + str(query) + "%'")

                pocet_vysledkov = cur.fetchone()


        elif registration_date_lte is not None and registration_date_gte is not None:
                cur.execute(
                    "SELECT id, br_court_name, kind_name, cin, registration_date, corporate_body_name, br_section, text, street,"
                    "postal_code, city FROM ov.or_podanie_issues WHERE (CAST(corporate_body_name AS text) LIKE '%" + str(
                        query) + "%'  OR CAST(cin AS text) LIKE '%" + str(query) + "%' OR CAST(city AS text) LIKE '%" + str(query) +
                    "%') AND registration_date BETWEEN '" + registration_date_gte + "' AND '" + registration_date_lte +
                    "' ORDER BY " + str(order_by) + " " + str(order_type) + " LIMIT " + per_page + " OFFSET " +
                    str((int(page) - 1) * int(per_page)) + ";")

                time = cur.fetchall()

                cur = conn.cursor()
                cur.execute("SELECT COUNT(id) FROM ov.or_podanie_issues WHERE (CAST(corporate_body_name AS text) LIKE '%" + str(query) +
                    "%'  OR CAST(cin AS text) LIKE '%" + str(query) + "%' OR CAST(city AS text) LIKE '%" + str(query) + "%')"
                    " AND registration_date BETWEEN '" + registration_date_gte + "' AND '" + registration_date_lte + "'")

                pocet_vysledkov = cur.fetchone()

        for row in time:
                zaznam = {
                             "id": row[0],
                             "br_court_name": row[1],
                             "kind_name": row[2],
                             "cin": row[3],
                             "registration_date": json.dumps(row[4], default=myconverter),
                             "corporate_body_name": row[5],
                             "br_section": row[6],
                             "text": row[7],
                             "street": row[8],
                             "postal_code": row[9],
                             "city": row[10]
                };
                zaznamy.append(zaznam)


        pocet_stran = 0
        i = int(pocet_vysledkov[0])
        while i > 0:
              pocet_stran = pocet_stran+1
              i = i - 10

        data = {
                "page": page,
                "per_page": per_page,
                "pages": pocet_stran,
                "total": int(pocet_vysledkov[0])
            }

        prvy_slovnik = {
                "items": zaznamy
            }

        druhy_slovnik = {
                "metadata": data
            }

        treti_slovnik = prvy_slovnik | druhy_slovnik

        json_object = json.dumps(treti_slovnik, ensure_ascii=False, indent=4, separators=(',', ':'))

        return HttpResponse(json_object, content_type="application/json")

    elif request.method == 'POST':
        body = request.body
        body_v_json = json.loads(body)
        chyby = []
        tohtorocny_datum = 0

        mam_br_court = 0
        mam_kind_name = 0
        mam_cin = 0
        mam_registration_date = 0
        mam_corporate_body_name = 0
        mam_br_section = 0
        mam_br_insertion = 0
        mam_text = 0
        mam_street = 0
        mam_postal_code = 0
        mam_city = 0
        address_line = ''

        for kluc in body_v_json:
            if kluc == 'br_court_name':
                mam_br_court = 1
                br_court = body_v_json[kluc]
                spravny_vystup = {
                    "br_court_name": body_v_json[kluc]
                }

            elif kluc == 'kind_name':
                mam_kind_name = 1
                kind = body_v_json[kluc]
                spravny_vystup['kind_name'] = kind

            elif kluc == 'cin':
                mam_cin = 1
                cislo_cin = body_v_json[kluc]
                spravny_vystup['cin'] = cislo_cin
                if isinstance(body_v_json[kluc], int) == False:
                    chyba = {
                        "field": kluc,
                        "reasons": "not_number"
                    }
                    chyby.append(chyba)

            elif kluc == 'registration_date':
                mam_registration_date = 1
                registration_date = body_v_json[kluc]
                spravny_vystup['registration_date'] = body_v_json[kluc]
                registration_date = str(registration_date)
                if registration_date[0] == '2':
                    if registration_date[1] == '0':
                        if registration_date[2] == '2':
                            if registration_date[3] == '1':
                                tohtorocny_datum = 1



            elif kluc == 'corporate_body_name':
                mam_corporate_body_name = 1
                spravny_vystup['corporate_body_name'] = body_v_json[kluc]
                corporate = body_v_json[kluc]

            elif kluc == 'br_section':
                mam_br_section = 1
                section = body_v_json[kluc]
                spravny_vystup['br_section'] = body_v_json[kluc]

            elif kluc == 'br_insertion':
                mam_br_insertion = 1
                insertion = body_v_json[kluc]
                spravny_vystup['br_insertion'] = body_v_json[kluc]

            elif kluc == 'text':
                mam_text = 1
                zadany_text = body_v_json[kluc]
                spravny_vystup['text'] = body_v_json[kluc]

            elif kluc == 'street':
                mam_street = 1
                address_line = body_v_json[kluc]
                ulica = body_v_json[kluc]
                spravny_vystup['street'] = body_v_json[kluc]

            elif kluc == 'postal_code':
                mam_postal_code = 1
                address_line = address_line + ", " + str(body_v_json[kluc])
                postove_cislo = body_v_json[kluc]
                spravny_vystup['postal_code'] = body_v_json[kluc]

            elif kluc == 'city':
                mam_city = 1
                address_line = address_line + " " + str(body_v_json[kluc])
                mesto = body_v_json[kluc]
                spravny_vystup['city'] = body_v_json[kluc]
                spravny_vystup['address_line'] = address_line

        if (mam_br_court == 0):
            chybajuci_br_court = {
                "field": "br_court_name",
                "reasons": ["required"]
            }
            chyby.append(chybajuci_br_court)

        if (mam_kind_name == 0):
            chybajuce_kind_name = {
                "field": "kind_name",
                "reasons": ["required"]
            }
            chyby.append(chybajuce_kind_name)

        if (mam_cin == 0):
            chybajuci_cin = {
                "field": "cin",
                "reasons": ["required"]
            }
            chyby.append(chybajuci_cin)

        if (tohtorocny_datum == 0):
            zly_datum = {
                "field": "registration_date",
                "reasons": ["invalid_range"]
            }
            chyby.append(zly_datum)

        if (mam_registration_date == 0):
            chybajuci_registration_date = {
                "field": "registration_date",
                "reasons": ["required"]
            }
            chyby.append(chybajuci_registration_date)

        if (mam_corporate_body_name == 0):
            chybajuce_corporate_body_name = {
                "field": "corporate_body_name",
                "reasons": ["required"]
            }
            chyby.append(chybajuce_corporate_body_name)

        if (mam_br_section == 0):
            chybajuci_br_section = {
                "field": "br_section",
                "reasons": ["required"]
            }
            chyby.append(chybajuci_br_section)

        if (mam_br_insertion == 0):
            chybajuci_br_insertion = {
                "field": "br_insertion",
                "reasons": ["required"]
            }
            chyby.append(chybajuci_br_insertion)

        if (mam_text == 0):
            chybajuci_text = {
                "field": "text",
                "reasons": ["required"]
            }
            chyby.append(chybajuci_text)

        if (mam_street == 0):
            chybajuca_street = {
                "field": "street",
                "reasons": ["required"]
            }
            chyby.append(chybajuca_street)

        if (mam_postal_code == 0):
            chybajuci_postal_code = {
                "field": "postal_code",
                "reasons": ["required"]
            }
            chyby.append(chybajuci_postal_code)

        if (mam_city == 0):
            chybajuce_mesto = {
                "field": "city",
                "reasons": ["required"]
            }
            chyby.append(chybajuce_mesto)

        if chyby:
            chyby_na_vstupe = {
                "errors": chyby
            };

            json_object = json.dumps(chyby_na_vstupe, ensure_ascii=False, indent=4, separators=(',', ':'))
            return HttpResponse(json_object, status=422, content_type="application/json")

        if not chyby:
            'bulletin issue id je vzdy o jedno vacsie ako predchadzajuce'

            cur.execute("""INSERT INTO ov.or_podanie_issues (id, bulletin_issue_id, raw_issue_id, br_mark, br_court_code, br_court_name,
              kind_code, kind_name, cin, registration_date, corporate_body_name, br_section,
              br_insertion, text, created_at, updated_at, address_line, street, postal_code, city) 
              VALUES (DEFAULT , 2593, 2455864, '-', '-', (%s), '-', (%s), (%s), (%s),  
              (%s), (%s), (%s), (%s), now(), now(), (%s), (%s), (%s), (%s));""",
                        (br_court, kind, cislo_cin, registration_date, corporate, section, insertion, zadany_text,
                         address_line, ulica,
                         postove_cislo, mesto))

            conn.commit()

            cur.execute("SELECT id FROM ov.or_podanie_issues ORDER BY id DESC LIMIT 1")
            idecko = cur.fetchone()
            spravny_vystup['id'] = idecko[0]

            json_object = json.dumps(spravny_vystup, ensure_ascii=False, indent=4, separators=(',', ':'))

            cur.execute("SELECT number FROM ov.bulletin_issues ORDER BY id DESC LIMIT 1")
            number = cur.fetchone()
            cislo_zvysene_o_jedno = number[0] + 1

            cur.execute("""INSERT INTO ov.bulletin_issues (id, year, number, published_at, created_at, updated_at)
              VALUES (DEFAULT, 2021, (%s), now(), now(), now());""", [cislo_zvysene_o_jedno])

            conn.commit()

            cur.execute("""INSERT INTO ov.raw_issues (id, bulletin_issue_id, file_name, content, created_at, updated_at)
              VALUES (DEFAULT, 2594, '-', '-', now(), now());""")

            conn.commit()

            return HttpResponse(body, status=201, content_type="application/json")



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

    return HttpResponse(json_object, content_type="application/json")
