import asyncio


class Server(asyncio.Protocol):
    def connection_made(self, transport):
        print('Connection from {}'.format(transport.get_extra_info('peername')))
        print('Server host:', transport.get_extra_info('sockname'))
        self.transport = transport

    def data_received(self, data):
        message = data.decode()
        try:
            numbers = [int(value.strip()) for value in message.split(',')]
            result = sum(numbers)
            if result > 100:
                raise ValueError('Sum of numbers must be less than 100')

            self.transport.write(str(result).encode())

        except ValueError as e:
            print(e)
            self.transport.write(str(e).encode())
        finally:
            self.transport.close()


async def run_server(shutdown_event):
    loop = asyncio.get_running_loop()

    server = await loop.create_server(
        lambda: Server(),
        '127.0.0.1', 8888
    )

    async with server:
        while not shutdown_event.is_set():
            await asyncio.sleep(1)
        server.close()
        await server.wait_closed()

if __name__ == '__main__':
    shutdown_event = asyncio.Event()
    asyncio.run(run_server(shutdown_event))
