from fastapi import APIRouter

from services.fuel_updater import fuel_cache

router = APIRouter()


@router.get("/fuel")
def get_fuel():
    return fuel_cache