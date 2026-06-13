from __future__ import annotations

import httpx
import pytest

from roamwise.adapters.maps import AmapClient, MissingAmapApiKeyError
from roamwise.core.models import GeoPoint, RouteMode


@pytest.mark.asyncio
async def test_amap_geocode_normalizes_first_result() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v3/geocode/geo"
        assert request.url.params["key"] == "test-key"
        assert request.url.params["address"] == "西湖"
        return httpx.Response(
            200,
            json={
                "status": "1",
                "info": "OK",
                "geocodes": [
                    {
                        "formatted_address": "浙江省杭州市西湖区西湖",
                        "location": "120.155070,30.274085",
                    }
                ],
            },
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        client = AmapClient(
            api_key="test-key",
            http_client=http_client,
            base_url="https://example.test",
        )
        point = await client.geocode("西湖")

    assert point.longitude == 120.155070
    assert point.latitude == 30.274085
    assert point.label == "浙江省杭州市西湖区西湖"


@pytest.mark.asyncio
async def test_amap_driving_route_normalizes_first_path() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v3/direction/driving"
        assert request.url.params["origin"] == "121.4737,31.2304"
        return httpx.Response(
            200,
            json={
                "status": "1",
                "info": "OK",
                "route": {
                    "taxi_cost": "120.5",
                    "paths": [
                        {
                            "distance": "194000",
                            "duration": "8400",
                            "strategy": "速度优先",
                        }
                    ],
                },
            },
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        client = AmapClient(
            api_key="test-key",
            http_client=http_client,
            base_url="https://example.test",
        )
        route = await client.route_driving(
            GeoPoint(longitude=121.4737, latitude=31.2304),
            GeoPoint(longitude=120.1551, latitude=30.2741),
        )

    assert route.mode == RouteMode.DRIVING
    assert route.distance_meters == 194000
    assert route.duration_minutes == 140
    assert route.cost_estimate == 120.5
    assert route.evidence[0].source_name == "Amap"


@pytest.mark.asyncio
async def test_amap_transit_route_normalizes_first_option() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v3/direction/transit/integrated"
        return httpx.Response(
            200,
            json={
                "status": "1",
                "info": "OK",
                "route": {
                    "transits": [
                        {
                            "distance": "42000",
                            "duration": "5400",
                            "cost": "8",
                            "segments": [
                                {
                                    "walking": {"distance": "450"},
                                    "bus": {"buslines": [{"name": "地铁1号线"}]},
                                },
                                {
                                    "walking": {"distance": "300"},
                                    "bus": {"buslines": [{"name": "地铁2号线"}]},
                                },
                            ],
                        }
                    ]
                },
            },
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        client = AmapClient(
            api_key="test-key",
            http_client=http_client,
            base_url="https://example.test",
        )
        route = await client.route_transit(
            GeoPoint(longitude=121.4737, latitude=31.2304),
            GeoPoint(longitude=120.1551, latitude=30.2741),
            city="上海",
            destination_city="杭州",
        )

    assert route.mode == RouteMode.TRANSIT
    assert route.distance_meters == 42000
    assert route.duration_minutes == 90
    assert route.transfer_count == 1
    assert route.walking_distance_meters == 750
    assert route.route_summary == "地铁1号线 -> 地铁2号线"


@pytest.mark.asyncio
async def test_amap_requires_api_key() -> None:
    client = AmapClient(api_key="")
    with pytest.raises(MissingAmapApiKeyError):
        await client.geocode("西湖")
