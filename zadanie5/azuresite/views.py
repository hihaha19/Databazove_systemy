from django.db.models import Count, Q
from django.http import HttpResponse
import psycopg2
import json
import datetime
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from azuresite.models import OrPodanieIssues, Companies, RawIssues, BulletinIssues

"""- na necisto prvu migraciu dam make migration, vygeneruje sa 1. migracia, druhu naviazem na prvu, ktoru uz teraz mam 
a prepisem to v databaze
- ked zacinam pouzivat orm, nech tam uz mam zmigrovane modely
- potrebujem mat zmigrovane modely, nech mi funguje aplikacia s orm
- bud pridam novu migraciu, za tu, ktoru tam uz mam, oznacit ju ako hotovu, vygenerovat si migraciu a nastavit si ju
do databazy, nech je executnuta, nech sa ju nesnazi vytvorit ju znova, nemozem dat migrate command, lebo sa bude snazit
spravit tabulky nanovo, napisat do databazy, ze je to hotove
- daju sa aj fake migracie"""

@csrf_exempt
def v2_submissions(request):
    zaznamy = []

    if request.method == 'GET':
        query = request.GET.get('query')
        registration_date_gte = request.GET.get('registration_date_gte')

        order_type = request.GET.get('order_type')
        if order_type is None:
            order_type = "DESC"

        usporiadaj_podla = request.GET.get('order_by')
        if usporiadaj_podla is None:
            usporiadaj_podla = "id"
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

        limit = int(per_page) + int((int(page) - 1) * int(per_page))
        order_type = order_type.upper()

        if registration_date_lte is not None:
            date_time_obj = datetime.datetime.strptime(registration_date_lte, '%Y-%m-%d %H:%M:%S.%f')
            registration_date_lte = date_time_obj.strftime("%Y-%m-%d")

        if registration_date_gte is not None:
            date_time_obj = datetime.datetime.strptime(registration_date_gte, '%Y-%m-%d %H:%M:%S.%f')
            registration_date_gte = date_time_obj.strftime("%Y-%m-%d")

        if query is None and registration_date_gte is None and registration_date_lte is None:
            if order_type == "ASC":
                results = OrPodanieIssues.objects.all().order_by(usporiadaj_podla)[int((int(page) - 1) * int(per_page)):limit]

            elif order_type == "DESC":
                results = OrPodanieIssues.objects.all().order_by(usporiadaj_podla).reverse()[int((int(page) - 1) * int(per_page)):limit]

            pocet_vysledkov = OrPodanieIssues.objects.all().count()


        elif registration_date_gte is None and registration_date_lte is None:
            if order_type == "ASC":
                results = (OrPodanieIssues.objects.filter(
                corporate_body_name__icontains=query) | OrPodanieIssues.objects.filter(cin__contains=query) \
                      | OrPodanieIssues.objects.filter(city__icontains=query)).order_by(usporiadaj_podla)[int((int(page) - 1) * int(per_page)):limit]

            elif order_type == "DESC":
                results = (OrPodanieIssues.objects.filter(
                    corporate_body_name__icontains=query) | OrPodanieIssues.objects.filter(cin__contains=query) \
                          | OrPodanieIssues.objects.filter(city__icontains=query)).order_by(usporiadaj_podla).reverse()[int((int(page) - 1) * int(per_page)):limit]
            pocet_vysledkov = (OrPodanieIssues.objects.filter(
                corporate_body_name__icontains=query) | OrPodanieIssues.objects.filter(cin__contains=query) \
                      | OrPodanieIssues.objects.filter(city__icontains=query)).count()

        elif registration_date_lte is not None and registration_date_gte is not None:
            if order_type == "ASC":
                results = (OrPodanieIssues.objects.filter(
                    corporate_body_name__icontains=query) | OrPodanieIssues.objects.filter(cin__contains=query) \
                          | OrPodanieIssues.objects.filter(city__icontains=query))&OrPodanieIssues.objects.filter(registration_date__gte=registration_date_gte) \
                        &OrPodanieIssues.objects.filter(registration_date__lte=registration_date_lte).order_by(usporiadaj_podla)[int((int(page) - 1) * int(per_page)):limit]

            elif order_type == "DESC":
                results = (OrPodanieIssues.objects.filter(
                    corporate_body_name__icontains=query) | OrPodanieIssues.objects.filter(cin__contains=query) \
                          | OrPodanieIssues.objects.filter(city__icontains=query))&OrPodanieIssues.objects.filter(registration_date__gte=registration_date_gte) \
                        &OrPodanieIssues.objects.filter(registration_date__lte=registration_date_lte).order_by(usporiadaj_podla).reverse()[int((int(page) - 1) * int(per_page)):limit]

            pocet_vysledkov = ((OrPodanieIssues.objects.filter(
                    corporate_body_name__icontains=query) | OrPodanieIssues.objects.filter(cin__contains=query) \
                          | OrPodanieIssues.objects.filter(city__icontains=query))&OrPodanieIssues.objects.filter(registration_date__gte=registration_date_gte) \
                        &OrPodanieIssues.objects.filter(registration_date__lte=registration_date_lte)).count()

        for rows in results:
            zaznam = {
                "id": rows.id,
                "br_court_name": rows.br_court_name,
                "kind_name": rows.kind_name,
                "cin": rows.cin,
                "registration_date": json.dumps(rows.registration_date, default=myconverter),
                "corporate_body_name": rows.corporate_body_name,
                "br_section": rows.br_section,
                "text": rows.text,
                "street": rows.street,
                "postal_code": rows.postal_code,
                "city": rows.city
            }
            zaznamy.append(zaznam)

        pocet_stran = 0
        i = pocet_vysledkov
        while i > 0:
            pocet_stran = pocet_stran + 1
            i = i - int(per_page)

        data = {
            "page": page,
            "per_page": per_page,
            "pages": pocet_stran,
            "total": pocet_vysledkov
        }

        prvy_slovnik = {
            "items": zaznamy
        }

        druhy_slovnik = {
            "metadata": data
        }

        treti_slovnik = prvy_slovnik.copy()
        treti_slovnik.update(druhy_slovnik)



        json_object = json.dumps(treti_slovnik, ensure_ascii=False, indent=4, separators=(',', ':'))

        return HttpResponse(json_object, status=200, content_type="application/json")

    elif request.method == 'POST':
        body = request.body
        body_v_json = json.loads(body)
        chyby = []
        tohtorocny_datum = 0

        zaznam_posledneho_id = OrPodanieIssues.objects.order_by('id').reverse()[:1]

        for rows in zaznam_posledneho_id:
            posledne_id = rows.id

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

        neplatna_adresa = 0

        spravny_vystup = {
            "id": posledne_id+1
        }

        for kluc in body_v_json:
            if kluc == 'br_court_name':
                mam_br_court = 1
                br_court = body_v_json[kluc]
                if isinstance(body_v_json[kluc], str) == False:
                    chyba = {
                        "field": kluc,
                        "reasons": "not_string"
                    }
                    chyby.append(chyba)

                else:
                    spravny_vystup['br_court_name'] = body_v_json[kluc]

            elif kluc == 'kind_name':
                mam_kind_name = 1
                kind = body_v_json[kluc]
                if isinstance(body_v_json[kluc], str) == False:
                    chyba = {
                        "field": kluc,
                        "reasons": "not_string"
                    }
                    chyby.append(chyba)
                else:
                    spravny_vystup['kind_name'] = kind

            elif kluc == 'cin':
                mam_cin = 1
                cislo_cin = body_v_json[kluc]
                if isinstance(body_v_json[kluc], int) == False:
                    chyba = {
                        "field": kluc,
                        "reasons": "not_number"
                    }
                    chyby.append(chyba)
                else:
                    spravny_vystup['cin'] = cislo_cin

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
                if isinstance(body_v_json[kluc], str) == False:
                    chyba = {
                        "field": kluc,
                        "reasons": "not_string"
                    }
                    chyby.append(chyba)


            elif kluc == 'br_section':
                mam_br_section = 1
                section = body_v_json[kluc]
                spravny_vystup['br_section'] = body_v_json[kluc]
                if isinstance(body_v_json[kluc], str) == False:
                    chyba = {
                        "field": kluc,
                        "reasons": "not_string"
                    }
                    chyby.append(chyba)

            elif kluc == 'br_insertion':
                mam_br_insertion = 1
                insertion = body_v_json[kluc]
                spravny_vystup['br_insertion'] = body_v_json[kluc]
                if isinstance(body_v_json[kluc], str) == False:
                    chyba = {
                        "field": kluc,
                        "reasons": "not_string"
                    }
                    chyby.append(chyba)

            elif kluc == 'text':
                mam_text = 1
                zadany_text = body_v_json[kluc]
                spravny_vystup['text'] = body_v_json[kluc]
                if isinstance(body_v_json[kluc], str) == False:
                    chyba = {
                        "field": kluc,
                        "reasons": "not_string"
                    }
                    chyby.append(chyba)

            elif kluc == 'street':
                mam_street = 1

                ulica = body_v_json[kluc]
                spravny_vystup['street'] = body_v_json[kluc]
                if isinstance(body_v_json[kluc], str) == False:
                    neplatna_adresa = 1
                    chyba = {
                        "field": kluc,
                        "reasons": "not_string"
                    }
                    chyby.append(chyba)
                else:
                    address_line = body_v_json[kluc]

            elif kluc == 'postal_code':
                mam_postal_code = 1
                address_line = address_line + ", " + str(body_v_json[kluc])
                postove_cislo = body_v_json[kluc]
                spravny_vystup['postal_code'] = body_v_json[kluc]

            elif kluc == 'city':
                mam_city = 1
                if neplatna_adresa != 1:
                    address_line = address_line + " " + str(body_v_json[kluc])
                mesto = body_v_json[kluc]
                spravny_vystup['city'] = body_v_json[kluc]
                if isinstance(body_v_json[kluc], str) == False:
                    neplatna_adresa = 1
                    chyba = {
                        "field": kluc,
                        "reasons": "not_string"
                    }
                    chyby.append(chyba)
                if neplatna_adresa != 1:
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
            registration_date = registration_date[:4] + '-' + registration_date[4:]
            registration_date = registration_date[:7] + '-' + registration_date[7:]
            datum_upravy = timezone.now()

            zaznam_na_vlozenie_do_podanie_issues = OrPodanieIssues(bulletin_issue_id = 2593, raw_issue_id = 2455864, br_mark = '-',
                    br_court_code = '-', br_court_name = br_court, kind_code = '-', kind_name = kind, cin = cislo_cin,
                    registration_date=registration_date, corporate_body_name = corporate, br_section = section,
                    br_insertion=insertion, text=zadany_text, created_at = timezone.now(), updated_at = timezone.now(),
                    address_line = address_line, street = ulica, postal_code = postove_cislo, city = mesto)

            zaznam_na_vlozenie_do_podanie_issues.save()

            zaznam_na_vlozenie_do_raw_issues = RawIssues(bulletin_issue_id=2594, file_name='-', content='-',
                                                         created_at=timezone.now(), updated_at=timezone.now())

            zaznam_na_vlozenie_do_raw_issues.save()
            cislo_z_bulletin_issues = BulletinIssues.objects.order_by('id').reverse()[:1]

            for rows in cislo_z_bulletin_issues:
                cislo = rows.number

            cislo_z_bulletin_issues = cislo + 1


            zaznam_na_vlozenie_do_bulletin_issues = BulletinIssues(year=2021, number=cislo_z_bulletin_issues,
                                    published_at=datum_upravy, created_at=timezone.now(), updated_at=timezone.now())
            zaznam_na_vlozenie_do_bulletin_issues.save()
            json_object = json.dumps(spravny_vystup, ensure_ascii=False, indent=4, separators=(',', ':'))

            return HttpResponse(json_object, status=201, content_type="application/json")


@csrf_exempt
def v2_ziskaj_vymaz(request, cislo_id):
    if request.method == 'DELETE':
        vymazane_riadky = OrPodanieIssues.objects.filter(id=cislo_id).delete()

        if vymazane_riadky[0] > 0:
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

    if request.method == 'GET':
        hladany_zaznam = OrPodanieIssues.objects.filter(id=cislo_id)
        zaznamy = []

        for rows in hladany_zaznam:
            zaznam = {
                "id": rows.id,
                "br_court_name": rows.br_court_name,
                "kind_name": rows.kind_name,
                "cin": rows.cin,
                "registration_date": json.dumps(rows.registration_date, default=myconverter),
                "corporate_body_name": rows.corporate_body_name,
                "br_section": rows.br_section,
                "br_insertion": rows.br_insertion,
                "text": rows.text,
                "street": rows.street,
                "postal_code": rows.postal_code,
                "city": rows.city
            }
            zaznamy.append(zaznam)

        json_object = json.dumps(zaznamy, ensure_ascii=False, indent=4, separators=(',', ':'))

        return HttpResponse(json_object, status=200, content_type="application/json")

    if request.method == 'PUT':
        try:
            hladany_zaznam = OrPodanieIssues.objects.get(id=cislo_id)
        except OrPodanieIssues.DoesNotExist:
            hladany_zaznam = None

        if hladany_zaznam == None:
            zaznam_neexistuje = {
                "message": "Záznam neexistuje"
            };

            error = {
                "error": zaznam_neexistuje
            };

            json_object = json.dumps(error, ensure_ascii=False, indent=4, separators=(',', ':'))

            return HttpResponse(json_object, status=404, content_type="application/json")

        body = request.body
        if body == b'':
            return HttpResponse(status=422, content_type="application/json")

        body_v_json = json.loads(body)
        chyby = []
        tohtorocny_datum = 0
        kluc_je_datum = 0

        for kluc in body_v_json:
            if kluc == 'br_court_name':
                je_string = isinstance(body_v_json[kluc], str)

                if je_string == True:
                    novy_br_court = body_v_json[kluc]
                    hladany_zaznam.br_court_name = novy_br_court
                    hladany_zaznam.save()

                else:
                    nie_je_string = {
                        "field": "br_court_name",
                        "reasons": ["not_string"]
                    }
                    chyby.append(nie_je_string)


            elif kluc == 'kind_name':
                nove_kind_name = body_v_json[kluc]
                je_string = isinstance(nove_kind_name, str)
                if je_string == True:
                    hladany_zaznam.kind_name = nove_kind_name
                    hladany_zaznam.save()

                else:
                    nie_je_string = {
                        "field": "kind_name",
                        "reasons": ["not_string"]
                    }
                    chyby.append(nie_je_string)

            elif kluc == 'cin':
                novy_cin = body_v_json[kluc]
                je_integer = isinstance(novy_cin, int)
                if je_integer == True:
                    hladany_zaznam.cin = novy_cin
                    hladany_zaznam.save()

                else:
                    nie_je_integer = {
                        "field": "cin",
                        "reasons": ["not_number"]
                    }
                    chyby.append(nie_je_integer)

            elif kluc == 'registration_date':
                kluc_je_datum = 1
                novy_registration_date = body_v_json[kluc]
                novy_registration_date = str(novy_registration_date)
                if novy_registration_date[0] == '2':
                    if novy_registration_date[1] == '0':
                        if novy_registration_date[2] == '2':
                            if novy_registration_date[3] == '1':
                                tohtorocny_datum = 1
                                novy_registration_date = novy_registration_date[:4] + '-' + novy_registration_date[4:]
                                novy_registration_date = novy_registration_date[:7] + '-' + novy_registration_date[7:]
                                hladany_zaznam.registration_date = novy_registration_date
                                hladany_zaznam.save()

            elif kluc == 'corporate_body_name':
                novy_name = body_v_json[kluc]
                je_string = isinstance(novy_name, str)
                if je_string == True:
                    hladany_zaznam.corporate_body_name = novy_name
                    hladany_zaznam.save()

                else:
                    nie_je_string = {
                        "field": "corporate_body_name",
                        "reasons": ["not_string"]
                    }
                    chyby.append(nie_je_string)

            elif kluc == 'br_section':
                novy_br_section = body_v_json[kluc]
                je_string = isinstance(novy_br_section, str)
                if je_string == True:
                    hladany_zaznam.br_section = novy_br_section
                    hladany_zaznam.save()
                else:
                    nie_je_string = {
                        "field": "br_section",
                        "reasons": ["not_string"]
                    }
                    chyby.append(nie_je_string)

            elif kluc == 'br_insertion':
                novy_br_insertion = body_v_json[kluc]
                je_string = isinstance(novy_br_insertion, str)
                if je_string == True:
                    hladany_zaznam.br_insertion = novy_br_insertion
                    hladany_zaznam.save()

                else:
                    nie_je_string = {
                        "field": "br_insertion",
                        "reasons": ["not_string"]
                    }
                    chyby.append(nie_je_string)

            elif kluc == 'text':
                novy_text = body_v_json[kluc]
                je_string = isinstance(novy_text, str)
                if je_string == True:
                    hladany_zaznam.text = novy_text
                    hladany_zaznam.save()

                else:
                    nie_je_string = {
                        "field": "text",
                        "reasons": ["not_string"]
                    }
                    chyby.append(nie_je_string)

            elif kluc == 'street':
                nova_ulica = body_v_json[kluc]
                je_string = isinstance(nova_ulica, str)
                if je_string == True:
                    hladany_zaznam.street = nova_ulica
                    hladany_zaznam.save()
                else:
                    nie_je_string = {
                        "field": "street",
                        "reasons": ["not_string"]
                    }
                    chyby.append(nie_je_string)

            elif kluc == 'postal_code':
                nove_psc = body_v_json[kluc]
                je_string = isinstance(nove_psc, str)
                if je_string == True:
                    hladany_zaznam.postal_code = nove_psc
                    hladany_zaznam.save()
                else:
                    nie_je_string = {
                        "field": "postal_code",
                        "reasons": ["not_string"]
                    }
                    chyby.append(nie_je_string)

            elif kluc == 'city':
                nove_mesto = body_v_json[kluc]
                je_string = isinstance(nove_mesto, str)
                if je_string == True:
                    hladany_zaznam.city = nove_mesto
                    hladany_zaznam.save()
                else:
                    nie_je_string = {
                        "field": "city",
                        "reasons": ["not_string"]
                    }
                    chyby.append(nie_je_string)

            if tohtorocny_datum == 0 & kluc_je_datum == 1:
                if (tohtorocny_datum == 0):
                    zly_datum = {
                        "field": "registration_date",
                        "reasons": ["invalid_range"]
                    }
                    chyby.append(zly_datum)

        if chyby:
            chyby_na_vstupe = {
                "errors": chyby
            };

            json_object = json.dumps(chyby_na_vstupe, ensure_ascii=False, indent=4, separators=(',', ':'))
            return HttpResponse(json_object, status=422, content_type="application/json")


        else:
            hladany_zaznam = OrPodanieIssues.objects.filter(id=cislo_id)
            zaznamy = []

            for rows in hladany_zaznam:
                zaznam = {
                    "id": rows.id,
                    "br_court_name": rows.br_court_name,
                    "kind_name": rows.kind_name,
                    "cin": rows.cin,
                    "registration_date": json.dumps(rows.registration_date, default=myconverter),
                    "corporate_body_name": rows.corporate_body_name,
                    "br_section": rows.br_section,
                    "br_insertion": rows.br_insertion,
                    "text": rows.text,
                    "street": rows.street,
                    "postal_code": rows.postal_code,
                    "city": rows.city
                }
                zaznamy.append(zaznam)

            json_object = json.dumps(zaznamy, ensure_ascii=False, indent=4, separators=(',', ':'))
            return HttpResponse(json_object, status=201, content_type="application/json")

@csrf_exempt
def v2_companies(request):
    query = request.GET.get('query')
    last_update_gte = request.GET.get('last_update_gte')

    order_type = request.GET.get('order_type')
    if order_type is None:
        order_type = "DESC"

    order_type = order_type.upper()

    order_by = request.GET.get('order_by')
    if order_by is None:
        order_by = "cin"

    last_update_lte = request.GET.get('last_update_lte')

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

    limit = int(per_page) + int((int(page) - 1) * int(per_page))

    zaznamy = []

    if query is None and last_update_lte is None and last_update_gte is None:
            if order_type == "ASC":
                results = Companies.objects.all().order_by(order_by)[int((int(page) - 1) * int(per_page)):limit]

            elif order_type == "DESC":
                results = Companies.objects.all().order_by(order_by).reverse()[int((int(page) - 1) * int(per_page)):limit]

            pocet_vysledkov = Companies.objects.all().count()


    elif last_update_gte is None and last_update_lte is None:
            if order_type == "ASC":
                results = (Companies.objects.filter(
                    name__icontains=query) | Companies.objects.filter(address_line__icontains=query)).order_by(order_by)[
                          int((int(page) - 1) * int(per_page)):limit]

            elif order_type == "DESC":
                results = (Companies.objects.filter(
                   name__icontains=query) | Companies.objects.filter(address_line__icontains=query)).order_by(
                    order_by).reverse()[int((int(page) - 1) * int(per_page)):limit]

                pocet_vysledkov = (Companies.objects.filter(
                name__icontains=query)| Companies.objects.filter(address_line__icontains=query)).count()

    elif last_update_gte is not None and last_update_lte is not None:
            if order_type == "ASC":
                results = (Companies.objects.filter(
                    name__icontains=query) | Companies.objects.filter(address_line__icontains=query)) & Companies.objects.filter(
                    last_update__gte=last_update_gte) \
                          & Companies.objects.filter(last_update__lte=last_update_lte).order_by(
                    order_by)[int((int(page) - 1) * int(per_page)):limit]

            elif order_type == "DESC":
                results = (Companies.objects.filter(
                    name__icontains=query) | Companies.objects.filter(address_line__icontains=query)) & Companies.objects.filter(
                    last_update__gte=last_update_gte) \
                          & Companies.objects.filter(last_update__lte=last_update_lte).order_by(
                    order_by).reverse()[int((int(page) - 1) * int(per_page)):limit]

            pocet_vysledkov = ((Companies.objects.filter(
                name__icontains=query) | Companies.objects.filter(
                        address_line__icontains=query)) & Companies.objects.filter(
                last_update__gte=last_update_gte) \
                               & Companies.objects.filter(last_update__lte=last_update_lte)).count()


    for rows in results:
          zaznam = {
              "cin": rows.cin,
              "name": rows.name,
              "br_section": rows.br_section,
              "address_line": rows.address_line,
              "last_update": rows.last_update,
          }
          zaznamy.append(zaznam)


    pocet_stran = 0
    i = pocet_vysledkov
    while i > 0:
       pocet_stran = pocet_stran + 1
       i = i - per_page

    data = {
       "page": page,
       "per_page": per_page,
       "pages": pocet_stran,
       "total": pocet_vysledkov
    }

    prvy_slovnik = {
       "items": zaznamy
    }

    druhy_slovnik = {
       "metadata": data
    }

    treti_slovnik = prvy_slovnik.copy()
    treti_slovnik.update(druhy_slovnik)

    json_object = json.dumps(treti_slovnik, ensure_ascii=False, indent=4, separators=(',', ':'))
    return HttpResponse(json_object, status=200, content_type="application/json")

@csrf_exempt
def companies(request):
    conn = psycopg2.connect(host="localhost",
                            port="5432", dbname="postgres", user="postgres", password="1Neviemco123")
    cur = conn.cursor()
    zaznamy = []

    query = request.GET.get('query')
    last_update_gte = request.GET.get('last_update_gte')


    order_type = request.GET.get('order_type')
    if order_type is None:
        order_type = "DESC"

    order_by = request.GET.get('order_by')
    if order_by is None:
        order_by = "cin"

    last_update_lte = request.GET.get('last_update_lte')

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


    if query is None and last_update_lte is None and last_update_gte is None:
        cur.execute("SELECT firmy.cin, firmy.name, firmy.br_section, firmy.address_line, firmy.last_update, podanie_pocet.or_podanie_issues_count, znizenie_pocet.znizenie_imania_issues_count, "
                    "likvidator_pocet.likvidator_issues_count, vyrovnanie_pocet.konkurz_vyrovnanie_issues_count, konkurz_pocet.konkurz_restrukturalizacia_actors_count "
                    "FROM ov.companies as firmy "
                    "LEFT JOIN (SELECT COUNT(a.company_id) AS or_podanie_issues_count, a.company_id FROM ov.or_podanie_issues a GROUP BY a.company_id) as podanie_pocet "
                    "ON podanie_pocet.company_id = firmy.cin "
                    "LEFT JOIN (SELECT COUNT(b.company_id) AS likvidator_issues_count, b.company_id FROM ov.likvidator_issues b GROUP BY b.company_id) as likvidator_pocet "
                    "ON likvidator_pocet.company_id = firmy.cin "
                    "LEFT JOIN (SELECT COUNT(c.company_id) AS konkurz_vyrovnanie_issues_count, c.company_id from ov.konkurz_vyrovnanie_issues c GROUP BY c.company_id) as vyrovnanie_pocet "
                    "ON vyrovnanie_pocet.company_id = firmy.cin "
                    "LEFT JOIN (SELECT COUNT(d.company_id) AS znizenie_imania_issues_count, d.company_id from ov.znizenie_imania_issues d GROUP BY d.company_id) as znizenie_pocet "
                    "ON znizenie_pocet.company_id = firmy.cin LEFT JOIN (SELECT COUNT(e.company_id) AS konkurz_restrukturalizacia_actors_count, e.company_id from ov.konkurz_restrukturalizacia_actors e GROUP BY e.company_id) as konkurz_pocet "
                    "ON konkurz_pocet.company_id = firmy.cin "
                    "ORDER BY " + str(order_by) + " " + str(order_type) + " LIMIT " + str(per_page) + " OFFSET " + str((int(page) - 1) * int(per_page)) + " ;")

        vysledok_query = cur.fetchall()
        cur = conn.cursor()

        cur.execute("SELECT COUNT(cin) FROM ov.companies")

        pocet_vysledkov = cur.fetchone()


    elif last_update_gte is None and last_update_lte is None:
        cur.execute("SELECT firmy.cin, firmy.name, firmy.br_section, firmy.address_line, firmy.last_update, podanie_pocet.or_podanie_issues_count, znizenie_pocet.znizenie_imania_issues_count, "
                    "likvidator_pocet.likvidator_issues_count, vyrovnanie_pocet.konkurz_vyrovnanie_issues_count, konkurz_pocet.konkurz_restrukturalizacia_actors_count "
                    "FROM ov.companies as firmy "
                    "LEFT JOIN (SELECT COUNT(a.company_id) AS or_podanie_issues_count, a.company_id FROM ov.or_podanie_issues a GROUP BY a.company_id) as podanie_pocet "
                    "ON podanie_pocet.company_id = firmy.cin "
                    "LEFT JOIN (SELECT COUNT(b.company_id) AS likvidator_issues_count, b.company_id FROM ov.likvidator_issues b GROUP BY b.company_id) as likvidator_pocet "
                    "ON likvidator_pocet.company_id = firmy.cin "
                    "LEFT JOIN (SELECT COUNT(c.company_id) AS konkurz_vyrovnanie_issues_count, c.company_id from ov.konkurz_vyrovnanie_issues c GROUP BY c.company_id) as vyrovnanie_pocet "
                    "ON vyrovnanie_pocet.company_id = firmy.cin "
                    "LEFT JOIN (SELECT COUNT(d.company_id) AS znizenie_imania_issues_count, d.company_id from ov.znizenie_imania_issues d GROUP BY d.company_id) as znizenie_pocet "
                    "ON znizenie_pocet.company_id = firmy.cin "
                    "LEFT JOIN (SELECT COUNT(e.company_id) AS konkurz_restrukturalizacia_actors_count, e.company_id from ov.konkurz_restrukturalizacia_actors e GROUP BY e.company_id) as konkurz_pocet "
                    "ON konkurz_pocet.company_id = firmy.cin "
                    "WHERE CAST (name AS text) LIKE '%" + str(query) + "%' OR CAST(address_line AS text) LIKE '%" + str(query) + "%' "
                    "ORDER BY " + str(order_by) + " " + str(order_type) + "  LIMIT " + str(per_page) + " OFFSET " + str((int(page) - 1) * int(per_page)) + " ;")

        vysledok_query = cur.fetchall()

        cur = conn.cursor()
        cur.execute("SELECT COUNT(cin) FROM ov.companies WHERE CAST (name AS text) LIKE '%" + str(query) + "%' OR CAST(address_line AS text) LIKE '%" + str(query) + "%'")
        pocet_vysledkov = cur.fetchone()


    elif last_update_gte is not None and last_update_lte is not None:
        cur.execute("SELECT firmy.cin, firmy.name, firmy.br_section, firmy.address_line, firmy.last_update, podanie_pocet.or_podanie_issues_count, znizenie_pocet.znizenie_imania_issues_count, "
                    "likvidator_pocet.likvidator_issues_count, vyrovnanie_pocet.konkurz_vyrovnanie_issues_count, konkurz_pocet.konkurz_restrukturalizacia_actors_count "
                    "FROM ov.companies as firmy "
                    "LEFT JOIN (SELECT COUNT(a.company_id) AS or_podanie_issues_count, a.company_id FROM ov.or_podanie_issues a GROUP BY a.company_id) as podanie_pocet "
                    "ON podanie_pocet.company_id = firmy.cin "
                    "LEFT JOIN (SELECT COUNT(b.company_id) AS likvidator_issues_count, b.company_id FROM ov.likvidator_issues b GROUP BY b.company_id) as likvidator_pocet "
                    "ON likvidator_pocet.company_id = firmy.cin "
                    "LEFT JOIN (SELECT COUNT(c.company_id) AS konkurz_vyrovnanie_issues_count, c.company_id from ov.konkurz_vyrovnanie_issues c GROUP BY c.company_id) as vyrovnanie_pocet "
                    "ON vyrovnanie_pocet.company_id = firmy.cin "
                    "LEFT JOIN (SELECT COUNT(d.company_id) AS znizenie_imania_issues_count, d.company_id from ov.znizenie_imania_issues d GROUP BY d.company_id) as znizenie_pocet "
                    "ON znizenie_pocet.company_id = firmy.cin "
                    "LEFT JOIN (SELECT COUNT(e.company_id) AS konkurz_restrukturalizacia_actors_count, e.company_id from ov.konkurz_restrukturalizacia_actors e GROUP BY e.company_id) as konkurz_pocet "
                    "ON konkurz_pocet.company_id = firmy.cin "
                    "WHERE (CAST (name AS text) LIKE '%" + str(query) + "%' OR CAST(address_line AS text) LIKE '%" + str(query) +
                    "%') AND last_update BETWEEN '" + last_update_gte + "' AND '" + last_update_lte + "' ORDER BY " + str(order_by) + " " + str(order_type) + "  LIMIT " + str(per_page) + " "
                    "OFFSET " + str((int(page) - 1) * int(per_page)) + " ;")

        vysledok_query = cur.fetchall()

        cur = conn.cursor()
        cur.execute("SELECT COUNT(cin) FROM ov.companies WHERE (CAST (name AS text) LIKE '%" + str(query) + "%' "
        "OR CAST(address_line AS text) LIKE '%" + str(query) + "%') AND last_update BETWEEN '" + last_update_gte + "' AND '" + last_update_lte + "' ;")
        pocet_vysledkov = cur.fetchone()



    for row in vysledok_query:
            zaznam = {
                "cin": row[0],
                "name": row[1],
                "br_section": row[2],
                "address_line": row[3],
                "last_update": json.dumps(row[4], default=myconverter),
                "or_podanie_issues_count": row[5],
                "znizenie_imania_issues_count": row[6],
                "likvidator_issues_count": row[7],
                "konkurz_vyrovnanie_issues_count": row[8],
                "konkurz_restrukturalizacia_actors_count": row[9],
            };
            zaznamy.append(zaznam)

    pocet_stran = 0
    i = int(pocet_vysledkov[0])
    while i > 0:
        pocet_stran = pocet_stran + 1
        i = i - per_page

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

    treti_slovnik = prvy_slovnik.copy()
    treti_slovnik.update(druhy_slovnik)

    json_object = json.dumps(treti_slovnik, ensure_ascii=False, indent=4, separators=(',', ':'))

    return HttpResponse(json_object, status=200, content_type="application/json")


def home_view(request):
    return HttpResponse('Hello there')

def myconverter(o):
    if isinstance(o, datetime.date):
        return o.__str__()


@csrf_exempt
def vymaz(request, cislo_id):

    conn = psycopg2.connect(host="localhost",
                            port="5432", dbname="postgres", user="postgres", password="1Neviemco123")
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
    conn = psycopg2.connect(host="localhost",
                            port="5432", dbname="postgres", user="postgres", password="1Neviemco123")
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
              i = i - per_page

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

        treti_slovnik = prvy_slovnik.copy()
        treti_slovnik.update(druhy_slovnik)

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
