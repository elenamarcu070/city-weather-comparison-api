from django.shortcuts import render
from django.http import JsonResponse
from .services import build_city_bundle, compare_bundles


def home(request):
    return render(request, "cityinfo/home.html")


def compare_cities(request):
    if request.method == "POST":
        city1 = request.POST.get("city1")
        city2 = request.POST.get("city2")

        bundle1 = build_city_bundle(city1)
        bundle2 = build_city_bundle(city2)

        if not bundle1 or not bundle2:
            return JsonResponse({"error": "Oraș invalid"}, status=400)

        comparison = compare_bundles(bundle1, bundle2)

        return JsonResponse({
            "city1": bundle1,
            "city2": bundle2,
            "comparison": comparison
        })

    return JsonResponse({"error": "Invalid request"}, status=400)