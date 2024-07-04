import asyncio
import threading
import pytest
from client import run_client
from server import run_server

pytest_plugins = ('pytest_asyncio',)


def _run_server(stop_event):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    shutdown_event = asyncio.Event()
    server_task = loop.create_task(run_server(shutdown_event))

    try:
        while not stop_event.is_set():
            loop.run_until_complete(asyncio.sleep(1))
    finally:
        loop.call_soon_threadsafe(shutdown_event.set)
        loop.run_until_complete(server_task)
        loop.close()


@pytest.fixture(scope='session', autouse=True)
def setup():
    stop_event = threading.Event()
    thread = threading.Thread(target=_run_server, args=(stop_event,))
    thread.start()
    yield
    stop_event.set()
    thread.join()


class TestSumOfNumbers:
    @pytest.mark.asyncio
    async def test_sum_of_numbers_less_than_100(self, setup):
        assert await run_client(50, 15) == 65

    @pytest.mark.asyncio
    async def test_sum_of_numbers_equal_to_100(self, setup):
        assert await run_client(50, 50) == 100

    @pytest.mark.asyncio
    async def test_sum_of_numbers_equal_to_101(self, setup):
        with pytest.raises(ValueError, match='Sum of numbers must be less than 100'):
            await run_client(50, 55)

    @pytest.mark.asyncio
    async def test_sum_of_numbers_equal_to_0(self, setup):
        assert await run_client(0, 0) == 0

    @pytest.mark.asyncio
    async def test_sum_of_negative_numbers(self, setup):
        with pytest.raises(ValueError, match='Message values must be positive integers'):
            await run_client(-50, -50)

    @pytest.mark.asyncio
    async def test_sum_of_numbers_greater_than_100(self, setup):
        with pytest.raises(ValueError, match='Sum of numbers must be less than 100'):
            await run_client(50, 51)

    @pytest.mark.asyncio
    async def test_invalid_message(self, setup):
        with pytest.raises(ValueError, match='Message values must be positive integers'):
            await run_client(50, 'fifty')

    @pytest.mark.asyncio
    async def test_sum_of_floats(self, setup):
        with pytest.raises(ValueError, match='Message values must be positive integers'):
            await run_client(50.5, 15.5)

    @pytest.mark.asyncio
    async def test_sum_of_numbers_with_extra_values(self, setup):
        with pytest.raises(ValueError, match='Message must have 2 values separated by a comma'):
            await run_client(50, (15, 10))

    @pytest.mark.asyncio
    async def test_multiple_clients(self, setup):
        assert await run_client(86, 10) == 96
        assert await run_client(34, 45) == 79
        assert await run_client(1, 0) == 1
