from django.shortcuts import render
from django.http import JsonResponse
from .services import (
    obtine_coordonate,
    obtine_vreme,
    obtine_calitate_aer,
    obtine_informatii_tara,
    obtine_imagine,
    calculeaza_scoruri
)


# -------------------------------------------------
# PAGINA PRINCIPALĂ
# -------------------------------------------------
def pagina_principala(request):
    return render(request, "cityinfo/home.html")


# -------------------------------------------------
# FUNCȚIA DE COMPARAȚIE
# -------------------------------------------------
def compara_orase(request):

    if request.method == "POST":

        oras1 = request.POST.get("city1")
        oras2 = request.POST.get("city2")

        date1 = construieste_pachet_oras(oras1)
        date2 = construieste_pachet_oras(oras2)

        if not date1 or not date2:
            return JsonResponse({"error": "Oraș invalid"}, status=400)

        rezultat = compara_pachete(date1, date2)

        return JsonResponse({
            "oras1": date1,
            "oras2": date2,
            "rezultat": rezultat
        })

    return JsonResponse({"error": "Metodă invalidă"}, status=400)


# -------------------------------------------------
# CONSTRUIEȘTE DATE COMPLETE PENTRU UN ORAȘ
# -------------------------------------------------
def construieste_pachet_oras(nume_oras):

    coordonate = obtine_coordonate(nume_oras)
    if not coordonate:
        return None

    informatii_tara = obtine_informatii_tara(coordonate["cod_tara"])

    vreme_oras = obtine_vreme(
        lat=coordonate["lat"],
        lon=coordonate["lon"]
    )

    aer_oras = obtine_calitate_aer(
        coordonate["lat"],
        coordonate["lon"]
    )

    imagine_oras = obtine_imagine(nume_oras)

    scoruri_oras = calculeaza_scoruri(
        vreme_oras["temperatura"],
        aer_oras["pm25"],
        informatii_tara["populatie"]
    )

    # CAPITALA


    # Obținem coordonatele capitalei
    coordonate_capitala = obtine_coordonate(informatii_tara["capitala"])

    vreme_capitala = obtine_vreme(
        lat=coordonate_capitala["lat"],
        lon=coordonate_capitala["lon"]
    )
    
    # Obținem aer pentru capitală
    aer_capitala = obtine_calitate_aer(
        coordonate_capitala["lat"],
        coordonate_capitala["lon"]
)

    imagine_capitala = obtine_imagine(
        informatii_tara["capitala"]
    )

    scoruri_capitala = calculeaza_scoruri(
        vreme_capitala["temperatura"],
        aer_oras["pm25"],
        None
    )

    return {
        "oras": {
            "raw": {
                "lat": coordonate["lat"],
                "lon": coordonate["lon"],
                "cod_tara": coordonate["cod_tara"],
                "temperatura": vreme_oras["temperatura"],
                "pm25": aer_oras["pm25"],
                "populatie": informatii_tara["populatie"]
            },
            "meta": {
                "nume": nume_oras,
                "moneda": informatii_tara["moneda"],
                "imagine": imagine_oras
            },
            "procesare": scoruri_oras
        },
        "capitala": {
            "raw": {
                "nume": informatii_tara["capitala"],
                "temperatura": vreme_capitala["temperatura"],
                "pm25": aer_capitala["pm25"],
                "populatie": informatii_tara["populatie"]
            },
            "meta": {
                "imagine": imagine_capitala
            },
            "procesare": scoruri_capitala
        }
    }


# -------------------------------------------------
# COMPARĂ SCORURILE
# -------------------------------------------------
def compara_pachete(p1, p2):

    castigator_oras = (
        p1["oras"]["meta"]["nume"]
        if p1["oras"]["procesare"]["total"] >
           p2["oras"]["procesare"]["total"]
        else p2["oras"]["meta"]["nume"]
    )

    castigator_capitala = (
        p1["capitala"]["raw"]["nume"]
        if p1["capitala"]["procesare"]["total"] >
           p2["capitala"]["procesare"]["total"]
        else p2["capitala"]["raw"]["nume"]
    )

    return {
        "oras_castigator": castigator_oras,
        "capitala_castigatoare": castigator_capitala
    }