"""
Load testing for suggestions API endpoint.
Tests concurrent request handling and response time stability.
"""
import asyncio
import time
from typing import List
import httpx


BASE_URL = "http://localhost:8000"
ENDPOINT = "/api/v1/suggestions"


async def make_request(client: httpx.AsyncClient, query: str) -> dict:
    """
    Make a single suggestion request.

    Args:
        client: HTTP client
        query: Query text

    Returns:
        Response data with timing info
    """
    start = time.time()
    try:
        response = await client.post(
            f"{BASE_URL}{ENDPOINT}",
            json={"query": query},
            timeout=5.0
        )
        elapsed_ms = int((time.time() - start) * 1000)

        return {
            "status": response.status_code,
            "elapsed_ms": elapsed_ms,
            "query": query,
            "success": response.status_code == 200
        }
    except Exception as e:
        elapsed_ms = int((time.time() - start) * 1000)
        return {
            "status": 0,
            "elapsed_ms": elapsed_ms,
            "query": query,
            "success": False,
            "error": str(e)
        }


async def run_concurrent_test(num_requests: int, queries: List[str]) -> dict:
    """
    Run concurrent requests test.

    Args:
        num_requests: Number of concurrent requests
        queries: List of queries to test

    Returns:
        Test results with statistics
    """
    print(f"\n🔄 Running {num_requests} concurrent requests...")

    async with httpx.AsyncClient() as client:
        # Create tasks for concurrent requests
        tasks = []
        for i in range(num_requests):
            query = queries[i % len(queries)]
            tasks.append(make_request(client, query))

        # Execute all requests concurrently
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        total_time = time.time() - start_time

    # Calculate statistics
    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]
    response_times = [r["elapsed_ms"] for r in successful]

    stats = {
        "total_requests": num_requests,
        "successful": len(successful),
        "failed": len(failed),
        "total_time_sec": round(total_time, 2),
        "requests_per_sec": round(num_requests / total_time, 2),
        "avg_response_ms": round(sum(response_times) / len(response_times), 2) if response_times else 0,
        "min_response_ms": min(response_times) if response_times else 0,
        "max_response_ms": max(response_times) if response_times else 0,
        "p95_response_ms": round(sorted(response_times)[int(len(response_times) * 0.95)], 2) if response_times else 0,
        "p99_response_ms": round(sorted(response_times)[int(len(response_times) * 0.99)], 2) if response_times else 0
    }

    return stats


async def main():
    """Run load tests."""
    print("=" * 60)
    print("Suggestions API Load Test")
    print("=" * 60)

    # Test queries
    queries = [
        "park",
        "paspo",
        "rijbe",
        "verhu",
        "geboo",
        "huwe",
        "overl",
        "uitke",
        "afval",
        "water"
    ]

    # Test 1: 10 concurrent requests
    print("\n📊 Test 1: 10 concurrent requests")
    stats1 = await run_concurrent_test(10, queries)
    print(f"✓ Success rate: {stats1['successful']}/{stats1['total_requests']}")
    print(f"✓ Throughput: {stats1['requests_per_sec']} req/s")
    print(f"✓ Avg response: {stats1['avg_response_ms']}ms")
    print(f"✓ P95 response: {stats1['p95_response_ms']}ms")
    print(f"✓ P99 response: {stats1['p99_response_ms']}ms")

    # Wait a bit between tests
    await asyncio.sleep(2)

    # Test 2: 50 concurrent requests
    print("\n📊 Test 2: 50 concurrent requests")
    stats2 = await run_concurrent_test(50, queries)
    print(f"✓ Success rate: {stats2['successful']}/{stats2['total_requests']}")
    print(f"✓ Throughput: {stats2['requests_per_sec']} req/s")
    print(f"✓ Avg response: {stats2['avg_response_ms']}ms")
    print(f"✓ P95 response: {stats2['p95_response_ms']}ms")
    print(f"✓ P99 response: {stats2['p99_response_ms']}ms")

    # Wait a bit between tests
    await asyncio.sleep(2)

    # Test 3: 100 concurrent requests (stress test)
    print("\n📊 Test 3: 100 concurrent requests (stress test)")
    stats3 = await run_concurrent_test(100, queries)
    print(f"✓ Success rate: {stats3['successful']}/{stats3['total_requests']}")
    print(f"✓ Throughput: {stats3['requests_per_sec']} req/s")
    print(f"✓ Avg response: {stats3['avg_response_ms']}ms")
    print(f"✓ P95 response: {stats3['p95_response_ms']}ms")
    print(f"✓ P99 response: {stats3['p99_response_ms']}ms")

    # Summary
    print("\n" + "=" * 60)
    print("📋 Summary")
    print("=" * 60)

    all_passed = True

    # Check P95 < 200ms requirement
    if stats3['p95_response_ms'] < 200:
        print(f"✅ P95 response time: {stats3['p95_response_ms']}ms < 200ms (PASS)")
    else:
        print(f"❌ P95 response time: {stats3['p95_response_ms']}ms >= 200ms (FAIL)")
        all_passed = False

    # Check success rate > 99%
    success_rate = (stats3['successful'] / stats3['total_requests']) * 100
    if success_rate > 99:
        print(f"✅ Success rate: {success_rate:.1f}% > 99% (PASS)")
    else:
        print(f"❌ Success rate: {success_rate:.1f}% <= 99% (FAIL)")
        all_passed = False

    # Check concurrent handling (10+ req/s)
    if stats3['requests_per_sec'] >= 10:
        print(f"✅ Throughput: {stats3['requests_per_sec']} req/s >= 10 (PASS)")
    else:
        print(f"❌ Throughput: {stats3['requests_per_sec']} req/s < 10 (FAIL)")
        all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All load tests PASSED!")
    else:
        print("⚠️  Some load tests FAILED")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
